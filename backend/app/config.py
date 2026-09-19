import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    api_key: str = "dev-local-key-change-me"

    # LLM
    google_api_key: str
    google_genai_model: str = "gemini-2.5-flash"  # or gemini-2.5-pro / your chosen model

    # Postgres
    database_url: str
    adk_session_service_uri: str

    # Redis
    redis_url: str

    # DuckDB sandbox
    duckdb_sandbox_dir: str = "./data/sandbox"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

# Propagate to standard environment variables expected by google-genai
os.environ["GEMINI_API_KEY"] = settings.google_api_key
os.environ["GOOGLE_API_KEY"] = settings.google_api_key