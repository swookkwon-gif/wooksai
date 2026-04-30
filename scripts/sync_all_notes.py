import os
import json
import re
import subprocess
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API Key
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    GEMINI_API_KEY = GEMINI_API_KEY.strip('"').strip("'")
client = genai.Client(api_key=GEMINI_API_KEY)

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')

def get_all_existing_titles():
    titles = set()
    for root, _, files in os.walk(POSTS_DIR):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as md:
                    for line in md:
                        if line.startswith('title:'):
                            t = line.replace('title:', '').strip().strip('\'"')
                            t = t.replace('[GF2.0]', '').replace('[비즈니스 분석]', '').replace('[브랜드 탐구]', '').strip()
                            titles.add(t)
                            break
    return titles

def replace_footnotes(text):
    def replace_ref(match):
        refs = match.group(1)
        parts = []
        for p in refs.split(","):
            p = p.strip()
            if "-" in p:
                try:
                    start, end = map(int, p.split("-"))
                    for i in range(start, end + 1):
                        parts.append(f"[^{i}]")
                except:
                    parts.append(f"[^{p}]")
            else:
                parts.append(f"[^{p}]")
        return "".join(parts)
    return re.sub(r"\[([\d\s,\-]+)\]", replace_ref, text)

def format_content(text):
    text = replace_footnotes(text)
    # Find all footnotes used
    used_refs = set(re.findall(r"\[\^(\d+)\]", text))
    if used_refs:
        refs_out = "\n\n---\n### 레퍼런스\n"
        for ref in sorted(map(int, used_refs)):
            refs_out += f"[^{ref}]: 관련 소스 문서 내용 참조\n"
        text += refs_out
    return text

def analyze_note_with_gemini(title, content):
    prompt = f"""
다음은 사용자가 작성한 리서치 노트의 제목과 내용입니다.
이 노트를 블로그 포스트로 발행하기 위해 가장 적절한 '영어 파일명(slug)', '카테고리', '요약(excerpt)'을 생성해주세요.

노트 제목: {title}
노트 내용 일부: {content[:1000]}

[규칙]
- 파일명(slug)은 확장자 .md 없이 영소문자와 하이픈(-)만 사용하여 작성 (예: modern-marketing-strategy)
- 카테고리는 다음 네 가지 중 하나만 선택: "Marketing", "AI News", "AI Learnings", "Career"
- 요약(excerpt)은 150자 내외의 한국어로 작성
- JSON 형식으로만 응답 (예: {{"slug": "...", "category": "...", "excerpt": "..."}})
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API 2.5 Error: {e}")
        try:
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e2:
            print(f"Gemini API Error: {e2}")
            return {
                "slug": f"notebooklm-note-{hash(title)%100000}",
                "category": "3. AI Learnings",
                "excerpt": title
            }

def main():
    existing_titles = get_all_existing_titles()
    print(f"📦 발견된 기존 포스트 수: {len(existing_titles)}")

    print("🚀 NotebookLM 노트북 목록 가져오는 중...")
    nbs_res = subprocess.run(["nlm", "notebook", "list", "--json"], capture_output=True, text=True)
    if nbs_res.returncode != 0:
        print("❌ 노트북 목록을 가져오지 못했습니다.")
        return
        
    nbs_data = json.loads(nbs_res.stdout)
    notebooks = nbs_data if isinstance(nbs_data, list) else nbs_data.get('notebooks', [])
    
    published_count = 0
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)

    for nb in notebooks:
        nb_id = nb['id']
        print(f"🔍 노트북 탐색 중: {nb['title']} ({nb_id})")
        
        notes_res = subprocess.run(["nlm", "note", "list", nb_id, "--json"], capture_output=True, text=True)
        if notes_res.returncode != 0:
            continue
            
        try:
            notes_data = json.loads(notes_res.stdout)
            notes_list = notes_data if isinstance(notes_data, list) else notes_data.get('notes', [])
        except:
            continue
            
        for note in notes_list:
            title = note.get('title', 'Untitled')
            content = note.get('content', '')
            
            if not title or not content:
                continue
                
            # 심플한 중복 체크 (제목 일치 여부)
            # NotebookLM에서 제목을 비슷하게 쓰거나 동일하게 썼을 가능성 고려
            is_duplicate = False
            for ext_title in existing_titles:
                if title.lower() in ext_title.lower() or ext_title.lower() in title.lower():
                    is_duplicate = True
                    break
                    
            if is_duplicate:
                print(f"   ⏭️ 이미 포스팅된 노트 건너뜀: {title}")
                continue
                
            print(f"   ✨ 새로운 노트 발견: {title}")
            meta = analyze_note_with_gemini(title, content)
            
            cat_dir = meta['category']
            slug = meta['slug']
            excerpt = meta['excerpt'].replace("'", "''")
            
            target_dir = os.path.join(POSTS_DIR, cat_dir)
            os.makedirs(target_dir, exist_ok=True)
            
            file_name = f"{now_kst.strftime('%Y-%m-%d')}-{slug}.md"
            file_path = os.path.join(target_dir, file_name)
            
            formatted_content = format_content(content)
            
            frontmatter = f"""---
title: '{title.replace("'", "''")}'
date: {now_kst.strftime('%Y-%m-%dT%H:%M:%S+09:00')}
excerpt: '{excerpt}'
categories:
  - {cat_dir.split('. ')[-1]}
tags:
  - NotebookLM
  - AI Generated
---

"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + formatted_content)
                
            print(f"   ✅ 작성 완료: {file_name}")
            published_count += 1

    print(f"\n🎉 총 {published_count}개의 새로운 노트가 포스팅되었습니다!")

if __name__ == "__main__":
    main()
