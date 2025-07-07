import os
import feedparser
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ローカル実行時に .env を読み込む
load_dotenv()

# カンマ区切りで複数アカウント対応
TWITTER_USERS = [u.strip() for u in os.environ["TWITTER_USER"].split(",")]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

def fetch_and_notify_for_user(user):
    rss_url = f"https://twitrss.me/twitter_user_to_rss/?user={user}"
    print(f"[{user}] Fetching RSS feed: {rss_url}")

    now = datetime.utcnow()
    feed = feedparser.parse(rss_url)
    print(f"[{user}] Entries found: {len(feed.entries)}")

    for entry in feed.entries:
        # RSS の published（文字列）をデバッグ出力
        print(f"[{user}] Entry published at: {entry.get('published', 'N/A')}")

        pub = datetime(*entry.published_parsed[:6])
        # テスト用に過去5日以内のみ取得
        if now - pub > timedelta(days=5):
            print(f"[{user}] Skipping (older than 5 days): {pub}")
            continue

        # URL 抽出
        urls = []
        if hasattr(entry, "links"):
            for link in entry.links:
                href = link.get("href")
                if href and href.startswith("http"):
                    urls.append(href)
        print(f"[{user}] URLs extracted: {urls}")

        # Discord へ送信
        for url in set(urls):
            print(f"[{user}] Sending URL: {url}")
            res = requests.post(DISCORD_WEBHOOK_URL, json={"content": url})
            print(f"[{user}] Response status: {res.status_code}")
            if res.status_code not in (200, 204):
                print(f"[{user}] Failed to send {url}: {res.status_code}, {res.text}")

def main():
    for user in TWITTER_USERS:
        fetch_and_notify_for_user(user)

if __name__ == "__main__":
    main()
