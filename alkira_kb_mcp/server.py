"""Alkira Knowledge Plane — stdio MCP server.

Exposes three tools wrapping the rfp.alkira.cc REST API:

- kb_search   — retrieve excerpts from the Knowledge Plane (no LLM)
- kb_feedback — record thumbs-up/down + corrections
- kb_personas — list personas (cheap metadata, useful for framing answers)

The host is overridable via ALKIRA_KB_HOST env var (default rfp.alkira.cc);
auth is the X-API-Key header set from ALKIRA_API_KEY.

Why this narrow surface? See README for the design note. tl;dr: agents have
their own LLM and full conversation context, so server-side generation
(`/answer`, `/triage`) is duplicative and expensive. Agents should call
`kb_search` and synthesize themselves.
"""
from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import KBClient
from .config import assert_configured

mcp = FastMCP(
    "alkira-kb",
    instructions=(
        "Alkira's Knowledge Plane — answers questions about Alkira's product, "
        "deployment guides, RFP responses, and competitive positioning. Call "
        "kb_search to retrieve excerpts, then synthesize the answer yourself "
        "using your own context. Use kb_personas to see the framing styles "
        "used elsewhere (RFP-formal, security-qa, etc.) if you want a hint at "
        "how to shape an answer. Record kb_feedback when the user signals "
        "thumbs-up/down so the corpus learns."
    ),
)

_kb: KBClient | None = None


def _client() -> KBClient:
    global _kb
    if _kb is None:
        _kb = KBClient()
    return _kb


@mcp.tool()
async def kb_search(
    query: str,
    top_k: int = 5,
    collection: Optional[str] = None,
) -> dict[str, Any]:
    """Retrieve relevant document excerpts from the Knowledge Plane (no LLM).

    Args:
        query: Natural-language query or keywords.
        top_k: Max excerpts to return (1-20, default 5).
        collection: "rfp-formal" (security/compliance) or "sales-kb" (product/competitive). Omit for cross-collection fan-out.

    Returns {results: [{title, source, source_url, relevance, collection, text}], search_type, elapsed_ms}.
    Each result.source_url is a clickable Drive link where available — surface these to the user.
    """
    return await _client().search(query=query, collection=collection, top_k=top_k)


@mcp.tool()
async def kb_personas() -> dict[str, Any]:
    """List Knowledge Plane personas (framing styles used by the Answer Machine UIs).

    Useful as a hint when you're shaping an answer — e.g., persona "rfp-formal"
    suggests structured RFP prose, "security-qa" suggests compliance-questionnaire
    phrasing, "competitive" suggests differentiation framing.

    Returns a map of {persona_id: {name, description, search_strategy}}.
    """
    return await _client().personas()


@mcp.tool()
async def kb_feedback(
    query: str,
    answer: str,
    rating: str,
    correction: Optional[str] = None,
) -> dict[str, Any]:
    """Record feedback on a Knowledge Plane answer.

    Thumbs-down with a `correction` adds a fact-store entry that steers
    future answers to similar questions. Use sparingly — corrections do not
    auto-decay today.

    Args:
        query: The original question.
        answer: The answer that was rated (verbatim, so feedback log correlates).
        rating: "up" or "down".
        correction: Optional corrected answer. Only meaningful when rating="down".

    Returns {status: "recorded", fact_created: bool}.
    """
    return await _client().feedback(
        query=query, answer=answer, rating=rating, correction=correction
    )


def main() -> None:
    """Console-script entry. Runs the stdio MCP server."""
    assert_configured()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
