from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"
    frontend_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    supabase_url: str = ""
    supabase_anon_key: str = ""
    resume_storage_dir: str = "data/resumes"
    analysis_storage_dir: str = "data/analyses"
    max_resume_size_mb: int = 10
    anakin_api_key: str = ""
    anakin_api_url: str = ""
    jobs_cache_dir: str = "data/jobs"
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:4b"
    # xAI Grok – used exclusively for Fit Analysis explanation
    xai_api_key: str = ""
    xai_model: str = "grok-3-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
