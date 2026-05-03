#!/usr/bin/env python3
"""
agents/reviewer.py — 품질 검증 에이전트
Writer가 생성한 마크다운 포스트를 정규식으로 검증하고 자동 수정한다.
LLM 호출 없이 코드 레벨에서 품질을 강제한다.
카테고리별 차등 기준을 적용하여 억지로 분량을 늘리는 부작용을 방지한다.
"""
from skills.markdown_utils import (
    validate_post,
    auto_fix_content,
    load_quality_rules,
    count_words,
)


def review_and_fix(
    content: str,
    max_rounds: int = 2,
    category: str | None = None,
) -> tuple[str, list[dict]]:
    """
    마크다운 콘텐츠를 검증하고 자동 수정한다.
    
    Args:
        content: 마크다운 본문
        max_rounds: 최대 수정 라운드
        category: 포스트 카테고리 (카테고리별 차등 기준 적용)
    
    Returns:
        tuple: (수정된 콘텐츠, 남은 이슈 목록)
    """
    rules = load_quality_rules()

    for round_num in range(max_rounds):
        issues = validate_post(content, rules, category=category)

        if not issues:
            word_count = count_words(content)
            if round_num > 0:
                print(f"      ✅ Reviewer: 포맷 검증 통과 ({word_count}단어, 라운드 {round_num + 1})")
            else:
                print(f"      ✅ Reviewer: 포맷 검증 통과 ({word_count}단어)")
            return content, []

        # 자동 수정 가능한 이슈가 있으면 수정 적용
        auto_fixable = [i for i in issues if i.get("auto_fixable")]
        if auto_fixable:
            print(f"      🔧 Reviewer: {len(auto_fixable)}개 이슈 자동 수정 중 (라운드 {round_num + 1})")
            content = auto_fix_content(content)
        else:
            # 자동 수정 불가능한 이슈만 남았으면 루프 종료
            break

    # 최종 검증
    remaining = validate_post(content, rules, category=category)
    word_count = count_words(content)

    if remaining:
        errors = [i for i in remaining if i["severity"] == "error"]
        warnings = [i for i in remaining if i["severity"] == "warning"]
        print(f"      ⚠️ Reviewer: {len(errors)} error, {len(warnings)} warning ({word_count}단어)")
        for issue in remaining:
            severity_icon = "❌" if issue["severity"] == "error" else "⚠️"
            print(f"         {severity_icon} {issue['detail']}")
    else:
        print(f"      ✅ Reviewer: 모든 이슈 해결됨 ({word_count}단어)")

    return content, remaining


def review_llm_output(result: dict, category: str | None = None) -> list[str]:
    """
    LLM 출력(dict)을 검증하여 이슈 텍스트 목록을 반환한다.
    LLMClient.call_with_review()의 reviewer_fn으로 사용된다.
    
    카테고리별 차등 기준을 적용하여, 뉴스 단신에는 불필요하게
    높은 기준을 강제하지 않는다.
    
    Returns:
        list[str]: 이슈 설명 목록 (빈 리스트면 통과)
    """
    md_content = result.get("markdown_content", "")
    if not md_content:
        return ["markdown_content 필드가 비어있습니다."]

    issues = validate_post(md_content, category=category)
    feedback = []

    for issue in issues:
        if issue["severity"] == "error":
            if issue["rule"] == "min_word_count":
                current = issue.get("word_count", count_words(md_content))
                min_w = issue.get("min_words", 500)
                target_w = issue.get("target_words", 800)
                needed = min_w - current
                feedback.append(
                    f"[분량 부족] 현재 {current}단어 / 최소 {min_w}단어 (목표 {target_w}단어). "
                    f"{needed}단어 부족. 자연스러운 심층 분석(배경, 시사점, 사례)을 추가하세요. "
                    f"의미 없는 수식어나 반복은 피하세요."
                )
            else:
                feedback.append(issue["detail"])

    return feedback


def is_seo_ready(content: str, category: str | None = None) -> tuple[bool, int, int]:
    """
    포스트가 카테고리별 SEO 최소 기준을 충족하는지 확인한다.
    
    Returns:
        tuple: (달성 여부, 현재 단어 수, 최소 기준)
    """
    rules = load_quality_rules()
    word_limits = rules.get("category_word_limits", {})
    cat_config = word_limits.get(category, word_limits.get("default", {})) if category else word_limits.get("default", {})
    min_words = cat_config.get("min_words", 400)

    word_count = count_words(content)
    return word_count >= min_words, word_count, min_words
