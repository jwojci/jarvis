from jarvis.domain.documents import DocumentSection, StoredDocument
from jarvis.domain.books import ChapterContent, StoredChapter


class StorableDocumentFactory:
    """
    Creates a storable version of a DocumentSection.
    This contains the specific mapping logic, keeping the pipeline generic.
    """

    # Update this when adding new types
    _MAPPING = {
        ChapterContent: StoredChapter,
        # TechDocSection: StoredTechDocSection, # Example for the future
    }

    @classmethod
    def create(cls, section: DocumentSection) -> "StoredDocument":
        storable_class = cls._MAPPING.get(type(section))

        if not storable_class:
            raise TypeError(
                f"No storable class mapping found for section type {type(section)}"
            )

        # This dynamically creates the correct storable object (e.g., StoredChapter)
        # by passing the attributes from the section object.
        return storable_class(**section.model_dump())
