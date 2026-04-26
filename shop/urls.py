#Shop URLs

from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('support/',                        views.support,             name='support'),
    path('cart/',                           views.cart,                name='cart'),
    path('checkout/',                       views.checkout,            name='checkout'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation,  name='order_confirmation'),
    path('add/<int:product_id>/',           views.add_to_cart,         name='add_to_cart'),
    path('remove/<int:item_id>/',           views.remove_from_cart,    name='remove_from_cart'),
    path('wishlist/<int:product_id>/',      views.toggle_wishlist,     name='toggle_wishlist'),
    path('product/<int:product_id>/detail/', views.product_detail_ajax, name='product_detail'),
]
