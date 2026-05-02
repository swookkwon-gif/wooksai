#!/usr/bin/env python3
"""
research_pipeline.py — NotebookLM 리서치 통합 파이프라인
기존 4개 스크립트(nlm_auto_blogger, deep_research_daemon, gf2_auto_blogger,
generate_ai_survival_series)를 하나로 통합한 CLI 도구.

사용법:
  # Ad-hoc 단건 리서치
  python scripts/research_pipeline.py adhoc "오픈소스 LLM 100만 토큰 컨텍스트 기술"
  python scripts/research_pipeline.py adhoc "주제" --category "Tech" --mode deep

  # Daily Top3 뉴스
  python scripts/research_pipeline.py daily

  # 시리즈 챕터 생성
  python scripts/research_pipeline.py series --id ai-survival-guide --chapter 3

  # 시리즈 상태 확인
  python scripts/research_pipeline.py status --id ai-survival-guide
"""
import os
import sys
import argparse
import json
import time

# 프로젝트 루트 설정
sys.path.insert(0, os.path.dirname(__file__))

from agents.researcher import research_adhoc, research_daily_top3, research_series_chapter
from skills.config_loader import load_json


def load_series_registry() -> dict:
    """시리즈 레지스트리를 로드한다."""
    return load_json('series_registry.json')


def get_series(registry: dict, series_id: str) -> dict | None:
    """시리즈 ID로 시리즈 정보를 찾는다."""
    for s in registry.get("series", []):
        if s["id"] == series_id:
            return s
    return None


def cmd_adhoc(args):
    """Ad-hoc 단건 리서치 실행."""
    print("=" * 55)
    print(f"🔬 [Ad-hoc Research] {args.topic}")
    print("=" * 55)

    file_path = research_adhoc(
        topic=args.topic,
        category=args.category,
        research_mode=args.mode,
        notebook_id=args.notebook_id,
        slug=args.slug,
    )

    if file_path:
        print(f"\n🎉 성공! 파일: {file_path}")
        print("   git add/commit/push 후 블로그에 반영됩니다.")
    else:
        print("\n❌ 포스트 생성 실패")
        sys.exit(1)


def cmd_daily(args):
    """Daily Top3 뉴스 리서치 실행."""
    print("=" * 55)
    print("📰 [Daily Top 3] AI 뉴스 리서치")
    print("=" * 55)

    file_path = research_daily_top3()

    if file_path:
        print(f"\n🎉 성공! 파일: {file_path}")
    else:
        print("\n❌ 포스트 생성 실패")
        sys.exit(1)


def cmd_series(args):
    """시리즈 챕터 생성."""
    registry = load_series_registry()
    series = get_series(registry, args.id)

    if not series:
        print(f"❌ 시리즈 '{args.id}'를 찾을 수 없습니다.")
        print(f"   사용 가능한 시리즈: {[s['id'] for s in registry.get('series', [])]}")
        sys.exit(1)

    if not series.get("notebook_id"):
        print(f"❌ 시리즈 '{args.id}'에 노트북 ID가 설정되지 않았습니다.")
        sys.exit(1)

    # 특정 챕터 번호 지정
    chapters = series.get("chapters", [])

    if args.chapter:
        target = next((c for c in chapters if c["number"] == args.chapter), None)
        if not target:
            print(f"❌ 챕터 {args.chapter}을 찾을 수 없습니다.")
            sys.exit(1)
        chapters_to_gen = [target]
    else:
        # draft 상태인 챕터 모두 생성
        chapters_to_gen = [c for c in chapters if c.get("status") != "published"]

    if not chapters_to_gen:
        print(f"✅ 모든 챕터가 이미 발행되었습니다!")
        return

    print("=" * 55)
    print(f"📚 [Series] {series['title']}")
    print(f"   총 {len(chapters_to_gen)}개 챕터 생성 예정")
    print("=" * 55)

    for ch in chapters_to_gen:
        file_path = research_series_chapter(
            topic=ch["title"],
            series_id=args.id,
            series_title=series["title"],
            chapter_number=ch["number"],
            notebook_id=series["notebook_id"],
            slug=ch["slug"],
            category=series.get("category", "AI Learnings"),
        )

        if file_path:
            ch["status"] = "published"
        else:
            print(f"  ⚠️ 챕터 {ch['number']} 생성 실패, 다음 챕터로 넘어갑니다.")

        # Rate limit 방지
        if len(chapters_to_gen) > 1:
            print("  ⏳ 다음 챕터까지 60초 대기...")
            time.sleep(60)

    # 레지스트리 업데이트
    registry_path = os.path.join(os.path.dirname(__file__), 'config', 'series_registry.json')
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"\n📝 시리즈 레지스트리 업데이트 완료")


def cmd_status(args):
    """시리즈 상태를 출력한다."""
    registry = load_series_registry()

    if args.id:
        series_list = [get_series(registry, args.id)]
        if not series_list[0]:
            print(f"❌ 시리즈 '{args.id}'를 찾을 수 없습니다.")
            sys.exit(1)
    else:
        series_list = registry.get("series", [])

    for series in series_list:
        chapters = series.get("chapters", [])
        published = sum(1 for c in chapters if c.get("status") == "published")
        total = len(chapters)

        print(f"\n📚 {series['title']} ({series['id']})")
        print(f"   카테고리: {series.get('category', 'N/A')}")
        print(f"   진행률: {published}/{total} ({published/total*100:.0f}%)" if total else "   챕터 없음")
        print(f"   노트북: {series.get('notebook_id', 'N/A')}")
        print(f"   책 제목: {series.get('book', {}).get('target_title', 'N/A')}")

        if args.verbose:
            for ch in chapters:
                status_icon = "✅" if ch.get("status") == "published" else "⬜"
                print(f"     {status_icon} {ch['number']:2d}. {ch['title']}")


def main():
    parser = argparse.ArgumentParser(
        description="NotebookLM 리서치 통합 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="실행 모드")

    # adhoc
    p_adhoc = subparsers.add_parser("adhoc", help="Ad-hoc 단건 리서치")
    p_adhoc.add_argument("topic", help="리서치 주제")
    p_adhoc.add_argument("--category", default="Tech", help="블로그 카테고리 (기본: Tech)")
    p_adhoc.add_argument("--mode", default="fast", choices=["fast", "deep"], help="리서치 모드")
    p_adhoc.add_argument("--notebook-id", default=None, help="기존 노트북 ID")
    p_adhoc.add_argument("--slug", default=None, help="파일명 슬러그")
    p_adhoc.set_defaults(func=cmd_adhoc)

    # daily
    p_daily = subparsers.add_parser("daily", help="Daily Top 3 AI 뉴스")
    p_daily.set_defaults(func=cmd_daily)

    # series
    p_series = subparsers.add_parser("series", help="시리즈 챕터 생성")
    p_series.add_argument("--id", required=True, help="시리즈 ID")
    p_series.add_argument("--chapter", type=int, default=None, help="특정 챕터 번호 (없으면 미발행 전체)")
    p_series.set_defaults(func=cmd_series)

    # status
    p_status = subparsers.add_parser("status", help="시리즈 상태 확인")
    p_status.add_argument("--id", default=None, help="시리즈 ID (없으면 전체)")
    p_status.add_argument("-v", "--verbose", action="store_true", help="챕터 상세 출력")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
