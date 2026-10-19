from pydantic_settings import BaseSettings, SettingsConfigDict


# Global environment settings loaded via pydantic-settings.
# Values are mapped from the root .env file and validated on startup.
class Settings(BaseSettings):
    """
    Central application configuration.
    Validates required environment variables on boot so configuration
    mistakes fail fast instead of failing midway through a request.
    """

    # PostgreSQL / MySQL connection parameters
    db_connection: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # LLM & Vector Search settings
    # llm_provider accepts 'openai' or 'gemini' (defaults to Gemini if not set to openai)
    llm_provider: str
    llm_model_name: str
    llm_embedding_model: str
    google_api_key: str
    openai_api_key: str

    # Meta Cloud API settings for WhatsApp bot integration
    # meta_verify_token is used for Meta's webhook challenge handshake
    meta_verify_token: str
    meta_access_token: str
    meta_phone_number_id: str
    meta_graph_api_url: str

    # Telegram Bot webhook integration
    telegram_bot_token: str
    telegram_api_url: str

    # JWT authentication configuration for employee sessions
    jwt_secret_key: str
    jwt_algorithm: str

    # Storage directory where uploaded documents are kept before & after ingestion
    document_dir_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Singleton instance reused across the app
settings = Settings()
