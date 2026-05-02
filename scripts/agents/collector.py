#!/usr/bin/env python3
"""
agents/collector.py — 데이터 수집 에이전트
RSS 피드와 Gmail 뉴스레터에서 원시 데이터를 수집한다.
LLM 호출 없이 순수 데이터 수집만 담당한다.
"""
import time
import feedparser
from datetime import datetime, timezone, timedelta

from skills.config_loader import load_feeds
from skills.gmail_reader import get_gmail_service, get_label_id, fetch_newsletters
from state.state_manager import is_processed


def collect_rss(feeds: list[dict] | None = None) -> list[dict]:
    """
    RSS 피드에서 미처리 기사를 수집한다.
    
    Returns:
        list[dict]: [{"id", "source_type", "source_name", "title", "url", "content"}, ...]
    """
    if feeds is None:
        feeds = load_feeds()

    articles = []
    now = datetime.now(timezone.utc)

    for feed in feeds:
        print(f"\n🔍 대상 RSS: {feed['name']}")
        try:
            parsed_feed = feedparser.parse(feed['url'])
        except Exception as e:
            print(f" └ 파싱 실패: {e}")
            continue

        for entry in parsed_feed.entries:
            try:
                url_id = entry.get('link', entry.get('id', ''))
                if not url_id or is_processed("rss", url_id):
                    continue

                dt = (
                    datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    if 'published_parsed' in entry and entry.published_parsed
                    else now
                )
                if (now - dt).days > 2:
                    continue

                content = ""
                if 'content' in entry:
                    content = entry.content[0].value
                elif 'summary' in entry:
                    content = entry.summary

                title = entry.get('title', 'No Title')

                # 키워드 필터링
                keywords = feed.get('keywords', [])
                if keywords:
                    combined_text = (title + " " + content).lower()
                    if not any(k.lower() in combined_text for k in keywords):
                        continue

                articles.append({
                    "id": url_id,
                    "source_type": "rss",
                    "source_name": feed['name'],
                    "title": title,
                    "url": entry.get('link', ''),
                    "content": content[:5000],  # 5000자 제한
                })
            except Exception:
                pass

    print(f" └ RSS 수집 완료: {len(articles)}건")
    return articles


def collect_gmail() -> dict[str, list[dict]]:
    """
    Gmail 뉴스레터를 발신자별로 그룹핑하여 수집한다.
    
    Returns:
        dict: {"발신자명": [{"id", "subject", "body"}, ...]}
    """
    print("\n🔍 대상 Gmail: AI News 뉴스레터")
    service = get_gmail_service()
    if not service:
        print(" └ Gmail 인증 실패")
        return {}

    label_id = get_label_id(service)
    if not label_id:
        print(" └ AI News 라벨을 찾을 수 없습니다")
        return {}

    newsletters = fetch_newsletters(service, label_id)
    if not newsletters:
        print(" └ 처리할 새로운 뉴스레터가 없습니다")
        return {}

    print(f" └ Gmail 수집 완료: {len(newsletters)}건")

    # 발신자별 그룹핑
    by_sender = {}
    for nl in newsletters:
        sender = nl['sender']
        if sender not in by_sender:
            by_sender[sender] = []
        by_sender[sender].append(nl)

    return by_sender


def collect_all() -> tuple[list[dict], dict[str, list[dict]]]:
    """RSS + Gmail 전체 수집을 실행한다."""
    rss_articles = collect_rss()
    gmail_groups = collect_gmail()
    return rss_articles, gmail_groups
