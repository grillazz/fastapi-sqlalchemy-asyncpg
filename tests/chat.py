import anyio
import httpx
import orjson


async def chat_with_endpoint():
    async with httpx.AsyncClient() as client:
        while True:
            # Get user input
            prompt = input("\nYou: ")
            if prompt.lower() == "exit":
                break

            # Send request to the API
            print("\nModel: ", end="", flush=True)
            async with client.stream(
                "POST",
                "http://0.0.0.0:8080/v1/ml/chat/",
                data={"prompt": prompt},
                timeout=60,
            ) as response:
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = orjson.loads(chunk)
                            print(data["content"], end="", flush=True)
                        except Exception as e:
                            print(f"\nError parsing chunk: {e}")


if __name__ == "__main__":
    anyio.run(chat_with_endpoint)
