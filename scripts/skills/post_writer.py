#!/usr/bin/env python3
"""
skills/post_writer.py — 마크다운 포스트 파일 저장 유틸리티
frontmatter 생성, 파일 저장, excerpt 추출을 담당한다.
"""
import os
import re
from datetime import datetime, timezone, timedelta

from skills.markdown_utils import generate_excerpt

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'content', 'posts', '2. AI News')


def ensure_posts_dir():
    """포스트 디렉토리가 존재하는지 확인하고 없으면 생성한다."""
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)


def create_post_file(
    filename_slug: str,
    post_title: str,
    content: str,
    category: str = "AI News",
    posts_dir: str | None = None,
) -> str:
    """
    마크다운 포스트 파일을 생성한다.
    
    Args:
        filename_slug: 파일명에 사용할 슬러그
        post_title: 포스트 제목
        content: 마크다운 본문
        category: 카테고리
        posts_dir: 포스트 저장 디렉토리 (기본: content/posts/2. AI News/)
    
    Returns:
        생성된 파일의 절대 경로
    """
    target_dir = posts_dir or POSTS_DIR
    ensure_posts_dir()

    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime("%Y-%m-%d")

    excerpt_text = generate_excerpt(content)

    frontmatter = f"""---
title: '{post_title.replace("'", "''")}'
date: '{date_str}'
excerpt: '{excerpt_text.replace("'", "''")}'
category: '{category.replace("'", "''")}'
---

"""
    filename = f"{date_str}-{filename_slug}.md"
    file_path = os.path.join(target_dir, filename)

    # 같은 날 같은 슬러그이면 기존 파일에 추가(append)
    mode = "w" if not os.path.exists(file_path) else "a"
    with open(file_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write(frontmatter)
        f.write(content + "\n\n")

    return file_path
