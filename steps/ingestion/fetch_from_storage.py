from loguru import logger
import asyncio
from jarvis.domain.mapping import get_category_from_object_key
from typing_extensions import Annotated

from zenml import step, get_step_context
from qdrant_client.http import models

from jarvis.infrastructure.storage_client import s3_client
from jarvis.infrastructure.vector_db_client import connection as qdrant_conn
from jarvis.settings import settings, DATA_SOURCES_CONFIG


def _download_file_sync(bucket_name: str, key: str) -> bytes:
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read()
    except Exception as e:
        logger.error(f"Error downloading {key}: {e}")
        return None


async def _process_files_concurrently(objects: list[dict]) -> list[dict]:
    loop = asyncio.get_running_loop()
    tasks = []
    valid_objects = []

    for obj in objects:
        key = obj["Key"]
        etag = obj["ETag"].strip('"')

        try:
            category = get_category_from_object_key(obj["Key"])
            collection_name = DATA_SOURCES_CONFIG[category]["collection"]
        except ValueError as e:
            continue

        conditions = [
            models.FieldCondition(
                key="metadata.source_file",
                match=models.MatchValue(value=key),
            ),
            models.FieldCondition(
                key="metadata.etag",
                match=models.MatchValue(value=etag),
            ),
        ]
        if (
            qdrant_conn.count(
                collection_name=collection_name,
                count_filter=models.Filter(must=conditions),
                exact=True,
            ).count
            > 0
        ):
            logger.info(f"Skipping {key}, already processed.")
            continue

        valid_objects.append(obj)

    logger.info(f"Starting download of {len(valid_objects)} files from storage.")

    for obj in valid_objects:
        task = loop.run_in_executor(
            None, _download_file_sync, settings.MINIO_BUCKET_NAME, obj["Key"]
        )
        tasks.append(task)

    if not tasks:
        return []

    results = await asyncio.gather(*tasks)

    files_to_process = []
    for obj, file_bytes in zip(valid_objects, results):
        if file_bytes is not None:
            files_to_process.append(
                {
                    "content_bytes": file_bytes,
                    "metadata": {
                        "source_file": obj["Key"],
                        "etag": obj["ETag"].strip('"'),
                    },
                }
            )
    return files_to_process


@step
def fetch_from_storage() -> Annotated[list, "raw_documents"]:
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=settings.MINIO_BUCKET_NAME)
    objects = [
        obj
        for page in pages
        if "Contents" in page
        for obj in page["Contents"]
        if not obj["Key"].endswith("/")
    ]

    docs = asyncio.run(_process_files_concurrently(objects))

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="raw_documents", metadata={"num_documents": len(docs)}
    )
    return docs
