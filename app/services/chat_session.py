"""In-memory conversation/session management for the websocket chat service.

Sessions are intentionally kept simple (a dict guarded by an ``asyncio.Lock``)
since each websocket connection owns exactly one session for its lifetime.
Swapping this for a Redis-backed store later (for multi-worker deployments)
only requires changing this module; the websocket endpoint only depends on
the small public API below.
"""

import asyncio
from uuid import UUID, uuid4

import attrs

from app.schemas.chat import ChatMessage


@attrs.define(slots=True)
class ChatSession:
    """Conversation history associated with one websocket connection."""

    id: UUID = attrs.field(factory=uuid4)
    messages: list[ChatMessage] = attrs.field(factory=list)

    def add(self, message: ChatMessage) -> None:
        """Append a message to this conversation."""
        self.messages.append(message)

    def history(self) -> list[ChatMessage]:
        """Return a copy of the conversation history."""
        return list(self.messages)


class ChatSessionManager:
    """Tracks active chat sessions keyed by their opaque session id.

    Each application lifespan owns its own manager, maintaining a consistent
    registry of active websocket chat sessions for that application.
    """

    def __init__(self) -> None:
        """Create an empty, lock-protected session registry."""
        self._sessions: dict[UUID, ChatSession] = {}
        self._lock = asyncio.Lock()

    async def create(self) -> ChatSession:
        """Create and register a new conversation."""
        session = ChatSession()
        async with self._lock:
            self._sessions[session.id] = session
        return session

    async def get(self, session_id: UUID) -> ChatSession | None:
        """Return the matching session, if it is active."""
        async with self._lock:
            return self._sessions.get(session_id)

    async def remove(self, session_id: UUID) -> None:
        """Remove a session from the active registry."""
        async with self._lock:
            self._sessions.pop(session_id, None)

    async def count(self) -> int:
        """Return the number of active sessions."""
        async with self._lock:
            return len(self._sessions)
