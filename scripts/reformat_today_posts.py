import os
import re
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News')
TARGET_FILES = [
    '2026-04-29-today-ai-top3-news-gf2-script.md',
    '2026-04-29-today-ai-top3-news-gf2.md',
    '2026-04-29-today-ai-top3-news.md'
]

def reformat_post(file_path):
    print(f"🔄 Reformatting {os.path.basename(file_path)}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter and body
    match = re.match(r'^(---\n.*?\n---\n)(.*)$', content, re.DOTALL)
    if not match:
        print(f"❌ Could not parse frontmatter in {file_path}")
        return
    
    frontmatter = match.group(1)
    body = match.group(2)

    prompt = f"""
다음은 인공지능 뉴스 블로그 포스트의 본문 내용입니다. 아래 지침에 따라 이 내용을 다시 작성(Reformat)해 주세요.

[원본 내용]
{body}

[작성 지침]
1. 본문 소제목(##) 아래의 '소식 요약', '시사점'과 같은 불필요한 영역별 제목을 삭제하고, 내용을 자연스러운 문단(줄글)으로 통합하세요.
2. 포스트 하단에 'Top 10 주요 뉴스 및 중요도 평가 테이블'을 마크다운 표 형식으로 반드시 생성하세요.
3. 표의 컬럼은 [순위, 기사 제목, 중요도 점수, 선정 사유]로 구성하세요.
4. '선정 사유'는 매우 구체적이어야 합니다. 단순히 '중요하다'가 아니라, 예를 들어 '6천억 달러 규모의 자본 투입이 일반적인 국방부 API 도입 뉴스보다 시장에 미치는 파급력이 훨씬 크기 때문'과 같이 구체적인 비교 우위와 파급력을 기술하세요.
5. 어조는 전문적인 테크 저널 목록형 어조(~이다, ~한다)를 사용하세요.
6. 텍스트가 깨지지 않게 표 내부 줄바꿈은 <br>을 사용하세요.
7. 마크다운 형식으로 응답하되, 다른 설명 없이 본문 내용만 출력하세요.
"""

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=8192
            )
        )
        
        new_body = response.text.strip()
        if new_body:
            # Check if AI output includes the frontmatter by mistake
            if new_body.startswith('---'):
                new_body = re.sub(r'^---\n.*?\n---\n', '', new_body, flags=re.DOTALL).strip()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + "\n" + new_body + "\n")
            print(f"✅ Successfully reformatted {file_path}")
        else:
            print(f"❌ Empty response for {file_path}")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

if __name__ == "__main__":
    for filename in TARGET_FILES:
        path = os.path.join(POSTS_DIR, filename)
        if os.path.exists(path):
            reformat_post(path)
        else:
            print(f"⚠️ File not found: {path}")
