"""Shared FastMCP app + tool registrations.

Both the stdio entry (`server.py`) and the HTTP entry (`server_http.py`) import
the `mcp` instance from this module. Tool definitions live here so we don't
duplicate them across transports.
"""
from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .client import KBClient

# Disable FastMCP's DNS-rebinding protection. Default `allowed_hosts=[]` rejects
# Cloud Run's *.run.app hostname with HTTP 421. We're behind Google's load
# balancer (host validation already happens upstream) AND every request is
# bearer-token gated (the real auth check). DNS-rebinding protection at the
# app layer is redundant and breaks the Cloud Run path. No effect on stdio
# (stdio doesn't process Host headers).
_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
)

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
    transport_security=_security,
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
