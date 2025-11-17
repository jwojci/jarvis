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

    @classmethod
    def from_str(cls, query: str) -> "Query":
        return Query(content=query.strip("\n "))

    def replace_content(self, new_content: str) -> "Query":
        return Query(id=self.id, content=new_content, metadata=self.metadata)


class EmbeddedQuery(Query):
    """Represents a query after embedding."""

    embedding: list[float]

    class Config:
        category = DataCategory.QUERIES
