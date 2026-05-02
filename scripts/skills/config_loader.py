#!/usr/bin/env python3
"""
skills/config_loader.py — 설정 파일 통합 로더
config/ 디렉토리의 JSON/TXT 파일을 로드하는 유틸리티.
"""
import os
import json

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')


def load_json(filename: str) -> dict | list:
    """config/ 디렉토리에서 JSON 파일을 로드한다."""
    path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(path):
        print(f"  ⚠️ 설정 파일 없음: {filename}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_feeds() -> list[dict]:
    """config/feeds.json을 로드한다."""
    feeds = load_json('feeds.json')
    return feeds if isinstance(feeds, list) else []


def load_prompts() -> dict:
    """config/prompts.json을 로드한다."""
    return load_json('prompts.json')


def load_quality_rules() -> dict:
    """config/quality_rules.json을 로드한다."""
    return load_json('quality_rules.json')


def load_eval_rules() -> str:
    """config/eval_rules.txt를 로드한다."""
    path = os.path.join(CONFIG_DIR, 'eval_rules.txt')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                return content
    return "- 판단 기준이 누적 중입니다."


def load_feedback() -> str:
    """config/feedback.json에서 Few-Shot 피드백 텍스트를 생성한다."""
    data = load_json('feedback.json')
    if not data:
        return "- 최신 수동 교정 예시가 없습니다."

    fb_data = data.get("feedbacks", []) if isinstance(data, dict) else data
    if not fb_data:
        return "- 최신 수동 교정 예시가 없습니다."

    feedback = ""
    for fb in fb_data[-5:]:  # 최근 5개만 반영
        feedback += (
            f"- 대상 기사/키워드: '{fb.get('keyword_or_title', '')}'\n"
            f"  -> (사용자 최종 점수: {fb.get('user_score', '')}점)\n"
            f"  -> 판단 이유: {fb.get('reasoning', '')}\n"
        )
    return feedback.strip()


def load_guidelines() -> tuple[str, str]:
    """평가 룰 + 피드백을 한 번에 로드한다. (기존 load_guidelines_and_feedback() 대체)"""
    return load_eval_rules(), load_feedback()
