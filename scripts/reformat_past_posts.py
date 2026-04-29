import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News')

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
2. 포스트 하단에 'Top 10 주요 뉴스 및 중요도 평가 테이블'을 마크다운 표 형식으로 반드시 생성하세요. (컬럼: 순위, 기사 제목, 중요도 점수, 선정 사유)
3. '선정 사유'는 단순 요약이 아니라 '자본 투입 규모가 크기 때문', '경쟁 생태계를 바꾸기 때문' 등 구체적이고 논리적인 이유를 적어주세요. 텍스트가 깨지지 않게 표 내부 줄바꿈은 <br>을 사용하세요.
4. **[주석 보존 및 양식 변경]**: 
   - 기존 본문에 있던 주석 번호(예: [1], [2])는 절대 지우지 말고 그 위치를 그대로 유지하세요.
   - 단, 본문 내의 주석 번호는 반드시 HTML 위첨자(Superscript) 태그와 마크다운 링크를 결합하여 `<sup>[[1]](URL)</sup>` 형태로 클릭 가능한 파란색 링크가 되도록 수정해 주세요. (원본 하단 레퍼런스의 URL을 찾아 매칭하세요. URL을 모른다면 `<sup>[1]</sup>` 형태라도 유지하세요.)
   - 포스트 가장 하단의 레퍼런스(참고문헌) 목록은 1번부터 번호 순서대로 정렬하고, 각 항목을 `* [1] [기사 제목](URL)` 형태의 클릭 가능한 마크다운 링크로 깔끔하게 정리해 주세요.
5. 어조는 전문적인 테크 저널 목록형 어조(~이다, ~한다)를 사용하세요.
6. 마크다운 형식으로 응답하되, 다른 설명 없이 본문 내용만 출력하세요.
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
    # Find all past daily/today top 3 posts
    files = os.listdir(POSTS_DIR)
    target_files = [f for f in files if "today-ai-top3-news" in f or "daily-ai-top3-news" in f]
    
    # Exclude the ones we already did today to save time? 
    # Wait, the user specifically asked to apply "today's changes to PAST posts", but also wanted the new footnote rules applied. 
    # So I should probably run it on ALL of them, including today's, to apply the new footnote superscript rule!
    for filename in target_files:
        path = os.path.join(POSTS_DIR, filename)
        reformat_post(path)
