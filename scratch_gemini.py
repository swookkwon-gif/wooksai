import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
api_key = os.environ.get("GEMINI_API_KEY").strip().strip('"').strip("'")

models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-pro"
]

payload = {
    "contents": [{"parts": [{"text": "Hello"}]}],
}

for m in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    resp = requests.post(url, json=payload)
    print(f"{m}: {resp.status_code}")

