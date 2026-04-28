import os
import re
import subprocess
import time
from datetime import datetime, timezone, timedelta

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '3. AI Learnings')
NOTEBOOK_ID = "56829e2f-fd47-4d20-be9f-f54a1c585deb"

TOPICS = [
    {"slug": "3-chatgpt-claude-gemini-guide", "title": "핵심 3대 챗봇 100% 활용법: ChatGPT vs Claude vs Gemini", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '핵심 3대 챗봇 100% 활용법: ChatGPT vs Claude vs Gemini'. 초보자가 각 챗봇의 장단점을 쉽게 이해하고, 어떤 상황에서 어떤 챗봇을 써야 하는지 실무 예시를 들어 비교 분석해주세요."},
    {"slug": "4-perplexity-search-revolution", "title": "정보 검색의 세대교체, 퍼플렉시티(Perplexity) 활용법", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '정보 검색의 세대교체, 퍼플렉시티(Perplexity)'. 기존 구글 검색과 퍼플렉시티의 차이점을 설명하고, 출처가 명확한 실시간 브리핑을 받아 자료 조사 시간을 단축하는 방법을 소개해주세요."},
    {"slug": "5-shadow-ai-and-security", "title": "섀도 AI(Shadow AI)의 위험성과 필수 보안 수칙", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '섀도 AI(Shadow AI)의 위험성과 필수 보안 수칙'. 회사 기밀이나 개인정보 유출 위험을 경고하고, 초보자가 알아야 할 안전한 AI 사용 가이드를 알려주세요."},
    {"slug": "6-notebooklm-custom-assistant", "title": "나만의 맞춤형 지식 비서 구축: NotebookLM 완벽 가이드", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '나만의 맞춤형 지식 비서 구축: NotebookLM 완벽 가이드'. 할루시네이션 없이 내 자료 안에서만 답을 찾는 원리와 오디오 오버뷰(팟캐스트) 기능을 활용하는 방법을 설명해주세요."},
    {"slug": "7-meeting-minutes-daglo-granola", "title": "회의록 지옥 탈출: 다글로(daglo) & Granola 활용법", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '회의록 지옥 탈출: 다글로(daglo) & Granola'. 한국어 음성 인식에 탁월한 다글로와 자동 요약에 강한 Granola를 활용해 회의록과 PPT 초안을 자동화하는 루틴을 소개해주세요."},
    {"slug": "8-design-canva-gamma", "title": "디자인 비전공자의 구세주: Canva & Gamma 꿀팁", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '디자인 비전공자의 구세주: Canva & Gamma'. 텍스트만으로 발표용 슬라이드와 카드뉴스를 전문가처럼 자동 디자인하는 두 도구의 활용법을 설명해주세요."},
    {"slug": "9-workflow-automation-relay-zapier", "title": "자연어로 만드는 업무 자동화: Relay.app & Zapier", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '자연어로 만드는 업무 자동화: Relay.app & Zapier'. 코딩 없이 '메일이 오면 요약해서 노션에 저장해' 같은 자연어로 업무 자동화 시스템을 구축하는 방법을 소개해주세요."},
    {"slug": "10-native-multimodal-practice", "title": "네이티브 멀티모달의 실무 적용 완벽 가이드", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '네이티브 멀티모달 실무 적용'. 텍스트, 이미지, 음성 등 여러 형태의 데이터를 동시에 분석하게 만드는 2026년형 멀티모달 AI 문제 해결법을 다뤄주세요."},
    {"slug": "11-agentic-thinking", "title": "에이전트 중심 사고(Agentic Thinking) 장착하기", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '에이전트 중심 사고(Agentic Thinking)'. AI를 단순 도구가 아닌 독립된 팀원으로 대하며, 워크플로우를 위임하고 감독하는 방법을 고급 사용자 관점에서 설명해주세요."},
    {"slug": "12-no-code-app-dev-cursor-antigravity", "title": "코드 0줄로 나만의 앱 만들기: Cursor & Antigravity", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '코드 0줄로 나만의 앱/웹 만들기: Cursor & Google Antigravity'. 코딩을 몰라도 에이전트형 IDE를 이용해 기획만으로 작동하는 소프트웨어를 개발하는 과정을 소개해주세요."},
    {"slug": "13-content-factory-daven-heygen", "title": "콘텐츠 자동 생성 공장: Daven AI & HeyGen", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: '콘텐츠 자동 생성 공장: Daven AI & HeyGen'. 한 줄의 한글 프롬프트로 대본, 영상, 음악을 생성하고 다국어 아바타 영상을 만드는 차세대 멀티미디어 제작법을 소개해주세요."},
    {"slug": "14-ai-copyright-fair-use", "title": "AI 저작권과 공정이용의 딜레마 극복하기", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: 'AI 저작권과 공정이용의 딜레마 극복'. AI가 만든 창작물의 저작권 문제와 기존 콘텐츠의 데이터 마이닝 시 침해 요소를 피하는 법적/윤리적 쟁점을 설명해주세요."},
    {"slug": "15-environmental-impact-slm", "title": "AI의 환경 영향과 올바른 모델 최적화(SLM) 전략", "prompt": "다음 블로그 포스트 초안을 작성해주세요. 주제: 'AI의 환경 영향과 올바른 모델 최적화'. AI의 막대한 전력 소비와 환경적 리스크를 짚어주고, 가벼운 모델(SLM)을 적재적소에 배치하는 경제적이고 윤리적인 실무 전략을 설명해주세요."}
]

def run_cmd(cmd_list, timeout=600):
    print(f"🔄 실행 중: {' '.join(cmd_list)}")
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        if result.returncode != 0:
            print(f"❌ 명령어 실행 실패 ({result.returncode}):\n{result.stderr}\n{result.stdout}")
            return False, result.stderr
        return True, result.stdout
    except subprocess.TimeoutExpired:
        print(f"❌ 실행 시간 초과 ({timeout}초)")
        return False, "Timeout"

def clean_markdown_output(text):
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].strip()
    if text.endswith("```"):
        text = text[:-len("```")].strip()
    return text

def run_series_generation():
    print("==================================================")
    print("🚀 [Auto Blogger] AI 생존 가이드 시리즈 연재 시작")
    print("==================================================")
    
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)

    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime('%Y-%m-%d')
    time_str = now_kst.strftime('%Y-%m-%dT%H:%M:%S+09:00')

    for i, topic in enumerate(TOPICS):
        file_path = os.path.join(POSTS_DIR, f"{date_str}-{topic['slug']}.md")
        
        # 파일이 이미 존재하면 스킵
        if os.path.exists(file_path):
            print(f"⏩ 이미 존재하는 포스트입니다. 스킵: {topic['title']}")
            continue
            
        print(f"\n[{i+1}/{len(TOPICS)}] 포스트 생성 중: {topic['title']}")
        
        # 추가 요구사항을 덧붙임
        full_prompt = topic["prompt"] + "\n\n요구사항: 마크다운 형식으로 가독성 좋게 작성. 제목(H1)은 넣지 말 것. 전문가이면서도 친절한 블로거 톤을 유지해 주세요."
        
        success, out = run_cmd(["nlm", "notebook", "query", NOTEBOOK_ID, full_prompt, "--timeout", "300"])
        
        if success:
            content = clean_markdown_output(out)
            
            frontmatter = f"""---
title: "{topic['title']}"
date: {time_str}
categories:
  - AI Learnings
tags:
  - AI Guide
  - Beginner
---

"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(frontmatter + content + "\n")
            print(f"✅ 포스트 저장 완료: {file_path}")
            
            # Git 커밋 및 푸시
            subprocess.run(["git", "add", file_path])
            subprocess.run(["git", "commit", "-m", f"feat: add post for {topic['slug']}"])
            subprocess.run(["git", "push", "origin", "main"])
            
            # 다음 포스트 생성 전 1분 대기 (Rate limit 방지)
            print("⏳ 1분 대기 중...")
            time.sleep(60)
        else:
            print(f"❌ 포스트 생성 실패: {topic['title']}")
            time.sleep(10)

if __name__ == "__main__":
    run_series_generation()
