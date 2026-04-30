import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API Key
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip('"').strip("'")
client = genai.Client(api_key=GEMINI_API_KEY)

FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '3. AI Learnings', '2026-04-28-ai-survival-guide-for-beginners.md')

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    original_content = f.read()

prompt = f"""
당신은 최고 수준의 테크 저널리스트이자 AI 트렌드 분석가입니다.
사용자의 요청에 따라 다음의 기존 '2026년 일반인을 위한 필수 AI 생존 가이드' 블로그 포스트를 대폭 확장하고 고도화해 주세요.

[필수 요구사항]
1. 기존 내용의 흐름과 `[초급]`, `[중급]`, `[고급]` 체계를 유지하세요.
2. 2026년 4월 기준으로 가장 유명하고 실무 성과가 압도적인 핵심 툴들을 포함하세요.
3. **반드시 포함해야 할 필수 툴:** NotebookLM, n8n (이 둘은 특히 강조)
4. **추가 권장 툴:** ChatGPT, Claude, Perplexity, Cursor, Google Antigravity 등
5. **각 툴마다 실제 비즈니스나 일상에서 거둔 '성공적인 활용 사례'를 반드시 2~3건씩 매우 상세하게 구체적으로 작성하세요.** (이것이 가장 중요한 업데이트 목적입니다.)
6. 문서의 가장 윗부분에 있는 Frontmatter (`---` 로 둘러싸인 메타데이터)는 그대로 유지하세요.
7. 마크다운 형식으로 작성하세요.

[기존 원본 텍스트]
{original_content}
"""

print("🚀 Gemini 2.5 Flash를 사용하여 포스트 업데이트 중...")

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=8192,
        )
    )
    new_content = response.text
except Exception as e:
    print(f"❌ Gemini 2.5 Flash 오류: {e}, fallback 사용 중...")
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=8192,
        )
    )
    new_content = response.text

# Ensure frontmatter is clean
if new_content.startswith('```markdown'):
    new_content = new_content.replace('```markdown\n', '')
    if new_content.endswith('```'):
        new_content = new_content[:-3]
elif new_content.startswith('```'):
    new_content = new_content.replace('```\n', '')
    if new_content.endswith('```'):
        new_content = new_content[:-3]

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content.strip() + '\n')

print("✅ 포스트 업데이트가 완료되었습니다!")
