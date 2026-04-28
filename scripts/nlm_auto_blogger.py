import os
import sys
import subprocess
import time
from datetime import datetime, timezone, timedelta
import re

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '3. Deep Dive')

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
        "지난 24시간 동안 발생한 전 세계 AI 기술 및 산업 뉴스 중 "
        "가장 파급력이 크고 중요한 3가지(Top 3) 뉴스를 구글 검색, Google News의 AI/Tech 섹션, "
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
위에서 리서치하여 저장한 'Top 3 뉴스 소스'를 바탕으로 아주 상세한 기술 블로그 포스트를 한국어로 작성해줘.

[작성 가이드라인]
1. 제목은 출력하지 마. (첫 줄은 바로 본문 도입부가 나오게 할 것)
2. 가장 중요한 3개의 뉴스를 각각 큰 소제목(##)으로 구분해줘.
3. 각 뉴스별 작성 체계:
   - [📍 소식 요약]: 해당 뉴스의 팩트와 핵심 내용을 2~3줄로 요약
   - [🔬 기술적 및 산업적 시사점]: 이 뉴스가 왜 중요한지, 개발자나 업계에 어떤 영향을 미칠지 깊이 있게 분석
4. 내용의 신뢰성을 위해 각 주장의 끝에 참조한 소스(출처)를 간략히 명시할 것.
5. 해요체/하십시오체를 쓰지 말고 전문적인 테크 저널 목록형 어조(~이다, ~한다)를 사용할 것.
"""
    success, article_content = run_cmd(["nlm", "notebook", "query", notebook_id, writing_prompt], timeout=600)
    if not success:
        print("❌ 포스트 텍스트 생성에 실패했습니다.")
        return
        
    # 출력된 텍스트 중 nlm CLI의 안내 텍스트(예: "Answer: ")를 제거하는 클리닝 작업
    clean_article = article_content
    prefix_match = re.search(r'(Answer:|Response:)(.*)', article_content, re.IGNORECASE | re.DOTALL)
    if prefix_match:
        clean_article = prefix_match.group(2).strip()

    # 4. 마크다운 파일 저장
    print(f"\n[Step 4] 블로그 업로드용 파일 저장 및 종료")
    slug_name = "today-ai-top3-news"
    file_name = f"{now_kst.strftime('%Y-%m-%d')}-{slug_name}.md"
    file_path = os.path.join(POSTS_DIR, file_name)
    
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    # 휴먼리더블 포스트 제목 생성
    display_title = f"[Daily Top 3] {now_kst.strftime('%m월 %d일')} AI 신기술 동향 및 심층 분석"
    frontmatter = f"""---
title: "{display_title}"
date: {now_kst.strftime('%Y-%m-%dT%H:%M:%S+09:00')}
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
