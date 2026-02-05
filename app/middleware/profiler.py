from __future__ import annotations

from fastapi import Request
from pyinstrument import Profiler
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import HTMLResponse, Response


class ProfilingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.query_params.get("pyprofile") == "true":
            profiler = Profiler(interval=0.001, async_mode="enabled")
            profiler.start()

            await call_next(request)

            profiler.stop()
            return HTMLResponse(
                profiler.output_html(),
                headers={"Content-Disposition": "attachment; filename=profile.html"},
            )

        return await call_next(request)