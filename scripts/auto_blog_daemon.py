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
from dotenv import load_dotenv

from state_manager import is_processed, mark_processed, save_evaluations
from auth import authenticate_gmail

load_dotenv(".env.local")
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

# =============== SHARED LLM HELPER ===============

ARTICLE_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "has_ai_news": {"type": "boolean"},
        "articles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "source_urls": {"type": "array", "items": {"type": "string"}},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "score": {"type": "number"},
                    "has_numbers": {"type": "boolean"},
                    "key_figures": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "summary", "source_urls", "keywords", "score"]
            }
        }
    },
    "required": ["has_ai_news", "articles"]
}

def call_llm_with_retry(prompt, schema, label="LLM"):
    """공용 LLM 호출 헬퍼 (재시도 + 모델 폴백)"""
    client = genai.Client(api_key=GEMINI_API_KEY)
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
                        response_schema=schema
                    )
                )
                raw_text = clean_json_response(response.text)
                return json.loads(raw_text)
            except json.JSONDecodeError as je:
                print(f"      ❌ [{label}] JSON 에러. 10초 대기 후 재시도... ({je})")
                time.sleep(10)
                break
            except Exception as e:
                err_msg = str(e)
                if any(x in err_msg for x in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]):
                    print(f"      [경고] [{label}] '{model_name}' API 제한. 다른 모델 시도...")
                    continue
                else:
                    print(f"      ❌ [{label}] API 실패: {e}")
                    return None
        print(f"      ❌ [{label}] 모든 모델 할당량 초과: 30초 대기 후 재시도... ({attempt+1}/3)")
        time.sleep(30)
    return None


# =============== RSS PROCESSING ===============


def collect_rss_articles(feeds):
    """RSS 피드를 수집하고 구조화된 기사 배열을 반환한다."""
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
                    "content": content
                })
            except Exception as e:
                pass

    if not items_to_process:
        print(" └ 처리할 새로운 기사가 없습니다.")
        return []

    print(f" └ 총 {len(items_to_process)}개의 새 기사 처리 중...")
    
    articles_text = ""
    for idx, item in enumerate(items_to_process, 1):
        snippet = item['content'][:5000]
        articles_text += f"\n\n--- 기사 {idx} (출처: {item['feed_name']}) ---\n제목: {item['title']}\n링크: {item['link']}\n"
        articles_text += f"내용(HTML): {snippet}\n"

    custom_rules, custom_feedback = load_guidelines_and_feedback()

    prompt = f"""
당신은 최고 수준의 AI 뉴스 에디터입니다.
아래 여러 RSS 소스에서 수집된 기사들을 분석하여 구조화된 JSON 배열로 반환하세요.

[사용자 맞춤형 평가 핵심 룰]
{custom_rules}

[최근 사용자 직접 교정 예시 (Few-Shot)]
{custom_feedback}

[원문 정보]
{articles_text}

[요구사항]
0. **엄격한 팩트 준수**: 절대 외부 지식을 개입시키거나 환각(Hallucination)을 만들지 마세요. 오직 제공된 원문 텍스트 내에 존재하는 사실과 수치만 엄격하게 요약해야 합니다.
1. AI, 머신러닝, LLM 비즈니스와 무관한 기사는 무시하세요.
2. AI 기사가 하나라도 있으면 has_ai_news=true, 아니면 false.
3. 각 기사를 개별 article 객체로 반환:
   - title: 한국어 제목
   - summary: 2-4문장 핵심 요약. 구체적 수치/금액을 반드시 포함.
   - source_urls: 원문 URL 배열 (절대 조작/축약 금지)
   - keywords: 핵심 키워드 3-5개 (예: ["Meta", "로봇", "인수"])
   - score: 1-5점 (5=핵심 트렌드, 1=단순 단신)
   - has_numbers: 금액/수치 포함 여부
   - key_figures: 핵심 수치 배열 (예: ["$150억", "20만 인스턴스"])
4. score 3점 미만 기사도 포함하되, 정확한 점수를 매기세요.
"""
    data = call_llm_with_retry(prompt, ARTICLE_ANALYSIS_SCHEMA, label="RSS")
    if not data:
        return []
    
    # Mark RSS items as processed
    for item in items_to_process:
        mark_processed("rss", item["id"])
    
    articles = data.get("articles", [])
    # 소스 이름 태깅
    for art in articles:
        art["source_name"] = "RSS (AITimes/Benzinga)"
    
    evals = [{"target": a["title"], "score": a["score"], "reasoning": ", ".join(a.get("keywords", []))} for a in articles]
    if evals:
        save_evaluations("Global AI News", evals)
    
    print(f"      ✅ RSS에서 {len(articles)}개 기사 분석 완료")
    time.sleep(5)
    return articles

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
                # Preserve links: convert <a href="URL">text</a> to "text (Link: URL)"
                html_code = re.sub(r'<a\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>', r'\2 (Link: \1)', html_code, flags=re.IGNORECASE|re.DOTALL)
                # Strip remaining HTML tags
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

