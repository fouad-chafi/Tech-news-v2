import logging
import time
import requests
import json
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

    def _is_generic_description(self, text: str) -> bool:
        """Check if description is too generic to be useful."""
        if not text or len(text.strip()) < 20:
            return True

        text_lower = text.lower().strip()
        generic_patterns = [
            r'^a blog post by',
            r'^read more',
            r'^click here',
            r'^learn more',
            r'^find out',
            r'^this article',
            r'^in this post',
            r'^continue reading'
        ]

        for pattern in generic_patterns:
            if re.match(pattern, text_lower):
                return True

        # Check if it's just the title repeated
        if len(text_lower) < 50:  # Very short descriptions are often generic
            return True

        return False

    def _should_fetch_webpage(self, entry, current_description: str, source_name: str = "") -> bool:
        """Determine if webpage fetching is warranted."""
        if current_description and not self._is_generic_description(current_description):
            return False

        # Only fetch webpage for articles from reputable sources
        if hasattr(entry, 'link') and entry.link:
            domain = urlparse(entry.link).netloc.lower()
            reputable_domains = [
                'huggingface.co', 'openai.com', 'deepmind.google',
                'anthropic.com', 'google.ai', 'microsoft.com',
                'techcrunch.com', 'arstechnica.com', 'wired.com'
            ]
            return any(domain.endswith(reputable) for reputable in reputable_domains)

        return False

    def _fetch_webpage_description(self, url: str) -> str:
        """Fetch webpage description as last resort, with improved logic."""
        try:
            response = self.session.get(url, timeout=5)  # Shorter timeout for better performance
            if response.status_code != 200:
                logger.debug(f"Failed to fetch webpage {url}: {response.status_code}")
                return ""

            content = response.text[:8000]  # Limit content size

            # Priority: meta description → og:description → first meaningful paragraph
            desc_patterns = [
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
                r'<meta[^>]+property=["\']twitter:description["\'][^>]+content=["\']([^"\']+)["\']',
                r'<article[^>]*>.*?<p[^>]*>(.*?)</p>',  # First paragraph in article
                r'<p[^>]*>(.*?)</p>'  # Any paragraph as fallback
            ]

            for pattern in desc_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    desc = self._clean_html(match.group(1))
                    if not self._is_generic_description(desc):
                        return desc

            return ""

        except Exception as e:
            logger.debug(f"Error fetching webpage description for {url}: {e}")
            return ""

    def fetch_feed(self, rss_url: str, max_articles: int = 10, source_name: str = "", default_image_url: str = "", existing_urls: List[str] = None) -> List[Dict[str, Any]]:
        self._wait_for_rate_limit()

        # Initialize existing URLs set for quick lookup
        existing_urls_set = set(existing_urls) if existing_urls else set()

        try:
            logger.info(f"Fetching RSS feed: {rss_url}")
            if existing_urls_set:
                logger.info(f"Filtering {len(existing_urls_set)} known URLs")

            # Check if this is a Reddit JSON feed
            if '/r/' in rss_url and rss_url.endswith('.json'):
                return self._fetch_reddit_json(rss_url, max_articles, source_name, default_image_url, existing_urls_set)

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

                    # Early filtering: skip if URL already exists in database
                    if normalized_url in existing_urls_set:
                        logger.debug(f"Skipping existing URL: {normalized_url}")
                        continue

                    # Enhanced description extraction following RSS standards
                    description = ''
                    description_source = 'none'

                    # Try content field first (most detailed, Atom standard)
                    if hasattr(entry, 'content') and entry.content:
                        description = self._clean_html(entry.content[0].value)
                        if description and not self._is_generic_description(description):
                            description_source = 'content'

                    # Try summary field (common in RSS/Atom)
                    if not description or self._is_generic_description(description):
                        if hasattr(entry, 'summary') and entry.summary:
                            summary_desc = self._clean_html(entry.summary)
                            if summary_desc and not self._is_generic_description(summary_desc):
                                description = summary_desc
                                description_source = 'summary'

                    # Try description field (RSS 2.0 standard)
                    if not description or self._is_generic_description(description):
                        if hasattr(entry, 'description') and entry.description:
                            rss_desc = self._clean_html(entry.description)
                            if rss_desc and not self._is_generic_description(rss_desc):
                                description = rss_desc
                                description_source = 'description'

                    # Try subtitle field (Atom feeds)
                    if not description or self._is_generic_description(description):
                        if hasattr(entry, 'subtitle') and entry.subtitle:
                            subtitle_desc = self._clean_html(entry.subtitle)
                            if subtitle_desc and not self._is_generic_description(subtitle_desc):
                                description = subtitle_desc
                                description_source = 'subtitle'

                    # Check for structured metadata (categories, author)
                    if not description or self._is_generic_description(description):
                        if hasattr(entry, 'tags') and entry.tags:
                            categories = [tag.term if hasattr(tag, 'term') else str(tag) for tag in entry.tags[:3]]
                            if categories:
                                description = f"Topics: {', '.join(categories)}"
                                description_source = 'metadata'

                    # Intelligent webpage fetching only for reputable sources
                    if not description or self._is_generic_description(description):
                        if self._should_fetch_webpage(entry, description, source_name):
                            webpage_desc = self._fetch_webpage_description(entry.link)
                            if webpage_desc:
                                description = webpage_desc
                                description_source = 'webpage'

                    # Final fallback with meaningful description
                    if not description or self._is_generic_description(description):
                        description = f"Article from {source_name}" if source_name else "Tech article"
                        description_source = 'fallback'

                    # Log description source for debugging
                    logger.debug(f"Description source for '{title[:50]}...': {description_source}")

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

    def _fetch_reddit_json(self, rss_url: str, max_articles: int, source_name: str, default_image_url: str, existing_urls_set: set) -> List[Dict[str, Any]]:
        """Fetch and parse Reddit JSON feed"""
        try:
            # Add limit parameter if not present
            if '?' not in rss_url:
                fetch_url = f"{rss_url}?limit={max_articles}"
            else:
                fetch_url = rss_url

            # Use custom headers for Reddit
            headers = {
                'User-Agent': 'TechNewsAggregator/1.0 (RSS Fetcher)',
                'Accept': 'application/json'
            }

            response = self.session.get(fetch_url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            articles = []
            processed_count = 0

            # Reddit JSON structure: {"kind": "Listing", "data": {"children": [...]}}
            if 'data' not in data or 'children' not in data['data']:
                logger.warning(f"Invalid Reddit JSON structure for {rss_url}")
                return []

            for item in data['data']['children'][:max_articles]:
                try:
                    if item.get('kind') != 't3':  # t3 = post
                        continue

                    post_data = item.get('data', {})
                    title = self._clean_html(post_data.get('title', ''))
                    url = post_data.get('url', '')

                    if not title or not url:
                        continue

                    # Normalize URL
                    normalized_url = self._normalize_url(url)

                    # Early filtering: skip if URL already exists
                    if normalized_url in existing_urls_set:
                        logger.debug(f"Skipping existing URL: {normalized_url}")
                        continue

                    # Extract description
                    description = ''
                    if post_data.get('selftext'):
                        description = self._clean_html(post_data['selftext'])
                        # Limit description length
                        if len(description) > 500:
                            description = description[:500] + "..."

                    # If no self-text, use a generic description
                    if not description:
                        description = f"Discussion from {source_name} on Reddit"

                    # Extract image URL
                    image_url = None
                    if post_data.get('thumbnail') and post_data['thumbnail'] not in ['self', 'default', 'nsfw']:
                        image_url = post_data['thumbnail']
                    elif post_data.get('preview') and post_data['preview'].get('images'):
                        # Use the first preview image
                        preview = post_data['preview']['images'][0]
                        if 'source' in preview and 'url' in preview['source']:
                            image_url = preview['source']['url']

                    # Use default image if no image found
                    if not image_url and default_image_url:
                        image_url = default_image_url

                    # Extract publication date
                    published_date = None
                    if post_data.get('created_utc'):
                        try:
                            import datetime
                            timestamp = post_data['created_utc']
                            published_date = datetime.datetime.fromtimestamp(timestamp)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid timestamp for Reddit post: {title}")

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

                    logger.debug(f"Processed Reddit article: {title[:50]}...")

                except Exception as e:
                    logger.error(f"Error processing Reddit item from {rss_url}: {e}")
                    continue

            logger.info(f"Successfully processed {processed_count} Reddit articles from {rss_url}")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching Reddit JSON {rss_url}: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for Reddit {rss_url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Reddit JSON {rss_url}: {e}")
            return []

    def get_feed_info(self, rss_url: str) -> Dict[str, Any]:
        try:
            self._wait_for_rate_limit()

            # Check if this is a Reddit JSON feed
            if '/r/' in rss_url and rss_url.endswith('.json'):
                return self._get_reddit_feed_info(rss_url)

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

    def _get_reddit_feed_info(self, rss_url: str) -> Dict[str, Any]:
        """Get info for Reddit JSON feed"""
        try:
            headers = {
                'User-Agent': 'TechNewsAggregator/1.0 (RSS Fetcher)',
                'Accept': 'application/json'
            }

            response = self.session.get(rss_url + '?limit=1', headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data:
                return {
                    'title': 'Reddit Feed',
                    'description': 'Reddit JSON feed',
                    'entries_count': 0,
                    'bozo': False
                }

            subreddit = data['data'].get('children', [{}])[0].get('data', {}).get('subreddit', 'Unknown')

            return {
                'title': f'r/{subreddit}',
                'description': f'Reddit subreddit: {subreddit}',
                'link': f"https://www.reddit.com/r/{subreddit}",
                'language': 'en',
                'entries_count': data['data'].get('dist', 0),
                'last_updated': '',
                'generator': 'Reddit API',
                'bozo': False
            }

        except Exception as e:
            logger.error(f"Failed to get Reddit feed info for {rss_url}: {e}")
            return {
                'title': 'Reddit Feed Error',
                'description': f'Failed to fetch Reddit feed info: {str(e)}',
                'entries_count': 0,
                'bozo': True,
                'bozo_exception': str(e)
            }