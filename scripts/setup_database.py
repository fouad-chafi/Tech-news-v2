#!/usr/bin/env python3
"""
Database Setup Script

This script sets up the initial database schema for the Tech News Aggregator.
It creates the necessary tables, indexes, and initial data.
"""

import sys
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

def create_database_schema():
    """
    Creates the database schema using SQL statements.
    Note: This script assumes the database exists and uuid-ossp extension is enabled.
    """
    schema_statements = [
        # Create categories table
        """
        CREATE TABLE IF NOT EXISTS categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        """,

        # Create sources table
        """
        CREATE TABLE IF NOT EXISTS sources (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL UNIQUE,
            rss_url TEXT NOT NULL,
            source_group TEXT,
            default_image_url TEXT,
            enabled BOOLEAN DEFAULT true,
            max_articles_per_fetch INTEGER DEFAULT 10,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        """,

        # Create articles table
        """
        CREATE TABLE IF NOT EXISTS articles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title TEXT NOT NULL,
            description TEXT,
            url TEXT NOT NULL UNIQUE,
            image_url TEXT,
            source_id UUID REFERENCES sources(id),
            published_date TIMESTAMP WITH TIME ZONE,
            relevance_score INTEGER CHECK (relevance_score >= 1 AND relevance_score <= 5),
            tone TEXT CHECK (tone IN ('informative', 'promotional', 'opinion', 'technical', 'news')),
            filtered BOOLEAN DEFAULT false,
            filter_reason TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );
        """,

        # Create article_categories junction table
        """
        CREATE TABLE IF NOT EXISTS article_categories (
            article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
            category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
            PRIMARY KEY (article_id, category_id)
        );
        """,

        # Create indexes
        """
        CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles(published_date DESC);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_articles_relevance_score ON articles(relevance_score DESC);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_articles_filtered ON articles(filtered);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_article_categories_article_id ON article_categories(article_id);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_article_categories_category_id ON article_categories(category_id);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_sources_enabled ON sources(enabled);
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_sources_group ON sources(source_group);
        """
    ]

    try:
        db_manager = DatabaseManager()

        # Check if tables already exist by trying to select from them
        logger.info("Checking existing database schema...")

        try:
            # Test if tables exist by running a simple query
            response = db_manager.client.table("sources").select("id").limit(1).execute()
            logger.info("Database schema already exists")
            return True
        except Exception as e:
            logger.info(f"Schema check failed: {e}")
            logger.info("Creating database schema...")

        # Create schema using direct SQL (this requires service role permissions)
        # For Supabase, you would typically create tables via the dashboard
        # or use the SQL editor in the Supabase dashboard

        logger.warning("Please create the following tables manually in Supabase dashboard:")
        logger.warning("1. Go to Supabase dashboard -> SQL Editor")
        logger.warning("2. Run the following SQL statements:")

        for statement in schema_statements:
            logger.warning(f"\n{statement}\n")

        logger.warning("After creating tables, run this script again to verify setup")

        # Test connection
        if db_manager.test_connection():
            logger.info("Database connection successful")

            # Try to create a test category to verify schema works
            try:
                test_category = db_manager.create_category("TEST")
                if test_category:
                    logger.info("Schema verification successful")
                    # Clean up test category
                    db_manager.client.table("categories").delete().eq("name", "TEST").execute()
                    logger.info("Test category cleaned up")
                    return True
                else:
                    logger.error("Schema verification failed - could not create test category")
                    return False
            except Exception as e:
                logger.error(f"Schema verification failed: {e}")
                return False
        else:
            logger.error("Database connection failed")
            return False

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def insert_initial_categories():
    """Insert initial categories into the database."""
    initial_categories = [
        "AI",
        "WEB",
        "DEV",
        "MOBILE",
        "CLOUD",
        "DEVOPS",
        "CYBERSECURITY",
        "DATA",
        "STARTUPS",
        "REDDIT",
        "NEWS",
        "GENERAL"
    ]

    try:
        db_manager = DatabaseManager()
        created_count = 0

        logger.info("Inserting initial categories...")
        for category_name in initial_categories:
            result = db_manager.create_category(category_name)
            if result:
                created_count += 1
                logger.info(f"Created category: {category_name}")
            else:
                logger.info(f"Category already exists: {category_name}")

        logger.info(f"Inserted {created_count} initial categories")
        return True

    except Exception as e:
        logger.error(f"Failed to insert initial categories: {e}")
        return False

def verify_setup():
    """Verify that the database setup is complete and working."""
    try:
        db_manager = DatabaseManager()

        logger.info("Verifying database setup...")

        # Test table existence
        tables_to_check = ["categories", "sources", "articles", "article_categories"]
        for table in tables_to_check:
            try:
                response = db_manager.client.table(table).select("id").limit(1).execute()
                logger.info(f"Table '{table}' exists and is accessible")
            except Exception as e:
                logger.error(f"Table '{table}' is not accessible: {e}")
                return False

        # Test basic operations
        logger.info("Testing basic database operations...")

        # Get categories count
        categories = db_manager.get_all_categories()
        logger.info(f"Found {len(categories)} categories in database")

        # Get articles count
        articles_count = db_manager.get_articles_count()
        logger.info(f"Total articles: {articles_count.get('total', 0)}")

        logger.info("Database setup verification completed successfully")
        return True

    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Tech News Aggregator - Database Setup")
    print("=" * 60)

    # Check configuration
    if not Config.validate():
        print("ERROR: Configuration validation failed. Please check your .env file.")
        return False

    print("\n1. Checking database configuration...")
    try:
        db_manager = DatabaseManager()
        if not db_manager.test_connection():
            print("ERROR: Database connection failed. Please check your Supabase configuration.")
            return False
        print("Database connection: OK")
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

    print("\n2. Setting up database schema...")
    if not create_database_schema():
        print("ERROR: Database schema setup failed.")
        return False

    print("\n3. Inserting initial categories...")
    if not insert_initial_categories():
        print("ERROR: Failed to insert initial categories.")
        return False

    print("\n4. Verifying setup...")
    if not verify_setup():
        print("ERROR: Setup verification failed.")
        return False

    print("\n" + "=" * 60)
    print("Database setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python scripts/populate_sources.py")
    print("2. Run: python main.py")
    print("\nYour Tech News Aggregator is ready to use!")

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nSetup failed with error: {e}")
        sys.exit(1)