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
    api_key: str
    base_url: str = Field(default="")

    # WhatsApp (Meta Graph API)
    meta_verify_token: str
    meta_access_token: str
    meta_phone_number_id: str
    meta_graph_api_url: str

    # Telegram Bot
    telegram_bot_token: str
    telegram_api_url: str

    # Storage directories
    document_dir_name: str = "./documents"
    vector_dir_name: str = Field(
        default="./vector_db/chroma_langchain_db",
        validation_alias=AliasChoices("vector_dir_name", "vector_db_dir", "chroma_db_dir"),
    )
    chroma_collection_name: str = Field(
        default="example_collection",
        validation_alias=AliasChoices("chroma_collection_name", "collection_name"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
