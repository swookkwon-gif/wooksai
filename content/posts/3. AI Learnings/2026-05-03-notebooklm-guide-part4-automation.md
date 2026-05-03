---
title: 'NotebookLM 100% 활용하기 (4편) — 블로그 자동화 파이프라인'
date: '2026-05-03'
excerpt: 'NotebookLM MCP CLI를 활용하여 리서치부터 블로그 포스트 발행까지 자동화하는 파이프라인을 구축합니다. 코드 한 줄로 Deep Research → 소스 분석 → 블로그 초안 생성 → 품질 검증까지 실행하는 방법을 다룹니다.'
category: 'AI Learnings'
tags: ['NotebookLM', 'MCP', '자동화', '블로그', 'CLI', '튜토리얼']
series: 'notebooklm-guide'
series_order: 4
word_count: 1800
reading_time: '9분'
---

[1편](/ko/posts/2026-05-03-notebooklm-guide-part1-intro)~[3편](/ko/posts/2026-05-03-notebooklm-guide-part3-studio)까지 NotebookLM의 UI 기반 사용법을 다뤘습니다. 이번 4편에서는 **프로그래밍으로 NotebookLM을 자동화**하는 방법을 다룹니다.

> 이 글은 개발자 또는 자동화에 관심 있는 파워유저를 대상으로 합니다.

---

## MCP CLI란?

**MCP (Model Context Protocol)**는 AI 시스템이 외부 도구와 데이터 소스에 연결되는 표준 프로토콜입니다. **NotebookLM MCP CLI**는 이 프로토콜을 통해 NotebookLM의 모든 기능을 **프로그래밍으로 제어**할 수 있게 해줍니다.

### 기존 방식 vs MCP CLI

| 기존 (웹 UI) | MCP CLI |
|-------------|---------|
| 브라우저에서 수동 클릭 | 터미널에서 명령어 실행 |
| 한 번에 하나씩 처리 | 배치 처리 가능 |
| 반복 작업 비효율적 | 스크립트로 자동화 |
| 결과를 수동으로 복사 | 파일로 직접 다운로드 |

---

## Step 1: MCP CLI 설치

### 설치 명령어

```bash
# uv (권장 — 빠르고 안정적)
uv tool install notebooklm-mcp-cli

# 또는 pip
pip install notebooklm-mcp-cli
```

### 인증 설정

```bash
# 자동 로그인 (브라우저 팝업)
nlm login

# 계정 전환
nlm login switch <profile>
```

`nlm login` 명령어를 실행하면 브라우저가 열리고 Google 계정 인증이 진행됩니다. 인증이 완료되면 토큰이 로컬에 저장되어, 이후 CLI 명령어를 바로 사용할 수 있습니다.

---

## Step 2: 기본 CLI 명령어

### 노트북 목록 확인

```bash
# 모든 노트북 조회
nlm notebooks list

# 결과 예시:
# ID: eac87d4a-2144-...  Title: AI and Cybersecurity  Sources: 54
# ID: 84a40771-cb67-...  Title: Autonomous AI Reasoning  Sources: 10
```

### 새 노트북 생성

```bash
nlm notebooks create --title "블로그 리서치 - AI 트렌드 2026"
```

### 소스 추가

```bash
# URL 소스 추가
nlm sources add --notebook <ID> --type url --url "https://example.com/article"

# 여러 URL 한 번에 추가
nlm sources add --notebook <ID> --type url --urls "url1,url2,url3"

# 텍스트 소스 추가
nlm sources add --notebook <ID> --type text --text "분석할 내용..." --title "메모"

# 파일 업로드
nlm sources add --notebook <ID> --type file --file-path "./report.pdf"
```

---

## Step 3: Deep Research 자동화

### 웹 리서치 실행

```bash
# Fast Research (약 30초, ~10개 소스)
nlm research start \
  --notebook <ID> \
  --query "AI agent security vulnerabilities 2026" \
  --mode fast \
  --source web

# Deep Research (약 5분, ~40개 소스)
nlm research start \
  --notebook <ID> \
  --query "AI agent security vulnerabilities 2026" \
  --mode deep \
  --source web
```

### 리서치 상태 확인 & 소스 가져오기

```bash
# 진행 상태 확인 (완료까지 대기)
nlm research status --notebook <ID> --max-wait 300

# 발견된 소스를 노트북에 가져오기
nlm research import --notebook <ID> --task-id <TASK_ID>
```

---

## Step 4: AI 질의응답 (프로그래밍)

