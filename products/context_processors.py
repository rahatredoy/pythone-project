from .models import Category


def shop_context(request):
    """Values that every template can use (navbar cart badge, category menu, footer)."""
    cart = request.session.get('cart', {})
    return {
        'cart_count': sum(cart.values()),
        'wishlist_ids': request.session.get('wishlist', []),
        'all_categories': Category.objects.all(),
    }
