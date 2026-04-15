#!/usr/bin/env python3
"""
Research Update Bot
-------------------
Continuously fetches and updates research files from Wikipedia, arXiv,
and RSS news feeds. Runs 24/7 on a configurable schedule.
"""

import os
import sys
import time
import logging
import signal
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
import feedparser
import schedule
import yaml
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging setup (configured after config is loaded)
# ---------------------------------------------------------------------------

def setup_logging(log_dir: str, log_level: str) -> logging.Logger:
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / f"bot_{datetime.now().strftime('%Y%m%d')}.log"

    level = getattr(logging, log_level.upper(), logging.INFO)
    fmt = "%(asctime)s  %(levelname)-8s  %(message)s"

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ]

    logging.basicConfig(level=level, format=fmt, handlers=handlers)
    return logging.getLogger("research_bot")


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Source fetchers
# ---------------------------------------------------------------------------

class WikipediaFetcher:
    BASE = "https://en.wikipedia.org/api/rest_v1/page/summary"

    def __init__(self, logger: logging.Logger):
        self.log = logger
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "ResearchUpdateBot/1.0"

    def fetch(self, page_title: str) -> Optional[dict]:
        url = f"{self.BASE}/{page_title}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {
                "title": data.get("title", page_title),
                "summary": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "last_modified": data.get("timestamp", ""),
            }
        except Exception as exc:
            self.log.warning("Wikipedia fetch failed for '%s': %s", page_title, exc)
            return None


class ArxivFetcher:
    BASE = "https://export.arxiv.org/api/query"

    def __init__(self, logger: logging.Logger, max_results: int = 5):
        self.log = logger
        self.max_results = max_results
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "ResearchUpdateBot/1.0"

    def fetch(self, category: str, keywords: list[str]) -> list[dict]:
        query_terms = " OR ".join(f'"{kw}"' for kw in keywords)
        params = {
            "search_query": f"cat:{category} AND ({query_terms})",
            "start": 0,
            "max_results": self.max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        try:
            resp = self.session.get(self.BASE, params=params, timeout=20)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            papers = []
            for entry in feed.entries:
                papers.append({
                    "title": entry.get("title", "").strip().replace("\n", " "),
                    "summary": entry.get("summary", "").strip()[:600],
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "authors": ", ".join(
                        a.get("name", "") for a in entry.get("authors", [])[:3]
                    ),
                })
            return papers
        except Exception as exc:
            self.log.warning("arXiv fetch failed for category '%s': %s", category, exc)
            return []


class RSSFetcher:
    def __init__(self, logger: logging.Logger, max_per_feed: int = 5):
        self.log = logger
        self.max_per_feed = max_per_feed

    def fetch(self, feed_url: str, feed_name: str, keywords: list[str]) -> list[dict]:
        try:
            feed = feedparser.parse(feed_url)
            kw_lower = [k.lower() for k in keywords]
            articles = []
            for entry in feed.entries:
                text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
                if any(k in text for k in kw_lower):
                    articles.append({
                        "title": entry.get("title", "").strip(),
                        "summary": BeautifulSoup(
                            entry.get("summary", ""), "lxml"
                        ).get_text()[:500],
                        "url": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": feed_name,
                    })
                    if len(articles) >= self.max_per_feed:
                        break
            return articles
        except Exception as exc:
            self.log.warning("RSS fetch failed for '%s': %s", feed_name, exc)
            return []


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------

def _section_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()[:8]


def write_research_file(
    output_dir: str,
    topic_name: str,
    wikipedia_data: Optional[dict],
    arxiv_papers: list[dict],
    rss_articles: list[dict],
    logger: logging.Logger,
) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    safe_name = topic_name.lower().replace(" ", "_").replace("/", "_")
    filepath = Path(output_dir) / f"{safe_name}.md"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# {topic_name}",
        f"\n> Last updated: **{now}**\n",
    ]

    # --- Wikipedia section ---
    if wikipedia_data:
        lines += [
            "## Overview (Wikipedia)",
            "",
            wikipedia_data["summary"],
            "",
            f"[Read more on Wikipedia]({wikipedia_data['url']})",
            "",
        ]

    # --- arXiv section ---
    if arxiv_papers:
        lines += ["## Latest Research Papers (arXiv)", ""]
        for i, paper in enumerate(arxiv_papers, 1):
            lines += [
                f"### {i}. {paper['title']}",
                f"- **Authors:** {paper['authors']}",
                f"- **Published:** {paper['published']}",
                f"- **Link:** {paper['url']}",
                "",
                paper["summary"],
                "",
            ]

    # --- News section ---
    if rss_articles:
        lines += ["## Recent News", ""]
        for article in rss_articles:
            lines += [
                f"### {article['title']}",
                f"- **Source:** {article['source']}",
                f"- **Published:** {article['published']}",
                f"- **Link:** {article['url']}",
                "",
                article["summary"],
                "",
            ]

    content = "\n".join(lines)
    filepath.write_text(content, encoding="utf-8")
    logger.info("Updated research file: %s", filepath)


