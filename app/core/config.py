from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"
    app_name: str = "defenda-motor"
    base_url: str = "http://localhost:8000"

    database_url: str

    supabase_url: str
    supabase_service_role_key: str
    supabase_storage_bucket: str = "case-files"

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    webhook_shared_secret: str
    signed_url_ttl_seconds: int = 3600
    report_brand_name: str = "defenda.ai"

    class Config:
        env_file = ".env"

settings = Settings()
