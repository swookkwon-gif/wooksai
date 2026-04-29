import os
import sys
import subprocess
import time
from datetime import datetime, timezone, timedelta
import re

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News')

def run_cmd(cmd_list, timeout=600):
    """서브프로세스로 NLM 명령어를 실행하고 로그를 기록합니다."""
    print(f"🔄 실행 중: {' '.join(cmd_list)}")
    try:
        # NLM 명령어가 표준 출력을 사용하므로 capture_output을 통해 로그를 잡습니다.
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        if result.returncode != 0:
            print(f"❌ 명령어 실행 실패 ({result.returncode}):\n{result.stderr}\n{result.stdout}")
            return False, result.stderr
        
        print(f"✅ 실행 성공.")
        return True, result.stdout
    except subprocess.TimeoutExpired:
        print(f"❌ 실행 시간 초과 ({timeout}초)")
        return False, "Timeout"

def generate_slug(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9가-힣\-]+', '-', text)
    text = re.sub(r'\-+', '-', text).strip('-')
    return text

def run_daily_ai_deep_research():
    print(f"==================================================")
    print(f"🚀 [NotebookLM Auto Blogger] 자동 생성 파이프라인 시작")
    print(f"==================================================")
    
    # 시간 기반 고유 노트북 이름
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime('%Y%m%d')
    notebook_name = f"Daily_AI_Top3_{date_str}"
    
    # 1. 새 노트북 생성
    print(f"\n[Step 1] NotebookLM 전용 노트북 생성: {notebook_name}")
    success, out = run_cmd(["nlm", "notebook", "create", notebook_name])
    if not success:
        return
        
    # 출력에서 노트북 UUID 추출
    notebook_id_match = re.search(r'ID:\s*([a-fA-F0-9\-]{36})', out)
    if not notebook_id_match:
        print("❌ 출력에서 노트북 ID를 추출하지 못했습니다.")
        return
    notebook_id = notebook_id_match.group(1)
    print(f"📌 노트북 생성 완료 (UUID: {notebook_id})")
    
    time.sleep(3)
    
    # 2. 딥 리서치 및 웹 소스 자동 수집 (지난 24시간 트렌드)
    # nlm research start 에 자연어 지시를 전달합니다.
    print(f"\n[Step 2] 자율 딥 리서치 시작 (웹 서칭 및 분석)")
    research_prompt = (
        "오늘 발생한 전 세계 AI 기술 및 산업 뉴스 중 "
        "가장 파급력이 크고 중요한 10가지 뉴스를 구글 검색, Google News의 AI/Tech 섹션, "
        "Hacker News, TechCrunch, TLDR AI 등 신뢰도 높은 소스에서 딥 리서치하여 소스로 추가해줘."
    )
    # CLI 구조에 따라 명령어가 실패할 경우를 대비해 두 가지 포맷을 순차 시도할 수 있습니다.
    success, out = run_cmd(["nlm", "research", "start", research_prompt, "--notebook-id", notebook_id, "--auto-import"], timeout=900)
    if not success:
        print("⚠️ 'research start' 실행에 이슈가 발생했습니다. 대체 쿼리(query)로 직접 지시합니다.")
        # 만약 research start 명령어 문법이 구버전이거나 맞지 않다면, 일반 query 로 검색을 지시합니다.
        run_cmd(["nlm", "notebook", "query", notebook_id, 
                 f"웹 검색을 활용해서 {research_prompt} 결과를 소스로 긁어와줘."], timeout=600)
                 
    print("⏳ AI가 방대한 분량의 웹 소스를 읽고 분석/저장할 시간을 충분히 확보합니다 (2분 대기 중)...")
    time.sleep(120)
    
    # 3. 마크다운 블로그 포스트 생성 요청
    print(f"\n[Step 3] Top 3 뉴스 기반 심층 마크다운 작성")
    writing_prompt = """
위에서 리서치하여 저장한 'Top 10 뉴스 소스'를 바탕으로 아주 상세한 기술 블로그 포스트를 한국어로 작성해줘.

[작성 가이드라인]
1. 메타 데이터 생성 (반드시 첫 두 줄에 작성):
   - 첫 번째 줄은 "TITLE: [제목]" 형식으로 작성하되, 대괄호 `[]`는 빼고 제목 텍스트만 적어. 제목은 가장 중요한 Top 3 뉴스의 핵심 팩트(키워드)만 콤마로 나열해 (예: TITLE: 구글 앤스로픽 400억 달러 투자, MS-오픈AI 계약 변경, 메타 AWS CPU 대규모 도입). '시사하는 바' 같은 주관적 문구는 절대 넣지 마.
   - 두 번째 줄은 "EXCERPT: [요약문]" 형식으로 전체 포스트를 2~3문장(약 100~150자)으로 요약한 프리뷰 텍스트를 적어.
2. 본문 서식: 가독성을 높이기 위해 텍스트 단락 구분을 명확히 하고, 적절한 줄바꿈을 사용할 것.
3. 이미지: 소스에 관련 이미지가 포함되어 있다면 마크다운 형식 `![설명](이미지URL)`으로 적절한 위치에 삽입해.
4. Top 3 심층 분석:
   - 가장 중요한 3개의 뉴스를 각각 큰 소제목(##)으로 구분해.
   - 각 뉴스별로 소식의 핵심을 요약하고(2~3줄), 이어서 기술적 및 산업적 시사점을 깊이 있게 분석하여 줄글로 자연스럽게 작성해. (단, '[소식 요약]', '[시사점]' 같은 영역별 제목이나 괄호 표기는 절대 사용하지 말고 자연스러운 문단으로 구성할 것)
5. Top 10 주요 뉴스 및 중요도 평가 테이블 (반드시 마크다운 표 형식 사용):
   - 포스트 하단에 추출된 10개의 뉴스를 나열하는 마크다운 테이블(표)을 생성해. (컬럼: 순위, 기사 제목, 중요도 점수, 선정 사유)
   - 이 중 앞서 다룬 3가지가 왜 Top 3로 선정되었는지, 그리고 나머지 기사들은 왜 순위가 밀렸는지 '선정 사유'에 매우 구체적인 논거를 들어 기술해. (단순히 '중요하다'가 아니라, 예를 들어 '6천억 달러 규모의 펀딩 지연이 국방부의 일상적인 AI 도입 뉴스보다 산업적 파급력이 훨씬 크기 때문'과 같이 구체적인 비교 우위와 자본/기술적 파급력을 기준으로 중요도를 평가할 것). 텍스트가 깨지지 않도록 표 내부의 줄바꿈은 `<br>` 태그를 사용해.
6. 레퍼런스 및 주석:
   - 본문 내에서 참고한 기사를 인용할 때는 반드시 HTML 위첨자 태그와 하이퍼링크를 결합하여 `<sup>[[1]](원본URL)</sup>` 형태로 클릭 가능한 파란색 링크가 되도록 작성해.
   - 포스트 가장 하단의 레퍼런스 섹션에는 본문에 사용된 주석 번호 1번부터 순서대로 정렬하여 `* [1] [기사 제목](URL)` 형태의 목록으로 명확하게 제공해.
7. 어조: 해요체/하십시오체를 쓰지 말고 전문적인 테크 저널 목록형 어조(~이다, ~한다)를 사용할 것.
"""
    success, article_content = run_cmd(["nlm", "notebook", "query", notebook_id, writing_prompt], timeout=600)
    if not success:
        print("❌ 포스트 텍스트 생성에 실패했습니다.")
        return
        
    # JSON 응답일 경우 처리
    clean_article = article_content
    import json
    try:
        data = json.loads(article_content)
        if 'value' in data and 'answer' in data['value']:
            clean_article = data['value']['answer']
    except json.JSONDecodeError:
        prefix_match = re.search(r'(Answer:|Response:)(.*)', article_content, re.IGNORECASE | re.DOTALL)
        if prefix_match:
            clean_article = prefix_match.group(2).strip()

    # 4. 마크다운 파일 저장
    print(f"\n[Step 4] 블로그 업로드용 파일 저장 및 종료")
    slug_name = "daily-ai-top3-news"
    file_name = f"{now_kst.strftime('%Y-%m-%d')}-{slug_name}.md"
    file_path = os.path.join(POSTS_DIR, file_name)
    
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    # 메타 데이터(제목, 요약) 추출
    display_title = f"Daily Top 3: {now_kst.strftime('%m월 %d일')} 주요 AI 뉴스"
    display_excerpt = "오늘의 핵심 글로벌 AI 및 기술 뉴스 동향을 요약합니다."
    
    lines = clean_article.split('\\n')
    content_start_idx = 0
    
    for i in range(min(5, len(lines))):
        line = lines[i].strip()
        if line.startswith("TITLE:"):
            display_title = line.replace("TITLE:", "").replace("[", "").replace("]", "").strip()
            content_start_idx = max(content_start_idx, i + 1)
        elif line.startswith("EXCERPT:"):
            display_excerpt = line.replace("EXCERPT:", "").replace("[", "").replace("]", "").strip()
            content_start_idx = max(content_start_idx, i + 1)
            
    clean_article = '\\n'.join(lines[content_start_idx:]).strip()

    # 휴먼리더블 포스트 제목 (기본값 대비 우선순위 반영)
    frontmatter = f"""---
title: '{display_title.replace("'", "''")}'
date: {now_kst.strftime('%Y-%m-%dT%H:%M:%S+09:00')}
excerpt: '{display_excerpt.replace("'", "''")}'
categories:
  - AI News
tags:
  - Deep Research
  - NotebookLM
  - Daily Top 3
---

"""
    final_content = frontmatter + clean_article
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"🎉 성공적으로 NotebookLM 무인 블로그 포스트가 생성되었습니다!")
    print(f"📁 위치: {file_path}")

if __name__ == "__main__":
    run_daily_ai_deep_research()
