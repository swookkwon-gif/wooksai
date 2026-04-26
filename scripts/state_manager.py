import os
import json

STATE_FILE = os.path.join(os.path.dirname(__file__), 'state.json')

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"rss": [], "gmail": [], "evaluations": {}}
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
            if "rss" not in state: state["rss"] = []
            if "gmail" not in state: state["gmail"] = []
            if "evaluations" not in state: state["evaluations"] = {}
            return state
    except json.JSONDecodeError:
        return {"rss": [], "gmail": [], "evaluations": {}}

def save_state(state):
    # 중복 방지를 위해 리스트 제한 로직 (최근 1500개 유지)
    state["rss"] = state.get("rss", [])[-1500:]
    state["gmail"] = state.get("gmail", [])[-1500:]
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def is_processed(source_type, item_id):
    state = load_state()
    return item_id in state.get(source_type, [])

def mark_processed(source_type, item_id):
    state = load_state()
    if item_id not in state.get(source_type, []):
        state[source_type].append(item_id)
        save_state(state)

def save_evaluations(source_name, evals_list):
    if not evals_list: return
    state = load_state()
    if "evaluations" not in state: state["evaluations"] = {}
    if source_name not in state["evaluations"]:
        state["evaluations"][source_name] = []
        
    from datetime import datetime, timezone, timedelta
    date_str = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d")
    
    for ev in evals_list:
        ev["date"] = date_str
        state["evaluations"][source_name].append(ev)
        
    # 최대 200개까지만 유지 (수집량 폭증 방지)
    state["evaluations"][source_name] = state["evaluations"][source_name][-200:]
    save_state(state)
