#!/usr/bin/env python3
"""
agents/writer.py — 포스트 작성 에이전트
Evaluator가 필터링한 기사 데이터를 바탕으로 마크다운 포스트를 작성한다.
포맷/스타일 규칙에만 집중한다.
"""
from datetime import datetime, timezone, timedelta
from slugify import slugify

from skills.llm_client import LLMClient
from skills.config_loader import load_prompts, load_guidelines
from agents.reviewer import review_llm_output


# ── JSON 스키마 ────────────────────────────────────────────────

RSS_SCHEMA = {
    "type": "object",
    "properties": {
        "has_ai_news": {"type": "boolean"},
        "evaluations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "score": {"type": "number"},
                    "reasoning": {"type": "string"},
                },
                "required": ["target", "score", "reasoning"],
            },
        },
        "markdown_content": {"type": "string"},
    },
    "required": ["has_ai_news", "evaluations", "markdown_content"],
}

NEWSLETTER_SCHEMA = {
    "type": "object",
    "properties": {
        "post_title": {"type": "string"},
        "evaluations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "target": {"type": "string"},
                    "score": {"type": "number"},
                    "reasoning": {"type": "string"},
                },
                "required": ["target", "score", "reasoning"],
            },
        },
        "markdown_content": {"type": "string"},
    },
    "required": ["post_title", "evaluations", "markdown_content"],
}


# ── RSS 포스트 작성 ────────────────────────────────────────────

def write_rss_post(articles: list[dict], llm: LLMClient) -> dict | None:
    """
    RSS 기사 목록을 바탕으로 종합 AI 뉴스 포스트를 작성한다.
    
    Args:
        articles: Collector가 수집한 기사 목록
        llm: LLMClient 인스턴스
    
    Returns:
        dict: {"has_ai_news": bool, "evaluations": list, "markdown_content": str}
    """
    prompts = load_prompts()
    custom_rules, custom_feedback = load_guidelines()

    # 기사 텍스트 조합
    articles_text = ""
    for idx, item in enumerate(articles, 1):
        articles_text += (
            f"\n\n--- 기사 {idx} (출처: {item['source_name']}) ---\n"
            f"제목: {item['title']}\n"
            f"링크: {item['url']}\n"
            f"내용(HTML): {item['content']}\n"
        )

    requirements = prompts.get("rss_requirements", "")

    prompt = f"""당신은 최고 수준의 AI 뉴스 에디터입니다.
아래 여러 RSS 소스에서 수집된 새 기사들을 바탕으로, 종합 AI 뉴스 마크다운 포스트 본문을 작성하세요.

[사용자 맞춤형 평가 핵심 룰]
{custom_rules}

[최근 사용자 직접 교정 예시 (Few-Shot)]
{custom_feedback}

[원문 정보]
{articles_text}

[요구사항]
{requirements}
"""

    return llm.call_with_review(
        prompt=prompt,
        schema=RSS_SCHEMA,
        reviewer_fn=review_llm_output,
        max_rounds=2,
    )


# ── 뉴스레터 포스트 작성 ──────────────────────────────────────

def write_newsletter_post(sender: str, letters: list[dict], llm: LLMClient) -> dict | None:
    """
    특정 발신자의 뉴스레터들을 바탕으로 블로그 포스트를 작성한다.
    
    Args:
        sender: 뉴스레터 발신자 이름
        letters: [{"subject": str, "body": str}, ...]
        llm: LLMClient 인스턴스
    
    Returns:
        dict: {"post_title": str, "evaluations": list, "markdown_content": str}
    """
    prompts = load_prompts()
    custom_rules, custom_feedback = load_guidelines()

    articles_text = ""
    for idx, letter in enumerate(letters, 1):
        articles_text += f"\n\n[제목: {letter['subject']}]\n{letter['body']}\n"

    requirements = prompts.get("gmail_requirements", "")
    # sender 변수를 요구사항 내에서 치환
    requirements = requirements.replace("{sender}", sender)

    prompt = f"""당신은 '윤(Yoon)' 님을 위한 수석 뉴스레터 AI 에디터입니다.
발신자 [{sender}](이)가 보낸 뉴스레터 데이터를 기반으로 블로그 포스트를 작성합니다.

[사용자 맞춤형 평가 핵심 룰]
{custom_rules}

[최근 사용자 직접 교정 예시 (Few-Shot)]
{custom_feedback}

[뉴스레터 데이터]
{articles_text}

[요구사항]
{requirements}
"""

    return llm.call_with_review(
        prompt=prompt,
        schema=NEWSLETTER_SCHEMA,
        reviewer_fn=review_llm_output,
        max_rounds=2,
    )
