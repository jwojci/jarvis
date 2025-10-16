import uuid
from pydantic import BaseModel
from abc import ABC, abstractmethod

from jarvis.domain.chunks import Chunk, PDFBookChunk
from jarvis.domain.documents import DocumentSection, ParsedDocument
from jarvis.domain.books import ChapterContent, BookMetadata
from jarvis.infrastructure.llm_clients import (
    get_chapter_summaries_from_llm,
    get_full_chapter_summary_from_llm,
    get_metadata_from_llm,
)


class DocumentSectionProcessor(ABC):
    """Abstract base class for processing a DocumentSection into final Chunks."""

    @abstractmethod
    def process(self, section: DocumentSection, **kwargs) -> list[Chunk]:
        pass

    @abstractmethod
    def extract_document_metadata(self, document: "ParsedDocument") -> BaseModel:
        pass


class BookChapterProcessor(DocumentSectionProcessor):
    """Specific processor for Book chapters coming from parsed PDFs"""

    def extract_document_metadata(self, document):
        snippet = document.content_md[:9000]
        return get_metadata_from_llm(snippet)

    def process(
        self, chapter: ChapterContent, book_metadata: BookMetadata, doc_id: uuid.UUID
    ) -> list[PDFBookChunk]:
        """Generates all final chunks for a single chapter"""
        final_chunks = []

        # 1. Generate Summary Nuggets
        summaries = get_chapter_summaries_from_llm(chapter)
        if summaries:
            for summary_text in summaries:
                final_chunks.append(
                    PDFBookChunk(
                        content=summary_text,
                        document_id=doc_id,
                        parent_id=chapter.id,
                        chunk_type="summary_nugget",
                        book_title=book_metadata.title,
                        authors=book_metadata.authors,
                        chapter_title=chapter.title,
                        metadata=chapter.metadata,
                    )
                )

        # 2. Generate Full Chapter Summary
        full_summary = get_full_chapter_summary_from_llm(chapter)
        if full_summary:
            final_chunks.append(
                PDFBookChunk(
                    content=full_summary,
                    document_id=doc_id,
                    parent_id=chapter.id,
                    chunk_type="summary_paragraph",
                    book_title=book_metadata.title,
                    authors=book_metadata.authors,
                    chapter_title=chapter.title,
                    metadata=chapter.metadata,
                )
            )

        # 3. TODO: Generate Hierarchical Chunks

        return final_chunks
