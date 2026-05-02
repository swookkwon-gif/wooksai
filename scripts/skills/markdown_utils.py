#!/usr/bin/env python3
"""마크다운 품질 검증 및 자동 수정 유틸리티

Reviewer Agent의 핵심 로직을 담당합니다.
정규식 기반으로 LLM 출력의 포맷 오류를 감지하고 자동 교정합니다.
"""
import re
import json
import os


def load_quality_rules():
    """config/quality_rules.json에서 검증 규칙을 로드"""
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'quality_rules.json')
    if os.path.exists(rules_path):
        with open(rules_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"format_checks": [], "content_checks": []}


def validate_post(content: str) -> list[dict]:
    """마크다운 포스트의 품질을 검증하고 발견된 이슈 목록을 반환합니다.

    Returns:
        [{"rule": "no_raw_urls", "severity": "error", "detail": "Line 5: https://..."}]
    """
    issues = []
    lines = content.split('\n')

    # 1. 원시 URL 노출 검사 (마크다운 링크 내부가 아닌 곳)
    for i, line in enumerate(lines, 1):
        # 마크다운 링크 패턴을 제거한 후 남은 URL이 있는지 확인
        cleaned = re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', line)
        cleaned = re.sub(r'<https?://[^>]+>', '', cleaned)
        raw_urls = re.findall(r'https?://\S+', cleaned)
        for url in raw_urls:
            issues.append({
                "rule": "no_raw_urls",
                "severity": "error",
                "detail": f"Line {i}: 원시 URL 노출 — {url[:80]}",
                "line": i
            })

    # 2. 소제목에 링크가 없는 경우 검사 (### 제목 형태인데 [제목](URL) 아닌 경우)
    for i, line in enumerate(lines, 1):
        if re.match(r'^###\s+(?!\[).+$', line.strip()):
            # URL이 괄호 안에 있지만 대괄호가 없는 경우
            if re.search(r'\(https?://', line):
                issues.append({
                    "rule": "heading_missing_link_bracket",
                    "severity": "error",
                    "detail": f"Line {i}: 소제목에 대괄호 없이 URL 직접 붙임",
                    "line": i
                })
            # URL이 아예 없는 소제목은 warning (원문 링크가 없을 수도 있으므로)

    # 3. H1 헤딩 중복 검사
    for i, line in enumerate(lines, 1):
        if re.match(r'^#\s+[^\n]+', line.strip()):
            issues.append({
                "rule": "no_h1_heading",
                "severity": "error",
                "detail": f"Line {i}: H1 헤딩이 본문에 포함됨",
                "line": i
            })

    # 4. 소제목 다음에 빈 줄이 없는 경우
    for i in range(len(lines) - 1):
        if re.match(r'^###\s+', lines[i]) and lines[i+1].strip() != '':
            issues.append({
                "rule": "empty_line_after_heading",
                "severity": "warning",
                "detail": f"Line {i+1}: 소제목 뒤에 빈 줄 없음",
                "line": i + 1
            })

    # 5. 최소 콘텐츠 길이 검사
    clean = re.sub(r'[#*`\[\]\(\)\n\r]', '', content)
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) < 100:
        issues.append({
            "rule": "min_content_length",
            "severity": "warning",
            "detail": f"콘텐츠가 너무 짧습니다 ({len(clean)}자)"
        })

    return issues


def auto_fix(content: str) -> str:
    """감지 가능한 포맷 오류를 자동 교정합니다.

    quick_review_and_fix()의 확장 버전입니다.
    """
    # 1. ### 제목(URL) → ### [제목](URL) 자동 수정
    content = re.sub(
        r'^(###\s+)([^\[\n]+?)\((https?://[^\)]+)\)\s*$',
        r'\1[\2](\3)',
        content, flags=re.MULTILINE
    )

    # 2. H1/H2 헤딩 제거
    content = re.sub(r'^#\s+[^\n]+\n*', '', content.lstrip())
    content = re.sub(r'^##\s+[^\n]+\n*', '', content.lstrip())

    # 3. 소제목 바로 다음 줄에 빈 줄 삽입
    content = re.sub(
        r'^(###\s+.+)\n([^\n])',
        r'\1\n\n\2',
        content, flags=re.MULTILINE
    )

    # 4. 마크다운 링크 바깥의 원시 URL을 [원문 보기](URL)로 래핑
    content = re.sub(
        r'(?<![(\["\'=])(https?://\S+)(?![)\]"\'])',
        r'[원문 보기](\1)',
        content
    )

    return content


def review_llm_output(data: dict) -> list[str]:
    """LLM 응답(dict)의 markdown_content를 검증하여 이슈 메시지 목록을 반환합니다.

    call_llm_with_review()의 reviewer_fn으로 사용됩니다.
    Returns: 이슈가 없으면 빈 리스트
    """
    md = data.get("markdown_content", "")
    if not md:
        return ["markdown_content가 비어있습니다."]

    issues = validate_post(md)
    error_issues = [i for i in issues if i["severity"] == "error"]

    if not error_issues:
        return []  # 통과

    return [f"[{i['rule']}] {i['detail']}" for i in error_issues]
