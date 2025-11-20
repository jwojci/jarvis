import asyncio
from typing_extensions import Annotated
from collections import defaultdict

from loguru import logger
from zenml import step, get_step_context

from jarvis.application.preprocessing.dispatchers import (
    EmbeddingDispatcher,
    ProcessingHandlerFactory,
)
from jarvis.application.utils import batch
from jarvis.domain.chunks import Chunk
from jarvis.domain.embedded_chunks import EmbeddedChunk


async def _process_chunk_and_embed(structured_sections, parsed_documents):
    sections_by_doc_id = defaultdict(list)
    for section in structured_sections:
        doc_id = section.metadata.get("document_id")
        if doc_id:
            sections_by_doc_id[doc_id].append(section)

    if not structured_sections:
        logger.warning("No sections to process. Returning empty list.")
        return []  # No sections to process

    metadata_tasks = [
        ProcessingHandlerFactory.create_handler(doc.category).extract_document_metadata(
            doc
        )
        for doc in parsed_documents
    ]

    metadata_results = await asyncio.gather(*metadata_tasks)

    doc_id_to_metadata = {
        str(doc.id): md for doc, md in zip(parsed_documents, metadata_results)
    }

    processing_tasks = []
    for document in parsed_documents:
        processor = ProcessingHandlerFactory.create_handler(document.category)
        doc_metadata = doc_id_to_metadata.get(str(document.id))

        if not doc_metadata or not getattr(doc_metadata, "title", None):
            logger.warning(
                f"Could not extract metadata for document {document.id}. Skipping all its sections."
            )
            continue

        logger.info(f"Processing document '{doc_metadata.title}'...")

        sections = sections_by_doc_id.get(str(document.id), [])
        for section in sections:
            task = processor.process(
                chapter=section,
                book_metadata=doc_metadata,
                doc_id=document.id,
            )
            processing_tasks.append(task)

    if not processing_tasks:
        logger.warning("No processing tasks created. Returning empty list.")
        return []

    all_chunks_results = await asyncio.gather(*processing_tasks, return_exceptions=True)

    all_processed_chunks = []
    for result in all_chunks_results:
        if isinstance(result, Exception):
            logger.error(f"Error during chunk processing: {result}")
        elif isinstance(result, list):
            all_processed_chunks.extend(result)

    logger.info(f"Total processed chunks before embedding: {len(all_processed_chunks)}")

    # Embedding stage
    embedded_chunks = []
    for batched_chunks in batch(all_processed_chunks, 32):
        batched_embedded_chunks = EmbeddingDispatcher.dispatch(batched_chunks)
        embedded_chunks.extend(batched_embedded_chunks)

    return all_processed_chunks, embedded_chunks


@step
def chunk_and_embed(
    structured_sections: Annotated[list, "structured_sections_for_processing"],
    parsed_documents: Annotated[list, "parsed_documents"],
) -> Annotated[list, "embedded_documents"]:
    """
    Takes parsed documents, processes them into chunks, and creates vector embeddings.
    it follows the 'Parser -> Chunker -> Processor -> Embedder' flow
    """
    logger.info(
        f"Step started. Received {len(structured_sections)} sections to process."
    )
    all_processed_chunks, embedded_chunks = asyncio.run(
        _process_chunk_and_embed(structured_sections, parsed_documents)
    )

    # Metadata
    step_context = get_step_context()
    output_metadata = _create_output_metadata(all_processed_chunks, embedded_chunks)
    step_context.add_output_metadata(
        output_name="embedded_documents", metadata=output_metadata
    )

    return embedded_chunks


def _create_output_metadata(
    chunks: list[Chunk], embedded_chunks: list[EmbeddedChunk]
) -> dict:
    """
    Creates a metadata dictionary for the ZenML step output
    """
    metadata = {"categories": {}}

    for chunk in chunks:
        category = chunk.get_category()
        if category not in metadata["categories"]:
            metadata["categories"][category] = {"num_chunks": 0, "authors": set()}

        metadata["categories"][category]["num_chunks"] += 1

        if hasattr(chunk, "authors") and chunk.authors:
            metadata["categories"][category]["authors"].update(chunk.authors)

    for category_meta in metadata["categories"].values():
        category_meta["authors"] = list(category_meta["authors"])

    metadata["total_chunks"] = len(chunks)
    metadata["total_embedded_chunks"] = len(embedded_chunks)

    return metadata
