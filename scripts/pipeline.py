#!/usr/bin/env python3
"""
pipeline.py — 메인 오케스트레이터
Collector → Writer(+Reviewer) → Publisher 순서로 에이전트를 호출한다.

GitHub Actions에서 기존 auto_blog_daemon.py 대신 이 파일을 호출:
  python scripts/pipeline.py
"""
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from slugify import slugify

# 프로젝트 루트 경로 설정 (scripts/ 기준)
sys.path.insert(0, os.path.dirname(__file__))

from skills.llm_client import LLMClient
from skills.markdown_utils import auto_fix_content
from skills.post_writer import create_post_file
from agents.collector import collect_rss, collect_gmail
from agents.writer import write_rss_post, write_newsletter_post
from agents.reviewer import review_and_fix
from state.state_manager import mark_processed, save_evaluations


def run_rss_pipeline(llm: LLMClient):
    """RSS 수집 → 작성 → 검증 → 발행 파이프라인"""
    print("\n" + "=" * 55)
    print("📰 [Phase: RSS Pipeline]")
    print("=" * 55)

    # 1. Collect
    articles = collect_rss()
    if not articles:
        return

    # 2. Write (평가 + 작성을 Writer가 한 번에 수행 — 기존 동작 호환)
    print(f"\n   📝 Writer: {len(articles)}개 기사 기반 포스트 작성 중...")
    result = write_rss_post(articles, llm)
    if result is None:
        print("   ❌ Writer 실패: LLM 응답 없음")
        return

    if not result.get("has_ai_news"):
        for item in articles:
            mark_processed("rss", item["id"])
        print("   ✅ 중요 기사(3점 이상)가 없어 포스트 생략 (처리완료 마킹)")
        return

    # 3. Review + Auto-fix
    md_content = result.get("markdown_content", "")
    md_content, remaining_issues = review_and_fix(md_content)

    # 4. Save evaluations
    evals = result.get("evaluations", [])
    if evals:
        save_evaluations("Global AI News", evals)

    # 5. Publish
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    title = f"[{now_kst.strftime('%m월 %d일')}] AI times, Benzinga 뉴스 요약"
    file_path = create_post_file("global-ai-news-summary", title, md_content)
    print(f"   ✅ RSS 포스트 저장: {os.path.basename(file_path)}")

    # 6. Mark processed
    for item in articles:
        mark_processed("rss", item["id"])


def run_gmail_pipeline(llm: LLMClient):
    """Gmail 뉴스레터 수집 → 작성 → 검증 → 발행 파이프라인"""
    print("\n" + "=" * 55)
    print("📧 [Phase: Gmail Newsletter Pipeline]")
    print("=" * 55)

    # 1. Collect
    gmail_groups = collect_gmail()
    if not gmail_groups:
        return

    # 2~5. 발신자별 처리
    for sender, letters in gmail_groups.items():
        print(f"\n   -> [{sender}] 뉴스레터 처리 중 ({len(letters)}개)")

        # 2. Write
        result = write_newsletter_post(sender, letters, llm)
        if result is None:
            print(f"   ❌ Writer 실패: [{sender}] LLM 응답 없음")
            continue

        md_content = result.get("markdown_content", "")
        if not md_content:
            for letter in letters:
                mark_processed("gmail", letter["id"])
            print(f"   ✅ 중요 기사(3점 이상)가 없어 포스트 생략")
            continue

        # 3. Review + Auto-fix
        md_content, remaining_issues = review_and_fix(md_content)

        # 4. Save evaluations
        evals = result.get("evaluations", [])
        if evals:
            save_evaluations(sender, evals)

        # 5. Publish
        post_title = result.get("post_title", "최신 AI 뉴스레터 동향")
        slug = slugify(sender) + "-newsletter"
        now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
        title = f"[{sender}] {post_title}"

        file_path = create_post_file(slug, title, md_content)
        print(f"   ✅ 뉴스레터 포스트 저장: {os.path.basename(file_path)}")

        # 6. Mark processed
        for letter in letters:
            mark_processed("gmail", letter["id"])

        # API Pacing
        print("   (발신자 간 대기 10초...)")
        time.sleep(10)


def main():
    print("=======================================================")
    print("🚀 [Multi-Agent Pipeline] Blog Post Generator v2.0")
    print("=======================================================")

    # LLM 클라이언트 초기화
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY is missing.")
        sys.exit(1)

    llm = LLMClient(api_key=api_key)

    # Pipeline 실행
    run_rss_pipeline(llm)

    print("\n" + "-" * 55)

    run_gmail_pipeline(llm)

    print("\n=======================================================")
    print("🎉 Multi-Agent Pipeline 완료!")
    print("=======================================================")


if __name__ == "__main__":
    main()
