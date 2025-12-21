import logging
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import feedparser
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

class RSSFetcher:
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.last_fetch_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TechNewsAggregator/1.0 (RSS Fetcher)'
        })

    def _wait_for_rate_limit(self) -> None:
        elapsed = time.time() - self.last_fetch_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_fetch_time = time.time()

    def _extract_image_url(self, entry) -> Optional[str]:
        image_url = None

        # Check for media:content or media:thumbnail
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    image_url = media.get('url')
                    break

        # Check for enclosures with image type
        if not image_url and hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if enclosure.type.startswith('image/'):
                    image_url = enclosure.href
                    break

        # Check for standard image tags in content/summary
        if not image_url:
            content = ''
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value if entry.content else ''
            elif hasattr(entry, 'summary'):
                content = entry.summary

            # Extract first image URL from HTML content
            img_match = re.search(r'<img[^>]+src="([^"]+)"', content, re.IGNORECASE)
            if img_match:
                image_url = img_match.group(1)

        # Check for specific feedparser image handling
        if not image_url and hasattr(entry, 'image'):
            if hasattr(entry.image, 'href'):
                image_url = entry.image.href

        return image_url

    def _clean_html(self, text: str) -> str:
        if not text:
            return ""

        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)

        # Decode HTML entities
        clean_text = re.sub(r'&nbsp;', ' ', clean_text)
        clean_text = re.sub(r'&amp;', '&', clean_text)
        clean_text = re.sub(r'&lt;', '<', clean_text)
        clean_text = re.sub(r'&gt;', '>', clean_text)
        clean_text = re.sub(r'&quot;', '"', clean_text)
        clean_text = re.sub(r'&#39;', "'", clean_text)

        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""

        # Remove fragments and normalize
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"

        return normalized

    def fetch_feed(self, rss_url: str, max_articles: int = 10, source_name: str = "", default_image_url: str = "") -> List[Dict[str, Any]]:
        self._wait_for_rate_limit()

        try:
            logger.info(f"Fetching RSS feed: {rss_url}")

            # Parse the feed
            feed = feedparser.parse(rss_url)

            # Check for parsing errors
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {rss_url}: {feed.bozo_exception}")

            # Check if feed has entries
            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in feed: {rss_url}")
                return []

            articles = []
            processed_count = 0

            for entry in feed.entries[:max_articles]:
                try:
                    # Extract basic article information
                    title = self._clean_html(getattr(entry, 'title', ''))
                    link = getattr(entry, 'link', '')

                    if not title or not link:
                        continue

                    # Normalize URL
                    normalized_url = self._normalize_url(link)

                    # Extract description
                    description = ''
                    if hasattr(entry, 'content') and entry.content:
                        description = self._clean_html(entry.content[0].value)
                    elif hasattr(entry, 'summary'):
                        description = self._clean_html(entry.summary)
                    elif hasattr(entry, 'description'):
                        description = self._clean_html(entry.description)

                    # Limit description length
                    if len(description) > 500:
                        description = description[:500] + "..."

                    # Extract image URL
                    image_url = self._extract_image_url(entry)

                    # Use default image if no image found
                    if not image_url and default_image_url:
                        image_url = default_image_url

                    # Extract publication date
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            published_date = datetime(*entry.published_parsed[:6])
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid publication date for article: {title}")
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        try:
                            published_date = datetime(*entry.updated_parsed[:6])
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid update date for article: {title}")

                    article = {
                        'title': title,
                        'url': normalized_url,
                        'description': description,
                        'image_url': image_url,
                        'published_date': published_date.isoformat() if published_date else None,
                        'source_name': source_name
                    }

                    articles.append(article)
                    processed_count += 1

                    logger.debug(f"Processed article: {title[:50]}...")

                except Exception as e:
                    logger.error(f"Error processing entry from {rss_url}: {e}")
                    continue

            logger.info(f"Successfully processed {processed_count} articles from {rss_url}")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching {rss_url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching {rss_url}: {e}")
            return []

    def validate_rss_url(self, rss_url: str) -> bool:
        try:
            parsed = urlparse(rss_url)
            return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
        except Exception:
            return False

    def test_feed_connection(self, rss_url: str) -> bool:
        try:
            self._wait_for_rate_limit()
            feed = feedparser.parse(rss_url)
            return hasattr(feed, 'entries') and len(feed.entries) > 0
        except Exception as e:
            logger.error(f"Failed to test feed connection {rss_url}: {e}")
            return False

    def get_feed_info(self, rss_url: str) -> Dict[str, Any]:
        try:
            self._wait_for_rate_limit()
            feed = feedparser.parse(rss_url)

            info = {
                'title': getattr(feed.feed, 'title', 'Unknown Feed'),
                'description': getattr(feed.feed, 'description', ''),
                'link': getattr(feed.feed, 'link', ''),
                'language': getattr(feed.feed, 'language', ''),
                'entries_count': len(feed.entries) if hasattr(feed, 'entries') else 0,
                'last_updated': getattr(feed.feed, 'updated', ''),
                'generator': getattr(feed.feed, 'generator', ''),
                'bozo': feed.bozo if hasattr(feed, 'bozo') else False
            }

            if feed.bozo and hasattr(feed, 'bozo_exception'):
                info['bozo_exception'] = str(feed.bozo_exception)

            return info

        except Exception as e:
            logger.error(f"Failed to get feed info for {rss_url}: {e}")
            return {
                'title': 'Error',
                'description': f'Failed to fetch feed info: {str(e)}',
                'entries_count': 0,
                'bozo': True,
                'bozo_exception': str(e)
            }