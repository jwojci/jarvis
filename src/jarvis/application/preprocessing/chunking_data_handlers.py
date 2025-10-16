import re
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from jarvis.domain.chunks import Chunk
from jarvis.domain.documents import DocumentSection
from jarvis.domain.books import ParsedBookDocument, ChapterContent
from jarvis.infrastructure.llm_clients import get_toc_from_llm


# from .operations import chunk_book, chunk_text

ParsedBookDocumentT = TypeVar("ParsedBookDocumentT", bound=ParsedBookDocument)
ChunkT = TypeVar("ChunkT", bound=Chunk)


class ChunkingDataHandler(ABC, Generic[ParsedBookDocumentT, ChunkT]):
    """
    Abstract class for all Chunking data handlers.
    """

    @abstractmethod
    def chunk(
        self, data_model: ParsedBookDocumentT, metadata: dict
    ) -> list[DocumentSection]:
        pass


class PDFChunkingHandler(ChunkingDataHandler):
    def chunk(self, data_model: ParsedBookDocument) -> list[ChapterContent]:
        """
        Parses and splits full markdown doc (a parsed PDF of a book) into a list of ChapterContent objects.
        """
        md_text = data_model.content_md

        base_metadata = {"document_id": data_model.id, **data_model.metadata}

        pattern = (
            r"(^(#{1,2})\s*(?:Table of Contents|Contents|TOC)[\s\S]*?)(?=\n^\2\s+)"
        )
        match = re.search(pattern, md_text, re.MULTILINE | re.IGNORECASE)
        if not match:
            # Handle books with no ToC: treat the whole book as one chapter
            return [
                ChapterContent(
                    title="Full Document",
                    chapter_number=1,
                    content=md_text,
                    metadata=base_metadata,
                )
            ]

        toc_text = match.group(1).strip()
        toc_structured = get_toc_from_llm(toc_text=toc_text)
        if not toc_structured:
            return []

        chapters_with_content = []
        for i, chapter in enumerate(toc_structured):
            # get the start of this chapter and get everything up to the start of next chapter
            start_title = re.escape(chapter.chapter_title)

            if i + 1 < len(toc_structured):
                end_title = re.escape(toc_structured[i + 1].chapter_title)
                # Pattern to find content between this chapter's title and the next
                pattern = (
                    rf"(^(#{{1,4}})\s*{start_title}[\s\S]*?)(?=\n^\2\s*{end_title})"
                )
            else:
                # This is the last chapter, so it goes to the end of the document
                pattern = rf"(^(#{{1,4}})\s*{start_title}[\s\S]*$)"

            chapter_match = re.search(pattern, md_text, re.MULTILINE | re.IGNORECASE)

            if chapter_match:
                content = chapter_match.group(1).strip()
                chapters_with_content.append(
                    ChapterContent(
                        chapter_number=chapter.chapter_number,
                        title=chapter.chapter_title,
                        content=content,
                        metadata=base_metadata,
                    )
                )

        return chapters_with_content
