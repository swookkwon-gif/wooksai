import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

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
사용자의 추가 요청에 따라 다음의 기존 가이드 블로그 포스트를 한 번 더 고도화해 주세요.

[필수 요구사항]
1. 본문(서론이나 각 섹션 도입부)에 다음 툴 선정 기준을 자연스럽게 언급해 주세요: "본 가이드의 AI 툴들은 미국 실리콘밸리를 비롯한 글로벌 테크 트렌드와 Reddit(r/artificial, r/LocalLLaMA 등) 실무자 커뮤니티의 생생한 피드백을 종합하여, 실제 생산성(ROI) 향상이 입증된 것들만 엄선했습니다."
2. **반드시 새로 추가해야 할 툴:** Gemini(Google), OpenClaw, Claude Code, Codex (기존 툴인 NotebookLM, n8n, ChatGPT, Claude, Perplexity, Cursor 등은 삭제하지 말고 반드시 유지하세요!)
   * 참고: OpenClaw는 2025-2026년에 걸쳐 화제가 된 로컬 구동 기반의 오픈소스 자율 AI 에이전트로, 파일 시스템 접근과 프로액티브 자동화가 특징입니다.
3. **새로 추가되는 4개의 툴(Gemini, OpenClaw, Claude Code, Codex)에 대해서도 실제 성공적인 활용 사례를 반드시 2~3건씩 매우 상세하고 구체적으로 작성하세요.**
4. 앞부분의 Frontmatter (`---` 로 둘러싸인 메타데이터)는 그대로 유지하세요.
5. 마크다운 형식으로 응답하세요.

[기존 원본 텍스트]
{original_content}
"""

print("🚀 Gemini 2.5 Flash를 사용하여 포스트 2차 업데이트 중...")

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
    print(f"❌ 오류: {e}")
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=8192,
        )
    )
    new_content = response.text

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

print("✅ 2차 포스트 업데이트가 완료되었습니다!")
