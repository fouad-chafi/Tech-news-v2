import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:1234/v1/chat/completions")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5-7b-instruct-1m")

    @classmethod
    def validate(cls) -> bool:
        required_vars = [
            cls.SUPABASE_URL,
            cls.SUPABASE_KEY,
            cls.SUPABASE_SERVICE_KEY,
            cls.LLM_API_URL,
            cls.LLM_MODEL
        ]
        return all(var for var in required_vars)

    @classmethod
    def get_supabase_config(cls) -> dict:
        return {
            "url": cls.SUPABASE_URL,
            "key": cls.SUPABASE_KEY,
            "service_key": cls.SUPABASE_SERVICE_KEY
        }

    @classmethod
    def get_llm_config(cls) -> dict:
        return {
            "api_url": cls.LLM_API_URL,
            "model": cls.LLM_MODEL
        }