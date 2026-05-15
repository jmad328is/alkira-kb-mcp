"""Thin async httpx wrapper over the Alkira Knowledge Plane REST API."""
from __future__ import annotations

from typing import Any, Optional

import httpx

from .config import ALKIRA_API_KEY, BASE_URL, DEFAULT_TIMEOUT


class KBClient:
    """One-process httpx.AsyncClient bound to the Knowledge Plane.

    Singleton-style: instantiated lazily by the server, reused across tool calls,
    closed only when the process exits.
    """

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"X-API-Key": ALKIRA_API_KEY},
            timeout=DEFAULT_TIMEOUT,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str) -> dict[str, Any]:
        resp = await self._client.get(path)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        resp = await self._client.post(path, json=body)
        resp.raise_for_status()
        return resp.json()

    async def personas(self) -> dict[str, Any]:
        return await self._get("/personas")

    async def search(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query, "top_k": top_k}
        if collection:
            body["collection"] = collection
        return await self._post("/search", body)

    async def feedback(
        self,
        query: str,
        answer: str,
        rating: str,
        correction: Optional[str] = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"query": query, "answer": answer, "rating": rating}
        if correction is not None:
            body["correction"] = correction
        return await self._post("/feedback", body)
