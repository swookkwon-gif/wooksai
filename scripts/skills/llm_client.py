#!/usr/bin/env python3
"""
skills/llm_client.py — 통합 LLM 클라이언트
모든 에이전트가 공유하는 Gemini API 호출 인터페이스.
모델 폴백, 재시도, JSON 파싱을 자동 처리한다.
"""
import os
import json
import time
from google import genai
from google.genai import types


class LLMClient:
    """Gemini API 통합 호출 클라이언트."""

    DEFAULT_MODELS = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash-8b',
    ]

    RETRYABLE_ERRORS = ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500"]

    def __init__(self, api_key: str | None = None, models: list[str] | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self.client = genai.Client(api_key=self.api_key)
        self.models = models or self.DEFAULT_MODELS

    # ── 핵심 API 호출 ──────────────────────────────────────────
    def call(
        self,
        prompt: str,
        schema: dict | None = None,
        temperature: float = 0.3,
        max_retries: int = 3,
    ) -> dict | str | None:
        """
        프롬프트를 전송하고 결과를 반환한다.
        - schema가 주어지면 JSON 응답을 dict로 파싱하여 반환
        - schema가 없으면 raw text 반환
        - 모든 모델 폴백 × 재시도를 자동 처리
        """
        config_kwargs = {"temperature": temperature}
        if schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = schema

        for attempt in range(max_retries):
            for model_name in self.models:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_kwargs),
                    )
                    raw_text = self._clean_json(response.text)

                    if schema:
                        return json.loads(raw_text)
                    return raw_text

                except json.JSONDecodeError as je:
                    print(f"      ❌ JSON 파싱 에러 ({model_name}): {je}")
                    # JSON 에러는 다른 모델로 재시도
                    continue
                except Exception as e:
                    err_msg = str(e)
                    if any(code in err_msg for code in self.RETRYABLE_ERRORS):
                        print(f"      [경고] '{model_name}' API 제한. 다른 모델 시도...")
                        continue
                    else:
                        print(f"      ❌ API 에러 ({model_name}): {e}")
                        break  # 복구 불가능한 에러 → 다음 재시도 라운드로

            print(f"      ⏳ 모든 모델 실패. {10 * (attempt + 1)}초 대기 후 재시도... ({attempt + 1}/{max_retries})")
            time.sleep(10 * (attempt + 1))

        print("      ❌ 최종 실패: 모든 재시도 소진")
        return None

    # ── Writer + Reviewer 루프 ─────────────────────────────────
    def call_with_review(
        self,
        prompt: str,
        schema: dict,
        reviewer_fn,
        max_rounds: int = 2,
        temperature: float = 0.3,
    ) -> dict | None:
        """
        LLM 호출 → reviewer_fn으로 검증 → 실패 시 피드백 포함 재호출.
        reviewer_fn(result_dict) → list[str] (이슈 목록, 빈 리스트면 통과)
        """
        current_prompt = prompt
        for round_num in range(max_rounds):
            result = self.call(current_prompt, schema=schema, temperature=temperature)
            if result is None:
                return None

            issues = reviewer_fn(result)
            if not issues:
                if round_num > 0:
                    print(f"      ✅ Review 통과 (라운드 {round_num + 1})")
                return result

            print(f"      🔄 Review 실패 (라운드 {round_num + 1}): {len(issues)}개 이슈 발견")
            # 피드백을 프롬프트에 추가하여 재호출
            fix_instructions = "\n".join(f"- {issue}" for issue in issues)
            current_prompt = (
                f"{prompt}\n\n"
                f"[이전 출력에서 발견된 오류 — 반드시 수정하세요]\n{fix_instructions}"
            )

        print(f"      ⚠️ 최대 라운드 도달. 최선의 결과 반환")
        return result

    # ── 유틸리티 ───────────────────────────────────────────────
    @staticmethod
    def _clean_json(text: str) -> str:
        """LLM 응답에서 ```json ... ``` 마커를 제거한다."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.startswith("```"):
            text = text[len("```"):].strip()
        if text.endswith("```"):
            text = text[:-len("```")].strip()
        return text
