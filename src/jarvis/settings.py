from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from jarvis.domain.types import DataCategory


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Gemini API
    GEMINI_MODEL_ID: str = "gemini-2.5-flash"
    GOOGLE_API_KEY: str | None = None

    # Huggingface API
    HUGGINGFACE_ACCESS_TOKEN: str | None = None

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "jarvis-bucket"

    # Qdrant vector database
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_CLOUD_URL: str = "str"
    QDRANT_APIKEY: str | None = None

    # RAG
    TEXT_EMBEDDING_MODEL_ID: str = "all-MiniLM-L6-v2"
    RERANKING_CROSS_ENCODER: str = "ms-marco-MiniLM-L-4-v2"
    RAG_MODEL_DEVICE: str = "cpu"


settings = Settings()

# Data Sources
DATA_SOURCES_CONFIG = {
    DataCategory.BOOKS: {"prefix": "books", "collection": "book_chunks"},
    DataCategory.PAPERS: {"prefix": "papers", "collection": "paper_chunks"},
}
