from zenml import pipeline
from loguru import logger
from steps import ingestion as ingestion_steps


@pipeline
def ingestion_pipeline():
    """
    This is the main orchestrator for the all the ingestion and feature engineering steps
    Parser -> Chunker -> Processor -> Embedder
    """
    raw_documents = ingestion_steps.fetch_from_storage()
    parsed_documents = ingestion_steps.parse_documents(raw_documents)

    storable_parents, sections_for_processing = ingestion_steps.structure_documents(
        parsed_documents=parsed_documents
    )

    parents_loaded_step = ingestion_steps.load_into_vector_db(
        documents=storable_parents
    )

    embedded_chunks = ingestion_steps.chunk_and_embed(
        structured_sections=sections_for_processing,
        parsed_documents=parsed_documents,
    )
    chunks_loaded_step = ingestion_steps.load_into_vector_db(documents=embedded_chunks)

    return [parents_loaded_step.invocation_id, chunks_loaded_step.invocation_id]
