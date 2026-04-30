import os
import re

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter
    parts = content.split('---')
    if len(parts) < 3:
        return False # Not a standard frontmatter markdown
        
    frontmatter = '---' + parts[1] + '---'
    body = '---'.join(parts[2:])

    # Find footnotes section
    # Footnotes are defined as `[^id]: text`
    footnote_defs = dict()
    
    # We will find all lines starting with [^d+]:
    def_pattern = re.compile(r'^\[\^(\d+)\]:\s*(.*)$', re.MULTILINE)
    for match in def_pattern.finditer(body):
        f_id = match.group(1)
        f_text = match.group(2)
        footnote_defs[f_id] = f_text

    if not footnote_defs:
        return False # No footnotes to process
        
    # Determine valid footnotes (must have http:// or https://)
    valid_old_ids = []
    for f_id, f_text in footnote_defs.items():
        if 'http://' in f_text or 'https://' in f_text:
            valid_old_ids.append(f_id)
            
    # Create mapping to new IDs
    valid_old_ids.sort(key=lambda x: int(x))
    old_to_new = {}
    for i, old_id in enumerate(valid_old_ids, 1):
        old_to_new[old_id] = str(i)

    # Remove the footnote definitions and the `### 레퍼런스` header from the body
    # We will reconstruct it later.
    # To do this safely, we find where the references start.
    # Usually it's `---` followed by `### 레퍼런스` or just `### 레퍼런스` at the end.
    ref_idx = body.rfind('### 레퍼런스')
    if ref_idx != -1:
        # Also remove the `---` before it if it exists
        dash_idx = body.rfind('---', 0, ref_idx)
        if dash_idx != -1 and body[dash_idx:ref_idx].strip() == '':
            body = body[:dash_idx]
        else:
            body = body[:ref_idx]
    else:
        # Just remove the definition lines
        body = def_pattern.sub('', body)

    body = body.strip()

    # Now process paragraphs
    paragraphs = body.split('\n\n')
    new_paragraphs = []
    
    marker_pattern = re.compile(r'\[\^(\d+)\]')
    
    for p in paragraphs:
        # Find all old markers in this paragraph
        found_old_ids = marker_pattern.findall(p)
        
        # Determine which ones are valid and get their new IDs
        valid_new_ids = []
        for old_id in found_old_ids:
            if old_id in old_to_new:
                new_id = old_to_new[old_id]
                if new_id not in valid_new_ids:
                    valid_new_ids.append(new_id)
                    
        # Remove all markers from paragraph
        p_clean = re.sub(r'\s*\[\^\d+\]', '', p)
        # Fix punctuation spaces
        p_clean = re.sub(r'\s+([.,!?])', r'\1', p_clean)
        
        # If there are valid new IDs, append them at the end of the paragraph
        if valid_new_ids:
            # Append markers like [^1][^2]
            markers_str = "".join([f"[^{nid}]" for nid in valid_new_ids])
            # If paragraph doesn't end with space, add one? 
            # Or just append. Usually it's good to just append: "문장입니다. [^1][^2]"
            p_clean = p_clean.strip() + f" {markers_str}"
            
        new_paragraphs.append(p_clean)

    new_body = '\n\n'.join(new_paragraphs)

    # Reconstruct references
    if valid_old_ids:
        refs_section = "\n\n---\n### 레퍼런스\n"
        for old_id in valid_old_ids:
            new_id = old_to_new[old_id]
            f_text = footnote_defs[old_id]
            refs_section += f"[^{new_id}]: {f_text}\n"
        new_body += refs_section

    final_content = frontmatter + '\n\n' + new_body.strip() + '\n'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    return True

def main():
    processed = 0
    for root, _, files in os.walk(POSTS_DIR):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                if process_file(path):
                    processed += 1
                    print(f"✅ 정돈 완료: {f}")
    
    print(f"\n🎉 총 {processed}개의 포스트 주석이 성공적으로 정리되었습니다!")

if __name__ == "__main__":
    main()
