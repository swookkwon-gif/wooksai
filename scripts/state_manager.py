import os
import json

STATE_FILE = os.path.join(os.path.dirname(__file__), 'state.json')

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"rss": [], "gmail": []}
    
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
            if "rss" not in state: state["rss"] = []
            if "gmail" not in state: state["gmail"] = []
            return state
    except json.JSONDecodeError:
        return {"rss": [], "gmail": []}

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
