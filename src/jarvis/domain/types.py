from enum import StrEnum


class DataCategory(StrEnum):
    PROMPT = "prompt"
    QUERIES = "queries"

    BOOKS = "books"  # Books meaning large PDF files (for now)
    PAPERS = "papers"  # Research papers
