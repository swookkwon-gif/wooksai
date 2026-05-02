#!/usr/bin/env python3
"""
agents/researcher.py — NotebookLM Deep Research 에이전트
ad-hoc, 시리즈, daily 3가지 모드를 지원하는 통합 리서치 에이전트.
"""
import os
import time
from datetime import datetime, timezone, timedelta

from skills.nlm_client import NotebookLMClient
from skills.llm_client import LLMClient
from skills.markdown_utils import auto_fix_content
from skills.post_writer import create_post_file
from skills.config_loader import load_guidelines
from agents.reviewer import review_and_fix


# ── 작성 프롬프트 ──────────────────────────────────────────────

RESEARCH_WRITING_PROMPT = """이 노트북에 저장된 모든 리서치 원문(Source)들을 종합하여,
'{topic}'에 대한 매우 깊이 있는 블로그 포스트를 작성해줘.

[요구사항]
1. 첫 번째 줄에 "TITLE: 포스트 제목" 형식으로 제목을 작성해. 제목은 핵심 팩트 키워드 중심으로.
2. 두 번째 줄에 "EXCERPT: 요약문" 형식으로 2~3문장 요약을 작성해.
3. 본문은 제목 없이 바로 시작. H1(#) 사용 금지, H2(##)와 H3(###)만 사용.
4. '배경 설명 → 핵심 기술 및 동향 → 비즈니스/산업 시사점 → 결론' 순서로 전개.
5. 한국어, 전문적인 테크 저널리스트 어조(~이다, ~한다).
6. 각 주장의 출처가 있다면 마크다운 링크 [텍스트](URL) 형식으로 자연스럽게 명시.
7. 원시 URL(http://...)을 텍스트로 노출하지 말 것.
8. 포스트 하단에 '## 📚 참고자료' 섹션을 추가하고 주요 출처를 나열할 것.
"""

DAILY_TOP3_PROMPT = """위에서 리서치하여 저장한 소스를 바탕으로 아주 상세한 기술 블로그 포스트를 한국어로 작성해줘.

[요구사항]
1. 첫 번째 줄: "TITLE: 키워드1, 키워드2, 키워드3" (Top 3 뉴스의 핵심 팩트만 콤마로 나열)
2. 두 번째 줄: "EXCERPT: 2~3문장 요약"
3. 본문에 H1(#) 사용 금지. 바로 첫 소제목(##)으로 시작.
4. Top 3 심층 분석: 가장 중요한 3개 뉴스를 각각 큰 소제목(##)으로 구분.
   - 핵심 요약(2~3줄) + 기술적/산업적 시사점을 자연스러운 문단으로 작성.
5. 하단에 Top 10 뉴스 마크다운 테이블 (순위, 기사 제목, 중요도 점수, 선정 사유).
6. 레퍼런스: 본문 내 인용은 [^1] 주석, 하단에 [^1]: [기사 제목](URL) 목록.
7. 어조: ~이다/~한다 체. 원시 URL 노출 금지.
"""

SERIES_WRITING_PROMPT = """이 노트북에 저장된 모든 소스를 종합하여,
'{topic}'에 대한 블로그 포스트를 작성해줘.

이 포스트는 시리즈 '{series_title}'의 {chapter_number}번째 챕터이다.

[요구사항]
1. 첫 번째 줄: "TITLE: 포스트 제목"
2. 두 번째 줄: "EXCERPT: 2~3문장 요약"
3. 본문에 H1(#) 사용 금지. H2(##)와 H3(###)만 사용.
4. 초보자가 이해할 수 있도록 친절하면서도 전문적인 톤으로 작성.
5. 실무 예시를 반드시 포함하여 독자가 바로 적용 가능하도록.
6. 포스트 하단에 '## 📚 참고자료' 섹션 추가.
7. 원시 URL 노출 금지, 마크다운 링크만 사용.
"""


# ── 메타데이터 추출 ────────────────────────────────────────────

def extract_metadata(raw_text: str) -> tuple[str, str, str]:
    """
    LLM 출력에서 TITLE, EXCERPT, 본문을 분리한다.
    
    Returns:
        tuple: (title, excerpt, content)
    """
    lines = raw_text.split('\n')
    title = ""
    excerpt = ""
    content_start = 0

    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").replace("[", "").replace("]", "").strip()
            content_start = max(content_start, i + 1)
        elif line.startswith("EXCERPT:"):
            excerpt = line.replace("EXCERPT:", "").replace("[", "").replace("]", "").strip()
            content_start = max(content_start, i + 1)

    content = '\n'.join(lines[content_start:]).strip()
    return title, excerpt, content


# ── 리서치 모드별 실행 ─────────────────────────────────────────

