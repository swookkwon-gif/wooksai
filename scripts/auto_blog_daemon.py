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

from state_manager import is_processed, mark_processed, save_evaluations
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

def load_guidelines_and_feedback():
    rules_path = os.path.join(os.path.dirname(__file__), 'custom_eval_rules.txt')
    feedback_path = os.path.join(os.path.dirname(__file__), 'feedback.json')
    
    rules = "- 판단 기준이 누적 중입니다."
    if os.path.exists(rules_path):
        with open(rules_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content: rules = content
            
    feedback = "- 최신 수동 교정 예시가 없습니다."
    if os.path.exists(feedback_path):
        try:
            with open(feedback_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                fb_data = raw_data.get("feedbacks", []) if isinstance(raw_data, dict) else raw_data
                
                if fb_data:
                    feedback = ""
                    # 최근 5개만 반영
                    for fb in fb_data[-5:]:
                        feedback += f"- 대상 기사/키워드: '{fb.get('keyword_or_title', '')}'\n  -> (사용자 최종 점수: {fb.get('user_score', '')}점)\n  -> 판단 이유: {fb.get('reasoning', '')}\n"
        except Exception:
            pass
            
    return rules, feedback.strip()

def create_markdown_post_file(filename_slug, post_title, content, category="AI News"):
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime("%Y-%m-%d")
    
    # AI가 본문 최상단에 강제 생성하는 제목들(H1, H2) 중복 방지를 위해 삭제
    content = re.sub(r'^#\s+[^\n]+\n*', '', content.lstrip())
    content = re.sub(r'^##\s+[^\n]+\n*', '', content.lstrip())
    
    # 본문 첫 부분을 바탕으로 excerpt(요약문) 자동 생성 (제목 반복 방지)
    clean_content = re.sub(r'<[^>]+>', '', content)
    clean_content = re.sub(r'https?://[^\s]+', '', clean_content)
    clean_content = re.sub(r'[#*`\[\]\(\)]', '', clean_content)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    excerpt_text = clean_content[:120] + "..." if len(clean_content) > 120 else clean_content
    excerpt_text = excerpt_text.replace('"', "'").replace('\n', ' ')
    
    frontmatter = f"""---
title: '{post_title.replace("'", "''")}'
date: '{date_str}'
excerpt: '{excerpt_text.replace("'", "''")}'
category: '{category.replace("'", "''")}'
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

def process_all_rss_feeds(feeds):
    items_to_process = []
    
    for feed in feeds:
        print(f"\n🔍 대상 RSS: {feed['name']}")
        parsed_feed = feedparser.parse(feed['url'])
        
        now = datetime.now(timezone.utc)
        
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
                    "feed_name": feed['name'],
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

    print(f" └ 총 {len(items_to_process)}개의 새 기사 처리 중...")
    
    # Process batch with LLM
    articles_text = ""
    for idx, item in enumerate(items_to_process, 1):
        snippet = item['content'][:5000]
        articles_text += f"\n\n--- 기사 {idx} (출처: {item['feed_name']}) ---\n제목: {item['title']}\n링크: {item['link']}\n"
        if item['img_tag']: articles_text += f"원본 이미지 태그: {item['img_tag']}\n"
        articles_text += f"내용(HTML): {snippet}\n"

    custom_rules, custom_feedback = load_guidelines_and_feedback()

    prompt = f"""
당신은 최고 수준의 AI 뉴스 에디터입니다.
아래 여러 RSS 소스에서 수집된 새 기사들을 바탕으로, 종합 AI 뉴스 마크다운 포스트 본문을 작성하세요.

[사용자 맞춤형 평가 핵심 룰]
{custom_rules}

[최근 사용자 직접 교정 예시 (Few-Shot)]
{custom_feedback}

[원문 정보]
{articles_text}

[요구사항]
1. AI, 머신러닝, LLM 비즈니스와 무관한 기사는 무시하세요.
2. AI 기사가 하나라도 있으면 `has_ai_news`를 true로, 아니면 false로 응답하세요.
3. 수집된 모든 기사에 대해 1~5점 척도로 중요도를 평가(`evaluations`)하세요. (5점: 핵심 트렌드, 1점: 아주 단순한 단신)
4. 기사들을 병합해 가독성 좋은 마크다운 포스트 본문(`markdown_content`)을 구성하되, **최소 3점 이상인 고가치 기사들만 골라서 포함**하세요.
5. 원문에 <img ...> 태그가 존재하면, 이 태그를 **한 글자도 고치지 말고 그대로 복사해서 삽입**하세요. 마크다운의 `![]()`로 변경하면 안 됩니다.
6. 포스트 최상단에 전체 메인 제목(H1, `# 제목`)을 절대 렌더링하지 마세요. 곧바로 첫 번째 소제목으로 시작하세요.
7. 소제목은 `### [기사 제목](링크)` 형식으로 작성하되, **반드시 그 바로 아래 줄을 한 칸 띄우고(빈 줄 삽입) 본문을 시작**하세요.
8. JSON 구조 응답 필수: {{"has_ai_news": bool, "evaluations": [{{"target": string, "score": number, "reasoning": string}}], "markdown_content": string}}
"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    response = None
    models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-flash-8b']
    
    for attempt in range(3):
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3, 
                        response_mime_type="application/json",
                        response_schema={
                            "type": "object",
                            "properties": {
                                "has_ai_news": {"type": "boolean"},
                                "evaluations": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "target": {"type": "string"},
                                            "score": {"type": "number"},
                                            "reasoning": {"type": "string"}
                                        },
                                        "required": ["target", "score", "reasoning"]
                                    }
                                },
                                "markdown_content": {"type": "string"}
                            },
                            "required": ["has_ai_news", "evaluations", "markdown_content"]
                        }
                    )
                )
                break
            except Exception as e:
                err_msg = str(e)
                if any(x in err_msg for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]):
                    print(f"      [경고] RSS 분석 '{model_name}' 모델 API 제한 발생. 다른 모델 시도...")
                    continue
                else:
                    print(f"   [에러] {e}")
                    break
        
        if response:
            raw_text = clean_json_response(response.text)
            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError as je:
                print(f"      ❌ API 실패: JSON 에러 발생. 10초 대기 후 재시도... ({je})")
                time.sleep(10)
                continue
                
            if data.get("has_ai_news"):
                result_md = data.get("markdown_content", "")
                evals = data.get("evaluations", [])
                if evals:
                    save_evaluations("Global AI News", evals)
                
                slug = "global-ai-news-summary"
                now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
                title = f"[{now_kst.strftime('%m월 %d일')}] AI times, Benzinga 뉴스 요약"
                create_markdown_post_file(slug, title, result_md, category="AI News")
                
                for item in items_to_process:
                    mark_processed("rss", item["id"])
                    
                print(f"      ✅ 포스트 완료 및 저장됨")
            else:
                for item in items_to_process:
                    mark_processed("rss", item["id"])
                print(f"      ✅ 중요 기사(3점 이상)가 없어 포스트 생략 (처리완료 마킹)")
            return
            
        print(f"      ❌ 모든 모델 할당량 초과: 30초 대기 후 재시도... ({attempt+1}/3)")
        time.sleep(30)
                
    # API Pacing
    time.sleep(5)

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
            data = part.get('body', {}).get('data', '')
            if data:
                html_code = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')
                # Strip HTML tags
                clean_text = re.sub(r'<[^>]+>', ' ', html_code)
                # Collapse multiple spaces and newlines
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
    # 기존 2일에서 7일로 확장하여 '기존 이메일'도 처리될 수 있도록 변경
    lookback_days = 7
    last_week = today - timedelta(days=lookback_days)
    start_date = last_week.strftime("%Y/%m/%d")
    
    print(f" └ Gmail 검색 범위: {start_date} 이후 (최근 {lookback_days}일)")
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
                print(f"    - [{sender}] {subject[:30]}...")
            except Exception as e:
                print(f"    - [오류] {msg_id} 본문 파싱 실패: {e}")
                pass
                
        time.sleep(0.5)

    client = genai.Client(api_key=GEMINI_API_KEY)

    for sender, letters in emails_by_sender.items():
        print(f"\n   -> [{sender}] 보낸 뉴스레터 파싱 중 ({len(letters)}개)")
        
        articles_text = ""
        for idx, letter in enumerate(letters, 1):
            articles_text += f"\n\n[제목: {letter['subject']}]\n{letter['body']}\n"
            
        custom_rules, custom_feedback = load_guidelines_and_feedback()
            
        prompt = f"""
당신은 '윤(Yoon)' 님을 위한 수석 뉴스레터 AI 에디터입니다.
발신자 [{sender}](이)가 보낸 뉴스레터 데이터를 기반으로 블로그 포스트를 작성합니다.

[사용자 맞춤형 평가 핵심 룰]
{custom_rules}

[최근 사용자 직접 교정 예시 (Few-Shot)]
{custom_feedback}

[뉴스레터 데이터]
{articles_text}

[요구사항]
1. 뉴스레터 내에서 소개된 각각의 주요 기사나 도구, 단신들에 대해 1~5점 척도로 퀄리티/중요도를 평가(`evaluations`)하세요. (5점: 핵심, 1점: 단순 가십)
2. 블로그 포스트의 본문(`markdown_content`)에는 평가 점수가 **3점 이상인 핵심 내용만 필터링하여 포함**하세요.
3. 뉴스레터 내용이 단신 나열 형태라면 원문을 최대한 유지하고 매끄럽게 교정하며, 긴 산문형이나 난잡하게 섞여있다면 개조식 리스트 형태로 깔끔히 요약하세요.
4. 발신자(`{sender}`)가 전하는 핵심 메시지에 맞춰 소제목(`###`) 단위로만 구분하세요. 포스트 최상단에 전체 제목(H1, `# 제목`)을 절대 쓰지 마세요.
5. JSON 구조 응답 필수: {{"evaluations": [{{"target": string, "score": number, "reasoning": string}}], "markdown_content": string}}
"""
        response = None
        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-1.5-flash-8b']
        
        for attempt in range(3):
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.3,
                            response_mime_type="application/json",
                            response_schema={
                                "type": "object",
                                "properties": {
                                    "evaluations": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "target": {"type": "string"},
                                                "score": {"type": "number"},
                                                "reasoning": {"type": "string"}
                                            },
                                            "required": ["target", "score", "reasoning"]
                                        }
                                    },
                                    "markdown_content": {"type": "string"}
                                },
                                "required": ["evaluations", "markdown_content"]
                            }
                        )
                    )
                    break
                except Exception as e:
                    err_msg = str(e)
                    if any(x in err_msg for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]):
                        print(f"      [경고] 뉴스레터 분석 '{model_name}' 모델 API 제한 발생. 다른 모델 시도...")
                        continue
                    else:
                        print(f"      ❌ API 실패: {e}")
                        break
                        
            if response:
                raw_text = clean_json_response(response.text)
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError as je:
                    print(f"      ❌ API 실패: JSON 에러 발생. 10초 대기 후 재시도... ({je})")
                    time.sleep(10)
                    response = None
                    continue
                
                result_md = data.get("markdown_content", "")
                evals = data.get("evaluations", [])
                if evals:
                    save_evaluations(sender, evals)
                    
                if result_md:
                    slug = slugify(sender) + "-newsletter"
                    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
                    title = f"[{sender}] 최신 AI 뉴스레터 동향"
                    
                    create_markdown_post_file(slug, title, result_md, category="AI News")
                    
                    for letter in letters:
                        mark_processed("gmail", letter["id"])
                        
                    print(f"      ✅ 포스트 완료 및 저장됨")
                else:
                    for letter in letters:
                        mark_processed("gmail", letter["id"])
                    print(f"      ✅ 중요 기사(3점 이상)가 없어 포스트 생략 (처리완료 마킹)")
                break
                
            print(f"      ❌ 모든 모델 할당량 초과: 30초 대기 후 재시도... ({attempt+1}/3)")
            time.sleep(30)
        
        # 발신자 간 고정 API Pacing 
        print("      (발신자 간 기본 대기 10초...)")
        time.sleep(10)

if __name__ == "__main__":
    print("=======================================================")
    print("🚀 [Auto Daemon] Booklog AI BlogPost Parser 봇 시작")
    print("=======================================================")
    
    # 1. RSS 처리
    process_all_rss_feeds(FEEDS)
        

    print("\n-------------------------------------------------------")
    
    # 2. Gmail 뉴스레터(Sender별) 처리
    process_gmail_newsletters()
    
    print("\n=======================================================")
    print("🎉 자동 파싱 작업이 성공적으로 종료되었습니다.")
    print("=======================================================")
