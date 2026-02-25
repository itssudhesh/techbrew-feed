# TechBrew RSS Feed

An auto-updating RSS feed for [Tech Brew](https://www.techbrew.com) — scraped every 6 hours and served via GitHub Pages.

## Feed URL

```
https://itssudhesh.github.io/techbrew-feed/feed.xml
```

Paste this URL into any RSS reader (Inoreader, Feedly, NetNewsWire, Reeder, etc.) to subscribe.

## What it does

- Scrapes the latest articles from techbrew.com every 6 hours via GitHub Actions
- Extracts the full article body, author, publish date, category, and cover image
- Generates a valid RSS 2.0 feed with `<content:encoded>` so articles render inline in your reader
- Commits and pushes the updated `feed.xml` automatically — no manual steps needed

## Project structure

```
├── scrape.py          # Scraper — fetches articles and builds feed.xml
├── scrape.yml         # GitHub Actions workflow (runs every 6 hours)
└── docs/
    └── feed.xml       # Generated RSS feed (served via GitHub Pages)
```

## Tech stack

- Python, Requests, BeautifulSoup
- GitHub Actions (scheduled cron)
- GitHub Pages (static file hosting)
