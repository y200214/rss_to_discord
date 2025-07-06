import os
import feedparser
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# カンマ区切りで複数アカウント対応
TWITTER_USERS = [u.strip() for u in os.environ["TWITTER_USER"].split(",")]
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

def fetch_and_notify_for_user(user):
    rss_url = f"https://twitrss.me/twitter_user_to_rss/?user={user}"
    now = datetime.utcnow()
    feed = feedparser.parse(rss_url)

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
                print(f"[{user}] Failed to send {url}: {res.status_code}")

def main():
    for user in TWITTER_USERS:
        fetch_and_notify_for_user(user)

if __name__ == "__main__":
    main()
