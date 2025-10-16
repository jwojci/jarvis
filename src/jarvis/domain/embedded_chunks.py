from abc import ABC
from pydantic import Field, UUID4
from typing import Optional

from jarvis.domain.base import VectorBaseDocument
from jarvis.domain.types import DataCategory


class EmbeddedChunk(VectorBaseDocument, ABC):
    """An abstract base class for a final, embeddable piece of content."""

    content: str
    document_id: UUID4  # The id of the ParsedBookDocument it came from
    embedding: list[float]
    parent_id: Optional[UUID4] = None  # Optional field for parent-child relationships
    metadata: dict = Field(default_factory=dict)


class EmbeddedPDFBookChunk(EmbeddedChunk):
    """A chunk derived from a book (PDF)."""

    book_title: str
    authors: str | list[str]
    chapter_title: str
    chunk_type: str

    class Config:
        name = "book_chunks"
        use_vector_index = True
        category = DataCategory.BOOKS
