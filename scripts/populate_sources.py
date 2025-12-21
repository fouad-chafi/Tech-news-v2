#!/usr/bin/env python3
"""
Sources Population Script

This script populates the database with RSS sources from sources.json file.
It creates source records and organizes them by groups.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from modules.db_manager import DatabaseManager
from config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_sources_file():
    """Load sources from sources.json file."""
    try:
        sources_file = Path(__file__).parent.parent / "sources.json"

        if not sources_file.exists():
            logger.error(f"Sources file not found: {sources_file}")
            return None

        with open(sources_file, 'r', encoding='utf-8') as f:
            sources_data = json.load(f)

        logger.info(f"Loaded sources data from {sources_file}")
        return sources_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse sources.json: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load sources file: {e}")
        return None

def populate_sources():
    """Populate the database with sources from sources.json."""
    try:
        # Load sources data
        sources_data = load_sources_file()
        if not sources_data or 'groups' not in sources_data:
            logger.error("Invalid sources data structure")
            return False

        db_manager = DatabaseManager()

        # Get statistics
        total_sources = 0
        created_sources = 0
        updated_sources = 0
        error_sources = 0

        logger.info("Starting sources population...")

        # Process each group
        for group_name, group_data in sources_data['groups'].items():
            group_display_name = group_data.get('name', group_name)
            group_sources = group_data.get('sources', [])

            logger.info(f"Processing group: {group_display_name} ({len(group_sources)} sources)")

            for source in group_sources:
                total_sources += 1

                # Validate source data
                if not all(key in source for key in ['name', 'rss_url']):
                    logger.warning(f"Skipping invalid source: missing required fields")
                    error_sources += 1
                    continue

                # Prepare source data
                source_data = {
                    'name': source['name'],
                    'rss_url': source['rss_url'],
                    'source_group': group_name,
                    'default_image_url': source.get('default_image_url', ''),
                    'enabled': True,
                    'max_articles_per_fetch': 10
                }

                try:
                    # Create or update source
                    result = db_manager.create_source_if_not_exists(source_data)

                    if result:
                        if result.get('created', False):  # If the source was newly created
                            created_sources += 1
                            logger.info(f"Created source: {source['name']}")
                        else:  # If the source already existed
                            updated_sources += 1
                            logger.info(f"Source already exists: {source['name']}")
                    else:
                        logger.error(f"Failed to create source: {source['name']}")
                        error_sources += 1

                except Exception as e:
                    logger.error(f"Error processing source {source['name']}: {e}")
                    error_sources += 1

        # Log results
        logger.info(f"Sources population completed:")
        logger.info(f"  Total sources processed: {total_sources}")
        logger.info(f"  Sources created: {created_sources}")
        logger.info(f"  Sources already existed: {updated_sources}")
        logger.info(f"  Sources with errors: {error_sources}")

        return True

    except Exception as e:
        logger.error(f"Failed to populate sources: {e}")
        return False

def validate_sources():
    """Validate that sources are properly populated and accessible."""
    try:
        db_manager = DatabaseManager()

        logger.info("Validating sources population...")

        # Get all sources
        sources_by_group = db_manager.get_sources_by_group()

        if not sources_by_group:
            logger.error("No sources found in database")
            return False

        total_sources = sum(len(sources) for sources in sources_by_group.values())
        enabled_sources = sum(
            len([s for s in sources if s.get('enabled', False)])
            for sources in sources_by_group.values()
        )

        logger.info(f"Found {total_sources} total sources in {len(sources_by_group)} groups")
        logger.info(f"Enabled sources: {enabled_sources}")

        # Display sources by group
        for group_name, sources in sources_by_group.items():
            enabled_count = sum(1 for s in sources if s.get('enabled', False))
            logger.info(f"  {group_name}: {enabled_count}/{len(sources)} enabled")

        # Test a few RSS URLs
        logger.info("Testing RSS feed accessibility...")
        from modules.rss_fetcher import RSSFetcher
        rss_fetcher = RSSFetcher()

        test_count = 0
        success_count = 0

        for group_name, sources in sources_by_group.items():
            for source in sources[:2]:  # Test first 2 sources per group
                test_count += 1
                try:
                    if rss_fetcher.test_feed_connection(source['rss_url']):
                        success_count += 1
                        logger.info(f"  ✓ {source['name']} - Accessible")
                    else:
                        logger.warning(f"  ✗ {source['name']} - Not accessible")
                except Exception as e:
                    logger.warning(f"  ✗ {source['name']} - Error: {e}")

        logger.info(f"RSS connectivity test: {success_count}/{test_count} feeds accessible")

        return True

    except Exception as e:
        logger.error(f"Source validation failed: {e}")
        return False

def display_statistics():
    """Display database statistics after population."""
    try:
        db_manager = DatabaseManager()

        logger.info("Database Statistics:")

        # Sources by group
        sources_by_group = db_manager.get_sources_by_group()
        for group_name, sources in sources_by_group.items():
            enabled_count = sum(1 for s in sources if s.get('enabled', False))
            total_count = len(sources)
            logger.info(f"  {group_name}: {enabled_count}/{total_count} enabled")

        # Categories
        categories = db_manager.get_all_categories()
        logger.info(f"  Total categories: {len(categories)}")

        # Articles
        articles_stats = db_manager.get_articles_count()
        logger.info(f"  Total articles: {articles_stats.get('total', 0)}")
        logger.info(f"  Active articles: {articles_stats.get('active', 0)}")
        logger.info(f"  Filtered articles: {articles_stats.get('filtered', 0)}")

        return True

    except Exception as e:
        logger.error(f"Failed to display statistics: {e}")
        return False

def show_menu():
    """Display interactive menu."""
    print("\n" + "=" * 50)
    print("SOURCES MANAGEMENT MENU")
    print("=" * 50)
    print("1. Show current sources in database")
    print("2. Add sources from sources.json")
    print("3. Test RSS feed connectivity")
    print("4. Clear all sources from database")
    print("5. Exit")
    print("=" * 50)

def show_current_sources():
    """Show current sources in database."""
    try:
        db_manager = DatabaseManager()
        sources_by_group = db_manager.get_sources_by_group()

        if not sources_by_group:
            print("No sources found in database.")
            return

        print("\nCurrent Sources in Database:")
        print("-" * 40)

        for group_name, sources in sources_by_group.items():
            enabled_count = sum(1 for s in sources if s.get('enabled', False))
            total_count = len(sources)
            print(f"\n{group_name} ({enabled_count}/{total_count} enabled):")

            for source in sources:
                status = "✓" if source.get('enabled', False) else "✗"
                print(f"  {status} {source['name']}")

    except Exception as e:
        print(f"Error retrieving sources: {e}")

def test_rss_connectivity():
    """Test RSS feed connectivity for sources in database."""
    try:
        db_manager = DatabaseManager()
        sources_by_group = db_manager.get_sources_by_group()

        if not sources_by_group:
            print("No sources found in database.")
            return

        print("\nTesting RSS Feed Connectivity:")
        print("-" * 40)

        from modules.rss_fetcher import RSSFetcher
        rss_fetcher = RSSFetcher()

        total_tested = 0
        total_success = 0

        for group_name, sources in sources_by_group.items():
            print(f"\n{group_name}:")

            for source in sources[:3]:  # Test only first 3 per group
                total_tested += 1
                try:
                    if rss_fetcher.test_feed_connection(source['rss_url']):
                        print(f"  ✓ {source['name']}: ACCESSIBLE")
                        total_success += 1
                    else:
                        print(f"  ✗ {source['name']}: NOT ACCESSIBLE")
                except Exception as e:
                    print(f"  ✗ {source['name']}: ERROR - {e}")

        print(f"\nSummary: {total_success}/{total_tested} feeds accessible")

    except Exception as e:
        print(f"Error testing connectivity: {e}")

def clear_sources():
    """Clear all sources from database."""
    try:
        from rich.prompt import Confirm
        if not Confirm.ask("Are you sure you want to delete ALL sources from database?"):
            print("Operation cancelled.")
            return

        db_manager = DatabaseManager()

        # This would need to be implemented in db_manager
        # For now, just show that this would clear sources
        print("Source clearing functionality would be implemented here.")
        print("This requires adding a delete_all_sources method to DatabaseManager.")

    except Exception as e:
        print(f"Error clearing sources: {e}")

def main():
    """Main interactive function."""
    print("=" * 60)
    print("Tech News Aggregator - Sources Management")
    print("=" * 60)

    # Check configuration
    if not Config.validate():
        print("ERROR: Configuration validation failed. Please check your .env file.")
        return False

    # Check database connection
    try:
        db_manager = DatabaseManager()
        if not db_manager.test_connection():
            print("ERROR: Database connection failed. Please check your Supabase configuration.")
            return False
        print("Database connection: OK")
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

    # Load sources configuration
    sources_data = load_sources_file()
    if not sources_data:
        print("ERROR: Failed to load sources configuration.")
        return False

    group_count = len(sources_data.get('groups', {}))
    source_count = sum(len(group.get('sources', [])) for group in sources_data.get('groups', {}).values())
    print(f"Sources configuration loaded: {source_count} sources in {group_count} groups")

    # Interactive menu
    while True:
        show_menu()

        try:
            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                show_current_sources()
            elif choice == "2":
                print("\nAdding sources from sources.json...")
                if populate_sources():
                    print("Sources added successfully!")
                else:
                    print("Failed to add sources.")
            elif choice == "3":
                test_rss_connectivity()
            elif choice == "4":
                clear_sources()
            elif choice == "5":
                print("Exiting sources management...")
                break
            else:
                print("Invalid choice. Please enter 1-5.")

        except KeyboardInterrupt:
            print("\nExiting sources management...")
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nNext step:")
    print("Run: python main.py")
    print("\nYour Tech News Aggregator is ready to use!")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nPopulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nPopulation failed with error: {e}")
        sys.exit(1)