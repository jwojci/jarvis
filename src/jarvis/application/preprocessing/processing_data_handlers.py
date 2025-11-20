import uuid
import asyncio
from pydantic import BaseModel
from abc import ABC, abstractmethod

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

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
    async def process(self, section: DocumentSection, **kwargs) -> list[Chunk]:
        pass

    @abstractmethod
    async def extract_document_metadata(self, document: "ParsedDocument") -> BaseModel:
        pass


class BookChapterProcessor(DocumentSectionProcessor):
    """Specific processor for Book chapters coming from parsed PDFs"""

    def __init__(self):
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""],
        )

    async def extract_document_metadata(self, document):
        snippet = document.content_md[:9000]
        return await get_metadata_from_llm(snippet)

    async def process(
        self, chapter: ChapterContent, book_metadata: BookMetadata, doc_id: uuid.UUID
    ) -> list[PDFBookChunk]:
        """Generates all final chunks for a single chapter"""
        final_chunks = []

        # LLM calls for summaries
        summary_task = get_chapter_summaries_from_llm(chapter)
        full_summary_task = get_full_chapter_summary_from_llm(chapter)

        # Split by header
        semantic_chunks = self.markdown_splitter.split_text(chapter.content)

        for semantic_chunk in semantic_chunks:
            header_metadata = semantic_chunk.metadata  # {header level, title}
            content = semantic_chunk.page_content

            sub_chunks = self.text_splitter.split_text(content)

            for sub_chunk in sub_chunks:
                combined_metadata = {
                    **chapter.metadata,
                    **header_metadata,
                    "chunk_source": "hierarchical_text",
                }

                final_chunks.append(
                    PDFBookChunk(
                        content=sub_chunk,
                        document_id=doc_id,
                        parent_id=chapter.id,
                        chunk_type="raw_text",
                        book_title=book_metadata.title,
                        authors=book_metadata.authors,
                        chapter_title=chapter.title,
                        metadata=combined_metadata,
                    )
                )

        # Await LLM results
        results = await asyncio.gather(summary_task, full_summary_task)
        summaries, full_summary = results

        # Add Summary Nuggets
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

        # Add full summary
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

        return final_chunks
