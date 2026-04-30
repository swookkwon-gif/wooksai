import re
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

file_path = "content/posts/2. AI News/2026-04-30-global-ai-news-summary.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

urls = re.findall(r'https?://[^\s\)"\']+', content)

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, context=ctx, timeout=5)
        print(f"[OK] {url}")
    except Exception as e:
        print(f"[ERROR {e}] {url}")
