from loguru import logger
from typing_extensions import Annotated
from zenml import step

from jarvis.application import utils
from jarvis.domain.base import VectorBaseDocument


@step
def load_into_vector_db(
    documents: Annotated[list, "documents"],
) -> Annotated[bool, "successful"]:
    logger.info(f"Loading {len(documents)} documents into vector storage.")

    grouped_documents = VectorBaseDocument.group_by_class(documents)
    for document_class, documents in grouped_documents.items():
        logger.info(f"Loading documents into {document_class.get_collection_name()}")

        for documents_batch in utils.batch(documents, size=4):
            try:
                document_class.bulk_insert(documents_batch)
            except Exception as e:
                logger.error(
                    f"Failed to insert documents into {document_class.get_collection_name()}: {e}"
                )

                return False

    return True
