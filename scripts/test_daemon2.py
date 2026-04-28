import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from auto_blog_daemon import get_gmail_service, fetch_unprocessed_newsletters, TARGET_LABEL_NAME

service = get_gmail_service()
res = service.users().labels().list(userId='me').execute()
label_id = next((l['id'] for l in res.get('labels', []) if TARGET_LABEL_NAME.lower() in l['name'].lower()), None)
unprocessed_ids = fetch_unprocessed_newsletters(service, label_id)

emails_by_sender = {}
for step in range(0, len(unprocessed_ids), 10):
    chunk = unprocessed_ids[step:step+10]
    for msg_id in chunk:
        try:
            msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = msg['payload'].get('headers', [])
            sender_full = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
            import re
            sender_match = re.match(r'(.*?)\s*<.*?>', sender_full)
            sender = sender_match.group(1).strip().replace('"', '') if sender_match else sender_full
            
            if not sender in emails_by_sender:
                emails_by_sender[sender] = []
            emails_by_sender[sender].append(msg_id)
        except Exception as e:
            print(f"Error fetching {msg_id}: {e}")

print(f"Senders ({len(emails_by_sender)}):")
for s, letters in emails_by_sender.items():
    print(f" - {s}: {len(letters)} emails")
