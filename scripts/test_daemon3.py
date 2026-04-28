import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from auto_blog_daemon import get_gmail_service, fetch_unprocessed_newsletters, TARGET_LABEL_NAME, get_email_body

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
            body = get_email_body(msg['payload'])
            
            if not sender in emails_by_sender:
                emails_by_sender[sender] = []
            emails_by_sender[sender].append({"len": len(body), "id": msg_id})
        except Exception as e:
            pass

max_chars = 0
for sender, letters in emails_by_sender.items():
    total_len = sum(l['len'] for l in letters)
    max_chars = max(max_chars, total_len)
    print(f"[{sender}] - {len(letters)} emails, Total Chars: {total_len}")

print(f"\nMax chars sent to Gemini for a single prompt: {max_chars}")
