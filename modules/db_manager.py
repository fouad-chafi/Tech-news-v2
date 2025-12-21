import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        load_dotenv()

        self.supabase_url: str = os.getenv('SUPABASE_URL')
        self.supabase_key: str = os.getenv('SUPABASE_SERVICE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials in .env file")

        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        }

    def test_connection(self) -> bool:
        try:
            url = f"{self.supabase_url}/rest/v1/"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error(f"Database connection test failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_categories(self) -> List[Dict[str, Any]]:
        try:
            url = f"{self.supabase_url}/rest/v1/categories?select=*"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get categories: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []

    def create_category(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.supabase_url}/rest/v1/categories"
            data = {'name': name}
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                logger.info(f"Created category: {name}")
                return response.json()[0] if response.json() else None
            else:
                logger.error(f"Failed to create category {name}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Failed to create category {name}: {e}")
            return None

    def article_exists(self, url: str) -> bool:
        try:
            request_url = f"{self.supabase_url}/rest/v1/articles?select=id&url=eq.{url}"
            response = requests.get(request_url, headers=self.headers)
            return len(response.json()) > 0 if response.status_code == 200 else False
        except Exception as e:
            logger.error(f"Failed to check if article exists: {e}")
            return False

    def create_article(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            url = f"{self.supabase_url}/rest/v1/articles"
            response = requests.post(url, headers=self.headers, json=article_data)
            if response.status_code in [200, 201]:
                logger.info(f"Created article: {article_data.get('title', 'Unknown')}")
                return response.json()[0] if response.json() else None
            else:
                logger.error(f"Failed to create article: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Failed to create article: {e}")
            return None

    def link_article_category(self, article_id: str, category_id: str) -> bool:
        try:
            url = f"{self.supabase_url}/rest/v1/article_categories"
            data = {
                'article_id': article_id,
                'category_id': category_id
            }
            response = requests.post(url, headers=self.headers, json=data)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to link article category: {e}")
            return False