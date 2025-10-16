from jarvis.settings import DATA_SOURCES_CONFIG
from .types import DataCategory

# This dict maps the directory name in the bucket to a DataCategory
PREFIX_TO_CATEGORY_MAP = {
    config["prefix"]: category for category, config in DATA_SOURCES_CONFIG.items()
}


def get_category_from_object_key(object_key: str) -> DataCategory:
    """Determines the data category based on the object key's prefix (directory)."""
    try:
        # "books/some_book.pdf" -> "books"
        prefix = object_key.split("/")[0]
        category = PREFIX_TO_CATEGORY_MAP.get(prefix)
        if category:
            return category
        else:
            raise ValueError(f"Unknown category prefix {prefix}")
    except (IndexError, ValueError) as e:
        raise ValueError(
            f"Could not determine category from object key '{object_key}'. "
            "Ensure it's in a category directory like 'books/your_file.pdf'."
        ) from e
