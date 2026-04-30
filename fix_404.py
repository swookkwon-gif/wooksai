import re

file_path = "content/posts/2. AI News/2026-04-30-global-ai-news-summary.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace any kr.benzinga.com/news/... URL that is likely truncated with the main site URL
# We know the specific ones that are broken, or we can just replace all long ones.
content = re.sub(r'(https://kr\.benzinga\.com/news/[^\)]+)', 'https://kr.benzinga.com/', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done fixing 404 links.")
