"""LLM client for Ollama integration with streaming support."""

import logging
from typing import Generator

from neo_code.config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for Ollama API with streaming and fallback support."""

    def __init__(self):
        self._settings = get_settings().ai
        self._client = None
        self._available: bool | None = None

    def _get_client(self):
        """Lazy-initialize the Ollama client."""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self._settings.ollama_host)
            except ImportError:
                logger.warning("ollama package not installed")
                self._client = None
        return self._client

    def is_available(self) -> bool:
        """Check if the Ollama backend is reachable."""
        if self._available is not None:
            return self._available

        client = self._get_client()
        if client is None:
            self._available = False
            return False

        try:
            client.list()
            self._available = True
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            self._available = False

        return self._available

    def generate(self, prompt: str, system_prompt: str, max_tokens: int = 512) -> str:
        """Generate a complete response (blocking)."""
        client = self._get_client()
        if client is None:
            return ""

        try:
            response = client.chat(
                model=self._settings.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                options={
                    "num_predict": max_tokens,
                    "temperature": self._settings.temperature,
                    "top_p": 0.9,
                },
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            # Try fallback model
            return self._try_fallback(prompt, system_prompt, max_tokens)

    def generate_stream(
        self, prompt: str, system_prompt: str, max_tokens: int = 512
    ) -> Generator[str, None, None]:
        """Yield response chunks for streaming display."""
        client = self._get_client()
        if client is None:
            return

        try:
            stream = client.chat(
                model=self._settings.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                options={
                    "num_predict": max_tokens,
                    "temperature": self._settings.temperature,
                    "top_p": 0.9,
                },
                stream=True,
            )
            for chunk in stream:
                yield chunk["message"]["content"]
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")

    def _try_fallback(self, prompt: str, system_prompt: str, max_tokens: int) -> str:
        """Try the fallback model."""
        client = self._get_client()
        if client is None:
            return ""

        try:
            response = client.chat(
                model=self._settings.fallback_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                options={
                    "num_predict": max_tokens,
                    "temperature": self._settings.temperature,
                },
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Fallback LLM error: {e}")
            return ""

    def get_model_info(self) -> dict:
        """Return info about available models."""
        client = self._get_client()
        if client is None:
            return {"status": "unavailable"}

        try:
            models = client.list()
            return {
                "status": "available",
                "models": [m["name"] for m in models.get("models", [])],
                "current": self._settings.model,
            }
        except Exception:
            return {"status": "error"}

    def reset_availability(self) -> None:
        """Reset the availability cache to force re-check."""
        self._available = None
