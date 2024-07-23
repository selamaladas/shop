from django.urls import path
from django.views.generic import RedirectView

from . import views
urlpatterns = [
    path('', views.index, name='index'),
    # users
    path('users/', views.users, name='users'),
    path('user', views.store_user, name='store_user'),
    path('user/<int:user_id>/', views.user, name='user'),
    path('user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    # products
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product, name='product'),
    path('search/', views.search, name='search'),
    path('search/<q>', views.search, name='search'),
    # categories
    path('categories/', views.categories, name='categories'),
    path('category/<int:category_id>/', views.category, name='category'),
    # cart
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('track_order/', views.track_order, name='track_order'),
    path('order/', views.make_order, name='make_order'),
    path('orders/', views.client_orders, name='orders'),
    # authentication
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/register/', views.user_register, name='register'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('accounts/reset_password/', views.reset_password, name='reset_password'),
]

