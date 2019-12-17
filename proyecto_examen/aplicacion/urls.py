"""
    urls logic
"""
from django.urls import path

# from datamodel import views
from aplicacion import views

urlpatterns = [
    path('productora/', views.productora, name='productora'),
]