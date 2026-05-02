#!/usr/bin/env python3
"""
agents/book_compiler.py — 책 컴파일 에이전트
시리즈 포스트들을 모아 책(마크다운/PDF)으로 컴파일한다.
"""
import os
import re
import json
from datetime import datetime, timezone, timedelta


CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'content')
BOOKS_DIR = os.path.join(CONTENT_DIR, 'books')


def _load_chapter_content(category: str, slug: str) -> str | None:
    """개별 챕터 포스트의 본문을 로드한다 (frontmatter 제거)."""
    posts_dir = os.path.join(CONTENT_DIR, 'posts', category)
    
    # 슬러그로 파일 검색
    if not os.path.exists(posts_dir):
        return None
    
    for filename in sorted(os.listdir(posts_dir)):
        if slug in filename and filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # frontmatter 제거
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    content = content[end_idx + 3:].strip()
            
            return content
    
    return None


def _extract_title_from_frontmatter(category: str, slug: str) -> str | None:
    """포스트의 frontmatter에서 title을 추출한다."""
    posts_dir = os.path.join(CONTENT_DIR, 'posts', category)
    if not os.path.exists(posts_dir):
        return None
    
    for filename in sorted(os.listdir(posts_dir)):
        if slug in filename and filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx != -1:
                    fm_block = content[3:end_idx]
                    match = re.search(r"title:\s*['\"]?(.+?)['\"]?\s*$", fm_block, re.MULTILINE)
                    if match:
                        return match.group(1).strip().strip("'\"")
            return None
    return None


def generate_toc(chapters: list[dict]) -> str:
    """목차(Table of Contents)를 생성한다."""
    toc = "# 목차\n\n"
    for ch in chapters:
        num = ch["number"]
        title = ch.get("title", f"챕터 {num}")
        status = ch.get("status", "draft")
        if status == "published":
            toc += f"**{num}장.** {title}\n\n"
        else:
            toc += f"*{num}장. {title} (준비 중)*\n\n"
    return toc


def generate_preface(series: dict) -> str:
    """시리즈 정보를 바탕으로 서문 틀을 생성한다."""
    title = series.get("book", {}).get("target_title", series.get("title", ""))
    desc = series.get("description", "")
    total = len(series.get("chapters", []))
    published = sum(1 for c in series.get("chapters", []) if c.get("status") == "published")
    
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    
    preface = f"""# {title}

---

## 서문

이 책은 블로그 시리즈 '{series.get('title', '')}'의 포스트들을 모아 엮은 것이다.

{desc}

총 {total}개의 챕터 중 {published}개가 수록되어 있으며, 
나머지는 향후 업데이트를 통해 추가될 예정이다.

*{now_kst.strftime('%Y년 %m월 %d일')} 컴파일*

---

"""
    return preface


def compile_book(series: dict, include_drafts: bool = False) -> str:
    """
    시리즈의 모든 발행된 챕터를 하나의 마크다운 문서로 컴파일한다.
    
    Args:
        series: 시리즈 레지스트리 항목
        include_drafts: True면 미발행 챕터도 포함
    
    Returns:
        컴파일된 전체 마크다운 문자열
    """
    category = series.get("category", "")
    chapters = series.get("chapters", [])
    
    if not include_drafts:
        chapters = [c for c in chapters if c.get("status") == "published"]
    
    # 1. 서문
    book_md = generate_preface(series)
    
    # 2. 목차
    book_md += generate_toc(chapters) + "\n---\n\n"
    
    # 3. 각 챕터
    compiled_count = 0
    for ch in chapters:
        if ch.get("status") != "published" and not include_drafts:
            continue
        
        content = _load_chapter_content(category, ch["slug"])
        if not content:
            print(f"  ⚠️ 챕터 {ch['number']} ({ch['slug']}) 파일을 찾을 수 없습니다.")
            continue
        
        # 챕터 헤더
        chapter_title = ch.get("title", f"챕터 {ch['number']}")
        actual_title = _extract_title_from_frontmatter(category, ch["slug"])
        if actual_title:
            chapter_title = actual_title
        
        book_md += f"# {ch['number']}장. {chapter_title}\n\n"
        
        # H1(#)을 H2(##)로 격하하여 챕터 제목과 충돌 방지
        content = re.sub(r'^# ', '## ', content, flags=re.MULTILINE)
        
        book_md += content + "\n\n---\n\n"
        compiled_count += 1
    
    # 4. 후기
    book_md += f"""# 후기

이 책에 수록된 {compiled_count}개의 글은 블로그에 먼저 연재된 후, 
책 형태로 재구성한 것이다. 최신 내용은 블로그에서 확인할 수 있다.

---

*이 책은 AI 도구의 도움을 받아 작성되었으며, 
인간 저자의 기획과 편집을 거쳐 발행되었습니다.*
"""
    
    return book_md


def save_book(series: dict, book_content: str) -> str:
    """컴파일된 책을 파일로 저장한다."""
    series_id = series.get("id", "unknown")
    book_dir = os.path.join(BOOKS_DIR, series_id)
    os.makedirs(book_dir, exist_ok=True)
    
    # 메타데이터 저장
    metadata = {
        "series_id": series_id,
        "title": series.get("book", {}).get("target_title", series.get("title")),
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "total_chapters": len(series.get("chapters", [])),
        "compiled_chapters": sum(1 for c in series.get("chapters", []) if c.get("status") == "published"),
    }
    
    meta_path = os.path.join(book_dir, "metadata.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 마크다운 저장
    book_path = os.path.join(book_dir, "book.md")
    with open(book_path, 'w', encoding='utf-8') as f:
        f.write(book_content)
    
    print(f"  📖 책 저장 완료: {book_path}")
    print(f"  📋 메타데이터: {meta_path}")
    
    return book_path


def export_pdf(book_md_path: str) -> str | None:
    """pandoc을 활용하여 마크다운을 PDF로 변환한다."""
    import subprocess
    
    pdf_path = book_md_path.replace('.md', '.pdf')
    
    try:
        result = subprocess.run(
            [
                "pandoc", book_md_path,
                "-o", pdf_path,
                "--pdf-engine=xelatex",
                "-V", "mainfont=NanumGothic",
                "-V", "geometry:margin=2.5cm",
                "-V", "fontsize=11pt",
                "--toc",
                "--toc-depth=2",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"  📄 PDF 생성 완료: {pdf_path}")
            return pdf_path
        else:
            print(f"  ⚠️ PDF 변환 실패: {result.stderr[:200]}")
            return None
    except FileNotFoundError:
        print("  ⚠️ pandoc이 설치되어 있지 않습니다. (brew install pandoc)")
        return None
    except subprocess.TimeoutExpired:
        print("  ⚠️ PDF 변환 시간 초과")
        return None
