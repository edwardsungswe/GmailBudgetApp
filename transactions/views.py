from django.shortcuts import render
from .models import Transaction
from collections import defaultdict
import json

def dashboard(request):
    transactions = Transaction.objects.all().order_by('date')  # Ascending order (oldest first)
    # Prepare data for the chart
    chart_data = defaultdict(lambda: {'dates': [], 'amounts': []})

    for transaction in transactions:
        chart_data[transaction.vendor]['dates'].append(str(transaction.date))
        chart_data[transaction.vendor]['amounts'].append(float(transaction.amount))  # Convert Decimal to float

    # Convert defaultdict to a regular dict and then to JSON
    chart_data = json.dumps(chart_data)
    print(chart_data)

    return render(request, 'dashboard.html', {'chart_data': chart_data, 'transactions': transactions})
