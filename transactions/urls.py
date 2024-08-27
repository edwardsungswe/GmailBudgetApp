# transactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  # URL for the dashboard
    # Other URLs...
]
