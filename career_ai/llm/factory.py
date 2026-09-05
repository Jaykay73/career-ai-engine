"""
LLM Provider Factory.
Instantiates and provides configured LLM providers (DeepSeek, Mock, etc.).
"""

from typing import Optional
from career_ai.llm.base import LLMProvider
from career_ai.llm.deepseek import DeepSeekProvider
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("llm_factory")

def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """Returns an instance of the requested or configured LLM provider."""
    name = (provider_name or settings.llm_provider).lower()
    
    if name == "deepseek":
        return DeepSeekProvider(
            api_key=settings.deepseek_api_key,
            model_name=settings.deepseek_model,
            base_url=settings.deepseek_base_url
        )
    else:
        logger.warning("Unknown LLM provider '%s', defaulting to DeepSeek.", name)
        return DeepSeekProvider()
