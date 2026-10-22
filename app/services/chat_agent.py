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
import httpx2
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
        """Initialize the delay between streamed words."""
        self.stream_delay_seconds = stream_delay_seconds

    def _compose_reply(self, messages: list[ChatMessage]) -> str:
        """Compose a canned response to the latest user message."""
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
        """Yield the canned reply one word at a time."""
        reply = self._compose_reply(messages)
        for word in reply.split(" "):
            await asyncio.sleep(self.stream_delay_seconds + random.uniform(0, 0.01))
            yield word + " "

    async def aclose(self) -> None:
        """Close resources; the local agent holds none."""


def _validate_base_url(
    _instance: OllamaChatAgent, _attribute: attrs.Attribute, value: str
) -> None:
    """Require an absolute HTTP(S) endpoint URL."""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https"):
        msg = f"base_url must be HTTP(S), got scheme '{parsed.scheme}' from '{value}'"
        raise ValueError(msg)
    if not parsed.netloc:
        msg = f"base_url must include a host, got '{value}'"
        raise ValueError(msg)


def _validate_timeout(
    _instance: OllamaChatAgent, _attribute: attrs.Attribute, value: float
) -> None:
    """Require a positive request timeout."""
    if value <= 0:
        msg = f"timeout must be positive, got {value}"
        raise ValueError(msg)


@attrs.define(slots=True, eq=False, hash=False)
class OllamaChatAgent:
    """Streams chat completions from an OpenAI-compatible endpoint.

    Works out of the box with a local Ollama server (``ollama serve``) but
    any OpenAI-compatible ``/chat/completions`` endpoint works too. This is
    a ready-to-swap-in replacement for :class:`LocalEchoAgent` once a real
    model should be used.

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
    _client: httpx2.AsyncClient = attrs.field(
        init=False,
        repr=False,
        metadata={"description": "Internal HTTP client for API communication"},
    )

    def __attrs_post_init__(self) -> None:
        """Create the HTTPX2 client after attrs validates the fields."""
        self._client = httpx2.AsyncClient(base_url=self.base_url, timeout=self.timeout)

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
                data = orjson.loads(line.removeprefix("data: "))
                choices = data.get("choices", [])
                if not choices:
                    continue
                content = choices[0].get("delta", {}).get("content", "")
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
