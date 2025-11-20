from loguru import logger
from io import BytesIO
from pathlib import Path

from jarvis.domain.documents import ParsedDocument, DocumentSection
from jarvis.domain.types import DataCategory
from jarvis.domain.chunks import Chunk
from jarvis.domain.base import VectorBaseDocument

from .parsing_data_handlers import PDFParsingHandler, ParsingDataHandler
from .chunking_data_handlers import ChunkingDataHandler, PDFChunkingHandler
from .processing_data_handlers import DocumentSectionProcessor, BookChapterProcessor
from .embedding_data_handlers import (
    EmbeddingDataHandler,
    QueryEmbeddingHandler,
    PDFBookEmbeddingHandler,
)


class ParsingHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> ParsingDataHandler:
        if data_category == DataCategory.BOOKS:
            return PDFParsingHandler()
        else:
            raise ValueError(f"Unsupported data category: {data_category}")


class ParsingDispatcher:
    factory = ParsingHandlerFactory()

    @classmethod
    def dispatch(
        cls, data_stream: BytesIO, filename: str, metadata: dict
    ) -> ParsedDocument:
        file_extension = Path(filename).suffix.lower()
        # TODO: This will break if we add arxiv papers
        # or something that isn't handled by BOOKS processing logic
        if file_extension == ".pdf":
            data_category = DataCategory.BOOKS
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        handler = cls.factory.create_handler(data_category=data_category)
        parsed_model = handler.parse(
            data_stream=data_stream, filename=filename, metadata=metadata
        )  # this has the etag

        logger.success(
            "Document parsed successfully.",
            data_category=data_category,
            cleaned_content_len=len(parsed_model.content_md),
        )

        return parsed_model


class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> ChunkingDataHandler:
        if data_category == DataCategory.BOOKS:
            return PDFChunkingHandler()
        else:
            raise ValueError(f"Unsupported data category: {data_category}")


class ChunkingDispatcher:
    factory = ChunkingHandlerFactory()

    @classmethod
    async def dispatch(cls, parsed_document: ParsedDocument) -> list[DocumentSection]:
        data_category = parsed_document.category
        handler = cls.factory.create_handler(data_category=data_category)

        sections = await handler.chunk(parsed_document)

        logger.success(
            "Document chunked successfully into structural sections.",
            num_sections=len(sections),
            data_category=data_category,
        )

        return sections


class ProcessingHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> DocumentSectionProcessor:
        if data_category == DataCategory.BOOKS:
            return BookChapterProcessor()
        else:
            raise ValueError(f"No processor available for category: {data_category}")


class ProcessingDispatcher:
    factory = ProcessingHandlerFactory()

    @classmethod
    async def dispatch(cls, section: DocumentSection, **kwargs) -> list[Chunk]:
        data_category = section.category

        handler = cls.factory.create_handler(data_category)

        return await handler.process(section, **kwargs)


class EmbeddingHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> EmbeddingDataHandler:
        if data_category == DataCategory.QUERIES:
            return QueryEmbeddingHandler()
        if data_category == DataCategory.BOOKS:
            return PDFBookEmbeddingHandler()
        else:
            raise ValueError("Unsupported data type")


class EmbeddingDispatcher:
    factory = EmbeddingHandlerFactory()

    @classmethod
    def dispatch(
        cls, data_model: VectorBaseDocument | list[VectorBaseDocument]
    ) -> VectorBaseDocument | list[VectorBaseDocument]:
        is_list = isinstance(data_model, list)
        if not is_list:
            data_model = [data_model]

        if len(data_model) == 0:
            return []

        data_category = data_model[0].get_category()
        assert all(
            data_model.get_category() == data_category for data_model in data_model
        ), "Data models must be of the same category."
        handler = cls.factory.create_handler(data_category)

        embedded_chunk_model = handler.embed_batch(data_model)

        if not is_list:
            embedded_chunk_model = embedded_chunk_model[0]

        logger.info("Data embedded successfully.", data_category=data_category)

        return embedded_chunk_model
