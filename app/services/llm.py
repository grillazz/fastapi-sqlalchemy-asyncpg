import httpx
import orjson
from typing import AsyncGenerator, Optional


class StreamLLMService:
    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        self.base_url = base_url
        self.model = "llama3.2"

    async def stream_chat(self, prompt: str) -> AsyncGenerator[bytes, None]:
        """Stream chat completion responses from LLM."""
        # Send initial user message
        yield orjson.dumps({"role": "user", "content": prompt}) + b"\n"

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            }

            async with client.stream(
                "POST", "/chat/completions", json=request_data, timeout=60.0
            ) as response:
                async for line in response.aiter_lines():
                    if not (line.startswith("data: ") and line != "data: [DONE]"):
                        continue
                    try:
                        data = orjson.loads(line[6:])  # Skip "data: " prefix
                        if (
                            content := data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        ):
                            yield (
                                orjson.dumps({"role": "model", "content": content})
                                + b"\n"
                            )
                    except Exception:
                        pass


def get_llm_service(base_url: Optional[str] = None) -> StreamLLMService:
    return StreamLLMService(base_url=base_url)
