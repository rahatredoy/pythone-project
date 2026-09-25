from django.urls import path

from . import admin_views, views

urlpatterns = [
    # ---------------- Customer website ----------------
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('search/', views.search, name='search'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:pk>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),

    # ---------------- Custom admin panel ----------------
    path('admin-panel/login/', admin_views.admin_login, name='admin_login'),
    path('admin-panel/logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin-panel/', admin_views.dashboard, name='dashboard'),

    path('admin-panel/products/', admin_views.products, name='admin_products'),
    path('admin-panel/products/add/', admin_views.product_form, name='admin_product_add'),
    path('admin-panel/products/<int:pk>/edit/', admin_views.product_form, name='admin_product_edit'),
    path('admin-panel/products/<int:pk>/delete/', admin_views.product_delete, name='admin_product_delete'),

    path('admin-panel/categories/', admin_views.categories, name='admin_categories'),
    path('admin-panel/categories/<int:pk>/edit/', admin_views.categories, name='admin_category_edit'),
    path('admin-panel/categories/<int:pk>/delete/', admin_views.category_delete, name='admin_category_delete'),

    path('admin-panel/orders/', admin_views.orders, name='admin_orders'),
    path('admin-panel/orders/<int:pk>/', admin_views.order_detail, name='admin_order_detail'),

    path('admin-panel/customers/', admin_views.customers, name='admin_customers'),
]
