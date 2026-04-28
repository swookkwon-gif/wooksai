import os, re, base64
from googleapiclient.discovery import build
from auth import authenticate_gmail

def get_email_body(payload, max_length=15000):
    text_content = ""
    def extract_text(part):
        nonlocal text_content
        mime_type = part.get('mimeType', '')
        if mime_type == 'text/plain':
            data = part.get('body', {}).get('data', '')
            if data:
                text_content += base64.urlsafe_b64decode(data).decode('utf-8', 'ignore') + "\n"
        elif mime_type == 'text/html':
            data = part.get('body', {}).get('data', '')
            if data:
                html_code = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')
                clean_text = re.sub(r'<[^>]+>', ' ', html_code)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                text_content += clean_text + "\n"
        elif 'parts' in part:
            for subpart in part['parts']:
                extract_text(subpart)
    extract_text(payload)
    return text_content[:max_length]

def debug():
    creds = authenticate_gmail(account="mail1")
    service = build('gmail', 'v1', credentials=creds)
    target_label = "AI News"
    res = service.users().labels().list(userId='me').execute()
    label_id = next((l['id'] for l in res.get('labels', []) if target_label.lower() in l['name'].lower()), None)
    
    results = service.users().messages().list(userId='me', q='after:2026/04/24', labelIds=[label_id], maxResults=5).execute()
    messages = results.get('messages', [])
    
    print(f"Messages to debug: {len(messages)}")
    for m in messages:
        try:
            print(f"Fetching {m['id']}...")
            msg = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
            headers = msg['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
            sender_full = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
            print(f"  Subject: {subject}")
            print(f"  From: {sender_full}")
            
            body = get_email_body(msg['payload'])
            print(f"  Body length: {len(body)}")
        except Exception as e:
            print(f"  FAILED: {e}")

if __name__ == "__main__":
    debug()
