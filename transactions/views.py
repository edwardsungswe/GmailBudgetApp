from django.shortcuts import render
from django.views.generic import FormView
from django.urls import reverse_lazy
from .models import Transaction, EmailFilter  # Ensure EmailFilter is imported
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from .forms import EmailFilterForm  # Import the EmailFilterForm

from django.views import View
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

class EditEmailFiltersView(FormView):
    template_name = 'emailFilter.html'  # The template for editing email filters
    form_class = EmailFilterForm  # Use the EmailFilterForm to handle user input
    success_url = reverse_lazy('transactions:dashboard')  # Redirect back to dashboard after success

    def form_valid(self, form):
        # Simply save the form data without linking it to a user
        form.save()
        return super().form_valid(form)



class SyncEmailsView(View):
    def post(self, request):
        date_range = request.POST.get('date_range')
        end_date = timezone.now()
        
        if date_range == 'all':
            start_date = None
        else:
            days_back = int(date_range)
            start_date = end_date - timedelta(days=days_back)
        
        # Fetch email filters
        email_filters = EmailFilter.objects.all()
        
        # Your logic to pull emails using the Gmail API based on the filters and date range
        # Assuming you have a function fetch_emails(filters, start_date, end_date)
        new_transactions = fetch_emails(email_filters, start_date, end_date)
        
        # Save new transactions to the database
        for transaction_data in new_transactions:
            Transaction.objects.create(**transaction_data)
        
        return redirect('transactions:dashboard')

def fetch_emails(email_filters, start_date, end_date):
    # Your logic to pull emails using the Gmail API based on the filters and date range
    # This is a placeholder function that returns dummy data
    print(email_filters)
    return [
        {'amount': 100.0, 'date': '2021-06-01', 'description': 'Electricity Bill', 'category': 'utilities', 'vendor': 'ABC Electric'},
        {'amount': 50.0, 'date': '2021-06-05', 'description': 'Grocery Shopping', 'category': 'groceries', 'vendor': 'XYZ Supermarket'},
    ]
def dashboard(request):
    transactions = Transaction.objects.all().order_by('date')  # Ascending order (oldest first)
    # Prepare data for the chart
    chart_data = defaultdict(lambda: {'dates': [], 'amounts': []})

    for transaction in transactions:
        chart_data[transaction.vendor]['dates'].append(str(transaction.date))
        chart_data[transaction.vendor]['amounts'].append(float(transaction.amount))  # Convert Decimal to float

    # Convert defaultdict to a regular dict and then to JSON
    chart_data = json.dumps(chart_data)
    return render(request, 'dashboard.html', {'chart_data': chart_data, 'transactions': transactions})


