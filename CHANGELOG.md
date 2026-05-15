# Changelog

## 0.1.0 — 2026-05-14

- Initial release. Three tools wrapping the Alkira Knowledge Plane REST API: `kb_search`, `kb_personas`, `kb_feedback`. Deliberately narrow — see README design note.
- Stdio transport via `mcp.server.fastmcp.FastMCP`.
- Auth via `ALKIRA_API_KEY` env var; host overridable via `ALKIRA_KB_HOST` (default `rfp.alkira.cc`).
- Distributed via `uvx --from git+...` — no PyPI publish step.
