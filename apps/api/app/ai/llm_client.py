"""
LLM client supporting OpenAI, Anthropic, and Ollama.
"""
import asyncio
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        try:
            if self.provider == LLMProvider.OPENAI:
                if not settings.OPENAI_API_KEY:
                    logger.warning("OpenAI API key not configured")
                    return
                import openai
                self._client = openai.AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL
                )
                logger.info(f"OpenAI client initialized with base_url: {settings.OPENAI_BASE_URL}")
                
            elif self.provider == LLMProvider.ANTHROPIC:
                if not settings.ANTHROPIC_API_KEY:
                    logger.warning("Anthropic API key not configured")
                    return
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized")
                
            elif self.provider == LLMProvider.OLLAMA:
                import openai
                self._client = openai.AsyncOpenAI(
                    base_url=settings.OLLAMA_BASE_URL,
                    api_key="ollama"  # Ollama doesn't need real API key
                )
                logger.info("Ollama client initialized")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
        except ImportError as e:
            logger.error(f"Failed to import LLM client library: {e}")
            raise
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text completion
        """
        if not self._client:
            raise RuntimeError("LLM client not initialized")
        
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            if self.provider == LLMProvider.OPENAI or self.provider == LLMProvider.OLLAMA:
                return await self._openai_complete(prompt, system_prompt, temp, tokens, **kwargs)
            elif self.provider == LLMProvider.ANTHROPIC:
                return await self._anthropic_complete(prompt, system_prompt, temp, tokens, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"LLM completion failed: {e}")
            raise
    
    async def _openai_complete(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.choices[0].message.content.strip()
    
    async def _anthropic_complete(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate completion using Anthropic API."""
        response = await self._client.messages.create(
            model=self.model,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.content[0].text.strip()
    
    async def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate JSON completion.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON response
        """
        import json
        
        json_instruction = "\n\nRespond ONLY with valid JSON. No other text."
        full_prompt = prompt + json_instruction
        
        if self.provider == LLMProvider.OPENAI or self.provider == LLMProvider.OLLAMA:
            response_format = {"type": "json_object"}
            result = await self.complete(
                full_prompt,
                system_prompt,
                response_format=response_format,
                **kwargs
            )
        else:
            result = await self.complete(full_prompt, system_prompt, **kwargs)
        
        # Parse JSON
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                raise ValueError(f"Failed to parse JSON from LLM response: {result}")


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
