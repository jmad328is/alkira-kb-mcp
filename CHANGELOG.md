# Changelog

## 0.2.0 — 2026-06-09

- Added streamable-HTTP transport (`server_http.py`) for remote-MCP clients that can't spawn a local stdio server (browser-based Claude, cowork, computer-use sessions, custom claude.ai connectors).
- Tool definitions extracted to shared `mcp_app.py`; both stdio (`server.py`) and HTTP (`server_http.py`) entries import the same `mcp` instance and tool registrations.
- HTTP entry: bearer-token middleware (constant-time compare against `MCP_HTTP_BEARER_TOKEN` env var) — server returns 401 for missing/wrong header.
- HTTP entry: FastMCP DNS-rebinding protection disabled (`TransportSecuritySettings(enable_dns_rebinding_protection=False)`) so the Cloud Run `*.run.app` hostname doesn't get rejected. Safe because Cloud Run's load balancer validates Host upstream + bearer middleware does real auth.
- New `Dockerfile` + `cloudbuild.yaml` for the HTTP container. Deployed to `alkira-sales` GCP project as Cloud Run service `alkira-kb-mcp-http`. Public + bearer-gated. URL stable: derive via `gcloud run services describe alkira-kb-mcp-http --region=us-central1 --project=alkira-sales --format='value(status.url)'`.
- `config.py` split: `assert_configured_stdio()` for stdio entry, `assert_configured_http()` for HTTP entry (also checks `MCP_HTTP_BEARER_TOKEN`).
- `pyproject.toml`: version bump 0.1.0 → 0.2.0, optional `http` dep group (`uvicorn[standard]`), new `alkira-kb-mcp-http` console script.

The stdio package install path is unchanged — `uvx --from git+https://github.com/jmad328is/alkira-kb-mcp alkira-kb-mcp` still works for Claude Desktop / Code users.

## 0.1.0 — 2026-05-14

- Initial release. Three tools wrapping the Alkira Knowledge Plane REST API: `kb_search`, `kb_personas`, `kb_feedback`. Deliberately narrow — see README design note.
- Stdio transport via `mcp.server.fastmcp.FastMCP`.
- Auth via `ALKIRA_API_KEY` env var; host overridable via `ALKIRA_KB_HOST` (default `rfp.alkira.cc`).
- Distributed via `uvx --from git+...` — no PyPI publish step.
