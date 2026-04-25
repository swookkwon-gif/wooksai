#!/usr/bin/env python3
import os
import sys
import time
import json
from datetime import datetime, timezone, timedelta
from slugify import slugify
import urllib.parse
import re

try:
    import feedparser
    from google import genai
    from google.genai import types
except ImportError:
    print("Required packages not found. Please run: pip install feedparser google-genai python-slugify")
    sys.exit(1)

# Gemini API Key 로드 
# (Booklog/.env.local 에서 로드하는 로직 추가)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                val = line.strip().split('=', 1)[1]
                os.environ['GEMINI_API_KEY'] = val.strip('"' + "'")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY is missing. Export it or add it to .env.local")
    sys.exit(1)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')

FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/feed/"},
    {"name": "Apple Machine Learning", "url": "https://machinelearning.apple.com/feed.xml"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "arXiv cs.AI (AI)", "url": "https://rss.arxiv.org/rss/cs.AI", "limit": 5}, # 논문은 최근 5개만 묶음
    {"name": "AITimes", "url": "https://cdn.aitimes.com/rss/gn_rss_allArticle.xml", "limit": 7},
    {
        "name": "Benzinga Korea", 
        "url": "https://kr.benzinga.com/feed/", 
        "keywords": ["ai", "인공지능", "로봇", "llm", "gpt", "엔비디아", "nvidia", "오픈ai", "구글", "테슬라", "자율주행", "반도체"],
        "limit": 5
    }
]

def extract_image_url(html_content):
    """HTML 본문에서 첫 번째 이미지 URL을 추출합니다."""
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    if img_match:
        return img_match.group(1)
    return ""

def parse_recent_rss_items(feed_config, days_limit=1.5):
    """지정된 피드에서 최근 게시물을 추출합니다."""
    url = feed_config['url']
    keywords = feed_config.get('keywords')
    max_items = feed_config.get('limit', 10)
    
    parsed = feedparser.parse(url)
    recent_items = []
    
    now = datetime.now(timezone.utc)
    limit_date = now - timedelta(days=days_limit)
    
    for entry in parsed.entries:
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                dt = datetime.fromtimestamp(time.mktime(entry.updated_parsed), timezone.utc)
            else:
                dt = now
            
            if dt >= limit_date:
                content = entry.get('content', [{'value': ''}])[0]['value']
                if not content: content = entry.get('description', '')
                if not content: content = entry.get('summary', '')
                
                title = entry.get('title', 'No Title')
                img_url = extract_image_url(content)
                
                # 키워드 사전 필터링
                if keywords:
                    combined_text = (title + " " + content).lower()
                    if not any(k.lower() in combined_text for k in combined_text.split() if k in keywords):
                        # Simple keyword check
                        if not any(k in combined_text for k in keywords):
                             continue
                
                recent_items.append({
                    "title": title,
                    "link": entry.get('link', ''),
                    "content": content,
                    "img_url": img_url,
                    "published": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "dt": dt
                })
        except Exception as e:
            print(f"[{url}] 항목 파싱 에러: {e}")
            
    return recent_items[:max_items]

def process_source_batch_with_llm(source_name, items):
    """다수의 기사를 한 번에 LLM에 전달하여 소스 단위 종합 요약본을 생성합니다."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # 여러 기사를 하나의 텍스트로 합치기
    articles_text = ""
    for idx, item in enumerate(items, 1):
        content_snippet = item['content'][:8000] if len(item['content']) > 8000 else item['content']
        articles_text += f"\n\n--- 기사 {idx} ---\n"
        articles_text += f"제목: {item['title']}\n"
        articles_text += f"링크: {item['link']}\n"
        
        # 이미지가 있다면 URL 정보를 추가로 제공
        if item.get('img_url'):
            articles_text += f"이미지 URL: {item['img_url']}\n"
            
        articles_text += f"내용(HTML포함): {content_snippet}\n"

    # 한국 시간 기준 날짜 생성
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str_kor = now_kst.strftime("%m월 %d일")

    prompt = f"""
당신은 최고 수준의 AI 전문 뉴스 에디터입니다. 아래는 오늘 [{source_name}] 등에서 수집된 {len(items)}개의 기사 정보입니다.

[원문 정보]
{articles_text}

