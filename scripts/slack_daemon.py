import time
import requests
import schedule
from datetime import datetime

import os

# =======================================================
# 환경 변수 설정
# =======================================================
# .env.local 파일에서 환경 변수(SLACK_WEBHOOK_URL)를 자동으로 읽어옵니다.
env_path = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key] = val.strip().strip('"').strip("'")

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_URL_HERE")

# 2. 로컬 대시보드 URL
DASHBOARD_URL = "http://localhost:3000/admin"

def send_slack_message(text):
    if SLACK_WEBHOOK_URL == "YOUR_SLACK_WEBHOOK_URL_HERE":
        print("⚠️ SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
        return
    
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 슬랙 메시지 전송 성공!")
    else:
        print(f"❌ 슬랙 전송 실패: {response.status_code}")

def push_morning_news():
    msg = (
        "🌅 *[AI News Flood]* 좋은 아침입니다!\n"
        "Yoon's AI가 어젯밤 전 세계 AI 뉴스를 모두 수집해 요약했습니다.\n"
        "출근길에 오늘자 뉴스를 확인하고 코멘트를 남겨볼까요?\n"
        f"👉 AI 편집장 만나기: {DASHBOARD_URL}"
    )
    send_slack_message(msg)

def push_lunch_paper():
    msg = (
        "🍔 *[하루 마케팅 논문]* 점심 식사 맛있게 하셨나요?\n"
        "오후 업무 시작 전, 마케팅 명저 논문을 하나 읽고 허리를 펴보세요!\n"
        "AI 편집장이 오늘 소개할 흥미로운 논문을 준비해 두었습니다.\n"
        f"👉 오늘의 논문 브리핑 받기: {DASHBOARD_URL}"
    )
    send_slack_message(msg)

def push_evening_career():
    msg = (
        "🌙 *[Career]* 오늘도 고생 많으셨습니다.\n"
        "마케터로서 오늘 하루 어떤 인사이트나 배움이 있으셨나요?\n"
        "거창할 필요 없이 한 줄만 남겨주시면 멋진 회고록으로 만들어 드릴게요.\n"
        f"👉 하루 회고하러 가기: {DASHBOARD_URL}"
    )
    send_slack_message(msg)

# 스케줄 등록
schedule.every().day.at("08:30").do(push_morning_news)
schedule.every().day.at("13:00").do(push_lunch_paper)
schedule.every().day.at("19:30").do(push_evening_career)

if __name__ == "__main__":
    print("🚀 Wook's AI Copilot 슬랙 푸시 데몬이 시작되었습니다.")
    print("스케줄: [아침 08:30] 뉴스 / [낮 13:00] 논문 / [저녁 19:30] 커리어 회고")
    print("종료하려면 Ctrl+C를 누르세요.\n")
    
    # 즉시 테스트 발송 (확인용)
    # push_lunch_paper()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
