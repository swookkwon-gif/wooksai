import os

base_dir = "content/posts/3. AI Learnings"

files_data = {
    "2026-04-29-notebooklm-deep-dive.md": {
        "inline": [("환각을 원천 차단하는 구글의 NotebookLM.", "환각을 원천 차단하는 구글의 NotebookLM.[^1]"),
                   ("출처(Citation) 추적:", "출처(Citation) 추적:[^2]"),
                   ("커스텀 지침 (Custom Instructions)", "커스텀 지침 (Custom Instructions)[^3]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [Google NotebookLM Official Blog](https://blog.google/technology/ai/notebooklm-audio-youtube-september-2024/)\n[^2]: [The AI Research Partner: How NotebookLM Makes Your Documents Work Smarter](https://www.baytechconsulting.com/blog/google-notebooklm-2025)\n[^3]: [NotebookLM Updates: October 2025](https://www.youreverydayai.com/notebooklm-updates-october-2025/)\n"
    },
    "2026-04-29-notebooklm-vs-others-gf2.md": {
        "inline": [("인터넷 전체에 퍼져 있는 방대한 데이터를 미리 학습(Pre-trained)하여 답변합니다.", "인터넷 전체에 퍼져 있는 방대한 데이터를 미리 학습(Pre-trained)하여 답변합니다.[^1]"),
                   ("환각이 절대 발생하지 않으며, 모든 문장에 정확한 원문 출처(페이지 번호, 단락)를 클릭 가능한 번호로 달아줍니다.", "환각이 절대 발생하지 않으며, 모든 문장에 정확한 원문 출처(페이지 번호, 단락)를 클릭 가능한 번호로 달아줍니다.[^2]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [ChatGPT vs Claude vs Gemini vs Perplexity vs NotebookLM (2026 Guide)](https://medium.com/@mohitaggarwal/chatgpt-vs-claude-vs-gemini-vs-perplexity-vs-notebooklm-2026-guide-8f7d3e2b1a5c)\n[^2]: [NotebookLM: Document-Grounded AI by Google](https://www.emergentmind.com/notebooklm-document-grounded-ai)\n"
    },
    "2026-04-29-openclaw-local-ai-agent.md": {
        "inline": [("바로 **'OpenClaw'**입니다.", "바로 **'OpenClaw'**입니다.[^1]"),
                   ("파일 시스템 제어 권한 (File System Access):", "파일 시스템 제어 권한 (File System Access):[^2]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [OpenClaw GitHub Repository](https://github.com/openclaw/openclaw)\n[^2]: [OpenClaw: Autonomous Local Agent on Medium](https://medium.com/openclaw-autonomous-local-agent)\n"
    },
    "2026-04-29-claude-code-cli-agent.md": {
        "inline": [("터미널 화면에서 동작하는 차세대 코딩 에이전트입니다.", "터미널 화면에서 동작하는 차세대 코딩 에이전트입니다.[^1]"),
                   ("자율 디버깅 무한 루프:", "자율 디버깅 무한 루프:[^2]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [Anthropic Official: Meet Claude Code](https://claude.com/)\n[^2]: [Claude Code CLI agent Review](https://tembo.io/blog/claude-code-review)\n"
    },
    "2026-04-29-cursor-ai-code-editor.md": {
        "inline": [("**'Cursor(커서)'**라는 낯선 에디터로 대거 이동하기 시작했습니다.", "**'Cursor(커서)'**라는 낯선 에디터로 대거 이동하기 시작했습니다.[^1]"),
                   ("@Codebase (프로젝트 전체 맥락 이해):", "@Codebase (프로젝트 전체 맥락 이해):[^2]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [Cursor AI vs. VS Code: 2025 Comparison](https://plainenglish.io/blog/cursor-vs-vs-code-the-future-of-coding-is-here)\n[^2]: [Why I'm Switching From VS Code to Cursor](https://dev.to/jigz/why-im-switching-from-vs-code-to-cursor-a-developers-perspective-4b0i)\n"
    },
    "2026-04-29-perplexity-ai-search-engine.md": {
        "inline": [("도구가 바로 **Perplexity(퍼플렉시티)**입니다.", "도구가 바로 **Perplexity(퍼플렉시티)**입니다.[^1]"),
                   ("Pro Search (프로 서치): 심층 탐색의 정수:", "Pro Search (프로 서치): 심층 탐색의 정수:[^2]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [Perplexity AI Official](https://www.perplexity.ai/)\n[^2]: [Perplexity Pro Search Update 2025](https://techcrunch.com/2025/01/15/perplexity-pro-search-update)\n"
    },
    "2026-04-29-codex-automated-data-bot.md": {
        "inline": [("**Codex(코덱스)**를 사내 시스템에 연동하는 순간", "**Codex(코덱스)**를 사내 시스템에 연동하는 순간[^1]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [OpenAI Codex Blog](https://openai.com/blog/openai-codex/)\n"
    },
    "2026-04-29-n8n-workflow-automation.md": {
        "inline": [("중심에 바로 **n8n(엔에이트엔)**이 있습니다.", "중심에 바로 **n8n(엔에이트엔)**이 있습니다.[^1]"),
                   ("비용의 한계를 부수는 셀프 호스팅(Self-hosting):", "비용의 한계를 부수는 셀프 호스팅(Self-hosting):[^2]")],
        "refs": "\n---\n### 레퍼런스\n[^1]: [n8n Official Documentation](https://docs.n8n.io/)\n[^2]: [Zapier vs Make vs n8n: Automation Showdown 2025](https://www.nocode.tech/blog/zapier-vs-make-vs-n8n)\n"
    }
}

for filename, mods in files_data.items():
    filepath = os.path.join(base_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # If references exist already, remove the old fake ones (e.g., from gf2 post)
        if "### 레퍼런스" in content:
            content = content.split("### 레퍼런스")[0].strip()
            
        # apply inline replacements
        for old, new in mods["inline"]:
            content = content.replace(old, new)
            
        # append new refs
        content += "\n" + mods["refs"]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filename}")
    else:
        print(f"File not found: {filename}")
