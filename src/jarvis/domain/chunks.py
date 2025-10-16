import uuid
from abc import ABC
from pydantic import Field, UUID4
from typing import Optional, List

from jarvis.domain.base import VectorBaseDocument
from jarvis.domain.types import DataCategory


class Chunk(VectorBaseDocument, ABC):
    """An abstract base class for a final, embeddable piece of content."""

    content: str
    document_id: UUID4  # The id of the ParsedBookDocument it came from
    parent_id: Optional[UUID4] = None  # Optional field for parent-child relationships
    metadata: dict = Field(default_factory=dict)


class PDFBookChunk(Chunk):
    """A chunk derived from a book (PDF)."""

    book_title: str
    authors: str | list[str]
    chapter_title: str
    chunk_type: str

    class Config:
        category = DataCategory.BOOKS