[요구사항]
1. 위 기사들 중 인공지능(AI), 머신러닝, LLM 및 AI 비즈니스 트렌드 등과 전혀 무관한 정치/일반 기사는 제외하세요.
2. AI 관련 기사가 하나도 없다면 `has_ai_news`를 false로 설정하세요.
3. AI 관련 기사가 1개 이상 존재한다면, `has_ai_news`를 true로 설정하고 이 기사들을 묶어 가독성 좋은 '하나의 마크다운 포스트' 본문(markdown_content)으로 구성하세요.
4. 요약 강도 조절 (매우 중요!): 원본 기사가 이미 충실하고 상세하게 설명되어 있다면, 무리하게 분량을 잘라내어 축소하지 마세요. 원래 정보의 깊이와 의미를 보존하면서 한글 표현만 아주 매끄럽게 번역/다듬어 주세요.
5. 이미지 포함 규칙: 기사의 [원문 정보]에 '이미지 URL' 항목이 존재한다면, 각 기사 당 **최대 1장**까지만 마크다운 문법(`![이미지 설명](이미지 URL)`)을 사용해 해당 기사의 소제목 바로 아래 등 적절한 위치에 삽입하세요.
6. 기사 간의 구분: 각 기사별로 반드시 클릭 가능한 링크가 포함된 소제목(`### [기사 제목](기사 링크)`)을 달아야 합니다.

반드시 아래에 정의된 JSON 스키마 구조로만 순수하게 응답하세요 (백틱(`) 등 포매팅 제외):
{{
    "has_ai_news": boolean,
    "title": "[{date_str_kor}] {source_name} 주요 뉴스 요약",
    "excerpt": "오늘 포함된 뉴스들의 전반적인 핵심을 아우르는 1문장 요약",
    "markdown_content": "목차(필요시) 및 각 기사별 세부 내용, 이미지 태그가 모두 병합된 완전한 마크다운 본문"
}}
"""
    import time
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            
            clean_text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_text)
            return data
        except Exception as e:
            err_msg = str(e)
            print(f"\nGemini API 에러 ({source_name}) [시도 {attempt+1}/3]: {err_msg}")
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                time.sleep(20) # wait 20s for rate limit
            else:
                return None
    return None

def create_markdown_post(source_name, result_data):
    """조합된 요약을 바탕으로 Booklog 포스팅용 마크다운 파일을 생성합니다."""
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)
        
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime("%Y-%m-%d")
    
    # 출처(Source)의 이름을 기반으로 slug를 만들어 하루 1개의 파일만 유지되도록 함
    slug = slugify(source_name)
    if len(slug) > 30:
        slug = slug[:30]
        
    filename = f"{date_str}-{slug}-summary.md"
    filepath = os.path.join(POSTS_DIR, filename)
    
    # 하루에 동일 소스에 대한 파일이 여러번 돌면 덮어씀 (가장 최신 뉴스 묶음으로 유지)
    if os.path.exists(filepath):
        print(f" ⚠️ 이미 동일 소스의 오늘자 포스트가 존재합니다. 내용을 최신화(덮어쓰기) 합니다: {filename}")
        
    frontmatter = f"""---
title: "{result_data['title'].replace('"', "'")}"
date: "{date_str}"
excerpt: "{result_data['excerpt'].replace('"', "'")}"
category: "Learning AI"
---

{result_data['markdown_content']}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        
    print(f" ✅ 일일 요약 포스트 생성 완료: {filename}")
    return True

def main():
    print("\n=======================================================")
    print("📡 Booklog RSS to Markdown (Batch Mode 통폐합) 가동 시작")
    print("=======================================================")
    
    for feed in FEEDS:
        print(f"\n🔍 대상 피드: {feed['name']}")
        items = parse_recent_rss_items(feed, days_limit=1.5)
        
        if not items:
            print(" └ 새로운 포스팅이 없습니다.")
            continue
            
        print(f" └ {len(items)}개의 최신 기사 발견! 소스별 종합 분석 및 요약 진행 중...")
        
        result = process_source_batch_with_llm(feed['name'], items)
        
        if not result:
            print(" └ [오류: API 에러 혹은 JSON 파싱 실패]")
            continue
            
        if not result.get("has_ai_news"):
            print(" └ [스킵: AI와 관련된 유의미한 뉴스가 없음]")
            continue
            
        print(" └ [통과: 종합 요약 마크다운 생성 중]")
        create_markdown_post(feed['name'], result)
            
    print("\n🎉 모든 RSS 데이터 수집 및 일일 종합 포스트 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()
