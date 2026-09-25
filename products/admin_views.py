"""
Custom dark admin panel views (/admin-panel/).

Only staff users (is_staff=True) can open these pages.
Create one with:  python manage.py createsuperuser
"""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Max, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, ProductForm
from .models import Category, Order, Product


def is_admin(user):
    return user.is_active and user.is_staff


# Decorator: if the user is not an admin, send them to the admin login page.
admin_required = user_passes_test(is_admin)   # login page = LOGIN_URL in settings.py


# ------------------------------------------------------------------
# Login / Logout
# ------------------------------------------------------------------

def admin_login(request):
    if is_admin(request.user):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and is_admin(user):
            login(request, user)
            return redirect(request.GET.get('next') or 'dashboard')
        messages.error(request, 'Invalid username or password (or you are not an admin).')

    return render(request, 'admin_panel/login.html')


def admin_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('admin_login')


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------

@admin_required
def dashboard(request):
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': Order.objects.count(),
        # a customer = a unique email address that placed an order
        'total_customers': Order.objects.values('email').distinct().count(),
        'recent_products': Product.objects.select_related('category')[:6],
        'recent_orders': Order.objects.all()[:5],
        'out_of_stock': Product.objects.filter(stock_quantity=0).count(),
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ------------------------------------------------------------------
# Products: CRUD
# ------------------------------------------------------------------

@admin_required
def products(request):
    """READ: list products with search and category filter."""
    product_list = Product.objects.select_related('category')

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')

    if query:
        product_list = product_list.filter(name__icontains=query)
    if category_id:
        product_list = product_list.filter(category_id=category_id)

    return render(request, 'admin_panel/products.html', {
        'products': product_list,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_id,
    })


@admin_required
def product_form(request, pk=None):
    """CREATE and UPDATE with the same form.
    /products/add/      -> pk is None -> empty form, save = INSERT
    /products/5/edit/   -> pk is 5    -> form filled with product 5, save = UPDATE"""
    product = get_object_or_404(Product, pk=pk) if pk else None

    if request.method == 'POST':
        # request.FILES contains the uploaded images
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            saved = form.save()
            messages.success(request, f'Product "{saved.name}" was {"updated" if product else "added"}.')
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin_panel/add_product.html', {
        'form': form,
        'product': product,
        'title': 'Edit Product' if product else 'Add Product',
    })


@admin_required
def product_delete(request, pk):
    """DELETE: only accepts POST so a product cannot be deleted by just opening a link."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" was deleted.')
    return redirect(request.POST.get('next') or 'admin_products')


# ------------------------------------------------------------------
# Categories
# ------------------------------------------------------------------

@admin_required
def categories(request, pk=None):
    """List categories (with product count). The form on the right side
    adds a new category, or edits one when pk is given (/categories/3/edit/)."""
    category = get_object_or_404(Category, pk=pk) if pk else None

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            saved = form.save()
            messages.success(request, f'Category "{saved.name}" was {"updated" if category else "added"}.')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)

    # annotate adds a "product_count" value to every category (SQL COUNT + GROUP BY)
    category_list = Category.objects.annotate(product_count=Count('products')).order_by('id')

    return render(request, 'admin_panel/categories.html', {
        'categories': category_list,
        'form': form,
        'editing': category,
    })


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        if category.products.exists():
            messages.error(request, f'"{category.name}" still has products. Move or delete them first.')
        else:
            category.delete()
            messages.success(request, f'Category "{category.name}" was deleted.')
    return redirect('admin_categories')


# ------------------------------------------------------------------
# Orders
# ------------------------------------------------------------------

@admin_required
def orders(request):
    order_list = Order.objects.annotate(item_count=Sum('items__quantity'))

    status = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()
    if status:
        order_list = order_list.filter(status=status)
    if query:
        order_list = order_list.filter(Q(customer_name__icontains=query) | Q(email__icontains=query))

    return render(request, 'admin_panel/orders.html', {
        'orders': order_list,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status,
        'query': query,
    })


@admin_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    # the admin can change the order status
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} is now "{new_status}".')
        return redirect('admin_order_detail', pk=order.pk)

    return render(request, 'admin_panel/order_detail.html', {
        'order': order,
        'items': order.items.all(),
        'status_choices': Order.STATUS_CHOICES,
    })


# ------------------------------------------------------------------
# Customers (people who placed orders, grouped by email)
# ------------------------------------------------------------------

@admin_required
def customers(request):
    customer_list = (
        Order.objects
        .values('email')                      # GROUP BY email
        .annotate(
            name=Max('customer_name'),
            phone=Max('phone'),
            order_count=Count('id'),
            total_spent=Sum('total_price'),
            last_order=Max('created_date'),
        )
        .order_by('-last_order')
    )

    query = request.GET.get('q', '').strip()
    if query:
        customer_list = customer_list.filter(Q(customer_name__icontains=query) | Q(email__icontains=query))

    return render(request, 'admin_panel/customers.html', {'customers': customer_list, 'query': query})
