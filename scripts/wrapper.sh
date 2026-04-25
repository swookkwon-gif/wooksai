#!/bin/bash
# 이 래퍼(Wrapper) 쉘 스크립트는 cron 에서 Python 스크립트를 안정적으로 실행시키기 위한 용도입니다.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR/.." || exit

# 가상환경 활성화 (Booklog 폴더 내의 .venv)
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# 실행할 대상을 첫 번째 파라미터로 받음 ('daemon' 또는 'weekly')
if [ "$1" == "daemon" ]; then
    echo "Running auto blog daemon..."
    python scripts/auto_blog_daemon.py
    
    # 깃허브 퍼블리싱 (블로그 업로드)
    echo "Pushing changes to GitHub..."
    git add content/posts/2.\ AI\ News/*.md
    git commit -m "auto: daily AI news blog post"
    git push origin main
    
elif [ "$1" == "weekly" ]; then
    echo "Running weekly summary..."
    python scripts/weekly_ai_summary.py
    
    # 깃허브 퍼블리싱 (블로그 업로드)
    echo "Pushing changes to GitHub..."
    git add content/posts/2.\ AI\ News/*weekly-ai-review.md
    git commit -m "auto: weekly AI review blog post"
    git push origin main
else
    echo "Usage: ./wrapper.sh [daemon|weekly]"
fi
