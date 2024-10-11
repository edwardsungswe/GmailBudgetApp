import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    # Check if token.json exists for previous valid authentication
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

def get_gmail_service(creds):
    # Create a Gmail API service object using the authenticated credentials
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_message_details(service, message_id):
    # Get the full message data using the message ID
    message = service.users().messages().get(userId='me', id=message_id).execute()
    
    print(f"Message snippet: {message['snippet']}")  # Print the message snippet

def list_messages(service):
    results = service.users().messages().list(userId='me').execute()
    messages = results.get('messages', [])
    
    if not messages:
        print('No messages found.')
    else:
        print('Messages:')
        for message in messages[:10]:  # Get the first 10 messages
            print(f"Message ID: {message['id']}")
            get_message_details(service, message['id'])


def get_filtered_emails(service, user_id='me', max_results=10):
    # Query to filter emails in the Primary category
    query = 'category:primary'

    # Call the Gmail API to fetch the first `maxResults` primary category emails
    results = service.users().messages().list(userId=user_id, q=query, maxResults=max_results).execute()

    messages = results.get('messages', [])

    print(f"Requested {max_results} emails, but received {len(messages)} messages.")
    
    if not messages:
        print("No messages found.")
    else:
        for message in messages:
            # Get the message details
            msg = service.users().messages().get(userId=user_id, id=message['id']).execute()
            
            # Extract the headers from the message payload
            headers = msg['payload']['headers']

            # Find the subject and sender (From) headers
            subject = None
            sender = None
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                if header['name'] == 'From':
                    sender = header['value']
            
            # Clean up the sender to remove the email domain
            if sender:
                # Extract the name (before '<') or the part before the '@' if no name is present
                if '<' in sender:
                    # Handle case with name and email (e.g., "John Doe <john.doe@example.com>")
                    sender_name = sender.split('<')[0].strip()
                else:
                    # Handle case with just the email (e.g., "john.doe@example.com")
                    sender_name = sender.split('@')[0].strip()
            
            # Print the subject and cleaned sender name
            if subject and sender_name:
                print(f"From: {sender_name} | Subject: {subject}")
            else:
                print("Email missing subject or sender.")
def main():
    creds = authenticate_gmail()
    service = get_gmail_service(creds)
    get_filtered_emails(service, max_results=10)
if __name__ == '__main__':
    main()
