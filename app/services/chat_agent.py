"""Pluggable async model-client adapter for the websocket chat service.

``ChatAgent`` is the small interface every model connector must satisfy:
given the full message history (system/user/assistant, matching Pydantic AI
message-history semantics), yield the assistant's reply as a stream of text
chunks. Swapping the local stub for a real model (OpenAI, a local Ollama
server, etc.) only requires implementing this protocol and pointing
``build_chat_agent`` at it - no changes to the websocket endpoint or session
handling are needed.
"""

import asyncio
import random
from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable
from urllib.parse import urlparse

import attrs
import httpx
import orjson

from app.config import ChatConfig
from app.schemas.chat import ChatMessage


@runtime_checkable
class ChatAgent(Protocol):
    """Adapter interface implemented by every model connector."""

    async def stream_reply(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """Yield the assistant reply for ``messages`` chunk by chunk.

        ``messages`` is the full conversation history (oldest first),
        following Pydantic AI's role-labeled message-history convention.
        """
        ...  # pragma: no cover - protocol stub, never called directly

    async def aclose(self) -> None:
        """Release any held resources (connections, clients, ...)."""


class LocalEchoAgent:
    """Dependency-free stub agent used for local development and tests.

    It requires no API keys or network access: it "thinks" briefly, then
    streams back a canned/echo response word by word, emulating the token
    streaming behaviour of a real LLM backend closely enough to exercise the
    full websocket flow end-to-end.
    """

    def __init__(self, stream_delay_seconds: float = 0.02) -> None:
        self.stream_delay_seconds = stream_delay_seconds

    def _compose_reply(self, messages: list[ChatMessage]) -> str:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        if not last_user:
            return "Hello! I'm a local stub agent. Send me a message to get started."
        greetings = ("hi", "hello", "hey")
        if last_user.strip().lower() in greetings:
            return "Hello there! How can I help you today?"
        return f"You said: {last_user!r}. This is a local echo response (stub agent)."

    async def stream_reply(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        reply = self._compose_reply(messages)
        for word in reply.split(" "):
            await asyncio.sleep(self.stream_delay_seconds + random.uniform(0, 0.01))
            yield word + " "

    async def aclose(self) -> None:
        return None


def _validate_base_url(instance: OllamaChatAgent, attribute: attrs.Attribute, value: str) -> None:
    """Validate that base_url is a valid HTTP(S) URL.

    Args:
        instance: The OllamaChatAgent instance being initialized.
        attribute: The attrs attribute descriptor for base_url.
        value: The URL string to validate.

    Raises:
        ValueError: If base_url is not a valid HTTP(S) URL.
    """
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https"):
        msg = f"base_url must be HTTP(S), got scheme '{parsed.scheme}' from '{value}'"
        raise ValueError(msg)
    if not parsed.netloc:
        msg = f"base_url must include a host, got '{value}'"
        raise ValueError(msg)


def _validate_timeout(instance: OllamaChatAgent, attribute: attrs.Attribute, value: float) -> None:
    """Validate that timeout is positive.

    Args:
        instance: The OllamaChatAgent instance being initialized.
        attribute: The attrs attribute descriptor for timeout.
        value: The timeout value in seconds.

    Raises:
        ValueError: If timeout is not positive.
    """
    if value <= 0:
        msg = f"timeout must be positive, got {value}"
        raise ValueError(msg)


def _create_httpx_client(instance: OllamaChatAgent) -> httpx.AsyncClient:
    """Factory function to create the httpx.AsyncClient with validated config.

    This function is called from __attrs_post_init__ after all field validators
    have run, ensuring the client is created with validated configuration.

    Args:
        instance: The OllamaChatAgent instance being initialized.

    Returns:
        An initialized httpx.AsyncClient configured with base_url and timeout.
    """
    return httpx.AsyncClient(base_url=instance.base_url, timeout=instance.timeout)


@attrs.define(slots=True, eq=False, hash=False)
class OllamaChatAgent:
    """Streams chat completions from an OpenAI-compatible endpoint.

    Works out of the box with a local Ollama server (``ollama serve``) but
    any OpenAI-compatible ``/chat/completions`` endpoint works too. This is
    a ready-to-swap-in replacement for :class:`LocalEchoAgent` once a real
    model should be used.

    Attrs Configuration:
        - slots=True: Memory-efficient attribute storage (~40-50% reduction)
        - eq=False, hash=False: Instances are not comparable (contain async resources)
    """

    model: str = attrs.field(
        metadata={
            "description": "LLM model identifier",
            "examples": ["llama3.2", "mistral", "neural-chat"],
        }
    )
    base_url: str = attrs.field(
        validator=_validate_base_url,
        metadata={
            "description": "OpenAI-compatible API endpoint base URL",
            "example": "http://localhost:11434/v1",
        },
    )
    timeout: float = attrs.field(
        default=60.0,
        validator=_validate_timeout,
        converter=float,
        metadata={
            "description": "Request timeout in seconds",
            "default": 60.0,
            "constraints": "Must be positive",
        },
    )
    _client: httpx.AsyncClient = attrs.field(
        init=False,
        repr=False,
        metadata={"description": "Internal HTTP client for API communication"},
    )

    def __attrs_post_init__(self) -> None:
        """Initialize the HTTP client after field validation.

        This hook is called by attrs after __init__ completes and all field
        validators have run. It's used to initialize the internal _client
        field which depends on validated configuration.
        """
        self._client = _create_httpx_client(self)

    async def stream_reply(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """Stream chat completion responses from the configured model.

        Args:
            messages: Full message history (oldest first) following Pydantic AI convention.

        Yields:
            Text chunks from the model's streaming response.
        """
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
        }
        async with self._client.stream(
            "POST", "/chat/completions", json=payload
        ) as response:
            async for line in response.aiter_lines():
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                try:
                    data = orjson.loads(line[6:])
                    content = (
                        data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    )
                except Exception:
                    content = ""
                if content:
                    yield content

    async def aclose(self) -> None:
        """Release the internal HTTP client resources."""
        await self._client.aclose()


def build_chat_agent(config: ChatConfig) -> ChatAgent:
    """Factory selecting the concrete :class:`ChatAgent` from ``config``."""
    if config.backend == "ollama":
        return OllamaChatAgent(base_url=config.base_url, model=config.model)
    return LocalEchoAgent(stream_delay_seconds=config.stream_delay_seconds)
