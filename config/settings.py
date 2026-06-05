from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Application Settings
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # AI Core Configuration
    LLM_PROVIDER: str = "ollama"  # "ollama", "llamacpp", or "openai"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "llama3.2:3b"
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # Memory System
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    SQLITE_DB_PATH: str = "data/qiyam.db"

    # WhatsApp Integration
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_API_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""

    # Security
    SECRET_KEY: str = "unsafe-default-secret-key-change-in-prod"
    MAX_EXECUTION_TIME_SECONDS: int = 30
    MAX_MEMORY_MB: int = 256

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
