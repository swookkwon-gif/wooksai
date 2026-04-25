#!/usr/bin/env python3
import os
import time
import json
import re
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY is missing.")
    import sys; sys.exit(1)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News')

def get_recent_posts(days=7):
    recent_texts = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    
    if not os.path.exists(POSTS_DIR):
        return []
        
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"): continue
        
        # 날짜 추출 2026-04-20-...
        match = re.match(r'^(\d{4}-\d{2}-\d{2})-', filename)
        if match:
            post_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if post_date >= cutoff_date:
                filepath = os.path.join(POSTS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 본문이 너무 길면 자름
                    if len(content) > 10000:
                        content = content[:10000]
                    recent_texts.append(f"\n[파일명: {filename}]\n{content}\n")
                    
    return recent_texts

def write_weekly_digest(content):
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime("%Y-%m-%d")
    month_week = f"{now_kst.month}월 {now_kst.day // 7 + 1}주차"
    
    post_title = f"{month_week} AI 주간 핵심 리뷰"
    
    frontmatter = f"""---
title: "{post_title}"
date: "{date_str}"
excerpt: "지난 1주일 가장 중요한 AI 트렌드 및 뉴스 결산"
category: "Weekly Digest"
---

"""
    filename = f"{date_str}-weekly-ai-review.md"
    file_path = os.path.join(POSTS_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content + "\n")
        
    print(f"✅ 주간 요약 포스트가 생성되었습니다: {filename}")

def run_weekly_summary():
    print("=======================================================")
    print("🗓️ [Weekly Summary] 주간 AI 리포트 결산 봇 시작")
    print("=======================================================")
    
    posts = get_recent_posts(7)
    if not posts:
        print("최근 7일간의 포스트가 없어 요약을 진행하지 않습니다.")
        return
        
    merged_text = "".join(posts)
    print(f"-> {len(posts)}개의 지난 1주일 포스트 수집 완료. AI 분석 중...")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
당신은 최고 수준의 AI 애널리스트입니다. 아래는 지난 1주일동안 쏟아진 '매일의 AI 뉴스/뉴스레터 요약본' 리스트입니다.

[지난 1주간의 뉴스 데이터]
{merged_text}

[요구사항]
1. 위 내용들을 꼼꼼히 분석하여, 지난 1주일 동안 AI 업계에서 가장 파급력이 크고 중요했던 'Top 5~7가지 핵심 트렌드 및 시사점'을 뽑아내세요.
2. 단순히 뉴스를 나열하지 말고, **서로 연관된 뉴스들은 하나의 거시적 트렌드**로 묶어서 분석적으로 서술하세요.
3. 각 핵심 트렌드는 마크다운 헤더(`###`)로 소제목을 달고, 하위에 글머리 기호(`-`)로 상세 내용과 의미(시사점)를 요약하세요.
4. 마지막에는 이번 주의 결론적인 1~2문단 총평("Weekly Conclusion")을 작성해주세요.
5. 블로그 포스트의 '본문 내용'만 순수하게 출력하세요. 백틱(```) 마크다운 코드블록이나 불필요한 메타 데이터는 절대로 쓰지 마세요.
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        result_text = response.text.replace("```markdown", "").replace("```", "").strip()
        write_weekly_digest(result_text)
    except Exception as e:
        print(f"❌ 주간 요약 생성 중 API 에러: {e}")

if __name__ == "__main__":
    run_weekly_summary()
