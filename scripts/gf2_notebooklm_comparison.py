import os
import re
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip('"').strip("'")
client = genai.Client(api_key=GEMINI_API_KEY)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '3. AI Learnings')
os.makedirs(POSTS_DIR, exist_ok=True)

prompt = """
당신은 최고 수준의 테크 저널리스트이자 AI 툴 애널리스트입니다. 구글 검색(Grounding)을 활용하여 구글의 AI 기반 연구 도구인 NotebookLM에 대해 심층 리서치하고 블로그 포스트를 작성하세요.

[요구사항]
1. 수많은 다른 AI 관련 도구(ChatGPT, Perplexity, Claude, 일반 RAG 툴 등 주요 도구 최소 4개 이상) 중에서 왜 NotebookLM이 독보적으로 중요한지 분석하세요. 
   - 주요 AI 도구 리스트를 나열하고, 각 툴의 '강점'과 '한계점'을 NotebookLM과 비교하여 구체적으로 서술하세요. (이 비교 섹션은 가독성을 위해 마크다운 표 형식을 적극 권장합니다)
2. NotebookLM의 핵심 가치 제안, 주요 기능, 그리고 사용자가 얻을 수 있는 이점을 상세히 분석하십시오. 특히 사용자가 빠르게 익힐 수 있고 실무나 학습에 즉각적으로 활용 가능한 기능들을 중심으로 조사하십시오.
3. 조사한 NotebookLM의 핵심 기능들을 '학습 용이성'과 '실용적 가치'를 기준으로 우선순위를 매겨 리스트 형태로 정리하십시오. 각 기능이 왜 유용한지에 대한 상세 설명을 포함하십시오.

[작성 가이드라인]
1. 메타 데이터 생성 (반드시 첫 두 줄에 작성):
   - 첫 줄: "TITLE: [제목]" (대괄호 없이 제목만 작성, 주관적인 꾸밈말 배제)
   - 두 번째 줄: "EXCERPT: [요약문]" (150자 내외)
2. 레퍼런스 및 주석:
   - 구글 검색을 통해 참조한 내용을 본문 내에 인용할 때는 마크다운 표준 주석 문법인 `[^1]` 형태를 사용하여 클릭 시 하단으로 스크롤 되도록 작성하세요.
   - 포스트 가장 하단에는 본문에 사용된 주석 번호 1번부터 순서대로 정렬하여 `[^1]: [기사 제목](URL)` 형태의 목록으로 명확하게 제공하세요. 
   - 만약 기사의 정확한 원본 URL을 제공할 수 없다면 억지로 가짜 URL을 생성하지 말고 `[^1]: 기사 제목` 형식으로 링크 없이 텍스트만 표기하세요.
3. 어조는 전문적인 테크 저널 목록형 어조(~이다, ~한다)를 사용할 것.
4. 마크다운 형식으로 작성할 것.
"""

print("🚀 Gemini Flash에 프롬프트 전송 중 (Google Search Grounding 사용)...")

try:
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=8192,
            tools=[{"google_search": {}}]
        )
    )
    article_content = response.text
except Exception as e:
    print(f"❌ API 호출 에러: {e}")
    # Fallback to gemini-flash-latest
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=8192,
                tools=[{"google_search": {}}]
            )
        )
        article_content = response.text
    except Exception as fallback_e:
        print(f"❌ Fallback API 호출 에러: {fallback_e}")
        exit(1)

if not article_content:
    print("❌ 응답 텍스트가 없습니다.")
    exit(1)

now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
slug_name = "notebooklm-vs-others-gf2"
file_name = f"{now_kst.strftime('%Y-%m-%d')}-{slug_name}.md"
file_path = os.path.join(POSTS_DIR, file_name)

display_title = f"NotebookLM과 주요 AI 툴 비교 분석"
display_excerpt = "다양한 AI 도구 속에서 NotebookLM이 지니는 독보적인 가치와 타 AI 툴과의 장단점을 심층 비교합니다."

lines = article_content.split('\n')
content_start_idx = 0

for i in range(min(10, len(lines))):
    line = lines[i].strip()
    if line.startswith("TITLE:"):
        display_title = line.replace("TITLE:", "").replace("[", "").replace("]", "").strip()
        display_title = f"[GF2.0] {display_title}"
        content_start_idx = max(content_start_idx, i + 1)
    elif line.startswith("EXCERPT:"):
        display_excerpt = line.replace("EXCERPT:", "").replace("[", "").replace("]", "").strip()
        content_start_idx = max(content_start_idx, i + 1)

if "[GF2.0]" not in display_title:
    display_title = f"[GF2.0] {display_title}"
        
clean_article = '\n'.join(lines[content_start_idx:]).strip()

frontmatter = f"""---
title: '{display_title.replace("'", "''")}'
date: {now_kst.strftime('%Y-%m-%dT%H:%M:%S+09:00')}
excerpt: '{display_excerpt.replace("'", "''")}'
categories:
  - AI Learnings
tags:
  - NotebookLM
  - Gemini Flash
  - Tool Comparison
---

"""

final_content = frontmatter + clean_article

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"🎉 성공적으로 Gemini Flash 분석 포스트가 생성되었습니다!")
print(f"📁 위치: {file_path}")
