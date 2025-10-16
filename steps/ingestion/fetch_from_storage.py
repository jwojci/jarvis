from loguru import logger
from jarvis.domain.mapping import get_category_from_object_key
from typing_extensions import Annotated

from zenml import step, get_step_context
from qdrant_client.http import models

from jarvis.infrastructure.storage_client import s3_client
from jarvis.infrastructure.vector_db_client import connection as qdrant_conn
from jarvis.settings import settings, DATA_SOURCES_CONFIG


@step
def fetch_from_storage() -> Annotated[list, "raw_documents"]:
    docs = _fetch_unprocessed_documents()

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="raw_documents", metadata={"num_documents": len(docs)}
    )
    return docs


def _fetch_unprocessed_documents():
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=settings.MINIO_BUCKET_NAME)

    objects = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                if obj["Key"].endswith("/"):
                    continue
                objects.append(obj)

    files_to_process = []

    for obj in objects:
        try:
            # Dynamically determine category and collection name
            category = get_category_from_object_key(obj["Key"])
            collection_name = DATA_SOURCES_CONFIG[category]["collection"]
        except ValueError as e:
            logger.warning(f"Skipping file `{obj["Key"]}` due to error: {e}")
            continue

        conditions = [
            models.FieldCondition(
                key="metadata.source_file",
                match=models.MatchValue(value=obj["Key"]),
            ),
            models.FieldCondition(
                key="metadata.etag",
                match=models.MatchValue(value=obj["ETag"].strip('"')),
            ),
        ]

        count = 0
        try:
            # Attempt to count docs in the collection
            count_result = qdrant_conn.count(
                collection_name=collection_name,
                count_filter=models.Filter(must=conditions),
                exact=True,
            )
            count = count_result.count
        except Exception as e:
            # If failed (collection not found), log it and proceed
            # the count remains 0 so the file will be processed
            logger.warning(
                f"Could not count objects in collection '{collection_name}', likely does not exist yet. Error: {e}"
            )

        if count > 0:
            logger.info(f"Skipping already processed file: {obj['Key']}")
            continue

        response = s3_client.get_object(
            Bucket=settings.MINIO_BUCKET_NAME, Key=obj["Key"]
        )
        file_bytes = response["Body"].read()

        document_data = {
            "content_bytes": file_bytes,
            "metadata": {"source_file": obj["Key"], "etag": obj["ETag"].strip('"')},
        }
        files_to_process.append(document_data)

    return files_to_process
