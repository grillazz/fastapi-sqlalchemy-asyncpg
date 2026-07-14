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


class OllamaChatAgent:
    """Streams chat completions from an OpenAI-compatible endpoint.

    Works out of the box with a local Ollama server (``ollama serve``) but
    any OpenAI-compatible ``/chat/completions`` endpoint works too. This is
    a ready-to-swap-in replacement for :class:`LocalEchoAgent` once a real
    model should be used.
    """

    def __init__(self, base_url: str, model: str) -> None:
        self.model = model
        self._client = httpx.AsyncClient(base_url=base_url, timeout=60.0)

    async def stream_reply(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
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
        await self._client.aclose()


def build_chat_agent(config: ChatConfig) -> ChatAgent:
    """Factory selecting the concrete :class:`ChatAgent` from ``config``."""
    if config.backend == "ollama":
        return OllamaChatAgent(base_url=config.base_url, model=config.model)
    return LocalEchoAgent(stream_delay_seconds=config.stream_delay_seconds)
