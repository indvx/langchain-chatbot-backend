from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application"""

    # Database credentials
    db_connection: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    # LLM Config
    llm_provider: str
    llm_model_name: str
    llm_embedding_model: str
    google_api_key: str
    openai_api_key: str

    # Meta Configuration for Whatsapp intergration
    meta_verify_token: str
    meta_access_token: str
    meta_phone_number_id: str
    meta_graph_api_url: str

    # Telegram Configuration
    telegram_bot_token: str
    telegram_api_url: str

    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str

    # Directory path Configuration
    document_dir_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
