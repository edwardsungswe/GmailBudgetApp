import os
import json
from django.shortcuts import render
from django.views.generic import FormView
from django.urls import reverse_lazy
from .models import Transaction, EmailFilter  # Ensure EmailFilter is imported
from collections import defaultdict
import json
from django.contrib.auth.decorators import login_required
from .forms import EmailFilterForm  # Import the EmailFilterForm
from django.views import View
from django.shortcuts import redirect, render
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings  # For handling settings like paths
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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


# 1. Function to authenticate Gmail
def authenticate_gmail():
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'token.json')
    
    # Check if token.json exists for previous valid authentication
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(settings.BASE_DIR, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
    
    return creds

# 2. Get Gmail service
def get_gmail_service(creds):
    # Create a Gmail API service object using the authenticated credentials
    service = build('gmail', 'v1', credentials=creds)
    return service

# 3. Function to list messages with filtering
def get_filtered_emails(service, user_id='me', max_results=10):
    # Query to filter emails in the Primary category
    query = 'category:primary'
    
    # Call the Gmail API to fetch the emails
    results = service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    emails = []  # To store email details
    
    if messages:
        for message in messages:
            msg = service.users().messages().get(userId=user_id, id=message['id']).execute()
            headers = msg['payload']['headers']
            
            # Extract subject and sender from the message headers
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
            
            if sender:
                # Clean up the sender to extract just the name
                if '<' in sender:
                    sender_name = sender.split('<')[0].strip()
                else:
                    sender_name = sender.split('@')[0].strip()
            
            # Append the email details to the list
            emails.append({
                'sender': sender_name,
                'subject': subject or "No Subject"
            })
    
    return emails

# 4. Django view to handle sync requests from dashboard.html
def sync_emails(request):
    if request.method == 'POST':
        # Get the number of emails to fetch from the POST request
        max_results = int(request.POST.get('max_results', 10))
        
        # Step 1: Authenticate Gmail
        creds = authenticate_gmail()
        service = get_gmail_service(creds)
        
        # Step 2: Get filtered emails
        emails = get_filtered_emails(service, max_results=max_results)
        
        # Step 3: Process and save to the Transaction model (optional)
        for email in emails:
            # Example of saving the email as a transaction
            # Customize as needed to match your model fields
            Transaction.objects.create(
                description=email['subject'],
                vendor=email['sender'],
                amount=0,  # Add logic to extract amount if applicable
                date="2023-01-01",  # Replace with actual date parsing logic
                category="others"  # Adjust this if email filters apply categories
            )
        
        # Return a success response to the frontend
        return JsonResponse({'status': 'success', 'emails_synced': len(emails)})

    return JsonResponse({'status': 'failed', 'error': 'Invalid request method'})

# 5. View to render the dashboard
def dashboard(request):
    transactions = Transaction.objects.all().order_by('date')
    return render(request, 'dashboard.html', {'transactions': transactions})
