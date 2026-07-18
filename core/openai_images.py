"""
AI image generation provider — a bespoke alternative to Pexels stock search.

Instead of resolving an image element's `query` to a stock photo URL, this
renders a custom, palette-matched image with OpenAI's gpt-image-1 and writes it
into run_dir/images/, registering it in the SAME manifest.json the Pexels cache
uses. Downstream (preview renderer + PPTX exporter) already resolve images via
that manifest, so generated images flow through unchanged.

Opt in with IMAGE_PROVIDER=openai (or config image_provider). Needs
OPENAI_API_KEY (already used by enhance.py). Every prompt gets a shared premium
style suffix so a deck's images read as ONE art-directed set rather than a pile
of unrelated AI pictures — this is what keeps the result looking premium.

Generation runs in parallel (bounded by a semaphore) and de-dupes identical
(prompt, size) pairs so the same picture is never paid for twice. Anything that
fails keeps its `query`, so the Pexels pass that runs afterwards is a natural
fallback.
"""

import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path

MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
DEFAULT_QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "high")   # low|medium|high|auto
MAX_CONCURRENCY = int(os.environ.get("OPENAI_IMAGE_CONCURRENCY", "4"))
GEN_TIMEOUT = 180.0
# transparent | opaque | auto. Use "transparent" for illustration/vector decks so
# the art has no baked background rectangle — it then sits cleanly on ANY slide
# color (a white-bg illustration on a dark slide looks like a pasted box).
BACKGROUND = os.environ.get("OPENAI_IMAGE_BACKGROUND", "auto")

# Shared base direction appended to every prompt so a deck's images read as ONE
# art-directed set. Defaults to premium editorial PHOTOGRAPHY; override the whole
# direction with OPENAI_IMAGE_STYLE to switch families — e.g. flat vector / 3D
# illustration decks (Slidesgo/Freepik-style corporate templates):
#   OPENAI_IMAGE_STYLE="flat 3D isometric vector illustration, corporate,
#     bright blue and cyan palette, clean solid white background, soft rounded
#     shapes, no text, no watermark, no logos"
_DEFAULT_BASE_STYLE = (
    "professional editorial photograph, cinematic soft lighting, "
    "shallow depth of field, refined muted color grade, minimal "
    "clean composition, high detail, photorealistic, "
    "no text, no watermark, no logos, no captions")
_BASE_STYLE = os.environ.get("OPENAI_IMAGE_STYLE", "").strip() or _DEFAULT_BASE_STYLE


def _api_key():
    return os.getenv("OPENAI_API_KEY")


def _image_elements(specs):
    for spec in specs:
        for el in (spec or {}).get("elements", []):
            if el.get("kind") == "image":
                yield el


def _prompt_of(el):
    # A fuller `image_prompt` (a sentence) beats a terse stock `query` for gen.
    return (el.get("image_prompt") or el.get("query") or "").strip()


def _size_for(el):
    """gpt-image-1 supports 1024x1024 / 1536x1024 / 1024x1536 — pick by the
    element's aspect ratio so the image fills its box without hard cropping."""
    w = el.get("width") or 0
    h = el.get("height") or 0
    if h and w and h > w * 1.15:
        return "1024x1536"
    if w and h and w > h * 1.15:
        return "1536x1024"
    return "1024x1024"


def _synthetic(prompt, size):
    """A stable https-scheme key (so the PPTX exporter treats it like a normal
    URL and finds it in the manifest) + the local filename it maps to."""
    h = hashlib.sha1(f"{prompt}|{size}".encode("utf-8")).hexdigest()[:16]
    return f"https://aigen.local/{h}.png", f"{h}.png"


async def generate_image_queries(specs, run_dir, *, style="", quality=None,
                                  concurrency=MAX_CONCURRENCY) -> int:
    """Generate an image for every image element carrying a prompt, cache it
    locally + in the manifest, and point the element's `src` at it. Clears the
    element's `query`/`image_prompt` on success so the later Pexels pass only
    touches failures. Returns the number generated. Safe no-op without a key."""
    key = _api_key()
    els = [el for el in _image_elements(specs) if _prompt_of(el)]
    if not els:
        return 0
    if not key:
        print("  [images] no OPENAI_API_KEY — skipping AI generation")
        return 0

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=key, timeout=GEN_TIMEOUT)
    quality = quality or DEFAULT_QUALITY
    style_suffix = (style.strip() + ", " if style.strip() else "") + _BASE_STYLE

    img_dir = Path(run_dir) / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = img_dir / "manifest.json"
    manifest = (json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest_path.exists() else {})

    jobs = {(_prompt_of(el), _size_for(el)) for el in els}   # unique work only
    sem = asyncio.Semaphore(max(1, concurrency))

    async def run(job):
        prompt, size = job
        url, fname = _synthetic(prompt, size)
        fpath = img_dir / fname
        if fpath.exists():                       # already generated this run
            return job, url
        async with sem:
            try:
                # `background` isn't a typed kwarg in older openai SDKs (<1.66);
                # pass it through extra_body so gpt-image-1 still honors it.
                extra = ({"background": BACKGROUND}
                         if BACKGROUND and BACKGROUND != "auto" else {})
                resp = await client.images.generate(
                    model=MODEL, prompt=f"{prompt}. {style_suffix}",
                    size=size, quality=quality, n=1, extra_body=extra)
                fpath.write_bytes(base64.b64decode(resp.data[0].b64_json))
                return job, url
            except Exception as e:  # noqa: BLE001 — never crash generation
                print(f"  [images] gen miss {prompt[:48]!r}: {e}")
                return job, None

    results = dict(await asyncio.gather(*[run(j) for j in jobs]))

    generated = 0
    for el in els:
        url = results.get((_prompt_of(el), _size_for(el)))
        if url:
            manifest[url] = _synthetic(_prompt_of(el), _size_for(el))[1]
            el["src"] = url
            el.pop("query", None)                # so Pexels won't overwrite it
            el.pop("image_prompt", None)
            generated += 1
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  [images] generated {generated}/{len(els)} image(s) via {MODEL} "
          f"(quality={quality}, parallel x{concurrency}) -> images/")
    return generated
