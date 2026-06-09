"""Alkira Knowledge Plane — streamable-HTTP MCP server.

Container-deployed to Cloud Run in the `alkira-sales` GCP project. Reachable
publicly at the Cloud Run URL; bearer-token auth on every request.

Why a separate entry from `server.py`: the stdio package is distributed to
SE laptops via uvx; this HTTP server is for remote clients (browser-based
Claude, claude.ai connectors, computer-use sessions) that can't run a local
stdio MCP. Same tool surface, different transport, different auth model.

Tool definitions are shared via `mcp_app.py`.
"""
from __future__ import annotations

import os
import secrets

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from .config import assert_configured_http
from .mcp_app import mcp


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Reject requests without a valid `Authorization: Bearer <token>` header.

    Compares the supplied token against MCP_HTTP_BEARER_TOKEN env var using
    constant-time compare. Returns 401 on any miss.
    """

    def __init__(self, app: ASGIApp, expected_token: str) -> None:
        super().__init__(app)
        self._expected_token = expected_token

    async def dispatch(self, request, call_next):
        auth_header = request.headers.get("authorization", "")
        prefix = "Bearer "
        if not auth_header.startswith(prefix):
            return JSONResponse(
                {"error": "Missing or malformed Authorization header"},
                status_code=401,
            )

        supplied = auth_header[len(prefix):].strip()
        if not secrets.compare_digest(supplied, self._expected_token):
            return JSONResponse({"error": "Invalid bearer token"}, status_code=401)

        return await call_next(request)


def build_app(bearer_token: str) -> Starlette:
    """Build the wrapped Starlette app for streamable-HTTP MCP.

    The FastMCP SDK exposes a Starlette ASGI app via streamable_http_app();
    we wrap it with bearer-token middleware before serving.
    """
    inner_app = mcp.streamable_http_app()
    inner_app.add_middleware(BearerTokenMiddleware, expected_token=bearer_token)
    return inner_app


def main() -> None:
    """Console-script entry. Serves streamable-HTTP MCP via uvicorn.

    Honors PORT env var (default 8080 — Cloud Run injects this). Bind to
    0.0.0.0 since Cloud Run routes traffic to the container's port.
    """
    import uvicorn

    assert_configured_http()
    bearer_token = os.environ["MCP_HTTP_BEARER_TOKEN"]
    port = int(os.getenv("PORT", "8080"))

    app = build_app(bearer_token)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
