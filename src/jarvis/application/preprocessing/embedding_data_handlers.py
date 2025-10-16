from abc import ABC, abstractmethod
from typing import Generic, TypeVar, cast

from jarvis.application.embeddings import EmbeddingModelSingleton
from jarvis.domain.chunks import Chunk, PDFBookChunk
from jarvis.domain.embedded_chunks import EmbeddedChunk, EmbeddedPDFBookChunk
from jarvis.domain.queries import Query, EmbeddedQuery

ChunkT = TypeVar("ChunkT", bound=Chunk)
EmbeddedChunkT = TypeVar("EmbeddedChunkT", bound=EmbeddedChunk)
embedding_model = EmbeddingModelSingleton()


class EmbeddingDataHandler(ABC, Generic[ChunkT, EmbeddedChunkT]):
    """
    Abstract class for all embedding logic
    """

    def embed(self, data_model: ChunkT) -> EmbeddedChunkT:
        return self.embed_batch([data_model])[0]

    def embed_batch(self, data_model: list[ChunkT]) -> list[EmbeddedChunkT]:
        embedding_model_input = [data_model.content for data_model in data_model]
        embeddings = embedding_model(embedding_model_input, to_list=True)

        embedded_chunk = [
            self.map_model(data_model, cast(list[float], embedding))
            for data_model, embedding in zip(data_model, embeddings, strict=False)
        ]

        return embedded_chunk

    @abstractmethod
    def map_model(self, data_model: ChunkT, embedding: list[float]) -> EmbeddedChunkT:
        pass


class QueryEmbeddingHandler(EmbeddingDataHandler):
    def map_model(self, data_model: Query, embedding: list[float]) -> EmbeddedQuery:
        return EmbeddedQuery(
            id=data_model.id,
            content=data_model.content,
            embedding=embedding,
            metadata={
                "embedding_model_id": embedding_model.model_id,
                "embedding_size": embedding_model.embedding_size,
                "max_input_length": embedding_model.max_input_length,
            },
        )


class PDFBookEmbeddingHandler(EmbeddingDataHandler):
    def map_model(
        self, data_model: PDFBookChunk, embedding: list[float]
    ) -> EmbeddedPDFBookChunk:
        return EmbeddedPDFBookChunk(
            id=data_model.id,
            content=data_model.content,
            embedding=embedding,
            document_id=data_model.document_id,
            parent_id=data_model.parent_id,
            chunk_type=data_model.chunk_type,
            chapter_title=data_model.chapter_title,
            book_title=data_model.book_title,
            authors=data_model.authors,
            metadata={
                "embedding_model_id": embedding_model.model_id,
                "embedding_size": embedding_model.embedding_size,
                "max_input_length": embedding_model.max_input_length,
            },
        )
