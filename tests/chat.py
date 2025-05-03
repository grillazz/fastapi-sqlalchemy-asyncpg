import anyio
import httpx
import orjson

API_URL = "http://localhost:8000/chat/"


async def chat_with_endpoint():
    async with httpx.AsyncClient() as client:
        while True:
            prompt = input("\nYou: ")
            if prompt.lower() == "exit":
                break

            print("\nModel: ", end="", flush=True)
            try:
                async with client.stream(
                    "POST", API_URL, data={"prompt": prompt}, timeout=60
                ) as response:
                    async for chunk in response.aiter_lines():
                        if not chunk:
                            continue

                        try:
                            print(orjson.loads(chunk)["content"], end="", flush=True)
                        except Exception as e:
                            print(f"\nError parsing chunk: {e}")
            except httpx.RequestError as e:
                print(f"\nConnection error: {e}")


if __name__ == "__main__":
    anyio.run(chat_with_endpoint)