def collect_gmail_articles():
    """Gmail 뉴스레터를 수집하고 구조화된 기사 배열을 반환한다."""
    print("\n🔍 대상 Gmail: swookkwon@gmail AI News")
    service = get_gmail_service()
    if not service: return []
    
    # Get Label ID
    res = service.users().labels().list(userId='me').execute()
    label_id = next((l['id'] for l in res.get('labels', []) if TARGET_LABEL_NAME.lower() in l['name'].lower()), None)
    
    if not label_id: return []
    
    unprocessed_ids = fetch_unprocessed_newsletters(service, label_id)
    if not unprocessed_ids:
        print(" └ 처리할 새로운 이메일 뉴스레터가 없습니다.")
        return []
        
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

    all_gmail_articles = []
    custom_rules, custom_feedback = load_guidelines_and_feedback()

    for sender, letters in emails_by_sender.items():
        print(f"\n   -> [{sender}] 보낸 뉴스레터 파싱 중 ({len(letters)}개)")
        
        articles_text = ""
        for idx, letter in enumerate(letters, 1):
            articles_text += f"\n\n[제목: {letter['subject']}]\n{letter['body']}\n"
            
        prompt = f"""
당신은 수석 뉴스레터 AI 에디터입니다.
발신자 [{sender}]가 보낸 뉴스레터에서 개별 뉴스 기사를 추출하여 구조화된 JSON 배열로 반환하세요.

[사용자 맞춤형 평가 핵심 룰]
{custom_rules}

[최근 사용자 직접 교정 예시 (Few-Shot)]
{custom_feedback}

[뉴스레터 데이터]
{articles_text}

[요구사항]
0. **엄격한 팩트 준수**: 절대 외부 지식을 개입시키거나 환각(Hallucination)을 만들지 마세요. 오직 제공된 원문 텍스트 내에 존재하는 사실과 수치만 엄격하게 요약해야 합니다.
1. 뉴스레터 내 각각의 뉴스 기사/도구/소식을 개별 article 객체로 추출하세요.
2. 각 article:
   - title: 한국어 제목
   - summary: 2-4문장 핵심 요약. 수치/금액을 반드시 포함.
   - source_urls: 원문 URL 배열 (뉴스레터에 포함된 링크 그대로 사용)
   - keywords: 핵심 키워드 3-5개
   - score: 1-5점 (5=핵심, 1=가십)
   - has_numbers: 금액/수치 포함 여부
   - key_figures: 핵심 수치 배열
3. AI/LLM과 무관한 기사도 추출하되 낮은 점수를 매기세요.
"""
        data = call_llm_with_retry(prompt, ARTICLE_ANALYSIS_SCHEMA, label=f"Gmail-{sender}")
        if data:
            articles = data.get("articles", [])
            for art in articles:
                art["source_name"] = sender
            all_gmail_articles.extend(articles)
            
            evals = [{"target": a["title"], "score": a["score"], "reasoning": ", ".join(a.get("keywords", []))} for a in articles]
            if evals:
                save_evaluations(sender, evals)
            
            # Mark emails as processed
            for letter in letters:
                mark_processed("gmail", letter["id"])
            print(f"      ✅ [{sender}] {len(articles)}개 기사 분석 완료")
        else:
            # LLM 실패 시에도 처리 완료 마킹 (무한 재시도 방지)
            for letter in letters:
                mark_processed("gmail", letter["id"])
        
        print("      (발신자 간 기본 대기 10초...)")
        time.sleep(10)
    
    return all_gmail_articles


# =============== PHASE 2: MERGE & CREATE DAILY DIGEST ===============

DAILY_DIGEST_SCHEMA = {
    "type": "object",
    "properties": {
        "post_title": {"type": "string"},
        "top_topics": {"type": "array", "items": {"type": "string"}},
        "markdown_content": {"type": "string"}
    },
    "required": ["post_title", "top_topics", "markdown_content"]
}

