# transactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),  # URL for the dashboard
    path('editEmailFilter/', views.EditEmailFiltersView.as_view(), name='edit_emails'),
    path('syncEmails/', views.SyncEmailsView.as_view(), name='sync_emails'),

]


