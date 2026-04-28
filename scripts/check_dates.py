import os
from googleapiclient.discovery import build
from auth import authenticate_gmail
from datetime import datetime, timedelta

def check_dates():
    creds = authenticate_gmail(account="mail1")
    service = build('gmail', 'v1', credentials=creds)
    target_label = "AI News"
    res = service.users().labels().list(userId='me').execute()
    label_id = next((l['id'] for l in res.get('labels', []) if target_label.lower() in l['name'].lower()), None)
    
    if not label_id: return
    
    # 7일 전부터 검색해봄
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d")
    results = service.users().messages().list(userId='me', q=f'after:{start_date}', labelIds=[label_id]).execute()
    messages = results.get('messages', [])
    
    print(f"Found {len(messages)} messages total in last 7 days.")
    for m in messages[:10]:
        msg = service.users().messages().get(userId='me', id=m['id'], format='metadata', metadataHeaders=['Subject', 'Date']).execute()
        headers = msg['payload']['headers']
        subject = next(h['value'] for h in headers if h['name'] == 'Subject')
        date = next(h['value'] for h in headers if h['name'] == 'Date')
        print(f"- {date}: {subject}")

if __name__ == "__main__":
    check_dates()
