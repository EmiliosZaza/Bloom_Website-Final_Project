from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('review/<int:product_id>/', views.submit_review, name='review'),
]
