from pydantic import Field

from jarvis.domain.base import VectorBaseDocument
from jarvis.domain.types import DataCategory


class Query(VectorBaseDocument):
    """Represents a user's query before embedding."""

    content: str

    metadata: dict = Field(default_factory=dict)

    class Config:
        name = "queries"
        use_vector_index = False
        category = DataCategory.QUERIES


class EmbeddedQuery(Query):
    """Represents a query after embedding."""

    embedding: list[float]
