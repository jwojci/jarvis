from typing import Tuple
from typing_extensions import Annotated
from zenml import step

from jarvis.application.preprocessing.dispatchers import ChunkingDispatcher
from jarvis.application.factories import StorableDocumentFactory
from jarvis.domain.documents import ParsedDocument
from jarvis.domain.books import StoredChapter, ChapterContent


@step
def structure_documents(parsed_documents: Annotated[list, "parsed_documents"]) -> Tuple[
    Annotated[list, "storable_parent_documents"],
    Annotated[list, "structured_sections_for_processign"],
]:
    storable_sections = []
    document_sections = []

    for document in parsed_documents:
        sections = ChunkingDispatcher.dispatch(document)
        document_sections.extend(sections)

        for section in sections:
            storable_sections.append(StorableDocumentFactory.create(section))

    return storable_sections, document_sections
