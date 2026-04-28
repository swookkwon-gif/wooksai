import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), 'state.json')

with open(STATE_FILE, 'r', encoding='utf-8') as f:
    state = json.load(f)

evals = state.get("evaluations", {})
report_lines = ["# 뉴스레터 발신자별 평가 요약\n"]

for sender, items in evals.items():
    avg_score = sum([i.get("score", 0) for i in items]) / len(items) if items else 0
    report_lines.append(f"## {sender}")
    report_lines.append(f"- 누적 기사 수: {len(items)}건")
    report_lines.append(f"- 평균 점수: {avg_score:.2f} / 5.0")
    report_lines.append("")
    # 최근 3개 코멘트
    report_lines.append("  [최근 코멘트]")
    for item in items[-3:]:
        report_lines.append(f"  * ({item.get('score')}점) {item.get('reasoning', '')}")
    report_lines.append("\n")

with open('evaluations_report.md', 'w') as f:
    f.write("\n".join(report_lines))

print("evaluations_report.md 생성 완료")
