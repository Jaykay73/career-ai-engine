"""
DeepSeek LLM Provider implementation.
Uses OpenAI-compatible client interface with DeepSeek API endpoints.
Provides structured Pydantic output validation and JSON extraction defenses.
"""

from typing import TypeVar, Type, Optional, Dict, Any
import json
import re
from openai import OpenAI
from pydantic import BaseModel

from career_ai.llm.base import LLMProvider
from career_ai.core.config import settings
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import LLMProviderError, LLMAuthenticationError, LLMResponseError

logger = get_logger("deepseek")

T = TypeVar("T", bound=BaseModel)

JSON_BLOCK_REGEX = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)

class DeepSeekProvider(LLMProvider):
    """DeepSeek API client conforming to LLMProvider interface."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or settings.deepseek_api_key
        self.model_name = model_name or settings.deepseek_model
        self.base_url = base_url or settings.deepseek_base_url

        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if not self.api_key or self.api_key == "your_deepseek_api_key_here":
            raise LLMAuthenticationError(
                "DeepSeek API key is not configured. Please set DEEPSEEK_API_KEY in your .env file or Settings."
            )
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000
    ) -> str:
        """Calls DeepSeek chat completion for free-form text."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except LLMAuthenticationError:
            raise
        except Exception as e:
            logger.error("DeepSeek API error in generate_text: %s", e)
            raise LLMProviderError(f"DeepSeek call failed: {e}")

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000
    ) -> T:
        """
        Generates structured JSON conforming to the Pydantic schema.
        Enforces JSON output instructions, extracts JSON block if wrapped,
        and validates with Pydantic.
        """
        json_schema_prompt = (
            f"\n\nCRITICAL REQUIREMENT: Return ONLY valid, parseable JSON conforming to this schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}\n"
            f"Do NOT include any conversational preamble, explanations, or markdown formatting outside the JSON."
        )

        full_system = (system_prompt or "") + json_schema_prompt

        raw_response = self.generate_text(
            prompt=prompt,
            system_prompt=full_system,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Attempt to clean and extract JSON
        clean_json_str = self._extract_json(raw_response)

        try:
            return schema.model_validate_json(clean_json_str)
        except Exception as validation_err:
            logger.warning("First validation attempt failed: %s. Raw was: %s", validation_err, clean_json_str[:200])
            # Attempt repair via a targeted corrective call
            return self._repair_structured(clean_json_str, schema, str(validation_err))

    def _extract_json(self, text: str) -> str:
        """Extracts JSON string from markdown codeblocks or raw text."""
        text = text.strip()
        match = JSON_BLOCK_REGEX.search(text)
        if match:
            return match.group(1).strip()
        
        # Look for { ... } bounds
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return text[start_idx : end_idx + 1].strip()

        return text

    def _repair_structured(self, invalid_json: str, schema: Type[T], error_msg: str) -> T:
        """Corrects malformed JSON using a fast repair prompt."""
        logger.info("Attempting JSON repair for schema %s", schema.__name__)
        repair_prompt = (
            f"The following JSON failed validation for schema {schema.__name__}.\n"
            f"Error: {error_msg}\n\n"
            f"INVALID JSON:\n{invalid_json}\n\n"
            f"Target Schema:\n{json.dumps(schema.model_json_schema(), indent=2)}\n\n"
            f"Fix the JSON so it parses and strictly matches the schema. Output ONLY valid JSON."
        )

        repaired_text = self.generate_text(prompt=repair_prompt, temperature=0.0)
        clean = self._extract_json(repaired_text)
        try:
            return schema.model_validate_json(clean)
        except Exception as e:
            raise LLMResponseError(f"Failed to produce valid JSON for {schema.__name__} after repair: {e}")
