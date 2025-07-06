import os
import feedparser
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ローカル実行時に .env を読み込む
load_dotenv()

TWITTER_USER        = os.environ["TWITTER_USER"]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
RSS_URL             = f"https://twitrss.me/twitter_user_to_rss/?user={TWITTER_USER}"

def fetch_and_notify():
    now = datetime.utcnow()
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        pub = datetime(*entry.published_parsed[:6])
        if now - pub > timedelta(minutes=10):
            continue

        urls = []
        if hasattr(entry, "links"):
            for link in entry.links:
                href = link.get("href")
                if href and href.startswith("http"):
                    urls.append(href)

        for url in set(urls):
            res = requests.post(DISCORD_WEBHOOK_URL, json={"content": url})
            if res.status_code not in (200, 204):
                print(f"Failed to send {url}: {res.status_code} {res.text}")

if __name__ == "__main__":
    fetch_and_notify()

