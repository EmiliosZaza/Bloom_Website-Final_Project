"""
Accounts URLs — auth and profile
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',        views.login_view,   name='login'),
    path('register/',     views.register_view, name='register'),
    path('logout/',       views.logout_view,  name='logout'),
    path('profile/',      views.profile,      name='profile'),
    path('dashboard/',    views.dashboard,    name='dashboard'),
    path('view/<int:product_id>/', views.record_view, name='record_view'),
]
