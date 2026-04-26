#!/usr/bin/env python3
import os
import time
import json
import re
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

import sys
sys.path.append(os.path.dirname(__file__))
from state_manager import load_state

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY is missing.")
    import sys; sys.exit(1)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts', '2. AI News')

def get_recent_posts(days=7):
    recent_texts = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    
    if not os.path.exists(POSTS_DIR):
        return []
        
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith(".md"): continue
        
        # 날짜 추출 2026-04-20-...
        match = re.match(r'^(\d{4}-\d{2}-\d{2})-', filename)
        if match:
            post_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if post_date >= cutoff_date:
                filepath = os.path.join(POSTS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 본문이 너무 길면 자름
                    if len(content) > 10000:
                        content = content[:10000]
                    recent_texts.append(f"\n[파일명: {filename}]\n{content}\n")
                    
    return recent_texts

def write_weekly_digest(content):
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    date_str = now_kst.strftime("%Y-%m-%d")
    month_week = f"{now_kst.month}월 {now_kst.day // 7 + 1}주차"
    
    post_title = f"{month_week} AI 주간 핵심 리뷰"
    
    frontmatter = f"""---
title: "{post_title}"
date: "{date_str}"
excerpt: "지난 1주일 가장 중요한 AI 트렌드 및 뉴스 결산"
category: "Weekly Digest"
---

"""
    filename = f"{date_str}-weekly-ai-review.md"
    file_path = os.path.join(POSTS_DIR, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.write(content + "\n")
        
    print(f"✅ 주간 요약 포스트가 생성되었습니다: {filename}")

def generate_evaluations_report(days=7):
    state = load_state()
    evals = state.get("evaluations", {})
    if not evals: return ""
    
    now = datetime.now()
    cutoff_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    
    stats = []
    for source, ev_list in evals.items():
        recent_scores = []
        for ev in ev_list:
            if ev.get("date", "") >= cutoff_date:
                # 숫자 또는 숫자형 문자열을 안전하게 처리
                try:
                    score = float(ev.get("score", 0))
                    recent_scores.append(score)
                except ValueError:
                    pass
        
        if recent_scores:
            avg_score = sum(recent_scores) / len(recent_scores)
            stats.append({"source": source, "count": len(recent_scores), "avg": avg_score})
            
    if not stats: return ""
    
    stats.sort(key=lambda x: x["avg"], reverse=True)
    
    report = "\n\n## 📊 [주간 지표] 발신자별(뉴스레터/RSS) 퀄리티 성과 리포트\n\n"
    report += "| 소스명 (발신자) | 평가된 기사 수 | 평균 점수 (5점 만점) |\n"
    report += "|---|---|---|\n"
    for s in stats:
        report += f"| {s['source']} | {s['count']} | {s['avg']:.2f} |\n"
        
    report += "\n> 💡 **Tip:** 평균 점수가 지속적으로 2점 이하인 뉴스레터는 추후 구독 해지를 고려해 볼 수 있습니다.\n"
    return report

def update_eval_rules():
    feedback_path = os.path.join(os.path.dirname(__file__), 'feedback.json')
    rules_path = os.path.join(os.path.dirname(__file__), 'custom_eval_rules.txt')
    
    if not os.path.exists(feedback_path): return
    
    try:
        with open(feedback_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            fb_data = raw_data.get("feedbacks", []) if isinstance(raw_data, dict) else raw_data
            
        if not fb_data: return
        
        recent_fb = fb_data[-20:]
        fb_text = ""
        for fb in recent_fb:
            fb_text += f"- 주제/기사명: '{fb.get('keyword_or_title', '')}', 기존점수: {fb.get('ai_score', '')}, 사용자부여점수: {fb.get('user_score', '')}\n"
            fb_text += f"  이유: {fb.get('reasoning', '')}\n"
            
        print("-> 최근 사용자 피드백을 기반으로 맞춤형 평가 룰(가이드라인)을 진화시킵니다...")
        
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""
당신은 AI 뉴스레터 에디터 봇의 시스템 개선 AI입니다.
아래는 뉴스레터 구독자(사용자)가 AI의 기사 평가 점수를 자신이 직접 정정한 피드백 기록입니다.

[사용자 오답노트/피드백]
{fb_text}

[요구사항]
위 피드백을 분석하여, 앞으로 AI 봇이 기사를 수집하고 1~5점 척도로 평가할 때 명심해야 할 [사용자 맞춤형 평가 핵심 룰]을 3~5개 항목의 불릿포인트(`-`)로 정리하세요. 
명확하고 구체적으로 작성하여, 이 텍스트만 읽으면 사용자의 취향에 맞게 높은 점수와 낮은 점수를 줄 수 있도록 하세요. (안정적인 구조화를 위해 불필요한 서문은 생략하세요)
"""
        response = None
        for attempt in range(5):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.2)
                )
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"      [룰 생성 대기] 429 에러 발생. 60초 대기 후 재시도... ({attempt+1}/5)")
                    time.sleep(60)
                else:
                    raise e
                    
        if not response: return
        
        new_rules = response.text.replace("```markdown", "").replace("```", "").strip()
        
        if new_rules:
            with open(rules_path, 'w', encoding='utf-8') as f:
                f.write(new_rules)
            print("✅ 맞춤형 평가 룰이 성공적으로 학습 및 업데이트되었습니다.")
            
    except Exception as e:
        print(f"❌ 룰 업데이트 중 에러 발생: {e}")

def run_weekly_summary():
    print("=======================================================")
    print("🗓️ [Weekly Summary] 주간 AI 리포트 결산 봇 시작")
    print("=======================================================")
    
    # 먼저 룰셋 진화 진행
    update_eval_rules()
    
    posts = get_recent_posts(7)
    if not posts:
        print("최근 7일간의 포스트가 없어 요약을 진행하지 않습니다.")
        return
        
    merged_text = "".join(posts)
    print(f"-> {len(posts)}개의 지난 1주일 포스트 수집 완료. AI 분석 중...")
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
당신은 최고 수준의 AI 애널리스트입니다. 아래는 지난 1주일동안 쏟아진 '매일의 AI 뉴스/뉴스레터 요약본' 리스트입니다.

[지난 1주간의 뉴스 데이터]
{merged_text}

[요구사항]
1. 위 내용들을 꼼꼼히 분석하여, 지난 1주일 동안 AI 업계에서 가장 파급력이 크고 중요했던 'Top 5~7가지 핵심 트렌드 및 시사점'을 뽑아내세요.
2. 단순히 뉴스를 나열하지 말고, **서로 연관된 뉴스들은 하나의 거시적 트렌드**로 묶어서 분석적으로 서술하세요.
3. 각 핵심 트렌드는 마크다운 헤더(`###`)로 소제목을 달고, 하위에 글머리 기호(`-`)로 상세 내용과 의미(시사점)를 요약하세요.
4. 마지막에는 이번 주의 결론적인 1~2문단 총평("Weekly Conclusion")을 작성해주세요.
5. 블로그 포스트의 '본문 내용'만 순수하게 출력하세요. 백틱(```) 마크다운 코드블록이나 불필요한 메타 데이터는 절대로 쓰지 마세요.
"""
    try:
        response = None
        for attempt in range(5):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.3)
                )
                break
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    print(f"      [주간 요약 대기] 429 에러 발생. 60초 대기 후 재시도... ({attempt+1}/5)")
                    time.sleep(60)
                else:
                    raise e
                    
        if not response:
            raise Exception("API Rate Limit 초과 (최대 재시도 실패)")
            
        result_text = response.text.replace("```markdown", "").replace("```", "").strip()
        
        # 발신자 성과 테이블 병합
        performance_report = generate_evaluations_report(7)
        if performance_report:
            result_text += performance_report
            
        write_weekly_digest(result_text)
    except Exception as e:
        print(f"❌ 주간 요약 생성 중 API 에러: {e}")

if __name__ == "__main__":
    run_weekly_summary()
