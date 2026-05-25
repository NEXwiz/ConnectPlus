from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    OPENROUTER_API_KEY: str
    GEMINI_API_KEY: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    ADZUNA_APP_ID: str = ""
    ADZUNA_APP_KEY: str = ""
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    EMBEDDING_MODEL: str = "openai/text-embedding-3-small"
    LLM_MODEL: str = "anthropic/claude-sonnet-4"
    EMBEDDING_DIMENSIONS: int = 1536

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
