"""
Local image cache shared by the QA preview renderer and the PPTX exporter.

Slide specs reference remote (Pexels) URLs. Downloading them once into
run_dir/images/ right after the specs land means:
  - the QA screenshot pass doesn't wait ~10-25s on remote image loads
  - the PPTX exporter reuses the local copies instead of re-downloading
  - a flaky/404 URL is discovered once (missing from the manifest; the
    preview falls back to the remote URL, renders broken, and the visual
    QA judge flags it for regeneration)

Layout: run_dir/images/<sha1[:16]>.<ext> + manifest.json {url: filename}.
"""

import asyncio
import hashlib
import json
from pathlib import Path

import httpx  # dependency of the anthropic SDK, already installed

FETCH_TIMEOUT = 12.0
_EXT_BY_MIME = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp",
                "image/gif": "gif", "image/svg+xml": "svg"}


def image_urls_from_specs(specs: list) -> list[str]:
    """Unique remote image srcs across slide specs, in first-seen order."""
    seen, out = set(), []
    for spec in specs:
        for el in (spec or {}).get("elements", []):
            src = el.get("src") or el.get("url") or ""
            if (el.get("kind") == "image" and src.startswith(("http://", "https://"))
                    and src not in seen):
                seen.add(src)
                out.append(src)
    return out


def load_manifest(run_dir: Path) -> dict:
    p = Path(run_dir) / "images" / "manifest.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


async def _fetch_one(client: httpx.AsyncClient, url: str, img_dir: Path) -> tuple[str, str] | None:
    try:
        resp = await client.get(url, timeout=FETCH_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        mime = (resp.headers.get("content-type") or "image/jpeg").split(";")[0].strip()
        ext = _EXT_BY_MIME.get(mime, "jpg")
        fname = f"{hashlib.sha1(url.encode()).hexdigest()[:16]}.{ext}"
        (img_dir / fname).write_bytes(resp.content)
        return url, fname
    except Exception as e:
        print(f"  [images] miss {url[:70]}: {e}")
        return None


async def prefetch_images(specs: list, run_dir: Path) -> dict:
    """Download every image URL in the specs into run_dir/images/.
    Returns and persists the {url: filename} manifest (merged with any
    existing manifest, so QA-regenerated slides only fetch what's new)."""
    run_dir = Path(run_dir)
    img_dir = run_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest(run_dir)

    todo = [u for u in image_urls_from_specs(specs) if u not in manifest]
    if todo:
        async with httpx.AsyncClient() as client:
            results = await asyncio.gather(*[
                _fetch_one(client, u, img_dir) for u in todo])
        manifest.update(dict(r for r in results if r))
        print(f"  [images] cached {sum(1 for r in results if r)}/{len(todo)} "
              f"new image(s) -> {img_dir.name}/")
    (img_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
