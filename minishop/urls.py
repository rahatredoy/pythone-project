"""
Main URL configuration of MiniShop.

/                -> customer website + admin panel (products/urls.py)
/admin/          -> shortcut that opens the MiniShop admin panel
/media/...       -> uploaded product images
"""
from django.conf import settings
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path('admin/', RedirectView.as_view(pattern_name='dashboard')),
    path('', include('products.urls')),

    # Serve uploaded product images (also on the server, where DEBUG is False)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
