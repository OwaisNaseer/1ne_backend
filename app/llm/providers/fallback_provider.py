"""
Fallback provider for tests and failure scenarios.
"""
import asyncio
import time
from typing import Optional, Dict, Any

from app.llm.base import BaseProvider
from app.llm.schemas import LLMResponse, TokenUsage


class FallbackProvider(BaseProvider):
    """Non-network provider for tests/failure fallback."""

    provider_name = "fallback"

    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a deterministic fallback response.

        Returns:
            LLMResponse with dummy values
        """
        # Simulate some latency
        await asyncio.sleep(0.01)
        
        latency_ms = 10
        
        return LLMResponse(
            content="This is a fallback response for testing.",
            model_used="fallback",
            provider=self.provider_name,
            token_usage=TokenUsage(prompt=0, completion=0, total=0),
            cost_estimate=0.0,
            latency_ms=latency_ms
        )

    def validate_config(self) -> bool:
        """Always returns True (no config needed)."""
        return True

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Return None (no model info for fallback)."""
        return None

