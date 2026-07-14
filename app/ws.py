"""Thin re-export module matching the suggested ``app/ws.py`` layout.

The actual websocket router lives in :mod:`app.api.chat` (consistent with
this project's convention of keeping all routers under ``app/api``). This
module simply re-exports it so the chat service can also be wired up as
``from app.ws import router``.
"""

from app.api.chat import router

__all__ = ["router"]
