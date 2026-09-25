"""
Customer website views (the shop that visitors see).

A view is a Python function that:
  1. receives a request,
  2. talks to the database using the Django ORM,
  3. returns a rendered template (HTML page).

The dark admin panel views are in admin_views.py.
"""
from decimal import Decimal

from django.contrib import messages
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product


# ------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------

def home(request):
    """Home page: hero slider, categories, featured, best selling and all products."""
    featured_products = Product.objects.filter(is_featured=True)[:6]

    # Best selling = products with the most units sold in orders.
    # Products never ordered (sold = NULL) come last, then sorted by number of reviews.
    best_selling = (
        Product.objects
        .annotate(sold=Sum('orderitem__quantity'))
        .order_by(F('sold').desc(nulls_last=True), '-review_count')[:6]
    )

    # every product in the database (newest first), shown in a grid at the bottom
    all_products = Product.objects.select_related('category')

    return render(request, 'customer/home.html', {
        'featured_products': featured_products,
        'best_selling': best_selling,
        'all_products': all_products,
    })


def product_list(request):
    """All Products page. Can be filtered by category: /products/?category=2"""
    products = Product.objects.all()
    selected_category = None

    category_id = request.GET.get('category')
    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=selected_category)

    return render(request, 'customer/product_list.html', {
        'products': products,
        'selected_category': selected_category,
        'page_title': selected_category.name if selected_category else 'All Products',
    })


def search(request):
    """Search products by name: /search/?q=laptop"""
    query = request.GET.get('q', '').strip()

    if query:
        # SQL: SELECT * FROM product WHERE name ILIKE '%laptop%'
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.none()

    return render(request, 'customer/product_list.html', {
        'products': products,
        'query': query,
        'page_title': f'Search results for "{query}"',
    })


def category_list(request):
    """Categories page. The categories themselves come from the context processor."""
    return render(request, 'customer/categories.html')


def product_detail(request, pk):
    """Product details page: /product/5/"""
    product = get_object_or_404(Product, pk=pk)

    # related products = other products in the same category
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:6]

    return render(request, 'customer/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


# ------------------------------------------------------------------
# Shopping cart (stored in the session, no login needed)
#
# request.session['cart'] looks like:  {'5': 2, '12': 1}
#                                       product id -> quantity
# ------------------------------------------------------------------

def get_cart_items(request):
    """Read the cart from the session and return a list of items + total."""
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    items = []
    total = Decimal('0')
    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total += subtotal
        items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return items, total


def set_cart_quantity(request, product, quantity):
    """Put `quantity` of a product in the cart (never more than the stock).
    A quantity of 0 removes the product from the cart."""
    cart = request.session.get('cart', {})
    quantity = min(quantity, product.stock_quantity)
    if quantity > 0:
        cart[str(product.id)] = quantity
    else:
        cart.pop(str(product.id), None)
    request.session['cart'] = cart


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        if not product.in_stock:
            messages.error(request, f'Sorry, "{product.name}" is out of stock.')
            return redirect('product_detail', pk=pk)

        already_in_cart = request.session.get('cart', {}).get(str(pk), 0)
        set_cart_quantity(request, product, already_in_cart + int(request.POST.get('quantity', 1)))
        messages.success(request, f'"{product.name}" was added to your cart.')

    # go back to the page the user came from
    return redirect(request.POST.get('next') or 'cart')


def cart_update(request, pk):
    """Change the quantity on the cart page. The remove button sends quantity 0."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        set_cart_quantity(request, product, int(request.POST.get('quantity', 1)))
    return redirect('cart')


def cart_view(request):
    items, total = get_cart_items(request)
    return render(request, 'customer/cart.html', {'items': items, 'total': total})


def checkout(request):
    """Show the checkout form. On submit, create an Order and its OrderItems."""
    items, total = get_cart_items(request)
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 1. create the order (INSERT INTO order ...)
            order = Order.objects.create(total_price=total, **form.cleaned_data)

            # 2. create one OrderItem per cart line and reduce stock
            for item in items:
                product = item['product']
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=item['quantity'],
                )
                product.stock_quantity -= item['quantity']
                product.save()

            # 3. empty the cart
            request.session['cart'] = {}
            return render(request, 'customer/order_success.html', {'order': order})
    else:
        form = CheckoutForm()

    return render(request, 'customer/checkout.html', {'form': form, 'items': items, 'total': total})


# ------------------------------------------------------------------
# Wishlist (also stored in the session): request.session['wishlist'] = [3, 7]
# ------------------------------------------------------------------

def wishlist_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        wishlist = request.session.get('wishlist', [])
        if pk in wishlist:
            wishlist.remove(pk)
            messages.info(request, f'"{product.name}" was removed from your wishlist.')
        else:
            wishlist.append(pk)
            messages.success(request, f'"{product.name}" was added to your wishlist.')
        request.session['wishlist'] = wishlist
    return redirect(request.POST.get('next') or 'wishlist')


def wishlist_view(request):
    products = Product.objects.filter(id__in=request.session.get('wishlist', []))
    return render(request, 'customer/product_list.html', {
        'products': products,
        'page_title': 'My Wishlist',
        'is_wishlist': True,
    })