def research_adhoc(
    topic: str,
    category: str = "Tech",
    research_mode: str = "fast",
    notebook_id: str | None = None,
    slug: str | None = None,
) -> str | None:
    """
    Ad-hoc 단건 리서치 → 블로그 포스트 발행.
    
    Args:
        topic: 리서치 주제
        category: 블로그 카테고리
        research_mode: "fast" 또는 "deep"
        notebook_id: 기존 노트북 사용 시 ID
        slug: 파일명 슬러그 (없으면 자동 생성)
    
    Returns:
        생성된 파일 경로 또는 None
    """
    nlm = NotebookLMClient()
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)

    # 1. 노트북 준비
    if not notebook_id:
        nb_title = f"Research_{now_kst.strftime('%Y%m%d_%H%M')}"
        notebook_id = nlm.create_notebook(nb_title)
        if not notebook_id:
            return None
        time.sleep(3)

    # 2. 딥 리서치
    print(f"\n  📡 리서치 시작: {topic}")
    success, _ = nlm.start_research(
        query=topic,
        notebook_id=notebook_id,
        mode=research_mode,
        timeout=900 if research_mode == "deep" else 300,
    )
    if not success:
        print("  ⚠️ 리서치 시작 실패 (일부 소스만 수집되었을 수 있습니다)")

    # 리서치 완료 대기
    wait_sec = 120 if research_mode == "deep" else 30
    print(f"  ⏳ 소스 분석 대기 중 ({wait_sec}초)...")
    time.sleep(wait_sec)

    # 3. 포스트 작성
    print(f"\n  📝 포스트 작성 중...")
    prompt = RESEARCH_WRITING_PROMPT.format(topic=topic)
    raw_article = nlm.query(notebook_id, prompt, timeout=600)
    if not raw_article:
        print("  ❌ 포스트 생성 실패")
        return None

    # 4. 메타데이터 추출 + 품질 검증
    title, excerpt, content = extract_metadata(raw_article)
    if not title:
        title = f"[Deep Dive] {topic}"
    if not excerpt:
        excerpt = f"{topic}에 대한 심층 분석"

    content, _ = review_and_fix(content)

    # 5. 파일 저장
    if not slug:
        import re
        slug = re.sub(r'[^a-z0-9가-힣\-]+', '-', topic.lower())
        slug = re.sub(r'\-+', '-', slug).strip('-')[:60]

    # 카테고리별 저장 경로
    posts_dir = os.path.join(
        os.path.dirname(__file__), '..', '..', 'content', 'posts', category
    )
    os.makedirs(posts_dir, exist_ok=True)

    file_path = create_post_file(slug, title, content, category=category, posts_dir=posts_dir)
    print(f"  ✅ 포스트 저장: {os.path.basename(file_path)}")
    return file_path


def research_daily_top3(
    research_query: str | None = None,
) -> str | None:
    """
    Daily Top 3 AI 뉴스 리서치 → 블로그 포스트 발행.
    기존 nlm_auto_blogger.py + gf2_auto_blogger.py 통합.
    """
    nlm = NotebookLMClient()
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)

    if not research_query:
        research_query = (
            f"오늘({now_kst.strftime('%Y년 %m월 %d일')}) 발생한 전 세계 AI 기술 및 산업 뉴스 중 "
            "가장 파급력이 크고 중요한 10가지 뉴스를 Google News, Hacker News, "
            "TechCrunch, TLDR AI 등에서 딥 리서치해줘."
        )

    # 1. 노트북 생성
    nb_title = f"Daily_AI_Top3_{now_kst.strftime('%Y%m%d')}"
    notebook_id = nlm.create_notebook(nb_title)
    if not notebook_id:
        return None
    time.sleep(3)

    # 2. 딥 리서치
    print(f"\n  📡 Daily Top3 리서치 시작")
    nlm.start_research(query=research_query, notebook_id=notebook_id, mode="fast")
    print("  ⏳ 소스 분석 대기 중 (60초)...")
    time.sleep(60)

    # 3. 포스트 작성
    print(f"\n  📝 Top 3 심층 포스트 작성 중...")
    raw_article = nlm.query(notebook_id, DAILY_TOP3_PROMPT, timeout=600)
    if not raw_article:
        print("  ❌ 포스트 생성 실패")
        return None

    # 4. 메타데이터 추출 + 품질 검증
    title, excerpt, content = extract_metadata(raw_article)
    if not title:
        title = f"Daily Top 3: {now_kst.strftime('%m월 %d일')} 주요 AI 뉴스"
    if not excerpt:
        excerpt = "오늘의 핵심 글로벌 AI 및 기술 뉴스 동향을 요약합니다."

    content, _ = review_and_fix(content)

    # 5. 파일 저장
    file_path = create_post_file("daily-ai-top3-news", title, content, category="AI News")
    print(f"  ✅ Daily Top3 포스트 저장: {os.path.basename(file_path)}")
    return file_path


def research_series_chapter(
    topic: str,
    series_id: str,
    series_title: str,
    chapter_number: int,
    notebook_id: str,
    slug: str,
    category: str = "AI Learnings",
) -> str | None:
    """
    시리즈 전용 노트북에서 특정 챕터를 작성한다.
    
    Args:
        topic: 챕터 주제
        series_id: 시리즈 ID
        series_title: 시리즈 전체 제목
        chapter_number: 챕터 번호
        notebook_id: 시리즈 전용 노트북 ID
        slug: 파일명 슬러그
        category: 블로그 카테고리
    """
    nlm = NotebookLMClient()

    # 시리즈 전용 프롬프트
    prompt = SERIES_WRITING_PROMPT.format(
        topic=topic,
        series_title=series_title,
        chapter_number=chapter_number,
    )

    # 이미 소스가 축적된 노트북에서 쿼리
    print(f"\n  📝 시리즈 [{series_title}] 챕터 {chapter_number}: {topic}")
    raw_article = nlm.query(notebook_id, prompt, timeout=600)
    if not raw_article:
        print("  ❌ 챕터 생성 실패")
        return None

    # 메타데이터 추출 + 품질 검증
    title, excerpt, content = extract_metadata(raw_article)
    if not title:
        title = topic

    content, _ = review_and_fix(content)

    # 파일 저장
    posts_dir = os.path.join(
        os.path.dirname(__file__), '..', '..', 'content', 'posts', category
    )
    os.makedirs(posts_dir, exist_ok=True)

    file_path = create_post_file(slug, title, content, category=category, posts_dir=posts_dir)
    print(f"  ✅ 챕터 저장: {os.path.basename(file_path)}")
    return file_path
