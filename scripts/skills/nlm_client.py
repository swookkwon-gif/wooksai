#!/usr/bin/env python3
"""
skills/nlm_client.py — NotebookLM CLI 통합 클라이언트
기존 4개 스크립트에 중복되었던 run_cmd()/run_nlm_cmd()를 하나로 통합한다.
nlm CLI 도구를 래핑하여 노트북 생성, 리서치, 쿼리 등을 제공한다.
"""
import re
import json
import subprocess
import time


class NotebookLMClient:
    """NotebookLM CLI(nlm) 통합 래퍼 클라이언트."""

    def __init__(self, default_timeout: int = 300):
        self.default_timeout = default_timeout

    # ── 핵심 CLI 실행 ──────────────────────────────────────────

    def _run(self, cmd_list: list[str], timeout: int | None = None) -> tuple[bool, str]:
        """nlm CLI 명령어를 실행하고 결과를 반환한다."""
        timeout = timeout or self.default_timeout
        print(f"  🔄 nlm: {' '.join(cmd_list)}")
        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if result.returncode != 0:
                print(f"  ❌ 실패 ({result.returncode}): {result.stderr[:200]}")
                return False, result.stderr
            return True, result.stdout
        except subprocess.TimeoutExpired:
            print(f"  ❌ 시간 초과 ({timeout}초)")
            return False, "Timeout"
        except FileNotFoundError:
            print("  ❌ 'nlm' 명령어를 찾을 수 없습니다. (설치: pip install notebooklm)")
            return False, "Not Found"

    # ── 노트북 관리 ────────────────────────────────────────────

    def create_notebook(self, title: str) -> str | None:
        """새 노트북을 생성하고 UUID를 반환한다."""
        success, out = self._run(["nlm", "notebook", "create", title])
        if not success:
            return None
        # 출력에서 UUID 추출
        match = re.search(r'ID:\s*([a-fA-F0-9\-]{36})', out)
        if match:
            notebook_id = match.group(1)
            print(f"  📌 노트북 생성 완료: {notebook_id}")
            return notebook_id
        # UUID가 없으면 출력 전체에서 다시 시도
        match = re.search(r'([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})', out)
        if match:
            return match.group(1)
        print("  ❌ 노트북 ID를 추출하지 못했습니다.")
        return None

    def delete_notebook(self, notebook_id: str) -> bool:
        """노트북을 삭제한다."""
        success, _ = self._run(["nlm", "notebook", "delete", notebook_id, "--confirm"])
        return success

    # ── 리서치 ─────────────────────────────────────────────────

    def start_research(
        self,
        query: str,
        notebook_id: str | None = None,
        mode: str = "fast",
        auto_import: bool = True,
        timeout: int = 900,
    ) -> tuple[bool, str]:
        """
        딥 리서치를 시작한다.
        
        Args:
            query: 리서치 주제
            notebook_id: 기존 노트북 ID (없으면 새로 생성)
            mode: "fast" (30초, ~10개 소스) 또는 "deep" (5분, ~40개 소스)
            auto_import: 소스 자동 임포트 여부
            timeout: 타임아웃 (초)
        """
        cmd = ["nlm", "research", "start", query, "--mode", mode]
        if notebook_id:
            cmd.extend(["--notebook-id", notebook_id])
        if auto_import:
            cmd.append("--auto-import")
        return self._run(cmd, timeout=timeout)

    def wait_research(self, notebook_id: str, timeout: int = 300) -> bool:
        """리서치 완료까지 폴링한다."""
        success, _ = self._run(
            ["nlm", "research", "status", "--notebook-id", notebook_id, "--wait", str(timeout)],
            timeout=timeout + 30,
        )
        return success

    # ── 소스 관리 ──────────────────────────────────────────────

    def add_source_url(self, notebook_id: str, url: str) -> bool:
        """URL 소스를 노트북에 추가한다."""
        success, _ = self._run(["nlm", "source", "add", "--notebook-id", notebook_id, "--url", url])
        return success

    def add_source_text(self, notebook_id: str, text: str, title: str = "Source") -> bool:
        """텍스트 소스를 노트북에 추가한다."""
        success, _ = self._run(
            ["nlm", "source", "add", "--notebook-id", notebook_id, "--text", text, "--title", title]
        )
        return success

    # ── 쿼리 ───────────────────────────────────────────────────

    def query(self, notebook_id: str, question: str, timeout: int = 600) -> str | None:
        """노트북 내 소스 기반으로 질의하고 답변을 반환한다."""
        success, out = self._run(
            ["nlm", "notebook", "query", notebook_id, question, "--timeout", str(timeout)],
            timeout=timeout + 30,
        )
        if not success:
            return None
        return self._clean_output(out)

    # ── 스튜디오 ───────────────────────────────────────────────

    def create_report(self, notebook_id: str, report_format: str = "Briefing Doc") -> bool:
        """스튜디오 보고서를 생성한다."""
        success, _ = self._run(
            ["nlm", "studio", "create", "--notebook-id", notebook_id, "--type", "report", "--format", report_format]
        )
        return success

    # ── 유틸리티 ───────────────────────────────────────────────

    @staticmethod
    def _clean_output(text: str) -> str:
        """CLI 출력에서 접두사와 불필요한 포맷을 제거한다."""
        # JSON 응답 처리
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                if 'value' in data and 'answer' in data['value']:
                    return data['value']['answer']
                if 'answer' in data:
                    return data['answer']
            return text
        except json.JSONDecodeError:
            pass

        # "Answer:" / "Response:" 접두사 제거
        match = re.search(r'(?:Answer:|Response:)(.*)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

        # 마크다운 코드 블록 제거
        text = text.strip()
        if text.startswith("```markdown"):
            text = text[len("```markdown"):].strip()
        if text.startswith("```"):
            text = text[3:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        return text
