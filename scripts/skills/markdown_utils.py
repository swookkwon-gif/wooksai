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


# ── 단어 수 / 글자 수 계산 ─────────────────────────────────────

def count_words(content: str) -> int:
    """마크다운 본문의 실제 단어 수를 계산한다 (마크다운 문법, URL 제거 후)."""
    clean = re.sub(r'---\n.*?\n---', '', content, flags=re.DOTALL)  # frontmatter
    clean = re.sub(r'https?://\S+', '', clean)       # URL 제거
    clean = re.sub(r'[#*`\[\]\(\)\-|>!]', '', clean) # 마크다운 기호
    clean = re.sub(r'\s+', ' ', clean).strip()
    return len(clean.split())


def count_chars(content: str) -> int:
    """마크다운 본문의 실제 글자 수를 계산한다."""
    clean = re.sub(r'---\n.*?\n---', '', content, flags=re.DOTALL)
    clean = re.sub(r'https?://\S+', '', clean)
    clean = re.sub(r'[#*`\[\]\(\)\-|>!]', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return len(clean)


def estimate_reading_time(word_count: int) -> int:
    """예상 읽기 시간(분)을 계산한다. 한글 기준 분당 약 200단어."""
    return max(1, round(word_count / 200))


# ── 검증 함수 ─────────────────────────────────────────────────

def validate_post(content: str, rules: dict | None = None, category: str | None = None) -> list[dict]:
    """
    마크다운 포스트의 품질을 검증하고 이슈 목록을 반환한다.
    카테고리별 차등 단어 수 기준을 적용한다.
    
    Args:
        content: 마크다운 본문
        rules: 품질 규칙 (없으면 자동 로드)
        category: 포스트 카테고리 (없으면 기본 기준 적용)
    
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

    # ── 카테고리별 단어 수 검사 ──
    word_limits = rules.get("category_word_limits", {})
    cat_config = word_limits.get(category, word_limits.get("default", {})) if category else word_limits.get("default", {})
    min_words = cat_config.get("min_words", 400)
    target_words = cat_config.get("target_words", 800)
    cat_desc = cat_config.get("description", "")

    word_count = count_words(content)
    if word_count < min_words:
        issues.append({
            "rule": "min_word_count",
            "severity": "error",
            "detail": (
                f"단어 수 부족 ({word_count}단어 < 최소 {min_words}단어). "
                f"[{category or 'default'}] 기준. {cat_desc}"
            ),
            "auto_fixable": False,
            "word_count": word_count,
            "min_words": min_words,
            "target_words": target_words,
        })
    elif word_count < target_words:
        issues.append({
            "rule": "below_target_words",
            "severity": "warning",
            "detail": (
                f"권장 분량 미달 ({word_count}단어 / 권장 {target_words}단어). "
                f"가능하면 심층 분석을 추가하세요."
            ),
            "auto_fixable": False,
            "word_count": word_count,
        })

    # ── 콘텐츠 공통 검사 ──
    for check in rules.get("content_checks", []):
        rule = check.get("rule", "")

        if rule == "has_source_links":
            link_count = len(re.findall(r'\[.*?\]\(https?://.*?\)', content))
            min_links = check.get("min_links", 1)
            if link_count < min_links:
                issues.append({
                    "rule": rule,
                    "severity": "warning",
                    "detail": f"출처 링크 부족 ({link_count}개 < 최소 {min_links}개)",
                    "auto_fixable": False,
                })

        elif rule == "has_references_section":
            pattern = check.get("pattern", "## 📚 참고자료")
            if not re.search(pattern, content):
                issues.append({
                    "rule": rule,
                    "severity": "warning",
                    "detail": "참고자료 섹션이 없습니다. '## 📚 참고자료'를 추가하세요.",
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
