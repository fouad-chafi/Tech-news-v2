#!/usr/bin/env python3
import logging
import sys
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from config import Config
from modules.db_manager import DatabaseManager
from modules.rss_fetcher import RSSFetcher
from modules.llm_analyzer import LLMAnalyzer
from modules.category_manager import CategoryManager
from modules.cli_interface import CLIInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tech_news_aggregator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TechNewsAggregator:
    def __init__(self):
        self.cli = CLIInterface()
        self.db_manager = None
        self.rss_fetcher = None
        self.llm_analyzer = None
        self.category_manager = None

    def initialize_system(self) -> bool:
        try:
            # Validate configuration
            if not Config.validate():
                self.cli.show_error("Configuration validation failed. Please check your .env file.")
                return False

            # Initialize database manager
            logger.info("Initializing database connection...")
            self.db_manager = DatabaseManager()

            # Initialize RSS fetcher
            logger.info("Initializing RSS fetcher...")
            self.rss_fetcher = RSSFetcher()

            # Initialize LLM analyzer
            logger.info("Initializing LLM analyzer...")
            self.llm_analyzer = LLMAnalyzer()

            # Initialize category manager
            logger.info("Initializing category manager...")
            self.category_manager = CategoryManager(self.db_manager)

            logger.info("System initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.cli.show_error("Failed to initialize system", e)
            return False

    def test_connections(self) -> bool:
        try:
            # Test database connection
            self.cli.print_separator()
            self.cli.console.print("[cyan]Testing database connection...[/cyan]")
            db_status = self.db_manager.test_connection()

            # Test LLM connection
            self.cli.console.print("[cyan]Testing LLM connection...[/cyan]")
            llm_status = self.llm_analyzer.test_connection()

            return self.cli.show_connection_status(db_status, llm_status)

        except Exception as e:
            logger.error(f"Connection testing failed: {e}")
            self.cli.show_error("Failed to test connections", e)
            return False

    def load_sources_from_file(self) -> Dict[str, Any]:
        try:
            sources_file = Path(__file__).parent / "sources.json"
            if not sources_file.exists():
                self.cli.show_error(f"Sources file not found: {sources_file}")
                return {}

            with open(sources_file, 'r', encoding='utf-8') as f:
                sources_data = json.load(f)

            logger.info(f"Loaded {len(sources_data.get('groups', {}))} source groups from file")
            return sources_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse sources.json: {e}")
            self.cli.show_error("Invalid JSON format in sources.json", e)
            return {}
        except Exception as e:
            logger.error(f"Failed to load sources file: {e}")
            self.cli.show_error("Failed to load sources file", e)
            return {}

    def sync_sources_to_database(self, sources_data: Dict[str, Any]) -> bool:
        try:
            if not sources_data or 'groups' not in sources_data:
                return False

            total_sources = 0
            created_sources = 0

            for group_name, group_data in sources_data['groups'].items():
                group_sources = group_data.get('sources', [])
                total_sources += len(group_sources)

                for source in group_sources:
                    source_data = {
                        'name': source['name'],
                        'rss_url': source['rss_url'],
                        'source_group': group_name,
                        'default_image_url': source.get('default_image_url', ''),
                        'enabled': True,
                        'max_articles_per_fetch': 10
                    }

                    result = self.db_manager.create_source_if_not_exists(source_data)
                    if result:
                        created_sources += 1

            logger.info(f"Synced {created_sources}/{total_sources} sources to database")
            return True

        except Exception as e:
            logger.error(f"Failed to sync sources to database: {e}")
            return False

    def process_articles(self, selected_groups: List[str], max_articles: int) -> Dict[str, Any]:
        results = {
            'sources_processed': 0,
            'articles_found': 0,
            'articles_analyzed': 0,
            'articles_stored': 0,
            'articles_filtered': 0,
            'new_categories': 0,
            'errors': 0
        }

        try:
            # Get enabled sources for selected groups
            enabled_sources = []
            for group in selected_groups:
                group_sources = self.db_manager.get_sources_by_group()
                if group in group_sources:
                    enabled_sources.extend([
                        source for source in group_sources[group]
                        if source.get('enabled', False)
                    ])

            if not enabled_sources:
                self.cli.show_warning("No enabled sources found for selected groups")
                return results

            results['sources_processed'] = len(enabled_sources)

            # Create progress bar
            progress = self.cli.create_progress_bar()

            with progress:
                # Main processing task
                main_task = progress.add_task(
                    f"[bold blue]Processing {len(enabled_sources)} sources...",
                    total=len(enabled_sources)
                )

                # Get existing categories for LLM context
                existing_categories = self.category_manager.get_all_categories()
                initial_category_count = len(existing_categories)

                # Pre-fetch all existing URLs to avoid duplicates
                self.cli.console.print("[cyan]Pre-checking existing articles in database...")
                existing_urls = set()
                try:
                    # Get all existing articles URLs (this is more efficient than checking one by one)
                    all_articles = self.db_manager.client.table("articles").select("url").execute()
                    for article in all_articles.data:
                        existing_urls.add(article.get('url', ''))
                    logger.info(f"Found {len(existing_urls)} existing articles to avoid duplicates")
                except Exception as e:
                    logger.error(f"Failed to fetch existing URLs: {e}")
                    existing_urls = set()

                for i, source in enumerate(enabled_sources):
                    try:
                        source_name = source.get('name', 'Unknown')
                        source_url = source.get('rss_url', '')
                        default_image = source.get('default_image_url', '')

                        # Update progress
                        progress.update(
                            main_task,
                            description=f"[cyan]Processing {source_name}..."
                        )

                        # Fetch articles from RSS feed
                        logger.info(f"Fetching articles from {source_name}")
                        articles = self.rss_fetcher.fetch_feed(
                            source_url,
                            max_articles,
                            source_name,
                            default_image,
                            list(existing_urls)
                        )

                        results['articles_found'] += len(articles)

                        if not articles:
                            logger.info(f"No articles found for {source_name}")
                            continue

                        # Analyze articles with LLM
                        logger.info(f"Analyzing {len(articles)} articles from {source_name}")
                        analyzed_articles = self.llm_analyzer.batch_analyze_articles(
                            articles,
                            existing_categories,
                            delay=0.5  # Delay between LLM requests
                        )

                        results['articles_analyzed'] += len(analyzed_articles)

                        # Store articles in database
                        for article in analyzed_articles:
                            try:
                                # Note: Duplicate check is now done at RSS fetching level for efficiency
                                # logger.debug(f"Processing article: {article['title'][:50]}...")
                                # if self.db_manager.article_exists(article['url']):
                                #     continue

                                # Prepare article data for database
                                article_data = {
                                    'title': article['title'],
                                    'description': article['description'],
                                    'url': article['url'],
                                    'image_url': article['image_url'],
                                    'source_id': source['id'],
                                    'published_date': article.get('published_date'),
                                    'relevance_score': article.get('relevance_score', 3),
                                    'tone': article.get('tone', 'news'),
                                    'filtered': article.get('should_filter', False),
                                    'filter_reason': article.get('filter_reason', '')
                                }

                                # Create article
                                created_article = self.db_manager.create_article(article_data)
                                if created_article:
                                    results['articles_stored'] += 1

                                    # Link to categories if not filtered
                                    if not article.get('should_filter', False):
                                        categories = article.get('categories', [])
                                        if categories:
                                            category_ids = self.category_manager.process_article_categories(categories)
                                            if category_ids:
                                                self.db_manager.link_article_to_categories(
                                                    created_article['id'],
                                                    category_ids
                                                )
                                else:
                                    results['articles_filtered'] += 1

                            except Exception as e:
                                logger.error(f"Error storing article {article.get('title', 'unknown')}: {e}")
                                results['errors'] += 1

                        # Refresh categories cache to get any new ones created by LLM
                        self.category_manager.refresh_cache()
                        existing_categories = self.category_manager.get_all_categories()

                        # Update progress
                        progress.advance(main_task)
                        self.cli.show_source_progress(
                            progress,
                            source_name,
                            len(articles),
                            len(analyzed_articles)
                        )

                    except Exception as e:
                        logger.error(f"Error processing source {source.get('name', 'unknown')}: {e}")
                        results['errors'] += 1
                        progress.advance(main_task)
                        continue

                # Calculate new categories created
                final_category_count = len(self.category_manager.get_all_categories())
                results['new_categories'] = final_category_count - initial_category_count

            return results

        except KeyboardInterrupt:
            self.cli.show_warning("Processing interrupted by user")
            return results
        except Exception as e:
            logger.error(f"Error during article processing: {e}")
            self.cli.show_error("Failed to process articles", e)
            results['errors'] += 1
            return results

    def run_interactive_mode(self) -> None:
        try:
            # Show welcome message
            self.cli.show_welcome()

            # Initialize system
            if not self.initialize_system():
                return

            # Test connections
            if not self.test_connections():
                return

            # Load sources
            sources_data = self.load_sources_from_file()
            if not sources_data:
                return

            # Sync sources to database
            if not self.sync_sources_to_database(sources_data):
                return

            # Get sources from database
            sources_by_group = self.db_manager.get_sources_by_group()
            if not sources_by_group:
                self.cli.show_warning("No sources found in database")
                return

            # Show available source groups
            self.cli.show_sources_by_group(sources_by_group)

            # Select source groups
            selected_groups = self.cli.select_source_groups(sources_by_group)
            if not selected_groups:
                self.cli.show_warning("No source groups selected")
                return

            # Configure max articles
            max_articles = self.cli.configure_max_articles()

            # Count total sources to be processed
            total_sources = 0
            for group in selected_groups:
                if group in sources_by_group:
                    total_sources += len([s for s in sources_by_group[group] if s.get('enabled', False)])

            if total_sources == 0:
                self.cli.show_warning("No enabled sources in selected groups")
                return

            # Show processing configuration
            self.cli.show_processing_start(selected_groups, total_sources, max_articles)

            # Confirm processing
            if not self.cli.confirm_action("Start processing?"):
                self.cli.show_warning("Processing cancelled by user")
                return

            # Process articles
            self.cli.print_separator()
            self.cli.console.print("[bold cyan]Starting article processing...[/bold cyan]")
            self.cli.print_separator()

            results = self.process_articles(selected_groups, max_articles)

            # Show results
            self.cli.print_separator()
            self.cli.show_processing_results(results)

            # Get final statistics
            final_stats = self.db_manager.get_articles_count()
            self.cli.console.print(f"[bold green]Database Statistics:[/bold green]")
            self.cli.console.print(f"Total articles in database: {final_stats.get('total', 0)}")
            self.cli.console.print(f"Active articles: {final_stats.get('active', 0)}")
            self.cli.console.print(f"Filtered articles: {final_stats.get('filtered', 0)}")

        except KeyboardInterrupt:
            self.cli.show_warning("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.cli.show_error("Application error", e)

    def run(self) -> None:
        try:
            logger.info("Starting Tech News Aggregator")
            self.run_interactive_mode()
            logger.info("Tech News Aggregator finished")

        except Exception as e:
            logger.error(f"Application failed to start: {e}")
            self.cli.show_error("Application failed to start", e)
        finally:
            self.cli.console.print("\n[bold cyan]Thank you for using Tech News Aggregator![/bold cyan]")

def main():
    aggregator = TechNewsAggregator()
    aggregator.run()

if __name__ == "__main__":
    main()