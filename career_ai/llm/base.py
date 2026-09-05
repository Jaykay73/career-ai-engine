"""
LLM Provider Abstraction.
Defines the base interface for pluggable LLM providers (DeepSeek, OpenAI, Gemini, etc.).
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Type, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    """Abstract interface for all LLM providers."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000
    ) -> str:
        """Generates raw text from the model."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> T:
        """Generates and validates structured output conforming to a Pydantic model."""
        pass
