from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import email
import json
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    """Authenticate and return Gmail API service"""
    creds_path = os.path.join('data', 'credentials.json')
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_emails(max_emails=50):
    """Fetch emails from Gmail and save them in emails.json"""
    service = get_service()
    results = service.users().messages().list(userId='me', maxResults=max_emails).execute()
    messages = results.get('messages', [])

    emails_list = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data['payload']
        headers = payload.get("headers", [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "")
        snippet = msg_data.get('snippet', "")

        # Extract body if exists
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode()
        else:
            body = base64.urlsafe_b64decode(payload['body'].get('data', b"")).decode()

        emails_list.append({
            "subject": subject,
            "from": sender,
            "snippet": snippet,
            "body": body
        })

    # Save to JSON
    # Save to /data/emails.json
    output_path = os.path.join('data', 'emails.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(emails_list, f, ensure_ascii=False, indent=4)


    return emails_list
