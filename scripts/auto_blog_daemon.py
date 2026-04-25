#!/usr/bin/env python3
import os
import re
import time
import json
import base64
import feedparser
from datetime import datetime, timezone, timedelta
from slugify import slugify
from google import genai
from google.genai import types
from googleapiclient.discovery import build

from state_manager import is_processed, mark_processed
from auth import authenticate_gmail

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY is missing. Export it or add it to .env.local")
    import sys; sys.exit(1)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News')
if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)

TARGET_LABEL_NAME = "AI News"

FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Apple Machine Learning", "url": "https://machinelearning.apple.com/rss.xml"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "arXiv cs.AI (AI)", "url": "http://export.arxiv.org/rss/cs.AI"},
    {"name": "AITimes", "url": "https://www.aitimes.com/rss/allArticle.xml", "keywords": ["인공지능", "AI", "머신러닝", "LLM", "모델"]},
    {"name": "Benzinga Korea", "url": "https://kr.benzinga.com/feed/", "keywords": ["AI", "인공지능", "엔비디아", "반도체"]}
]

def clean_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-len("```")].strip()
    return text

def create_markdown_post_file(filename_slug, post_title, content, category="AI News"):
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime("%Y-%m-%d")
    
    frontmatter = f"""---
title: "{post_title}"
date: "{date_str}"
excerpt: "{post_title} 요약"
category: "{category}"
---

"""
    filename = f"{date_str}-{filename_slug}.md"
    file_path = os.path.join(POSTS_DIR, filename)
    mode = "w" if not os.path.exists(file_path) else "a"
    
    with open(file_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(frontmatter)
        f.write(content + "\n\n")

# =============== RSS PROCESSING ===============

def extract_image_tag(html_content):
    img_match = re.search(r'(<img[^>]+>)', html_content, re.IGNORECASE)
    return img_match.group(1) if img_match else ""

def process_rss_feed(feed):
    print(f"\n🔍 대상 RSS: {feed['name']}")
    parsed_feed = feedparser.parse(feed['url'])
    
    now = datetime.now(timezone.utc)
    items_to_process = []
    
    for entry in parsed_feed.entries:
        try:
            url_id = entry.get('link', entry.get('id', ''))
            if not url_id or is_processed("rss", url_id):
                continue
                
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) if 'published_parsed' in entry and entry.published_parsed else now
            if (now - dt).days > 2:
                continue
            
            content = ""
            if 'content' in entry:
                content = entry.content[0].value
            elif 'summary' in entry:
                content = entry.summary
                
            title = entry.get('title', 'No Title')
            img_tag = extract_image_tag(content)
            
            # Keywords filtering
            keywords = feed.get('keywords', [])
            if keywords:
                combined_text = (title + " " + content).lower()
                if not any(k.lower() in combined_text for k in keywords):
                    continue
            
            items_to_process.append({
                "id": url_id,
                "title": title,
                "link": entry.get('link', ''),
                "content": content,
                "img_tag": img_tag
            })
        except Exception as e:
            pass

    if not items_to_process:
        print(" └ 처리할 새로운 기사가 없습니다.")
        return

    print(f" └ {len(items_to_process)}개의 새 기사 처리 중...")
    
    # Process batch with LLM
    articles_text = ""
    for idx, item in enumerate(items_to_process, 1):
        snippet = item['content'][:5000]
        articles_text += f"\n\n--- 기사 {idx} ---\n제목: {item['title']}\n링크: {item['link']}\n"
        if item['img_tag']: articles_text += f"원본 이미지 태그: {item['img_tag']}\n"
        articles_text += f"내용(HTML): {snippet}\n"

    prompt = f"""
당신은 최고 수준의 AI 뉴스 에디터입니다.
아래 [{feed['name']}] RSS에서 수집된 새 기사들을 바탕으로, 1개의 마크다운 종합 포스트 본문을 작성하세요.

[원문 정보]
{articles_text}

[요구사항]
1. AI, 머신러닝, LLM 비즈니스와 무관한 기사는 무시하세요.
2. AI 기사가 하나라도 있으면 `has_ai_news`를 true로, 아니면 false로 응답하세요.
3. 기사들을 병합해 가독성 좋은 마크다운 포스트 본문(`markdown_content`)을 구성하세요.
4. 원문에 <img ...> 태그가 존재하면, 이 태그를 **한 글자도 고치지 말고 그대로 복사해서 삽입**하세요. 마크다운의 `![]()`로 변경하면 안 됩니다.
5. 각 기사별로 소제목(`### [제목](링크)`)을 추가해 구분하세요.
6. JSON 구조 응답 필수: {{"has_ai_news": bool, "markdown_content": string}}
"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3, 
                    response_mime_type="application/json"
                )
            )
            raw_text = clean_json_response(response.text)
            data = json.loads(raw_text)
            
            if data.get("has_ai_news"):
                result_md = data.get("markdown_content", "")
                slug = slugify(feed['name'])
                now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
                title = f"[{now_kst.strftime('%m월 %d일')}] {feed['name']} 주요 뉴스 요약"
                create_markdown_post_file(slug, title, result_md)
                
                for item in items_to_process:
                    mark_processed("rss", item['id'])
                
                print(f" ✅ {feed['name']} 포스팅 완료.")
            else:
                for item in items_to_process:
                    mark_processed("rss", item['id'])
                print(f" └ 처리 완료 (AI 기사 아님)")
            break
        except Exception as e:
            if any(x in str(e) for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]):
                print(f"   [API 에러] {str(e)} -> 20s 대기 후 재시도...")
                time.sleep(20)
            else:
                print(f"   [에러] {e}")
                break

# =============== GMAIL PROCESSING ===============

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
            pass # html processing if needed
        elif 'parts' in part:
            for subpart in part['parts']:
                extract_text(subpart)
    
    extract_text(payload)
    if not text_content:
        data = payload.get('body', {}).get('data', '')
        if data:
            text_content = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')
    
    # Strip quoted email trails
    import re
    reply_patterns = [r'\nOn\s.*?\s*wrote:', r'\nFrom:\s.*?\nSent:\s', r'\n_{10,}', r'\n-----Original Message-----']
    first_match_idx = len(text_content)
    for pattern in reply_patterns:
        match = re.search(pattern, text_content, flags=re.IGNORECASE)
        if match and match.start() < first_match_idx:
            first_match_idx = match.start()
            
    text_content = text_content[:first_match_idx].strip()
    return text_content[:max_length]

def get_gmail_service():
    creds = authenticate_gmail(account="mail1")
    if not creds: return None
    return build('gmail', 'v1', credentials=creds)

def fetch_unprocessed_newsletters(service, label_id):
    today = datetime.now()
    last_week = today - timedelta(days=2)
    start_date = last_week.strftime("%Y/%m/%d")
    
    results = service.users().messages().list(userId='me', q=f'after:{start_date}', labelIds=[label_id], maxResults=50).execute()
    messages = results.get('messages', [])
    
    unprocessed = []
    for msg in messages:
        msg_id = msg['id']
        if not is_processed("gmail", msg_id):
            unprocessed.append(msg_id)
            
    return unprocessed

def process_gmail_newsletters():
    print("\n🔍 대상 Gmail: swookkwon@gmail AI News")
    service = get_gmail_service()
    if not service: return
    
    # Get Label ID
    res = service.users().labels().list(userId='me').execute()
    label_id = next((l['id'] for l in res.get('labels', []) if TARGET_LABEL_NAME.lower() in l['name'].lower()), None)
    
    if not label_id: return
    
    unprocessed_ids = fetch_unprocessed_newsletters(service, label_id)
    if not unprocessed_ids:
        print(" └ 처리할 새로운 이메일 뉴스레터가 없습니다.")
        return
        
    print(f" └ {len(unprocessed_ids)}개의 새 이메일 스크랩 중...")
    
    emails_by_sender = {}
    
    for step in range(0, len(unprocessed_ids), 10):
        chunk = unprocessed_ids[step:step+10]
        for msg_id in chunk:
            try:
                msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "No Subject")
                sender_full = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown Sender")
                
                # Extract clean sender name
                sender_match = re.match(r'(.*?)\s*<.*?>', sender_full)
                sender = sender_match.group(1).strip().replace('"', '') if sender_match else sender_full
                
                body = get_email_body(msg['payload'])
                
                if not sender in emails_by_sender:
                    emails_by_sender[sender] = []
                    
                emails_by_sender[sender].append({"id": msg_id, "subject": subject, "body": body})
            except Exception as e:
                pass
                
        time.sleep(0.5)

    client = genai.Client(api_key=GEMINI_API_KEY)

    for sender, letters in emails_by_sender.items():
        print(f"\n   -> [{sender}] 보낸 뉴스레터 파싱 중 ({len(letters)}개)")
        
        articles_text = ""
        for idx, letter in enumerate(letters, 1):
            articles_text += f"\n\n[제목: {letter['subject']}]\n{letter['body']}\n"
            
        prompt = f"""
