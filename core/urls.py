# core/urls.py

from django.urls import path
from . import views

app_name = 'core'  # Define the namespace

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    # Add other URLs as needed
]
