import os
import re

POSTS_DIR = "/Users/wook/WookAi/Booklog/content/posts"

mapping = {
    "1. Marketing": "Marketing",
    "Digital Marketing": "Marketing",
    "마케팅 논문": "Marketing",
    "2. AI News": "AI News",
    "AI News Flood": "AI News",
    "3. AI Learnings": "AI Learnings",
    "4. Career": "Career",
    "Career": "Career",
}

for root, _, files in os.walk(POSTS_DIR):
    for file in files:
        if file.endswith(".md"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            
            for old_cat, new_cat in mapping.items():
                old_str1 = f"categories:\n  - {old_cat}"
                new_str1 = f"categories:\n  - {new_cat}"
                new_content = new_content.replace(old_str1, new_str1)
                
                old_str2 = f"categories:\n  - '{old_cat}'"
                new_str2 = f"categories:\n  - '{new_cat}'"
                new_content = new_content.replace(old_str2, new_str2)
                
                old_str3 = f'categories:\n  - "{old_cat}"'
                new_str3 = f'categories:\n  - "{new_cat}"'
                new_content = new_content.replace(old_str3, new_str3)
                
                old_str4 = f'category: "{old_cat}"'
                new_str4 = f'category: "{new_cat}"'
                new_content = new_content.replace(old_str4, new_str4)
                
                old_str5 = f"category: '{old_cat}'"
                new_str5 = f"category: '{new_cat}'"
                new_content = new_content.replace(old_str5, new_str5)
                
                new_content = re.sub(rf"^category:\s*{re.escape(old_cat)}\s*$", f"category: {new_cat}", new_content, flags=re.MULTILINE)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {filepath}")