### 기본 쿼리

```bash
nlm query --notebook <ID> --query "이 소스들의 핵심 주제를 5개로 요약해줘"
```

### 대화 맥락 유지

```bash
# 첫 번째 질문
nlm query --notebook <ID> --query "AI 에이전트의 보안 위험을 분석해줘"
# → conversation_id: abc123 반환

# 후속 질문 (같은 대화 맥락)
nlm query --notebook <ID> \
  --query "그 중 가장 심각한 위험은 무엇인가?" \
  --conversation-id abc123
```

### 특정 소스만 지정

```bash
nlm query --notebook <ID> \
  --query "이 두 소스의 견해를 비교해줘" \
  --source-ids "source-id-1,source-id-2"
```

---

## Step 5: Studio 아티팩트 생성

### 보고서 생성 (Blog Post)

```bash
nlm studio create --notebook <ID> \
  --type report \
  --report-format "Blog Post" \
  --language ko
```

### 인포그래픽 생성

```bash
nlm studio create --notebook <ID> \
  --type infographic \
  --orientation landscape \
  --detail-level detailed \
  --language ko \
  --focus-prompt "AI 에이전트 보안 위협 비교"
```

### 오디오 오버뷰 생성

```bash
nlm studio create --notebook <ID> \
  --type audio \
  --audio-format deep_dive \
  --audio-length long \
  --language ko
```

### 아티팩트 다운로드

```bash
# 인포그래픽 다운로드
nlm studio download --notebook <ID> \
  --type infographic \
  --output ./output/infographic.png

# 보고서 다운로드
nlm studio download --notebook <ID> \
  --type report \
  --output ./output/report.md

# 데이터 표 다운로드
nlm studio download --notebook <ID> \
  --type data_table \
  --output ./output/data.csv
```

---

## 실전: 블로그 자동 발행 파이프라인

아래는 **리서치 → 분석 → 포스트 생성 → 발행**까지 전 과정을 자동화하는 파이프라인입니다.

### 파이프라인 아키텍처

<div class="workflow-timeline">
  <div class="workflow-step">
    <div class="workflow-step-badge badge-blue">1</div>
    <div class="workflow-step-content">
      <h4>💡 주제 입력</h4>
      <ul><li>"AI 에이전트 보안 위협 분석 2026"</li></ul>
    </div>
  </div>
  <div class="workflow-step">
    <div class="workflow-step-badge badge-indigo">2</div>
    <div class="workflow-step-content">
      <h4>🔍 Deep Research</h4>
      <ul>
        <li><code>nlm research start --mode deep</code></li>
        <li>40+ 소스 자동 수집</li>
      </ul>
    </div>
  </div>
  <div class="workflow-step">
    <div class="workflow-step-badge badge-violet">3</div>
    <div class="workflow-step-content">
      <h4>🧠 AI 분석</h4>
      <ul>
        <li><code>nlm query "핵심 주제 분석..."</code></li>
        <li>구조 설계 & 요약</li>
      </ul>
    </div>
  </div>
  <div class="workflow-step">
    <div class="workflow-step-badge badge-purple">4</div>
    <div class="workflow-step-content">
      <h4>🎨 아티팩트 생성</h4>
      <ul>
        <li><code>nlm studio create --type report</code></li>
        <li><code>nlm studio create --type infographic</code></li>
      </ul>
    </div>
  </div>
  <div class="workflow-step">
    <div class="workflow-step-badge badge-fuchsia">5</div>
    <div class="workflow-step-content">
      <h4>📥 다운로드 & 변환</h4>
      <ul>
        <li><code>nlm studio download</code></li>
        <li>Markdown → 블로그 포스트</li>
      </ul>
    </div>
  </div>
  <div class="workflow-step">
    <div class="workflow-step-badge badge-teal">6</div>
    <div class="workflow-step-content">
      <h4>🚀 Git Push & 배포</h4>
      <ul>
        <li><code>git add, commit, push</code></li>
        <li>블로그 자동 배포</li>
      </ul>
    </div>
  </div>
</div>

### 자동화 스크립트 예시

