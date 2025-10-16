from pydantic import BaseModel, Field


from .documents import ParsedDocument, DocumentSection, StoredDocument
from .types import DataCategory
from .base import VectorBaseDocument


class ParsedBookDocument(ParsedDocument):
    """A parsed document originating from a PDF book file."""

    category: DataCategory = DataCategory.BOOKS


class Chapter(BaseModel):
    chapter_title: str
    chapter_number: int | str


class TableOfContents(BaseModel):
    chapters: list[Chapter]


class ChapterContent(DocumentSection):
    """A specific type of DocumentSection representing a book chapter."""

    chapter_number: int | str
    category: DataCategory = DataCategory.BOOKS


class BookMetadata(BaseModel):
    title: str | None = None
    authors: list[str] | None = None
    publication_year: int | None = None


class StoredChapter(StoredDocument):
    """A DocumentSection (Chapter) that can be stored in the vector DB."""

    title: str
    chapter_number: int | str

    class Config:
        name = "book_chapters"
        use_vector_index = False  # No embedding needed
        category = DataCategory.BOOKS
