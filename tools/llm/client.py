"""LiteLLM-based LLM client."""

import json
import os
from dataclasses import dataclass
from typing import Optional

import litellm


# Suppress LiteLLM's verbose logging
litellm.suppress_debug_info = True


@dataclass
class LLMResponse:
    """Response from an LLM."""

    content: str
    model: str
    usage: Optional[dict] = None
    finish_reason: Optional[str] = None


class LLMClient:
    """
    LLM client using LiteLLM for unified access to multiple providers.

    LiteLLM supports 100+ LLM providers with a unified interface.
    See: https://docs.litellm.ai/docs/providers

    Model format examples:
        - "claude-sonnet-4-20250514" (Anthropic)
        - "gpt-4o" (OpenAI)
        - "gemini/gemini-pro" (Google)
        - "ollama/llama2" (Ollama local)
        - "groq/llama3-8b-8192" (Groq)
    """

    # Default models by provider
    DEFAULT_MODELS = {
        "anthropic": "claude-sonnet-4-20250514",
        "openai": "gpt-4o",
        "gemini": "gemini/gemini-2.0-flash",
        "groq": "groq/llama-3.3-70b-versatile",
        "ollama": "ollama/llama3.2",
    }

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            model: Model identifier in LiteLLM format.
                   If not specified, uses LITELLM_MODEL env var or defaults to Claude.
        """
        self.model = model or os.environ.get(
            "LITELLM_MODEL",
            self.DEFAULT_MODELS["anthropic"]
        )

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            LLMResponse with generated content
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = litellm.completion(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            } if response.usage else None,
            finish_reason=choice.finish_reason,
        )

    def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Generate structured JSON output matching a schema.

        Args:
            prompt: The user prompt
            schema: JSON schema for the expected output
            system: Optional system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Parsed dict matching the schema
        """
        # Add schema instructions to the prompt
        schema_prompt = f"""Please respond with valid JSON matching this schema:

```json
{json.dumps(schema, indent=2)}
```

{prompt}

Respond ONLY with valid JSON, no other text."""

        # Add JSON instruction to system prompt
        full_system = "You are a helpful assistant that responds only with valid JSON."
        if system:
            full_system = f"{system}\n\n{full_system}"

        response = self.generate(
            prompt=schema_prompt,
            system=full_system,
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for structured output
        )

        # Parse the JSON response
        try:
            content = response.content.strip()

            # Handle markdown code blocks
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first and last lines (code block markers)
                if lines[-1].strip() == "```":
                    lines = lines[1:-1]
                else:
                    lines = lines[1:]
                content = "\n".join(lines)

            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\n{response.content}")

    @property
    def provider(self) -> str:
        """Get the provider name from the model string."""
        if "/" in self.model:
            return self.model.split("/")[0]
        # Infer from model name
        if self.model.startswith("claude"):
            return "anthropic"
        if self.model.startswith("gpt"):
            return "openai"
        return "unknown"

    def __repr__(self) -> str:
        return f"LLMClient(model={self.model})"


def get_client(model: Optional[str] = None) -> LLMClient:
    """
    Get an LLM client instance.

    Args:
        model: Model identifier in LiteLLM format

    Returns:
        Configured LLMClient instance
    """
    return LLMClient(model=model)


def list_default_models() -> dict[str, str]:
    """List default models by provider."""
    return LLMClient.DEFAULT_MODELS.copy()
