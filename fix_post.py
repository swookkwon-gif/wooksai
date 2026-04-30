import re

file_path = "content/posts/2. AI News/2026-04-30-global-ai-news-summary.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove <img> tags
content = re.sub(r'<img[^>]*>', '', content)

# 2. Fix headings to proper markdown links
# Pattern: ### Title (http...)
# Title might have brackets like [4월29일]
def fix_heading(match):
    title = match.group(1).strip()
    url = match.group(2).strip()
    # if title is already enclosed in brackets, remove them so we don't nest [[title]] unless it's part of the text
    # Actually markdown handles [[4월29일] Title](URL) fine.
    return f"### [{title}]({url})"

content = re.sub(r'^###\s+(.*?)\s*\((https?://[^\)]+)\)', fix_heading, content, flags=re.MULTILINE)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done fixing post.")
