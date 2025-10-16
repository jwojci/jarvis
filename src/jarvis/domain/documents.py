import uuid
from pydantic import BaseModel, Field, UUID4
from abc import ABC

from .types import DataCategory
from .base import VectorBaseDocument


class ParsedDocument(BaseModel, ABC):
    """An abstract class for any document parsed from a raw source."""

    id: UUID4 = Field(default_factory=uuid.uuid4)
    source_filename: str
    content_md: str
    category: DataCategory

    metadata: dict = Field(default_factory=dict)


class DocumentSection(BaseModel, ABC):
    """An abstract base class for a logical section of a ParsedDocument."""

    id: UUID4 = Field(default_factory=uuid.uuid4)
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)

    category: DataCategory


class StoredDocument(VectorBaseDocument, ABC):
    """An abstract base class for a storable parent document (e.g., chapter, section)."""

    content: str
    metadata: dict = Field(default_factory=dict)
    category: DataCategory
