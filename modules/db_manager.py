import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: Optional[Client] = None
        self._connect()

    def _connect(self) -> None:
        try:
            supabase_config = Config.get_supabase_config()
            self.client = create_client(
                supabase_config["url"],
                supabase_config["service_key"]
            )
            logger.info("Connected to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def test_connection(self) -> bool:
        try:
            response = self.client.table("sources").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.table("sources").select("*").eq("enabled", True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get enabled sources: {e}")
            return []

    def get_all_categories(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.table("categories").select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table("categories").select("*").eq("name", name).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get category by name {name}: {e}")
            return None

    def create_category(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table("categories").insert({"name": name}).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to create category {name}: {e}")
            return None

    def article_exists(self, url: str) -> bool:
        try:
            response = self.client.table("articles").select("id").eq("url", url).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to check if article exists {url}: {e}")
            return False

    def create_article(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table("articles").insert(article_data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to create article: {e}")
            return None

    def link_article_to_categories(self, article_id: str, category_ids: List[str]) -> bool:
        try:
            links = [{"article_id": article_id, "category_id": cat_id} for cat_id in category_ids]
            response = self.client.table("article_categories").insert(links).execute()
            return len(response.data) == len(category_ids)
        except Exception as e:
            logger.error(f"Failed to link article {article_id} to categories: {e}")
            return False

    def get_sources_by_group(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            response = self.client.table("sources").select("*").execute()
            grouped = {}
            for source in response.data:
                group = source.get("source_group", "OTHER")
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(source)
            return grouped
        except Exception as e:
            logger.error(f"Failed to get sources by group: {e}")
            return {}

    def update_source_status(self, source_id: str, enabled: bool) -> bool:
        try:
            response = self.client.table("sources").update({"enabled": enabled}).eq("id", source_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to update source status {source_id}: {e}")
            return False

    def update_source_max_articles(self, source_id: str, max_articles: int) -> bool:
        try:
            response = self.client.table("sources").update({"max_articles_per_fetch": max_articles}).eq("id", source_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to update source max articles {source_id}: {e}")
            return False

    def get_articles_count(self) -> Dict[str, int]:
        try:
            total_response = self.client.table("articles").select("id", count="exact").execute()
            filtered_response = self.client.table("articles").select("id", count="exact").eq("filtered", True).execute()

            return {
                "total": total_response.count or 0,
                "filtered": filtered_response.count or 0,
                "active": (total_response.count or 0) - (filtered_response.count or 0)
            }
        except Exception as e:
            logger.error(f"Failed to get articles count: {e}")
            return {"total": 0, "filtered": 0, "active": 0}

    def create_source_if_not_exists(self, source_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            existing = self.client.table("sources").select("id").eq("name", source_data["name"]).execute()
            if existing.data:
                return existing.data[0]

            response = self.client.table("sources").insert(source_data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to create source {source_data.get('name', 'unknown')}: {e}")
            return None