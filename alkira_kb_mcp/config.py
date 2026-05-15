"""Environment-driven config for the MCP server."""
from __future__ import annotations

import os

ALKIRA_KB_HOST = os.getenv("ALKIRA_KB_HOST", "rfp.alkira.cc")
ALKIRA_API_KEY = os.getenv("ALKIRA_API_KEY", "")

BASE_URL = f"https://{ALKIRA_KB_HOST}/api/v1"

# Answer / triage can hit Gemini Pro for 5-8s/call; triage batches can be longer still.
DEFAULT_TIMEOUT = 90.0


def assert_configured() -> None:
    """Raise if required env vars are missing. Called once at server startup."""
    if not ALKIRA_API_KEY:
        raise RuntimeError(
            "ALKIRA_API_KEY is not set. Add it to the MCP server's env block "
            "in your Claude Desktop / Claude Code config."
        )
