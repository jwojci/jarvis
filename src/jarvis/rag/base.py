from typing import Any
from abc import ABC, abstractmethod

from langchain.prompts import PromptTemplate
from pydantic import BaseModel

from jarvis.domain.queries import Query


class PromptTemplateFactory(ABC, BaseModel):
    """Abstract base class for creating prompt templates."""

    @abstractmethod
    def create_template(self) -> PromptTemplate:
        """Create and return a PromptTemplate instance."""
        pass


class RAGStep(ABC):
    def __init__(self, mock: bool = False) -> None:
        self._mock = mock

    @abstractmethod
    def generate(self, query: Query, *args, **kwargs) -> Any:
        pass