# ---------------------------------------------------------------------------
# Core update routine
# ---------------------------------------------------------------------------

def run_update_cycle(config: dict, logger: logging.Logger) -> None:
    logger.info("=== Starting update cycle ===")

    bot_cfg = config["bot"]
    sources_cfg = config.get("sources", {})
    rss_feeds_cfg = config.get("rss_feeds", [])
    max_results = bot_cfg.get("results_per_source", 5)
    output_dir = bot_cfg.get("output_dir", "research")

    wiki = WikipediaFetcher(logger) if sources_cfg.get("wikipedia", True) else None
    arxiv = ArxivFetcher(logger, max_results) if sources_cfg.get("arxiv", True) else None
    rss = RSSFetcher(logger, max_results) if sources_cfg.get("rss_feeds", True) else None

    for topic in config.get("topics", []):
        name = topic["name"]
        logger.info("Processing topic: %s", name)

        # Wikipedia
        wiki_data = None
        if wiki and topic.get("wikipedia_page"):
            wiki_data = wiki.fetch(topic["wikipedia_page"])

        # arXiv
        papers: list[dict] = []
        if arxiv and topic.get("arxiv_category"):
            papers = arxiv.fetch(topic["arxiv_category"], topic.get("keywords", []))

        # RSS news
        articles: list[dict] = []
        if rss:
            for feed_cfg in rss_feeds_cfg:
                articles += rss.fetch(
                    feed_cfg["url"], feed_cfg["name"], topic.get("keywords", [])
                )

        write_research_file(output_dir, name, wiki_data, papers, articles, logger)

    logger.info("=== Update cycle complete ===")


# ---------------------------------------------------------------------------
# Signal handling for graceful shutdown
# ---------------------------------------------------------------------------

_running = True

def _handle_signal(sig, frame):
    global _running
    print(f"\nReceived signal {sig}. Shutting down gracefully...")
    _running = False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    config_path = os.environ.get("RESEARCH_BOT_CONFIG", "config.yaml")
    if not Path(config_path).exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    config = load_config(config_path)
    bot_cfg = config["bot"]

    logger = setup_logging(bot_cfg.get("log_dir", "logs"), bot_cfg.get("log_level", "INFO"))
    logger.info("Research Update Bot starting up")
    logger.info("Config: %s", config_path)

    interval = bot_cfg.get("update_interval_minutes", 60)
    logger.info("Update interval: %d minutes", interval)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Run once immediately on startup
    run_update_cycle(config, logger)

    # Schedule recurring runs
    schedule.every(interval).minutes.do(run_update_cycle, config=config, logger=logger)
    logger.info("Scheduled next run in %d minutes. Bot is running 24/7.", interval)

    while _running:
        schedule.run_pending()
        time.sleep(5)

    logger.info("Research Update Bot stopped.")


if __name__ == "__main__":
    main()
