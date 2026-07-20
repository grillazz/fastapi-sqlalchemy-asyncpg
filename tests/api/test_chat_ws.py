"""Tests for the websocket chat service using the local stub agent.

Uses Starlette's synchronous ``TestClient`` websocket support (rather than
the ``httpx.AsyncClient`` fixture used elsewhere) since it triggers the
FastAPI lifespan on ``__enter__``/``__exit__``, wiring up
``app.chat_agent`` / ``app.state.chat_sessions`` exactly like a real
server run.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.anyio


async def test_chat_ws_full_conversation_flow() -> None:
    with (
        TestClient(app) as client,
        client.websocket_connect("/v1/chat/ws") as websocket,
    ):
        # 1. connect
        connected = websocket.receive_json()
        assert connected["type"] == "connected"
        session_id = connected["session_id"]

        # 2. start conversation with a system prompt
        websocket.send_json(
            {"type": "start", "system_prompt": "You are a helpful assistant."}
        )
        started = websocket.receive_json()
        print(f"{started=}")
        assert started == {"type": "started", "session_id": session_id}

        # 3. send a user message and aggregate the streamed assistant chunks
        websocket.send_json({"type": "user_message", "content": "hello"})

        event = websocket.receive_json()
        aggregated = ""
        while event["type"] == "assistant_chunk":
            assert event["index"] >= 0
            aggregated += event["content"]
            event = websocket.receive_json()

        assert event["type"] == "assistant_message"
        assert event["message"]["role"] == "assistant"
        assert event["message"]["content"] == aggregated
        print(f"{event=}")
        print(f"{aggregated=}")
        assert "hello" in aggregated.lower()

        # 4. request full history (system + user + assistant)
        websocket.send_json({"type": "history_request"})
        history = websocket.receive_json()
        assert history["type"] == "history"
        roles = [m["role"] for m in history["messages"]]
        assert roles == ["system", "user", "assistant"]

        # 5. gracefully end the conversation
        websocket.send_json({"type": "end"})


async def test_chat_ws_invalid_event_returns_error() -> None:
    with (
        TestClient(app) as client,
        client.websocket_connect("/v1/chat/ws") as websocket,
    ):
        websocket.receive_json()  # connected

        websocket.send_json({"type": "not_a_real_event"})
        error = websocket.receive_json()
        assert error["type"] == "error"

        websocket.send_json({"type": "end"})


async def test_chat_ws_ask_question_and_print_model_answer() -> None:
    """Ask a real question over the websocket chat and print the model's answer.

    Runs against whatever ``ChatAgent`` is wired up via ``app.state.chat_agent``
    (the local stub agent by default, or a real Ollama-backed agent when
    ``CHAT_BACKEND=ollama`` is configured), exercising the full websocket
    conversation flow end-to-end.
    """
    question = "What is the capital of France?"

    with (
        TestClient(app) as client,
        client.websocket_connect("/v1/chat/ws") as websocket,
    ):
        # 1. connect
        connected = websocket.receive_json()
        assert connected["type"] == "connected"
        session_id = connected["session_id"]

        # 2. start conversation
        websocket.send_json(
            {"type": "start", "system_prompt": "You are a helpful assistant."}
        )
        started = websocket.receive_json()
        assert started == {"type": "started", "session_id": session_id}

        # 3. ask the question and aggregate the streamed answer
        websocket.send_json({"type": "user_message", "content": question})

        event = websocket.receive_json()
        answer = ""
        while event["type"] == "assistant_chunk":
            answer += event["content"]
            event = websocket.receive_json()

        assert event["type"] == "assistant_message"
        answer = event["message"]["content"]

        print(f"\nQuestion: {question}")
        print(f"Model answer: {answer}")

        assert isinstance(answer, str)
        assert answer.strip() != ""

        # 4. gracefully end the conversation
        websocket.send_json({"type": "end"})

