#!/usr/bin/env python3
"""
skills/markdown_utils.py — 마크다운 품질 검증 및 자동 수정 유틸리티
Reviewer 에이전트의 핵심 엔진. LLM 호출 없이 정규식으로 즉시 검증/교정한다.
"""
import re
import json
import os


def load_quality_rules() -> dict:
    """config/quality_rules.json을 로드한다."""
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'quality_rules.json')
    if os.path.exists(rules_path):
        with open(rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"format_checks": [], "content_checks": []}


# ── 자동 수정 함수들 ──────────────────────────────────────────

def fix_heading_links(content: str) -> str:
    """
    ### 기사제목(URL) → ### [기사제목](URL)
    LLM이 대괄호를 빼먹는 오류를 자동 교정한다.
    """
    return re.sub(
        r'^(###\s+)([^\[\n]+?)\((https?://[^\)]+)\)\s*$',
        r'\1[\2](\3)',
        content,
        flags=re.MULTILINE,
    )


def wrap_raw_urls(content: str) -> str:
    """
    본문 내 원시 URL을 [원문 보기](URL)로 래핑한다.
    이미 마크다운 링크 안에 있는 URL은 건드리지 않는다.
    """
    # 마크다운 링크 안의 URL은 제외하기 위해 lookbehind/lookahead 사용
    return re.sub(
        r'(?<![(\["\'])(?<!\]\()(?<!: )(https?://\S+)(?![)\]"\'])',
        r'[원문 보기](\1)',
        content,
    )


def strip_duplicate_h1(content: str) -> str:
    """본문 최상단의 H1(# 제목)과 H2(## 제목) 중복을 제거한다."""
    content = re.sub(r'^#\s+[^\n]+\n*', '', content.lstrip())
    content = re.sub(r'^##\s+[^\n]+\n*', '', content.lstrip())
    return content


def ensure_empty_line_after_headings(content: str) -> str:
    """### 소제목 바로 다음 줄이 빈 줄이 아니면 삽입한다."""
    return re.sub(
        r'(^###[^\n]+)\n([^\n])',
        r'\1\n\n\2',
        content,
        flags=re.MULTILINE,
    )


# ── 통합 자동 수정 ────────────────────────────────────────────

def auto_fix_content(content: str) -> str:
    """모든 자동 수정을 순서대로 적용한다."""
    content = strip_duplicate_h1(content)
    content = fix_heading_links(content)
    content = wrap_raw_urls(content)
    content = ensure_empty_line_after_headings(content)
    return content


# ── 검증 함수 ─────────────────────────────────────────────────

def validate_post(content: str, rules: dict | None = None) -> list[dict]:
    """
    마크다운 포스트의 품질을 검증하고 이슈 목록을 반환한다.
    이슈가 없으면 빈 리스트를 반환한다.
    
    Returns:
        list[dict]: [{"rule": str, "severity": str, "detail": str}, ...]
    """
    if rules is None:
        rules = load_quality_rules()

    issues = []

    # ── 포맷 검사 (정규식) ──
    for check in rules.get("format_checks", []):
        pattern = check.get("pattern", "")
        if not pattern:
            continue
        try:
            matches = re.findall(pattern, content, flags=re.MULTILINE)
            if matches:
                sample = matches[0] if isinstance(matches[0], str) else str(matches[0])
                issues.append({
                    "rule": check["rule"],
                    "severity": check.get("severity", "warning"),
                    "detail": f"[{check['rule']}] 위반 발견 ({len(matches)}건): '{sample[:80]}...'",
                    "auto_fixable": check.get("auto_fix", False),
                })
        except re.error:
            pass  # 잘못된 정규식은 무시

    # ── 콘텐츠 검사 ──
    for check in rules.get("content_checks", []):
        rule = check.get("rule", "")

        if rule == "min_word_count":
            clean = re.sub(r'[#*`\[\]\(\)\-]', '', content)
            clean = re.sub(r'https?://\S+', '', clean)
            word_count = len(clean.strip())
            min_count = check.get("min", 100)
            if word_count < min_count:
                issues.append({
                    "rule": rule,
                    "severity": "error",
                    "detail": f"본문이 너무 짧음 ({word_count}자 < 최소 {min_count}자)",
                    "auto_fixable": False,
                })

        elif rule == "has_source_links":
            link_count = len(re.findall(r'\[.*?\]\(https?://.*?\)', content))
            min_links = check.get("min_links", 1)
            if link_count < min_links:
                issues.append({
                    "rule": rule,
                    "severity": "warning",
                    "detail": f"출처 링크 부족 ({link_count}개 < 최소 {min_links}개)",
                    "auto_fixable": False,
                })

    return issues


def generate_excerpt(content: str, max_length: int = 120) -> str:
    """마크다운 본문에서 깨끗한 excerpt(요약문)을 생성한다."""
    clean = re.sub(r'<[^>]+>', '', content)
    clean = re.sub(r'https?://[^\s]+', '', clean)
    clean = re.sub(r'[#*`\[\]\(\)]', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    excerpt = clean[:max_length] + "..." if len(clean) > max_length else clean
    return excerpt.replace('"', "'").replace('\n', ' ')
