import os

from boto3.session import Session
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

# --- Module-Level Client ---
# This block of code will only run ONCE when the module is first imported.
try:
    if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY]):
        raise ValueError("MinIO environment variables are not fully set.")

    s3_client = Session(
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    ).client("s3", endpoint_url=f"http://{MINIO_ENDPOINT}")

    s3_client.list_buckets()
    logger.success("Connection to MinIO storage client established successfully.")

except Exception as e:
    logger.error(f"Failed to initialize MinIO storage client: {e}")
    s3_client = None


def get_storage_client():
    """Returns the shared S3 client instance."""
    if s3_client is None:
        raise ConnectionError(
            "Storage client is not available. Check connection settings."
        )
    return s3_client
