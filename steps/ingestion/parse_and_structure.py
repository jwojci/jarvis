from typing_extensions import Annotated
from io import BytesIO

from zenml import step

from jarvis.application.preprocessing.dispatchers import ParsingDispatcher


@step
def parse_documents(
    documents: Annotated[list, "raw_documents"],
) -> Annotated[list, "parsed_documents"]:
    parsed_documents = []
    for doc_data in documents:
        content_stream = BytesIO(doc_data["content_bytes"])
        metadata = doc_data["metadata"]
        filename = metadata["source_file"]

        parsed_document = ParsingDispatcher.dispatch(
            data_stream=content_stream, filename=filename, metadata=metadata
        )
        parsed_documents.append(parsed_document)

    return parsed_documents
