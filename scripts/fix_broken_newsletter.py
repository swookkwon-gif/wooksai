import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News', '2026-04-28-tldr-newsletter.md')

def fix_newsletter():
    print(f"🔄 Fixing {os.path.basename(FILE_PATH)}...")
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^(---\n.*?\n---\n)(.*)$', content, re.DOTALL)
    if not match:
        print(f"❌ Could not parse frontmatter")
        return
    
    frontmatter = match.group(1)
    body = match.group(2)

    prompt = f"""
다음은 AI 뉴스레터 요약 내용입니다. 이 내용이 가독성 있게 블로그 포스트로 노출되도록 마크다운 형식을 다듬어 주세요.

[원본 내용]
{body}

[지침]
1. 주제별 소제목(###) 아래의 내용들을 불렛 포인트( - )를 사용한 목록 형태로 정리해 주세요.
2. 문장 간에 적절한 줄바꿈을 추가하여 가독성을 높여 주세요.
3. 어조는 전문적인 테크 저널 어조(~이다, ~한다)를 유지하세요.
4. 마크다운 형식으로 응답하되, 다른 설명 없이 본문 내용만 출력하세요.
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
            # Fix date in frontmatter if needed (standardize it)
            if 'date: "2026-04-28"' in frontmatter:
                frontmatter = frontmatter.replace('date: "2026-04-28"', 'date: 2026-04-28T09:00:00+09:00')

            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(frontmatter + "\n" + new_body + "\n")
            print(f"✅ Successfully fixed {FILE_PATH}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_newsletter()
