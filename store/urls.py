from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path(
        'product/<int:id>/',
        views.product_detail,
        name='product_detail'
    ),

    path(
        'category/<int:id>/',
        views.category_products,
        name='category_products'
    ),

    path(
        'cart/',
        views.cart,
        name='cart'
    ),

    path(
        'add-to-cart/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path(
        'increase/<int:id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),

    path(
        'decrease/<int:id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),

    path(
        'remove/<int:id>/',
        views.remove_item,
        name='remove_item'
    ),

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'orders/',
        views.orders,
        name='orders'
    ),

    path(
        'order/<int:id>/',
        views.order_detail,
        name='order_detail'
    ),

    path(
        'order-success/',
        views.order_success,
        name='order_success'
    ),

    path(
        'wishlist/',
        views.wishlist,
        name='wishlist'
    ),

    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    path(
        'add-to-wishlist/<int:id>/',
        views.add_to_wishlist,
        name='add_to_wishlist'
    ),

    path(
        'remove-from-wishlist/<int:id>/',
        views.remove_from_wishlist,
        name='remove_from_wishlist'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'compare/',
        views.compare_products,
        name='compare_products'
    ),

    path(
        'media-debug/',
        views.media_check,
        name='media_check'
    ),
]

