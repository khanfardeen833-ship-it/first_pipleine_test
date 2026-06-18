"""
Real Pexels image search — resolves image-element `query` strings into actual
photo URLs.

Why this exists: the model can't know which numeric Pexels photo ID maps to
which picture, so when it fabricates `https://images.pexels.com/photos/{id}/...`
URLs the result is a random photo (a dog, a cliff, ...). Instead, image elements
carry a `query` (e.g. "bubble tea pastel cups") and this module turns it into a
real, relevant URL via the Pexels search API before the images are downloaded.

Needs PEXELS_API_KEY in the environment; if it's missing we leave srcs untouched.
"""

import asyncio
import os
from pathlib import Path

import httpx

SEARCH_URL = "https://api.pexels.com/v1/search"
SEARCH_TIMEOUT = 12.0
PER_PAGE = 12


def _api_key() -> str | None:
    return os.getenv("PEXELS_API_KEY")


def _image_elements(specs: list):
    for spec in specs:
        for el in (spec or {}).get("elements", []):
            if el.get("kind") == "image":
                yield el


def _orientation(el: dict) -> str:
    w = el.get("width") or 0
    h = el.get("height") or 0
    if h and w and h > w * 1.15:
        return "portrait"
    if w and h and w > h * 1.15:
        return "landscape"
    return "landscape"


def _best_url(photo: dict) -> str:
    src = photo.get("src", {}) or {}
    return (src.get("large2x") or src.get("large")
            or src.get("original") or src.get("medium") or "")


async def _search(client: httpx.AsyncClient, key: str, query: str,
                  orientation: str) -> list[dict]:
    resp = await client.get(
        SEARCH_URL,
        params={"query": query, "per_page": PER_PAGE, "orientation": orientation},
        headers={"Authorization": key},
        timeout=SEARCH_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("photos", []) or []


async def resolve_image_queries(specs: list) -> int:
    """For every image element carrying a non-empty `query`, set its `src` to a
    real Pexels photo URL. Distinct photos are handed out across elements so the
    same picture doesn't repeat. Returns the number of elements resolved.

    A guessed/legacy `src` is overwritten only when a `query` is present, so the
    model opts in by emitting `query`. Safe no-op without PEXELS_API_KEY."""
    key = _api_key()
    els = [el for el in _image_elements(specs) if (el.get("query") or "").strip()]
    if not els:
        return 0
    if not key:
        print("  [images] no PEXELS_API_KEY — leaving image srcs as-is")
        return 0

    # One API call per unique (query, orientation).
    wanted = {((el["query"].strip().lower()), _orientation(el)) for el in els}

    async with httpx.AsyncClient() as client:
        async def fetch(pair):
            query, orientation = pair
            try:
                return pair, await _search(client, key, query, orientation)
            except Exception as e:  # noqa: BLE001 — log and skip, never crash gen
                print(f"  [images] search miss {query!r}: {e}")
                return pair, []
        results = dict(await asyncio.gather(*[fetch(p) for p in wanted]))

    used_ids: set[int] = set()
    resolved = 0
    for el in els:
        query = el["query"].strip().lower()
        orientation = _orientation(el)
        photos = (results.get((query, orientation))
                  or results.get((query, "landscape"))
                  or results.get((query, "portrait")) or [])
        pick = next((p for p in photos if p.get("id") not in used_ids), None)
        if pick is None and photos:
            pick = photos[0]  # exhausted uniques — reuse rather than drop
        url = _best_url(pick) if pick else ""
        if url:
            used_ids.add(pick.get("id"))
            el["src"] = url
            resolved += 1
    print(f"  [images] resolved {resolved}/{len(els)} image quer(y/ies) "
          f"via Pexels search")
    return resolved
