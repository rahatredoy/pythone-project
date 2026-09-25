"""
Main URL configuration of MiniShop.

/                -> customer website + admin panel (products/urls.py)
/admin/          -> shortcut that opens the MiniShop admin panel
/media/...       -> uploaded product images (only while DEBUG=True)
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', RedirectView.as_view(pattern_name='dashboard')),
    path('', include('products.urls')),
]

# Serve uploaded images during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
