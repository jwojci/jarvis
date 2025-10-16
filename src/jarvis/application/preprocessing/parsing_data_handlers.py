from loguru import logger
from abc import ABC, abstractmethod
from io import BytesIO
import pymupdf
import pymupdf4llm

from jarvis.domain.books import ParsedBookDocument


class ParsingDataHandler(ABC):
    """Abstract class for all parsing data handlers."""

    @abstractmethod
    def parse(
        self, data_stream: BytesIO, filename: str, metadata: dict
    ) -> ParsedBookDocument:
        pass


class PDFParsingHandler(ParsingDataHandler):
    """Specific handler for parsing PDFs"""

    def parse(
        self, data_stream: BytesIO, filename: str, metadata: dict
    ) -> ParsedBookDocument:
        doc = pymupdf.open(stream=data_stream, filetype="pdf")
        md_text = pymupdf4llm.to_markdown(doc)

        return ParsedBookDocument(
            source_filename=filename, content_md=md_text, metadata=metadata
        )
