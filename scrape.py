import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

BASE_URL = "https://www.techbrew.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def get_article_details(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
        if not title:
            og = soup.find("meta", property="og:title")
            title = og["content"] if og else ""

        # Image
        img_meta = soup.find("meta", itemprop="image")
        image_url = img_meta["content"] if img_meta else ""

        # Date
        date_meta = soup.find("meta", itemprop="datePublished")
        if date_meta:
            date_str = date_meta["content"][:10]
        else:
            time_tag = soup.find("time")
            date_str = time_tag.get_text(strip=True) if time_tag else ""

        # Author
        author_tag = soup.find("a", href=lambda h: h and h.startswith("/contributor/"))
        author = author_tag.get_text(strip=True) if author_tag else ""

        # Category
        bookmarklet = soup.find("div", attrs={"data-vertical": True})
        category = bookmarklet["data-vertical"].replace("-", " ").title() if bookmarklet else ""

        # Description
        desc_meta = soup.find("meta", property="og:description")
        description = desc_meta["content"] if desc_meta else ""

        return title, image_url, date_str, author, category, description

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return "", "", "", "", "", ""


def build_feed():
    r = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    seen = set()
    for a in soup.select("a[href^='/stories/']"):
        href = a["href"]
        if href not in seen:
            seen.add(href)
            links.append(href)

    items = []
    for href in links:
        url = BASE_URL + href
        print(f"Fetching {url}")
        title, image_url, date_str, author, category, description = get_article_details(url)
        if not title:
            continue
        items.append({
            "title": title,
            "url": url,
            "image": image_url,
            "date": date_str,
            "author": author,
            "category": category,
            "description": description
        })
        time.sleep(0.5)

    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:dc="http://purl.org/dc/elements/1.1/">\n<channel>\n'
    rss += '<title>Tech Brew</title>\n'
    rss += f'<link>{BASE_URL}</link>\n'
    rss += '<description>Tech Brew scraped feed</description>\n'

    for item in items:
        rss += "<item>\n"
        rss += f"  <title>{escape_xml(item['title'])}</title>\n"
        rss += f"  <link>{escape_xml(item['url'])}</link>\n"
        if item["date"]:
            rss += f"  <pubDate>{item['date']}</pubDate>\n"
        if item["author"]:
            rss += f"  <dc:creator>{escape_xml(item['author'])}</dc:creator>\n"
        if item["category"]:
            rss += f"  <category>{escape_xml(item['category'])}</category>\n"
        if item["description"]:
            rss += f"  <description>{escape_xml(item['description'])}</description>\n"
        if item["image"]:
            img_url = escape_xml(item["image"])
            rss += f'  <media:content url="{img_url}" medium="image"/>\n'
        rss += "</item>\n"

    rss += "</channel>\n</rss>"

    os.makedirs("docs", exist_ok=True)
    with open("docs/feed.xml", "w") as f:
        f.write(rss)
    print(f"Feed written with {len(items)} items.")

build_feed()
