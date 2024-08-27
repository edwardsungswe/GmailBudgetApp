
# transactions/views.py
from django.shortcuts import render
from .models import Transaction

def dashboard(request):
    transactions = Transaction.objects.all()  # Fetch all transactions
    return render(request, 'dashboard.html', {'transactions': transactions})
