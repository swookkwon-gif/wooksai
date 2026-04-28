import os
import sys
import subprocess
import time
from datetime import datetime, timezone, timedelta
import re

# 블로그 포스트 저장 경로
POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '3. Deep Dive')

def run_nlm_cmd(cmd_list, timeout=300):
    """
    Subprocess를 사용하여 nlm(NotebookLM CLI) 명령어를 실행하고 결과를 반환합니다.
    """
    try:
        print(f"🔄 실행 중: {' '.join(cmd_list)}")
        # 사용자 터미널 환경의 PATH를 상속받기 위해 shell=True 로 실행 경로 우회 가능성을 엽니다.
        # NLM 도구가 전역 설치되어 있어야 합니다.
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False # 에러가 나도 직접 처리하기 위해 False
        )
        if result.returncode != 0:
            print(f"❌ 명령어 실행 실패 ({result.returncode}):\n{result.stderr}")
            return False, result.stderr
        
        print(f"✅ 실행 완료.")
        return True, result.stdout
    except subprocess.TimeoutExpired:
        print(f"❌ 실행 시간 초과 ({timeout}초)")
        return False, "Timeout"
    except FileNotFoundError:
        print("❌ 'nlm' 명령어를 찾을 수 없습니다. (PATH 문제 혹은 설치되지 않음)")
        print("터미널에 'nlm'이 설치되어 있는지 확인해주세요.")
        return False, "Not Found"

def generate_slug(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9가-힣\-]+', '-', text)
    text = re.sub(r'\-+', '-', text).strip('-')
    return text

def run_deep_research(topic: str):
    print(f"==================================================")
    print(f"🤖 [Deep Research Daemon] NotebookLM 파이프라인 시작")
    print(f"==================================================")
    print(f"📌 리서치 주제: {topic}")
    
    # 1. 고유한 노트북 이름 생성 (날짜+시간 기반)
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime('%Y%m%d_%H%M')
    notebook_name = f"DeepDive_{date_str}"
    
    # 2. 노트북 생성
    print(f"\n[Step 1] NotebookLM 전용 노트북 생성: {notebook_name}")
    success, out = run_nlm_cmd(["nlm", "notebook", "create", notebook_name])
    if not success:
        return
        
    time.sleep(2)
    
    # 3. 딥 리서치 및 웹 소스 수집 시작
    # nlm research start 명령어는 자체적으로 웹 검색 -> 소스 추가를 수행합니다.
    print(f"\n[Step 2] 에이전틱 리서치 시작 (웹 크롤링 및 소스 추가)")
    success, out = run_nlm_cmd(["nlm", "research", "start", topic], timeout=600)
    if not success:
        print("⚠️ 리서치 소스 수집 중 오류가 발생했습니다. (일부 소스만 저장되었을 수 있습니다.)")
    
    # 리서치 텀 확보
    print("⏳ 데이터 수집 및 업로드 동기화를 위해 10초 대기 중...")
    time.sleep(10)
    
    # 4. 종합 쿼리 작성 및 마크다운 포스트 생성
    print(f"\n[Step 3] 수집된 Source 기반 심층 마크다운 기사 생성")
    query_prompt = f"""
이 노트북에 저장된 모든 리서치 원문(Source)들을 종합하여, 
'{topic}'에 대한 매우 깊이 있는 블로그 포스트를 작성해줘.

[요구사항]
1. 제목은 넣지 마 (첫 번째 줄은 항상 바로 본문이 시작되도록)
2. '배경 설명 -> 핵심 기술 및 동향 -> 비즈니스/산업 시사점 -> 결론' 순서로 전개할 것.
3. 한국어로 자연스럽고 전문적인 '테크 저널리스트' 어조(해요체/하십시오체 금지, ~이다/~한다 체 사용)로 작성.
4. 마크다운 양식을 철저히 지키되, 각 주장의 출처(Source 번호 혹은 이름)가 있다면 자연스럽게 괄호로 명시할 것.
"""
    # 쿼리 명령시 --notebook <name> 옵션이나 직접 지정 방식이 필요할 수 있습니다.
    # 만약 CLI가 포맷터(JSON)를 지원하지 않는 경우 stdout을 파싱해야 합니다.
    success, article_content = run_nlm_cmd(["nlm", "notebook", "query", notebook_name, query_prompt], timeout=600)
    
    if not success:
        print("❌ 포스트 생성 실패")
        return
        
    # 결과물을 터미널 요약 출력에서 걷어내는 전처리 (필요시)
    # CLI 특성상 "[NotebookLM] Answer: ..." 같은 접두사가 붙을 수 있습니다.
    clean_article = article_content
    prefix_match = re.search(r'(Answer:|Response:)(.*)', article_content, re.IGNORECASE | re.DOTALL)
    if prefix_match:
        clean_article = prefix_match.group(2).strip()

    # 5. 파일 저장
    print(f"\n[Step 4] 블로그 업로드용 마크다운 파일 저장")
    slug = generate_slug(topic)
    file_name = f"{now_kst.strftime('%Y-%m-%d')}-{slug}.md"
    file_path = os.path.join(POSTS_DIR, file_name)
    
    os.makedirs(POSTS_DIR, exist_ok=True)
    
    # Frontmatter 조립
    display_title = f"[Deep Dive] {topic}"
    frontmatter = f"""---
title: "{display_title}"
date: {now_kst.strftime('%Y-%m-%dT%H:%M:%S+09:00')}
categories:
  - Deep Dive
tags:
  - Deep Research
  - NotebookLM
  - AI
---

"""
    final_content = frontmatter + clean_article
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"🎉 성공적으로 딥 리서치 포스트가 생성되었습니다!")
    print(f"📁 위치: {file_path}")
    print("\n블로그 변경사항을 확인한 뒤, Github로 Push하면 자동 배포됩니다 (Actions 사용시).")

if __name__ == "__main__":
    test_topic = "최신 오픈소스 LLM의 100만 토큰 컨텍스트 지원 기술과 효율성"
    if len(sys.argv) > 1:
        test_topic = sys.argv[1]
        
    run_deep_research(test_topic)
