from loguru import logger
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse


from jarvis.settings import settings

load_dotenv()


class QdrantDatabaseConnector:
    _instance: QdrantClient | None = None

    def __new__(cls, *args, **kwargs) -> QdrantClient:
        if cls._instance is None:
            try:
                if settings.USE_QDRANT_CLOUD:
                    cls._instance = QdrantClient(
                        url=settings.QDRANT_CLOUD_URL, api_key=settings.QDRANT_API_KEY
                    )

                    uri = settings.QDRANT_CLOUD_URL
                else:
                    cls._instance = QdrantClient(
                        host=settings.QDRANT_DATABASE_HOST,
                        port=settings.QDRANT_DATABASE_PORT,
                    )

                    uri = f"{settings.QDRANT_DATABASE_HOST}:{settings.QDRANT_DATABASE_PORT}"

                logger.success(f"Connection to Qdrant DB successful: {uri}")
            except UnexpectedResponse:
                logger.exception(
                    "Couldn't connect to Qdrant.",
                    host=settings.QDRANT_DATABASE_HOST,
                    port=settings.QDRANT_DATABASE_PORT,
                    url=settings.QDRANT_CLOUD_URL,
                )

                raise

        return cls._instance


connection = QdrantDatabaseConnector()
