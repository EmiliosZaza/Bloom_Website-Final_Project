#Admin panel URLs — staff only

from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('',                             views.dashboard,        name='dashboard'),

    # Products
    path('products/',                    views.products,         name='products'),
    path('products/add/',                views.product_add,      name='product_add'),
    path('products/<int:product_id>/edit/',   views.product_edit,   name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    # Categories
    path('categories/',                  views.categories,       name='categories'),
    path('categories/add/',              views.category_add,     name='category_add'),
    path('categories/<int:cat_id>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:cat_id>/subcategory/add/', views.subcategory_add, name='subcategory_add'),

    # Users
    path('users/',                       views.users,            name='users'),
    path('users/<int:user_id>/toggle-staff/', views.user_toggle_staff, name='user_toggle_staff'),
    path('users/<int:user_id>/delete/',  views.user_delete,      name='user_delete'),
]