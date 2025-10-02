import pymupdf
import pymupdf4llm

from jarvis.infrastructure.storage_client import get_storage_client


def ingest_from_storage(bucket_name: str, object_name: str):
    s3 = get_storage_client()
    print(object_name)
    s3.download_file(bucket_name, object_name, f"tmp/{object_name}")

    doc = pymupdf.open(f"tmp\{object_name}")
    md_text = pymupdf4llm.to_markdown(doc)

    with open(f"tmp\{object_name}.md", "w", encoding="utf-8") as md_file:
        md_file.write(md_text)


ingest_from_storage("jarvis-bucket", "LLM-Engineers-Handbook.pdf")
