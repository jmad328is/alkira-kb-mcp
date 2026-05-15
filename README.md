# alkira-kb-mcp

MCP server for the **Alkira Answer Machine** — the Knowledge Plane (`rfp.alkira.cc`) as native tool calls in Claude Desktop or Claude Code.

Three tools, stdio transport, distributed via `uvx`. No server-side changes, no PyPI publish.

## Setup

### 1. Install `uv` (one-time)

```bash
brew install uv
# or: pip install uv
```

`uvx` ships with `uv`.

### 2. Get your API key

Ask Justin for an MCP-clients API key (separate from the shared UI key so MCP traffic shows up distinctly in logs).

### 3. Add to your Claude Desktop config

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "alkira-kb": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/jmad328is/alkira-kb-mcp",
        "alkira-kb-mcp"
      ],
      "env": {
        "ALKIRA_API_KEY": "<your-mcp-key>"
      }
    }
  }
}
```

Restart Claude Desktop. First invocation downloads + caches the package (~5-10s); subsequent invocations are instant.

For **Claude Code**, the equivalent block goes in `~/.claude/settings.json` under `mcpServers` — same shape.

### 4. (Optional) Override the host

If you're testing against a different host (staging, the planned `kb.alkira.cc` cutover), add `ALKIRA_KB_HOST` to the `env` block:

```json
"env": {
  "ALKIRA_API_KEY": "...",
  "ALKIRA_KB_HOST": "kb.alkira.cc"
}
```

Default is `rfp.alkira.cc`.

## Tools

| Tool | What it does |
|---|---|
| `kb_search` | Retrieve excerpts from the Knowledge Plane (no LLM). Cross-collection fan-out by default. Returns text + Drive citations. |
| `kb_personas` | List the framing styles used elsewhere (`rfp-formal`, `security-qa`, `competitive`, …) — useful as a hint for how to shape an answer. |
| `kb_feedback` | Record thumbs up/down. Thumbs-down + correction adds a fact-store entry that steers future answers. |

## Design note — why only 3 tools?

The REST API exposes 6 endpoints. This package deliberately exposes only the 3 that make sense for an *agent* consumer.

**Excluded:**
- **`/answer` (LLM-generated prose)** — the desktop agent has its own LLM and the user's full conversation context. Calling `/answer` means paying Gemini server-side to write prose that the agent will then re-synthesize anyway. Cleaner: agent calls `kb_search`, synthesizes the answer itself using its own context and the persona hint from `kb_personas`. Cheaper, less telephone-game drift, framing shaped by the actual user.
- **`/triage` (batch classify Auto/Review/Human)** — purpose-built for the Fargate questionnaire UI handling 800-question RFP intake. Not a workflow that fits a local agent.
- **`/models`** — only mattered when `kb_answer` was exposed.

If this assumption changes (e.g., a non-agent MCP consumer appears), revisit.

## Updating

`uvx` caches the package. To force a refresh after this repo updates:

```bash
uvx --refresh --from git+https://github.com/jmad328is/alkira-kb-mcp alkira-kb-mcp --help
```

…or just delete `~/.cache/uv/git-v0/` and restart Claude Desktop.

## Troubleshooting

- **`ALKIRA_API_KEY is not set`** at startup → missing `env.ALKIRA_API_KEY` in your Claude config.
- **`401 Unauthorized`** on every call → key is set but wrong, revoked, or has a trailing newline. Ask Justin.
- **`5xx` on `kb_search`** → Cloud Run cold start. Retry once.
- **No tools showing up in Claude** → `uvx` may have a $PATH issue. Run `which uvx` to confirm; an absolute path in `command` works too.

## License

Proprietary — internal Alkira use only.