```python
#!/usr/bin/env python3
"""NotebookLM → Blog Post 자동 발행 파이프라인"""

import subprocess
import json
import time
from datetime import date

def run_nlm(args):
    """NLM CLI 명령어 실행"""
    result = subprocess.run(
        ["nlm"] + args,
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.stdout else None

def auto_blog_pipeline(topic, category="AI Learnings"):
    """블로그 자동 발행 파이프라인"""
    
    # 1. 노트북 생성
    notebook = run_nlm([
        "notebooks", "create", 
        "--title", f"Blog Research: {topic}"
    ])
    nb_id = notebook["id"]
    print(f"✅ 노트북 생성: {nb_id}")
    
    # 2. Deep Research 실행
    research = run_nlm([
        "research", "start",
        "--notebook", nb_id,
        "--query", topic,
        "--mode", "deep",
        "--source", "web"
    ])
    task_id = research["task_id"]
    
    # 3. 리서치 완료 대기
    print("⏳ Deep Research 진행 중...")
    run_nlm([
        "research", "status",
        "--notebook", nb_id,
        "--max-wait", "300"
    ])
    
    # 4. 소스 가져오기
    run_nlm([
        "research", "import",
        "--notebook", nb_id,
        "--task-id", task_id
    ])
    print("✅ 소스 가져오기 완료")
    
    # 5. 블로그 보고서 생성
    run_nlm([
        "studio", "create",
        "--notebook", nb_id,
        "--type", "report",
        "--report-format", "Blog Post",
        "--language", "ko"
    ])
    time.sleep(60)  # 생성 대기
    
    # 6. 인포그래픽 생성
    run_nlm([
        "studio", "create",
        "--notebook", nb_id,
        "--type", "infographic",
        "--orientation", "landscape",
        "--language", "ko",
        "--focus-prompt", topic
    ])
    time.sleep(120)  # 생성 대기
    
    # 7. 다운로드
    today = date.today().isoformat()
    slug = topic.lower().replace(" ", "-")[:50]
    
    run_nlm([
        "studio", "download",
        "--notebook", nb_id,
        "--type", "report",
        "--output", f"content/posts/{category}/{today}-{slug}.md"
    ])
    
    run_nlm([
        "studio", "download",
        "--notebook", nb_id,
        "--type", "infographic",
        "--output", f"public/images/{slug}-infographic.png"
    ])
    
    print(f"✅ 블로그 포스트 생성 완료: {today}-{slug}.md")

# 실행
auto_blog_pipeline("AI 에이전트 보안 위협 분석 2026")
```

---

## 배치 처리: 여러 노트북 동시 작업

### 여러 노트북에 같은 질문

```bash
nlm batch query \
  --notebook-names "AI Research,Cybersecurity" \
  --query "2026년 가장 중요한 트렌드를 3가지로 요약해줘"
```

### 교차 노트북 쿼리

```bash
nlm cross-notebook-query \
  --tags "ai,security" \
  --query "공통적으로 언급되는 위험 요소는?"
```

---

## GitHub Actions 연동

GitHub Actions에 파이프라인을 연동하면, 정기적으로 블로그를 자동 발행할 수 있습니다:

```yaml
# .github/workflows/auto-blog.yml
name: Auto Blog Pipeline
on:
  schedule:
    - cron: '0 9 * * 1'  # 매주 월요일 9시
  workflow_dispatch:      # 수동 실행

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install NLM CLI
        run: pip install notebooklm-mcp-cli
      - name: Run Pipeline
        env:
          NLM_AUTH_TOKEN: ${{ secrets.NLM_AUTH_TOKEN }}
        run: python scripts/auto_blog_nlm.py
      - name: Commit & Push
        run: |
          git config user.name "Blog Bot"
          git config user.email "bot@blog.com"
          git add content/ public/images/
          git commit -m "auto: new blog post generated"
          git push
```

---

## 핵심 정리

| 기능 | CLI 명령어 | 용도 |
|------|----------|------|
| 노트북 생성 | `nlm notebooks create` | 주제별 노트북 |
| Deep Research | `nlm research start` | 자동 소스 수집 |
| AI 쿼리 | `nlm query` | 소스 분석 |
| 아티팩트 생성 | `nlm studio create` | 보고서/인포그래픽 |
| 다운로드 | `nlm studio download` | 파일 저장 |
| 배치 처리 | `nlm batch` | 대량 처리 |

**다음 편(5편)**에서는 이 파이프라인을 확장하여 **블로그 시리즈를 책으로 컴파일하는 워크플로우**를 다룹니다.

## 📚 참고자료

- [NotebookLM MCP CLI GitHub](https://github.com/nicholasgriffintn/notebooklm-mcp)
- [Model Context Protocol 공식 문서](https://modelcontextprotocol.io/)
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [NotebookLM API 참고](https://notebooklm.google.com)