당신은 '윤(Yoon)' 님을 위한 수석 뉴스레터 AI 에디터입니다.
발신자 [{sender}](이)가 보낸 뉴스레터 데이터를 기반으로 블로그 포스트를 작성합니다.

[뉴스레터 데이터]
{articles_text}

[요구사항]
1. 뉴스레터 내용이 **이미 주제별로 짧고 깔끔하게 큐레이션(요약)된 형태라면(예: 단신 나열 형태)**:
   - 지나치게 더 축약하지 말고, 원문의 문맥과 정보를 최대한 유지하면서 번역 투를 매끄러운 한글로만 교정하세요.
2. 뉴스레터 내용이 **아주 긴 산문형이거나 정보가 난잡하게 섞여있는 형태라면**:
   - 가독성을 위해 불필요한 서술어를 빼고 핵심(도구, 시사점, 링크 등)만 간결한 리스트(개조식) 형태로 깔끔히 요약하세요.
3. 발신자(`{sender}`)가 전하는 핵심 메시지에 맞춰 적절한 소제목들을 마크다운(`###`)으로 잡아주세요.
4. 블로그 포스트의 본문에 들어갈 내용만 순수하게 `markdown_content` 필드에 작성하세요.
5. JSON 구조 응답 필수: {{"markdown_content": string}}
"""
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        response_mime_type="application/json"
                    )
                )
                raw_text = clean_json_response(response.text)
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError as je:
                    print(f"      ❌ API 실패: JSON 에러 발생. 10초 대기 후 재시도... ({je})")
                    time.sleep(10)
                    continue
                
                result_md = data.get("markdown_content", "")
                if result_md:
                    slug = slugify(sender) + "-newsletter"
                    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
                    title = f"[{sender}] 최신 AI 뉴스레터 동향"
                    
                    create_markdown_post_file(slug, title, result_md, category="AI News")
                    
                    for letter in letters:
                        mark_processed("gmail", letter["id"])
                        
                    print(f"      ✅ 완료 및 저장됨")
                break
            except Exception as e:
                err_msg = str(e)
                if any(x in err_msg for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]):
                    print(f"      [API 에러] 429/500 Rate Limit 에러 발생. 60초 대기 후 재시도... (시도 {attempt+1}/3)")
                    time.sleep(60)
                else:
                    print(f"      ❌ API 실패: {e}")
                    break
        
        # 발신자 간 고정 대기로 Rate Limit 방어
        print("      (Rate limit 방어 대기 45초...)")
        time.sleep(45)

if __name__ == "__main__":
    print("=======================================================")
    print("🚀 [Auto Daemon] Booklog AI BlogPost Parser 봇 시작")
    print("=======================================================")
    
    # 1. RSS 처리
    for feed in FEEDS:
        process_rss_feed(feed)
        time.sleep(1)
        
    print("\n-------------------------------------------------------")
    
    # 2. Gmail 뉴스레터(Sender별) 처리
    process_gmail_newsletters()
    
    print("\n=======================================================")
    print("🎉 자동 파싱 작업이 성공적으로 종료되었습니다.")
    print("=======================================================")
