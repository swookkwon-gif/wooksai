#!/usr/bin/env python3
"""
book_pipeline.py — 책 출간 파이프라인
시리즈 포스트를 컴파일하여 책(마크다운/PDF)으로 출간한다.

사용법:
  # 시리즈 목록 확인
  python scripts/book_pipeline.py status

  # 특정 시리즈 상세 확인
  python scripts/book_pipeline.py status --id data-statistics -v

  # 책 컴파일 (마크다운)
  python scripts/book_pipeline.py compile --id data-statistics

  # 책 미리보기 (첫 3개 챕터만)
  python scripts/book_pipeline.py preview --id data-statistics

  # PDF 출력
  python scripts/book_pipeline.py export --id data-statistics --format pdf
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from skills.config_loader import load_json
from agents.book_compiler import compile_book, save_book, export_pdf


def load_series_registry() -> dict:
    return load_json('series_registry.json')


def get_series(registry: dict, series_id: str) -> dict | None:
    for s in registry.get("series", []):
        if s["id"] == series_id:
            return s
    return None


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
        pct = f"{published/total*100:.0f}%" if total else "N/A"

        print(f"\n{'='*50}")
        print(f"📚 {series['title']}")
        print(f"{'='*50}")
        print(f"  ID:       {series['id']}")
        print(f"  카테고리:  {series.get('category', 'N/A')}")
        print(f"  진행률:   {published}/{total} ({pct})")
        print(f"  책 제목:  {series.get('book', {}).get('target_title', 'N/A')}")
        print(f"  노트북:   {series.get('notebook_id', 'N/A')}")

        if args.verbose:
            print(f"\n  {'─'*46}")
            for ch in chapters:
                icon = "✅" if ch.get("status") == "published" else "⬜"
                print(f"  {icon} {ch['number']:2d}. {ch['title']}")


def cmd_compile(args):
    """시리즈를 책으로 컴파일한다."""
    registry = load_series_registry()
    series = get_series(registry, args.id)

    if not series:
        print(f"❌ 시리즈 '{args.id}'를 찾을 수 없습니다.")
        sys.exit(1)

    chapters = series.get("chapters", [])
    published = [c for c in chapters if c.get("status") == "published"]

    if not published:
        print(f"❌ 발행된 챕터가 없습니다.")
        sys.exit(1)

    print(f"{'='*55}")
    print(f"📖 책 컴파일: {series.get('book', {}).get('target_title', series['title'])}")
    print(f"   발행 챕터: {len(published)}/{len(chapters)}")
    print(f"{'='*55}")

    book_content = compile_book(series)
    book_path = save_book(series, book_content)

    # 글자 수 / 예상 페이지 수 출력
    char_count = len(book_content)
    page_estimate = char_count // 1500  # 한글 기준 약 1500자/페이지
    print(f"\n  📊 총 {char_count:,}자 ({page_estimate}페이지 예상)")
    print(f"\n🎉 컴파일 완료! → {book_path}")


def cmd_preview(args):
    """책 미리보기 (첫 N개 챕터)."""
    registry = load_series_registry()
    series = get_series(registry, args.id)

    if not series:
        print(f"❌ 시리즈 '{args.id}'를 찾을 수 없습니다.")
        sys.exit(1)

    # 처음 3개 챕터만
    preview_series = dict(series)
    published = [c for c in series.get("chapters", []) if c.get("status") == "published"]
    preview_series["chapters"] = published[:3]

    print(f"📖 미리보기 (처음 {min(3, len(published))}개 챕터)")
    book_content = compile_book(preview_series)

    # 터미널에 첫 2000자만 출력
    print("\n" + "─" * 55)
    print(book_content[:2000])
    if len(book_content) > 2000:
        print(f"\n... (이하 {len(book_content) - 2000:,}자 생략)")
    print("─" * 55)


def cmd_export(args):
    """책을 특정 포맷으로 내보낸다."""
    registry = load_series_registry()
    series = get_series(registry, args.id)

    if not series:
        print(f"❌ 시리즈 '{args.id}'를 찾을 수 없습니다.")
        sys.exit(1)

    books_dir = os.path.join(os.path.dirname(__file__), '..', 'content', 'books', args.id)
    book_md_path = os.path.join(books_dir, "book.md")

    if not os.path.exists(book_md_path):
        print(f"❌ 먼저 'compile'을 실행하여 book.md를 생성해주세요.")
        print(f"   python scripts/book_pipeline.py compile --id {args.id}")
        sys.exit(1)

    if args.format == "pdf":
        print(f"📄 PDF 출력 중...")
        result = export_pdf(book_md_path)
        if result:
            print(f"\n🎉 PDF 생성 완료! → {result}")
        else:
            print(f"\n❌ PDF 생성 실패")
            sys.exit(1)
    else:
        print(f"✅ 마크다운 파일 이미 존재: {book_md_path}")


def main():
    parser = argparse.ArgumentParser(
        description="📚 책 출간 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="명령")

    # status
    p_status = subparsers.add_parser("status", help="시리즈 상태 확인")
    p_status.add_argument("--id", default=None, help="시리즈 ID")
    p_status.add_argument("-v", "--verbose", action="store_true")
    p_status.set_defaults(func=cmd_status)

    # compile
    p_compile = subparsers.add_parser("compile", help="시리즈를 책으로 컴파일")
    p_compile.add_argument("--id", required=True, help="시리즈 ID")
    p_compile.set_defaults(func=cmd_compile)

    # preview
    p_preview = subparsers.add_parser("preview", help="책 미리보기")
    p_preview.add_argument("--id", required=True, help="시리즈 ID")
    p_preview.set_defaults(func=cmd_preview)

    # export
    p_export = subparsers.add_parser("export", help="책 내보내기")
    p_export.add_argument("--id", required=True, help="시리즈 ID")
    p_export.add_argument("--format", default="markdown", choices=["markdown", "pdf"])
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
