import httpx
import orjson
from typing import AsyncGenerator, Optional


class StreamLLMService:
    def __init__(self, base_url: str = "http://localhost:11434/v1"):
        self.base_url = base_url
        self.model = "llama3.2"

    async def stream_chat(self, prompt: str) -> AsyncGenerator[bytes, None]:
        """Stream chat completion responses from LLM."""
        # Send user message first
        user_msg = {
            "role": "user",
            "content": prompt,
        }
        yield orjson.dumps(user_msg) + b"\n"

        # Open client as context manager and stream responses
        async with httpx.AsyncClient(base_url=self.base_url) as client:
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
                        try:
                            json_line = line[6:]  # Remove "data: " prefix
                            data = orjson.loads(json_line)
                            content = (
                                data.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if content:
                                model_msg = {"role": "model", "content": content}
                                yield orjson.dumps(model_msg) + b"\n"
                        except Exception:
                            pass


# FastAPI dependency
def get_llm_service(base_url: Optional[str] = None) -> StreamLLMService:
    return StreamLLMService(base_url=base_url or "http://localhost:11434/v1")
