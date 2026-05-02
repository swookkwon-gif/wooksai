#!/usr/bin/env python3
"""통합 LLM 클라이언트 — 모든 에이전트가 공유하는 Gemini API 호출 인터페이스

중복되어 있던 3중 루프(재시도 × 모델 폴백) 로직을 하나로 통합합니다.
"""
import os
import time
import json

from google import genai
from google.genai import types


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 모델 폴백 순서 (비용/성능 기준)
DEFAULT_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-8b',
]

RETRIABLE_ERRORS = ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]


def clean_json_response(text):
    """API 응답에서 마크다운 코드블록 래핑을 제거"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.startswith("```"):
        text = text[len("```"):].strip()
    if text.endswith("```"):
        text = text[:-len("```")].strip()
    return text


def call_llm(
    prompt: str,
    response_schema: dict = None,
    temperature: float = 0.3,
    max_retries: int = 3,
    models: list = None,
    retry_delay: int = 30,
    label: str = "LLM",
) -> dict | str | None:
    """Gemini API를 호출하고, 모델 폴백 + 재시도 + JSON 파싱을 자동 처리합니다.

    Args:
        prompt: LLM에 전달할 프롬프트
        response_schema: JSON 스키마 (없으면 텍스트로 반환)
        temperature: 생성 온도
        max_retries: 전체 재시도 횟수
        models: 시도할 모델 목록 (기본: DEFAULT_MODELS)
        retry_delay: 모든 모델 실패 시 대기 시간(초)
        label: 로그에 표시할 작업명

    Returns:
        response_schema가 있으면 파싱된 dict, 없으면 텍스트 str.
        완전히 실패하면 None.
    """
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY is missing.")
        return None

    client = genai.Client(api_key=GEMINI_API_KEY)
    models = models or DEFAULT_MODELS

    config_kwargs = {"temperature": temperature}
    if response_schema:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = response_schema

    for attempt in range(max_retries):
        for model_name in models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )

                raw_text = clean_json_response(response.text)

                if response_schema:
                    try:
                        return json.loads(raw_text)
                    except json.JSONDecodeError as je:
                        print(f"      ❌ [{label}] JSON 파싱 실패 ({model_name}): {je}")
                        # JSON 파싱 실패 시 다음 모델로
                        continue
                else:
                    return raw_text

            except Exception as e:
                err_msg = str(e)
                if any(x in err_msg for x in RETRIABLE_ERRORS):
                    print(f"      [경고] [{label}] '{model_name}' API 제한. 다른 모델 시도...")
                    continue
                else:
                    print(f"      ❌ [{label}] API 에러: {e}")
                    break  # 비재시도 에러는 모델 루프 탈출

        print(f"      ❌ [{label}] 모든 모델 실패. {retry_delay}초 대기 후 재시도... ({attempt+1}/{max_retries})")
        time.sleep(retry_delay)

    print(f"      ❌ [{label}] 최대 재시도 초과. 포기합니다.")
    return None


def call_llm_with_review(
    prompt: str,
    response_schema: dict,
    reviewer_fn,
    max_rounds: int = 2,
    **kwargs,
) -> dict | None:
    """Writer + Reviewer 루프를 자동 실행합니다.

    Args:
        prompt: 초기 프롬프트
        response_schema: JSON 응답 스키마
        reviewer_fn: 결과를 검증하는 함수. 문제가 있으면 list[str], 없으면 빈 리스트 반환.
        max_rounds: 최대 재작성 횟수
        **kwargs: call_llm에 전달할 추가 인자

    Returns:
        검증을 통과한(또는 최선의) dict 결과
    """
    current_prompt = prompt

    for round_num in range(max_rounds):
        result = call_llm(current_prompt, response_schema=response_schema, **kwargs)
        if result is None:
            return None

        issues = reviewer_fn(result)
        if not issues:
            return result  # 통과!

        print(f"      🔄 [{kwargs.get('label', 'LLM')}] Reviewer 이슈 {len(issues)}건 발견. 재작성 요청... (round {round_num+1}/{max_rounds})")

        # 이슈를 프롬프트에 추가하여 재시도
        fix_instructions = "\n".join(f"- {issue}" for issue in issues)
        current_prompt = prompt + f"""

[중요: 이전 출력에서 다음 문제가 발견되었습니다. 반드시 수정하세요]
{fix_instructions}
"""

    return result  # 마지막 결과라도 반환
