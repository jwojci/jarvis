from typing import Tuple
import asyncio
from typing_extensions import Annotated
from zenml import step

from jarvis.application.preprocessing.dispatchers import ChunkingDispatcher
from jarvis.application.factories import StorableDocumentFactory


async def _get_sections(document):
    return await ChunkingDispatcher.dispatch(document)


async def _process_all_documents(documents):
    tasks = [_get_sections(doc) for doc in documents]
    results = await asyncio.gather(*tasks)
    return results


@step
def structure_documents(
    parsed_documents: Annotated[list, "parsed_documents"],
) -> Tuple[
    Annotated[list, "storable_parent_documents"],
    Annotated[list, "structured_sections_for_processign"],
]:
    storable_sections = []
    document_sections = []

    all_sections_lists = asyncio.run(_process_all_documents(parsed_documents))

    for sections in all_sections_lists:
        document_sections.extend(sections)
        for section in sections:
            storable_sections.append(StorableDocumentFactory.create(section))

    return storable_sections, document_sections
