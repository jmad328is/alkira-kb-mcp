"""Environment-driven config for the MCP server."""
from __future__ import annotations

import os

# Backend Knowledge Plane API — same target for both stdio and HTTP servers.
ALKIRA_KB_HOST = os.getenv("ALKIRA_KB_HOST", "rfp.alkira.cc")
ALKIRA_API_KEY = os.getenv("ALKIRA_API_KEY", "")

BASE_URL = f"https://{ALKIRA_KB_HOST}/api/v1"

# Answer / triage can hit Gemini Pro for 5-8s/call; triage batches can be longer still.
DEFAULT_TIMEOUT = 90.0


def assert_configured_stdio() -> None:
    """Stdio server startup check — only needs the backend key.

    Stdio clients (Claude Desktop / Code) authenticate against this server
    implicitly by spawning it themselves; no inbound auth.
    """
    if not ALKIRA_API_KEY:
        raise RuntimeError(
            "ALKIRA_API_KEY is not set. Add it to the MCP server's env block "
            "in your Claude Desktop / Claude Code config."
        )


def assert_configured_http() -> None:
    """HTTP server startup check — needs backend key AND inbound bearer token.

    Inbound auth: every request must carry an Authorization: Bearer header
    matching MCP_HTTP_BEARER_TOKEN. The HTTP server is publicly reachable,
    so token absence is a fatal configuration error.
    """
    assert_configured_stdio()
    if not os.getenv("MCP_HTTP_BEARER_TOKEN"):
        raise RuntimeError(
            "MCP_HTTP_BEARER_TOKEN is not set. The HTTP MCP server requires "
            "a bearer token for inbound auth. Set this from Secret Manager "
            "in the Cloud Run service env block."
        )
