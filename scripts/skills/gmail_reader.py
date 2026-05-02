#!/usr/bin/env python3
"""
skills/gmail_reader.py — Gmail 뉴스레터 본문 파싱 유틸리티
auto_blog_daemon.py에서 추출한 Gmail API 관련 로직.
"""
import re
import base64
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from auth import authenticate_gmail


TARGET_LABEL_NAME = "AI News"


def get_gmail_service():
    """Gmail API 서비스 객체를 반환한다."""
    creds = authenticate_gmail(account="mail1")
    if not creds:
        return None
    return build('gmail', 'v1', credentials=creds)


def get_email_body(payload: dict, max_length: int = 15000) -> str:
    """Gmail 메시지 payload에서 본문 텍스트를 추출한다."""
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
                # Preserve links: convert <a href="URL">text</a> to "text (Link: URL)"
                html_code = re.sub(
                    r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                    r'\2 (Link: \1)',
                    html_code,
                    flags=re.IGNORECASE | re.DOTALL,
                )
                clean_text = re.sub(r'<[^>]+>', ' ', html_code)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                text_content += clean_text + "\n"
        elif 'parts' in part:
            for subpart in part['parts']:
                extract_text(subpart)

    extract_text(payload)
    if not text_content:
        data = payload.get('body', {}).get('data', '')
        if data:
            text_content = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')

    # Strip quoted email trails
    reply_patterns = [
        r'\nOn\s.*?\s*wrote:',
        r'\nFrom:\s.*?\nSent:\s',
        r'\n_{10,}',
        r'\n-----Original Message-----',
    ]
    first_match_idx = len(text_content)
    for pattern in reply_patterns:
        match = re.search(pattern, text_content, flags=re.IGNORECASE)
        if match and match.start() < first_match_idx:
            first_match_idx = match.start()

    text_content = text_content[:first_match_idx].strip()
    return text_content[:max_length]


def fetch_newsletters(service, label_id: str, lookback_days: int = 7) -> list[dict]:
    """
    미처리 뉴스레터 이메일 목록을 가져온다.
    
    Returns:
        list[dict]: [{"id": str, "subject": str, "sender": str, "body": str}, ...]
    """
    from state.state_manager import is_processed

    today = datetime.now()
    last_week = today - timedelta(days=lookback_days)
    start_date = last_week.strftime("%Y/%m/%d")

    print(f" └ Gmail 검색 범위: {start_date} 이후 (최근 {lookback_days}일)")
    results = service.users().messages().list(
        userId='me', q=f'after:{start_date}', labelIds=[label_id], maxResults=50
    ).execute()
    messages = results.get('messages', [])

    newsletters = []
    for msg in messages:
        msg_id = msg['id']
        if is_processed("gmail", msg_id):
            continue

        try:
            full_msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = full_msg['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
            sender_full = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")

            sender_match = re.match(r'(.*?)\s*<.*?>', sender_full)
            sender = sender_match.group(1).strip().replace('"', '') if sender_match else sender_full

            body = get_email_body(full_msg['payload'])
            newsletters.append({
                "id": msg_id,
                "subject": subject,
                "sender": sender,
                "body": body,
            })
            print(f"    - [{sender}] {subject[:40]}...")
        except Exception as e:
            print(f"    - [오류] {msg_id} 본문 파싱 실패: {e}")

    return newsletters


def get_label_id(service) -> str | None:
    """TARGET_LABEL_NAME에 해당하는 라벨 ID를 반환한다."""
    res = service.users().labels().list(userId='me').execute()
    return next(
        (l['id'] for l in res.get('labels', []) if TARGET_LABEL_NAME.lower() in l['name'].lower()),
        None,
    )
