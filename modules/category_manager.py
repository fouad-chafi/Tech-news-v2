import logging
from typing import List, Dict, Set, Optional
from modules.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class CategoryManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.category_cache: Dict[str, str] = {}  # name -> id mapping
        self.category_set: Set[str] = set()  # For quick existence checks
        self._load_categories()

    def _load_categories(self) -> None:
        try:
            logger.info("Loading existing categories from database")
            categories = self.db_manager.get_all_categories()

            self.category_cache.clear()
            self.category_set.clear()

            for category in categories:
                name = category.get('name', '').upper()
                category_id = category.get('id', '')

                if name and category_id:
                    self.category_cache[name] = category_id
                    self.category_set.add(name)

            logger.info(f"Loaded {len(self.category_cache)} categories into cache")

        except Exception as e:
            logger.error(f"Failed to load categories from database: {e}")

    def refresh_cache(self) -> None:
        logger.info("Refreshing category cache")
        self._load_categories()

    def get_all_categories(self) -> List[str]:
        return sorted(list(self.category_set))

    def category_exists(self, category_name: str) -> bool:
        if not category_name:
            return False
        return category_name.upper() in self.category_set

    def get_category_id(self, category_name: str) -> Optional[str]:
        if not category_name:
            return None
        return self.category_cache.get(category_name.upper())

    def create_category(self, category_name: str) -> Optional[str]:
        if not category_name or not category_name.strip():
            logger.warning("Attempted to create empty category")
            return None

        normalized_name = category_name.strip().upper()

        if self.category_exists(normalized_name):
            logger.info(f"Category '{normalized_name}' already exists")
            return self.get_category_id(normalized_name)

        try:
            logger.info(f"Creating new category: {normalized_name}")

            category_data = self.db_manager.create_category(normalized_name)

            if category_data and category_data.get('id'):
                category_id = category_data['id']
                self.category_cache[normalized_name] = category_id
                self.category_set.add(normalized_name)
                logger.info(f"Successfully created category '{normalized_name}' with ID: {category_id}")
                return category_id
            else:
                logger.error(f"Failed to create category '{normalized_name}': No ID returned")
                return None

        except Exception as e:
            logger.error(f"Error creating category '{normalized_name}': {e}")
            return None

    def get_or_create_categories(self, category_names: List[str]) -> List[str]:
        category_ids = []

        for name in category_names:
            if not name or not name.strip():
                continue

            normalized_name = name.strip().upper()

            # Check cache first
            if self.category_exists(normalized_name):
                category_id = self.get_category_id(normalized_name)
                if category_id:
                    category_ids.append(category_id)
                    continue

            # Create new category
            category_id = self.create_category(normalized_name)
            if category_id:
                category_ids.append(category_id)
            else:
                logger.warning(f"Failed to get or create category: {normalized_name}")

        return category_ids

    def normalize_category_name(self, category_name: str) -> str:
        if not category_name:
            return ""

        # Basic normalization
        normalized = category_name.strip().upper()

        # Common category mappings for consistency
        category_mappings = {
            'AI': 'AI',
            'ARTIFICIAL INTELLIGENCE': 'AI',
            'MACHINE LEARNING': 'AI',
            'ML': 'AI',
            'DEEP LEARNING': 'AI',
            'NEURAL NETWORKS': 'AI',
            'WEB': 'WEB',
            'WEB DEVELOPMENT': 'WEB',
            'FRONTEND': 'WEB',
            'BACKEND': 'WEB',
            'FULL STACK': 'WEB',
            'DEV': 'DEV',
            'DEVELOPMENT': 'DEV',
            'PROGRAMMING': 'DEV',
            'CODING': 'DEV',
            'SOFTWARE': 'DEV',
            'MOBILE': 'MOBILE',
            'MOBILE DEVELOPMENT': 'MOBILE',
            'IOS': 'MOBILE',
            'ANDROID': 'MOBILE',
            'CLOUD': 'CLOUD',
            'CLOUD COMPUTING': 'CLOUD',
            'AWS': 'CLOUD',
            'AZURE': 'CLOUD',
            'GCP': 'CLOUD',
            'DEVOPS': 'DEVOPS',
            'DEV OPS': 'DEVOPS',
            'CYBERSECURITY': 'CYBERSECURITY',
            'SECURITY': 'CYBERSECURITY',
            'INFOSEC': 'CYBERSECURITY',
            'DATA': 'DATA',
            'DATA SCIENCE': 'DATA',
            'BIG DATA': 'DATA',
            'ANALYTICS': 'DATA',
            'STARTUP': 'STARTUPS',
            'STARTUPS': 'STARTUPS',
            'BUSINESS': 'STARTUPS',
            'REDDIT': 'REDDIT',
            'NEWS': 'NEWS',
            'TECH NEWS': 'NEWS',
            'GENERAL': 'GENERAL',
            'OTHER': 'GENERAL',
        }

        return category_mappings.get(normalized, normalized)

    def process_article_categories(self, categories: List[str]) -> List[str]:
        if not categories:
            return [self.create_category('GENERAL')] or []

        processed_categories = []
        normalized_names = set()

        for cat in categories:
            if not cat:
                continue

            normalized = self.normalize_category_name(cat)

            # Skip duplicates
            if normalized in normalized_names:
                continue

            normalized_names.add(normalized)

            # Create category if it doesn't exist
            if not self.category_exists(normalized):
                self.create_category(normalized)

            # Get the category ID
            category_id = self.get_category_id(normalized)
            if category_id:
                processed_categories.append(category_id)

        # If no valid categories found, add GENERAL
        if not processed_categories:
            general_id = self.create_category('GENERAL')
            if general_id:
                processed_categories.append(general_id)

        return processed_categories

    def get_category_stats(self) -> Dict[str, int]:
        try:
            # This would require a more complex query to count articles per category
            # For now, return basic stats
            return {
                'total_categories': len(self.category_cache),
                'cached_categories': len(self.category_set)
            }
        except Exception as e:
            logger.error(f"Failed to get category stats: {e}")
            return {'total_categories': 0, 'cached_categories': 0}

    def cleanup_unused_categories(self) -> int:
        logger.warning("Category cleanup not implemented yet")
        return 0

    def import_categories_from_list(self, category_list: List[str]) -> Dict[str, int]:
        stats = {
            'total': len(category_list),
            'created': 0,
            'existing': 0,
            'errors': 0
        }

        for category_name in category_list:
            if not category_name or not category_name.strip():
                stats['errors'] += 1
                continue

            normalized_name = self.normalize_category_name(category_name.strip())

            if self.category_exists(normalized_name):
                stats['existing'] += 1
            else:
                category_id = self.create_category(normalized_name)
                if category_id:
                    stats['created'] += 1
                else:
                    stats['errors'] += 1

        logger.info(f"Category import completed: {stats}")
        return stats