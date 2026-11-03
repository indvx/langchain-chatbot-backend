from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or .env file."""

    # Database connection
    db_connection: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str = Field(validation_alias=AliasChoices("db_name", "db_database"))

    # LLM & embeddings ('gemini' or 'openai')
    llm_provider: str
    llm_model_name: str
    llm_embedding_model: str
    google_api_key: str
    openai_api_key: str

    # WhatsApp (Meta Graph API)
    meta_verify_token: str
    meta_access_token: str
    meta_phone_number_id: str
    meta_graph_api_url: str

    # Telegram Bot
    telegram_bot_token: str
    telegram_api_url: str

    # Uploads directory
    document_dir_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
