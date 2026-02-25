import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

BASE_URL = "https://www.techbrew.com"

def build_feed():
    r = requests.get(BASE_URL + "/search", headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    seen = set()

    for a in soup.select("a[href^='/stories/']"):
        href = a["href"]
        if href in seen:
            continue
        seen.add(href)

        article = a.find("article")
        if not article:
            continue

        # Get title from content wrapper
        content = article.find("div", class_=lambda c: c and "ContentWrapper" in c)
        title = content.get_text(strip=True) if content else a.get_text(strip=True)
        if not title:
            continue

        # Get image
        img = article.find("img")
        image_url = ""
        if img and img.get("src") and not img["src"].startswith("data:"):
            image_url = img["src"]

        # Extract date from URL
        parts = href.split("/")
        try:
            date_str = f"{parts[2]}-{parts[3]}-{parts[4]}"
        except IndexError:
            date_str = datetime.today().strftime("%Y-%m-%d")

        items.append({
            "title": title,
            "url": BASE_URL + href,
            "image": image_url,
            "date": date_str
        })

    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">\n<channel>\n'
    rss += '<title>Tech Brew</title>\n'
    rss += f'<link>{BASE_URL}</link>\n'
    rss += '<description>Tech Brew scraped feed</description>\n'

    for item in items:
        rss += "<item>\n"
        rss += f"  <title>{item['title']}</title>\n"
        rss += f"  <link>{item['url']}</link>\n"
        rss += f"  <pubDate>{item['date']}</pubDate>\n"
        if item["image"]:
            img_url = item["image"]
            rss += f'  <media:content url="{img_url}" medium="image"/>\n'
        rss += "</item>\n"

    rss += "</channel>\n</rss>"

    os.makedirs("docs", exist_ok=True)
    with open("docs/feed.xml", "w") as f:
        f.write(rss)
    print(f"Feed written with {len(items)} items.")

build_feed()
