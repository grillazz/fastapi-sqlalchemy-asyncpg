"""Streaming client for OpenAI-compatible chat completion endpoints."""

from collections.abc import AsyncIterator

import httpx2
import orjson


class StreamLLMService:
    """Send prompts to an LLM endpoint and yield newline-delimited JSON events."""

    def __init__(self, base_url: str = "http://localhost:11434/v1") -> None:
        """Configure the endpoint and default model."""
        self.base_url = base_url
        self.model = "llama3.2"

    async def stream_chat(self, prompt: str) -> AsyncIterator[bytes]:
        """Yield the prompt followed by streamed model response chunks."""
        user_msg = {
            "role": "user",
            "content": prompt,
        }
        yield orjson.dumps(user_msg) + b"\n"

        async with httpx2.AsyncClient(base_url=self.base_url) as client:
            async with client.stream(
                "POST",
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = orjson.loads(line.removeprefix("data: "))
                        choices = data.get("choices", [])
                        if not choices:
                            continue
                        content = choices[0].get("delta", {}).get("content", "")
                        if content:
                            model_msg = {"role": "model", "content": content}
                            yield orjson.dumps(model_msg) + b"\n"


def get_llm_service(base_url: str | None = None) -> StreamLLMService:
    """Build the service using the supplied URL or its local default."""
    return StreamLLMService(base_url=base_url or "http://localhost:11434/v1")
