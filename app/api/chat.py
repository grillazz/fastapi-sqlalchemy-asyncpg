"""Websocket endpoint implementing the chat flow.

Mirrors the Pydantic AI chat-app interaction pattern: a client connects,
receives a ``connected`` event with its session id, may ``start`` a
conversation (optionally seeding a system prompt), then repeatedly sends
``user_message`` events. Each user message is appended to the session's
message history (role/content shaped like Pydantic AI's message history) and
forwarded to the pluggable :class:`~app.services.chat_agent.ChatAgent`, whose
reply is streamed back as ``assistant_chunk`` events followed by a single
aggregated ``assistant_message``. Clients can also request the full history
(``history_request``) or gracefully close the conversation (``end``).

Example flow (JSON payloads, one per websocket text frame)::

    -> (connect)
    <- {"type": "connected", "session_id": "..."}
    -> {"type": "start", "system_prompt": "You are a helpful assistant."}
    <- {"type": "started", "session_id": "..."}
    -> {"type": "user_message", "content": "Hello there"}
    <- {"type": "assistant_chunk", "index": 0, "content": "Hello "}
    <- {"type": "assistant_chunk", "index": 1, "content": "there! "}
    <- {"type": "assistant_message", "message": {"role": "assistant", "content": "Hello there! "}}
    -> {"type": "history_request"}
    <- {"type": "history", "messages": [...]}
    -> {"type": "end"}
    (connection closed by client/server)
"""

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter, ValidationError
from rotoger import get_logger

from app.schemas.chat import (
    AssistantChunk,
    AssistantMessage,
    ChatError,
    ChatMessage,
    ClientEvent,
    Connected,
    ConversationStarted,
    EndConversation,
    HistoryResponse,
    RequestHistory,
    SendUserMessage,
    StartConversation,
)
from app.services.chat_agent import ChatAgent
from app.services.chat_session import ChatSession, ChatSessionManager

logger = get_logger()

router = APIRouter()

_client_event_adapter: TypeAdapter[Any] = TypeAdapter(ClientEvent)


async def _handle_start(
    websocket: WebSocket, session: ChatSession, event: StartConversation
) -> None:
    session.messages.clear()
    if event.system_prompt:
        session.add(ChatMessage(role="system", content=event.system_prompt))
    await websocket.send_json(
        ConversationStarted(session_id=session.id).model_dump(mode="json")
    )


async def _handle_user_message(
    websocket: WebSocket, session: ChatSession, agent: ChatAgent, event: SendUserMessage
) -> None:
    session.add(ChatMessage(role="user", content=event.content))

    chunks: list[str] = []
    index = 0
    async for chunk in agent.stream_reply(session.history()):
        chunks.append(chunk)
        await websocket.send_json(
            AssistantChunk(index=index, content=chunk).model_dump(mode="json")
        )
        index += 1

    assistant_message = ChatMessage(role="assistant", content="".join(chunks))
    session.add(assistant_message)
    await websocket.send_json(
        AssistantMessage(message=assistant_message).model_dump(mode="json")
    )


async def _handle_history_request(websocket: WebSocket, session: ChatSession) -> None:
    await websocket.send_json(
        HistoryResponse(messages=session.history()).model_dump(mode="json")
    )


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket) -> None:
    """Websocket chat endpoint. See module docstring for the event flow."""
    await websocket.accept()

    agent: ChatAgent = websocket.app.chat_agent
    session_manager: ChatSessionManager = ChatSessionManager()
    session = await session_manager.create()

    await websocket.send_json(Connected(session_id=session.id).model_dump(mode="json"))

    try:
        while True:
            raw = await websocket.receive_json()
            try:
                event = _client_event_adapter.validate_python(raw)
            except ValidationError as exc:
                await websocket.send_json(
                    ChatError(message=f"Invalid event: {exc}").model_dump(mode="json")
                )
                continue

            match event:
                case StartConversation():
                    await _handle_start(websocket, session, event)
                case SendUserMessage():
                    await _handle_user_message(websocket, session, agent, event)
                case RequestHistory():
                    await _handle_history_request(websocket, session)
                case EndConversation():
                    break
    except WebSocketDisconnect:
        await logger.ainfo("Chat websocket disconnected", session_id=str(session.id))
    finally:
        await session_manager.remove(session.id)
