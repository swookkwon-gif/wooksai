import os
import re

POSTS_DIR = "/Users/wook/WookAi/Booklog/content/posts"

dir_to_cat = {
    "Marketing": "Marketing",
    "2. AI News": "AI News",
    "3. AI Learnings": "AI Learnings",
    "4. Career": "Career",
}

for root, _, files in os.walk(POSTS_DIR):
    for file in files:
        if file.endswith(".md"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find frontmatter
            match = re.match(r'^(---\n.*?\n---\n)(.*)$', content, re.DOTALL)
            if not match:
                continue
                
            frontmatter = match.group(1)
            body = match.group(2)
            
            # Extract current category/categories
            has_cat = False
            
            # Check if there is already a category
            cat_match1 = re.search(r'^category:\s*(.+)$', frontmatter, re.MULTILINE)
            cat_match2 = re.search(r'^categories:\n(?:\s+-\s+.*\n)+', frontmatter, re.MULTILINE)
            
            new_cat_value = ""
            for dirname, catname in dir_to_cat.items():
                if dirname in filepath:
                    new_cat_value = catname
                    break
            
            if not new_cat_value:
                new_cat_value = "AI Learnings" # default fallback
                
            new_frontmatter = frontmatter
            changed = False
            
            if cat_match1:
                old_cat = cat_match1.group(1).strip(" \"'")
                if old_cat != new_cat_value:
                    new_frontmatter = re.sub(r'^category:\s*.+$', f'category: {new_cat_value}', new_frontmatter, flags=re.MULTILINE)
                    changed = True
            elif cat_match2:
                # Replace the whole categories block with a single category string
                new_frontmatter = new_frontmatter.replace(cat_match2.group(0), f'category: {new_cat_value}\n')
                changed = True
            else:
                # Add category before tags or at the end of frontmatter
                if 'tags:' in new_frontmatter:
                    new_frontmatter = new_frontmatter.replace('tags:', f'category: {new_cat_value}\ntags:')
                elif 'description:' in new_frontmatter:
                    new_frontmatter = new_frontmatter.replace('description:', f'category: {new_cat_value}\ndescription:')
                elif 'excerpt:' in new_frontmatter:
                    new_frontmatter = new_frontmatter.replace('excerpt:', f'category: {new_cat_value}\nexcerpt:')
                else:
                    new_frontmatter = new_frontmatter.replace('\n---\n', f'\ncategory: {new_cat_value}\n---\n', 1)
                changed = True
                
            if changed:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_frontmatter + body)
                print(f"Set category to {new_cat_value} in {file}")
