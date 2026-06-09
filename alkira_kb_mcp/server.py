"""Alkira Knowledge Plane — stdio MCP server.

Distributed via `uvx --from git+https://github.com/jmad328is/alkira-kb-mcp
alkira-kb-mcp`. Runs locally on the SE's machine, speaks stdio to Claude
Desktop / Claude Code. Calls the rfp.alkira.cc REST API over HTTPS for the
actual data.

Tool definitions live in `mcp_app.py` and are shared with the HTTP entry
point (`server_http.py`).
"""
from __future__ import annotations

from .config import assert_configured_stdio
from .mcp_app import mcp


def main() -> None:
    """Console-script entry. Runs the stdio MCP server."""
    assert_configured_stdio()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