def merge_and_create_daily_digest(all_articles):
    """모든 소스의 분석 결과를 받아 하나의 통합 포스트 생성."""
    if not all_articles:
        print("\n⚠️ 통합할 기사가 없습니다.")
        return
    
    # 3점 미만 기사 필터링
    quality_articles = [a for a in all_articles if a.get("score", 0) >= 3]
    low_articles = [a for a in all_articles if a.get("score", 0) < 3]
    
    if not quality_articles:
        print("\n⚠️ 3점 이상 기사가 없어 포스트를 생략합니다.")
        return
    
    # 소스 목록 집계
    source_names = sorted(set(a.get("source_name", "Unknown") for a in all_articles))
    
    print(f"\n📝 통합 다이제스트 생성 중...")
    print(f"   총 {len(all_articles)}개 기사 (3점 이상: {len(quality_articles)}개, 미만: {len(low_articles)}개)")
    print(f"   소스: {', '.join(source_names)}")
    
    articles_json = json.dumps(quality_articles, ensure_ascii=False, indent=2)
    low_json = json.dumps([{"title": a["title"], "source_name": a.get("source_name",""), "score": a["score"]} for a in low_articles], ensure_ascii=False) if low_articles else "[]"
    
    prompt = f"""
당신은 AI 데일리 다이제스트 수석 편집장입니다.
아래는 여러 소스에서 수집 + 분석한 AI 뉴스 기사 목록입니다.
이를 하나의 통합 일간 뉴스 포스트(마크다운 본문)으로 재구성하세요.

[3점 이상 주요 기사]
{articles_json}

[3점 미만 단신 (하단 테이블용)]
{low_json}

[통합 규칙]
0. **엄격한 팩트 준수**: 제공된 JSON 데이터(제목, 요약, 수치 등)에 없는 외부 지식을 절대로 덧붙이거나 환각(Hallucination)을 통해 상상해서 지어내지 마세요. 철저하게 주어진 텍스트 내용 안에서만 병합하세요.
1. **중복 뉴스 병합**: 같은 사건/발표를 다루는 기사들(keywords가 유사)을 하나로 합침.
   - 병합 시 모든 소스 이름을 "**소스:** A · B · C" 형태로 표기
   - 가장 상세한 summary를 기준으로 작성
2. **중요도 순 정렬** (위에서 아래로):
   - 🔥🔥 S등급: 3개 이상 소스가 보도 AND 구체적 금액/수치 포함
   - 🔥 A등급: 2개 이상 소스 보도 OR (빅테크 관련 + 금액)
   - 📰 B등급: 1개 소스, 기술적 깊이 있음
   - 📌 C등급: 단신 → 하단 "기타 뉴스 요약" 테이블
3. **포맷**:
   - 포스트 최상단에 전체 메인 제목(H1, `# 제목`)을 절대 쓰지 마세요.
   - 각 뉴스: `## 등급아이콘 순번. 제목` (예: `## 🔥 1. 메타 로봇 스타트업 인수`)
   - 뉴스 아래: `**소스:** 7min.ai · AITimes (2개 소스 보도)` 
   - 본문 2-4문장 + 핵심 수치가 있으면 불릿으로 강조
   - 원문 링크: `[원문: 사이트명](URL)` 형태 (원시 URL 절대 노출 금지)
   - 뉴스 사이 `---` 구분선
   - 하단에 C등급 단신은 `## 📌 기타 뉴스 요약` 마크다운 테이블
4. **post_title**: 날짜 없이 핵심 토픽 2-3개 포함한 매력적 제목
   (예: "메타 로봇 스타트업 인수, MCP 보안 취약점 발견, Grok 4.3 출시")
5. **top_topics**: 상위 3개 토픽 키워드 배열 (태그용)
"""
    data = call_llm_with_retry(prompt, DAILY_DIGEST_SCHEMA, label="Daily Digest")
    if not data:
        print("      ❌ 통합 다이제스트 생성 실패")
        return
    
    result_md = data.get("markdown_content", "")
    post_title = data.get("post_title", "AI 데일리 다이제스트")
    top_topics = data.get("top_topics", [])
    
    if not result_md:
        print("      ❌ 생성된 본문이 비어 있습니다.")
        return
    
    # 포스트 상단에 소스 요약 라인 추가
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    source_line = f"> 📊 오늘의 AI 뉴스: **{len(quality_articles)}건** | 소스: {', '.join(source_names)}\n\n---\n\n"
    result_md = source_line + result_md
    
    slug = "daily-ai-digest"
    title = f"[{now_kst.strftime('%m월 %d일')}] AI 데일리 다이제스트 — {post_title}"
    
    create_markdown_post_file(slug, title, result_md, category="AI News")
    print(f"      ✅ 통합 다이제스트 포스트 완료: {title}")


if __name__ == "__main__":
    print("=======================================================")
    print("🚀 [Auto Daemon] Booklog AI BlogPost Parser 봇 시작")
    print("=======================================================")
    
    all_articles = []
    
    # Phase 1: 소스별 수집 + 분석
    print("\n--- Phase 1: 소스별 수집 + 분석 ---")
    
    rss_articles = collect_rss_articles(FEEDS)
    all_articles.extend(rss_articles)
        
    print("\n-------------------------------------------------------")
    
    gmail_articles = collect_gmail_articles()
    all_articles.extend(gmail_articles)
    
    # Phase 2: 통합 다이제스트 생성
    print("\n--- Phase 2: 통합 다이제스트 생성 ---")
    merge_and_create_daily_digest(all_articles)
    
    print("\n=======================================================")
    print("🎉 자동 파싱 작업이 성공적으로 종료되었습니다.")
    print("=======================================================")
