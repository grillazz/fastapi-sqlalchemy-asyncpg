"""In-memory conversation/session management for the websocket chat service.

Sessions are intentionally kept simple (a dict guarded by an ``asyncio.Lock``)
since each websocket connection owns exactly one session for its lifetime.
Swapping this for a Redis-backed store later (for multi-worker deployments)
only requires changing this module; the websocket endpoint only depends on
the small public API below.
"""

import asyncio
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.schemas.chat import ChatMessage


@dataclass(slots=True)
class ChatSession:
    id: UUID = field(default_factory=uuid4)
    messages: list[ChatMessage] = field(default_factory=list)

    def add(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def history(self) -> list[ChatMessage]:
        return list(self.messages)


class ChatSessionManager:
    """Tracks active chat sessions keyed by their opaque session id."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, ChatSession] = {}
        self._lock = asyncio.Lock()

    async def create(self) -> ChatSession:
        session = ChatSession()
        async with self._lock:
            self._sessions[session.id] = session
        return session

    async def get(self, session_id: UUID) -> ChatSession | None:
        async with self._lock:
            return self._sessions.get(session_id)

    async def remove(self, session_id: UUID) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def count(self) -> int:
        async with self._lock:
            return len(self._sessions)
