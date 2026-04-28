import os
from googleapiclient.discovery import build
from auth import authenticate_gmail

def test_gmail():
    print("Testing Gmail API...")
    creds = authenticate_gmail(account="mail1")
    if not creds:
        print("Failed to authenticate.")
        return
        
    service = build('gmail', 'v1', credentials=creds)
    res = service.users().labels().list(userId='me').execute()
    labels = res.get('labels', [])
    
    target_label = "AI News"
    label_id = None
    print("Available Labels:")
    for l in labels:
        if 'name' in l and target_label.lower() in l['name'].lower():
            label_id = l['id']
            print(f"  FOUND MATCH: {l['name']} (ID: {label_id})")
            
    if not label_id:
        print(f"Could not find label '{target_label}'")
        return
        
    from datetime import datetime, timedelta
    today = datetime.now()
    last_week = today - timedelta(days=2)
    start_date = last_week.strftime("%Y/%m/%d")
    query = f'after:{start_date}'
    
    print(f"Querying messages: {query} with label {label_id}")
    results = service.users().messages().list(userId='me', q=query, labelIds=[label_id], maxResults=50).execute()
    messages = results.get('messages', [])
    print(f"Found {len(messages)} messages.")
    
    from state_manager import is_processed
    unprocessed = [m['id'] for m in messages if not is_processed("gmail", m['id'])]
    print(f"Unprocessed messages: {len(unprocessed)}")

if __name__ == "__main__":
    test_gmail()
