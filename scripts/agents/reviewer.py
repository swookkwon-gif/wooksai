#!/usr/bin/env python3
"""
agents/reviewer.py — 품질 검증 에이전트
Writer가 생성한 마크다운 포스트를 정규식으로 검증하고 자동 수정한다.
LLM 호출 없이 코드 레벨에서 품질을 강제한다.
"""
from skills.markdown_utils import (
    validate_post,
    auto_fix_content,
    load_quality_rules,
    count_words,
)


# SEO 최소 기준
SEO_MIN_WORDS = 1000


def review_and_fix(content: str, max_rounds: int = 2) -> tuple[str, list[dict]]:
    """
    마크다운 콘텐츠를 검증하고 자동 수정한다.
    
    Args:
        content: 마크다운 본문
        max_rounds: 최대 수정 라운드
    
    Returns:
        tuple: (수정된 콘텐츠, 남은 이슈 목록)
    """
    rules = load_quality_rules()

    for round_num in range(max_rounds):
        issues = validate_post(content, rules)

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
    remaining = validate_post(content, rules)
    word_count = count_words(content)

    if remaining:
        print(f"      ⚠️ Reviewer: {len(remaining)}개 이슈 잔존 ({word_count}단어)")
        for issue in remaining:
            severity_icon = "❌" if issue["severity"] == "error" else "⚠️"
            print(f"         {severity_icon} [{issue['severity']}] {issue['detail']}")
    else:
        print(f"      ✅ Reviewer: 모든 이슈 해결됨 ({word_count}단어)")

    return content, remaining


def review_llm_output(result: dict) -> list[str]:
    """
    LLM 출력(dict)을 검증하여 이슈 텍스트 목록을 반환한다.
    LLMClient.call_with_review()의 reviewer_fn으로 사용된다.
    
    단어 수가 SEO 기준(1000단어) 미달이면 재작성을 요청하는
    구체적인 피드백을 반환한다.
    
    Returns:
        list[str]: 이슈 설명 목록 (빈 리스트면 통과)
    """
    md_content = result.get("markdown_content", "")
    if not md_content:
        return ["markdown_content 필드가 비어있습니다."]

    issues = validate_post(md_content)
    feedback = []

    for issue in issues:
        if issue["severity"] == "error":
            if issue["rule"] == "min_word_count":
                current = issue.get("word_count", count_words(md_content))
                needed = SEO_MIN_WORDS - current
                feedback.append(
                    f"[SEO 기준 미달] 현재 {current}단어로 최소 {SEO_MIN_WORDS}단어에 "
                    f"{needed}단어 부족합니다. 각 섹션에 배경 분석, 구체적 수치, "
                    f"산업 시사점, 사례를 추가하여 분량을 확장하세요."
                )
            elif issue["rule"] == "min_char_count":
                feedback.append(
                    f"[글자 수 부족] {issue['detail']}. "
                    f"각 문단을 3문장 이상으로 확장하세요."
                )
            else:
                feedback.append(issue["detail"])

    return feedback


def is_seo_ready(content: str) -> tuple[bool, int]:
    """
    포스트가 SEO 최소 기준(1000단어)을 충족하는지 확인한다.
    
    Returns:
        tuple: (달성 여부, 현재 단어 수)
    """
    word_count = count_words(content)
    return word_count >= SEO_MIN_WORDS, word_count
