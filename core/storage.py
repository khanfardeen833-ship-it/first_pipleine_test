"""
MongoDB storage layer.

Collections:
  presentations  — frontend-created, one doc per request
                   { _id, userId, prompt, slides, status, createdAt, updatedAt }
                   status flow:  pending → processing → done | failed

  outlines       — pipeline-created, one doc per presentation
                   { _id, presentationId, userId, status, outline,
                     deckId, summary, createdAt, updatedAt }
                   status flow:  pending → generating → done | failed

  decks          — final rendered deck, one doc per completed outline
                   { _id, outlineId, presentationId, userId,
                     slides, summary, createdAt }
                   slides[] — merged per-slide format: every element has
                   content + design (position, style, animation) together
"""

import os
from datetime import datetime, timezone

import motor.motor_asyncio

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        uri = os.environ.get("MONGODB_URI", "")
        if not uri:
            raise RuntimeError("MONGODB_URI env var not set")
        _client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        db_name = uri.rstrip("/").split("/")[-1].split("?")[0] or "bildory-editor"
        _db = _client[db_name]
    return _db


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# presentations collection  (owned by frontend)
# ---------------------------------------------------------------------------

async def claim_pending_presentation() -> dict | None:
    """
    Atomically find one pending presentation and mark it 'processing'.
    Returns the document (pre-update) or None if nothing is pending.

    Processes newest submissions first so a re-submitted prompt always
    gets a fresh outline, not an old queued one.
    """
    db = _get_db()
    doc = await db.presentations.find_one_and_update(
        {"status": "pending"},
        {"$set": {"status": "processing", "updatedAt": _now()}},
        sort=[("createdAt", -1)],  # newest first — prevents stale re-submissions
        return_document=False,
    )
    return doc


async def create_presentation(
    user_id: str,
    prompt: str,
    slides: int,
    density: str = "Standard",
    audience: str = "Executive Leadership",
    tone: str = "",
    fontFamily: str = "Trebuchet MS",
    fontSize: str = "Medium",
    palette: str = "midnight",
    imageSource: str = "pexels",
    pageNumbers: bool = True,
) -> str:
    """
    Create a new presentation document with configuration metadata.
    Always creates a fresh document with a new ID.

    Returns the new presentation_id (str).
    """
    from bson import ObjectId
    db = _get_db()
    now = _now()

    # Ensure values are never None
    density = density or "Standard"
    audience = audience or "Executive Leadership"
    fontFamily = fontFamily or "Trebuchet MS"
    fontSize = fontSize or "Medium"
    palette = palette or "midnight"
    imageSource = imageSource or "pexels"
    tone = tone if tone is not None else ""
    pageNumbers = pageNumbers if pageNumbers is not None else True

    print(f"[storage] Inserting presentation with: fontFamily={fontFamily}, palette={palette}, density={density}")

    result = await db.presentations.insert_one({
        "userId": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
        "prompt": prompt.strip(),
        "slides": slides,
        "density": density,
        "audience": audience,
        "tone": tone,
        "fontFamily": fontFamily,
        "fontSize": fontSize,
        "palette": palette,
        "imageSource": imageSource,
        "pageNumbers": pageNumbers,
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
        "__v": 0,
    })
    return str(result.inserted_id)


async def mark_presentation_done(presentation_id, outline_id: str) -> None:
    """
    Set presentations.status = 'done' after outline is saved to outlines collection.
    Also stores a reference to the outline document.
    """
    from bson import ObjectId
    db = _get_db()
    # Accept both ObjectId and string forms
    _id = ObjectId(presentation_id) if isinstance(presentation_id, str) else presentation_id
    result = await db.presentations.update_one(
        {"_id": _id},
        {"$set": {
            "status": "done",
            "outlineId": outline_id,
            "updatedAt": _now(),
        }},
    )
    if result.matched_count == 0:
        raise RuntimeError(f"mark_presentation_done: no document matched _id={presentation_id}")


async def mark_presentation_failed(presentation_id, error: str) -> None:
    """Set presentations.status = 'failed'."""
    from bson import ObjectId
    db = _get_db()
    _id = ObjectId(presentation_id) if isinstance(presentation_id, str) else presentation_id
    await db.presentations.update_one(
        {"_id": _id},
        {"$set": {
            "status": "failed",
            "error": error,
            "updatedAt": _now(),
        }},
    )


# ---------------------------------------------------------------------------
# outlines collection  (owned by pipeline)
# ---------------------------------------------------------------------------

async def create_outline_doc(
    presentation_id: str,
    user_id: str,
    outline: dict,
    density: str = "Standard",
    audience: str = "Executive Leadership",
    tone: str = "",
    fontFamily: str = "Trebuchet MS",
    fontSize: str = "Medium",
    palette: str = "midnight",
    imageSource: str = "pexels",
    pageNumbers: bool = True,
) -> str:
    """
    Insert a new document into the outlines collection with config metadata.
    Returns the inserted document _id (as str).
    """
    db = _get_db()
    from bson import ObjectId
    oid = ObjectId()
    doc = {
        "_id": oid,
        "presentationId": presentation_id,
        "userId": user_id,
        "status": "pending",
        "outline": outline,
        "summary": None,
        "config": {
            "density": density,
            "audience": audience,
            "tone": tone,
            "fontFamily": fontFamily,
            "fontSize": fontSize,
            "palette": palette,
            "imageSource": imageSource,
            "pageNumbers": pageNumbers,
        },
        "createdAt": _now(),
        "updatedAt": _now(),
    }
    await db.outlines.insert_one(doc)
    return str(oid)


async def set_outline_generating(outline_id: str) -> None:
    """Mark outline document as 'generating' (Opus batches started)."""
    from bson import ObjectId
    db = _get_db()
    await db.outlines.update_one(
        {"_id": ObjectId(outline_id)},
        {"$set": {"status": "generating", "updatedAt": _now()}},
    )


async def save_deck_to_outline(
    outline_id: str,
    deck: dict,
    summary: dict,
    deck_id: str | None = None,
) -> None:
    """Store the finished deck JSON + summary into the outline document."""
    from bson import ObjectId
    db = _get_db()
    fields = {
        "status": "done",
        "summary": summary,
        "updatedAt": _now(),
    }
    if deck_id is not None:
        fields["deckId"] = deck_id
    await db.outlines.update_one(
        {"_id": ObjectId(outline_id)},
        {"$set": fields},
    )


async def mark_outline_failed(outline_id: str, error: str) -> None:
    """Mark outline document as 'failed'."""
    from bson import ObjectId
    db = _get_db()
    await db.outlines.update_one(
        {"_id": ObjectId(outline_id)},
        {"$set": {
            "status": "failed",
            "error": error,
            "updatedAt": _now(),
        }},
    )


async def get_outline(outline_id: str) -> dict | None:
    """Fetch an outline document by its _id."""
    from bson import ObjectId
    db = _get_db()
    return await db.outlines.find_one({"_id": ObjectId(outline_id)})


async def get_outline_by_presentation(presentation_id: str) -> dict | None:
    """Fetch the outline document for a given presentation."""
    db = _get_db()
    return await db.outlines.find_one({"presentationId": presentation_id})


async def update_outline_content(outline_id: str, outline: dict) -> None:
    """Save an edited outline (frontend edit before deck generation)."""
    from bson import ObjectId
    db = _get_db()
    await db.outlines.update_one(
        {"_id": ObjectId(outline_id)},
        {"$set": {"outline": outline, "updatedAt": _now()}},
    )


async def list_outlines(limit: int = 20) -> list:
    """List recent outline documents (newest first), without the deck field."""
    db = _get_db()
    cursor = (
        db.outlines
        .find({}, projection={"deck": 0})
        .sort("createdAt", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


# ---------------------------------------------------------------------------
# decks collection  (final generated deck JSON)
# ---------------------------------------------------------------------------

_ARRAY_TYPE_MAP = {
    "shapeElements": "shape",
    "iconElements":  "icon",
    "chartElements": "chart",
    "tableElements": "table",
    "imageElements": "image",
    "embedElements": "embed",
}


def _build_slides(deck: dict) -> list:
    """
    Merge the scattered deck structure into one document per slide.

    Raw deck keeps content (text strings) and design (positions, styles)
    in separate sections. This collapses them so every element on a slide
    sits together with its content AND its design data.
    """
    files     = deck.get("files", {})
    content   = files.get("content", {})
    changelog = files.get("changelog", {}).get("slides", {})

    # Build a flat lookup: element_id → {type, ...content_fields}
    elem_content: dict[str, dict] = {}
    for array_key, type_name in _ARRAY_TYPE_MAP.items():
        for rec in content.get(array_key, []):
            elem_content[rec["id"]] = {"type": type_name, **{k: v for k, v in rec.items() if k != "id"}}

    slides = []
    for slide in content.get("slides", []):
        slide_id  = slide["id"]
        cl_elems  = changelog.get(slide_id, {}).get("elements", {})

        # Build a lookup of text content for this slide
        text_lookup = {t["id"]: t for t in slide.get("textElements", [])}

        elements = []
        for elem_id, cl_data in cl_elems.items():
            merged = {"id": elem_id}

            if elem_id in text_lookup:
                t = text_lookup[elem_id]
                merged["type"]             = t.get("type", "text")
                merged["content"]          = t.get("content", "")
                merged["formattedContent"] = t.get("formattedContent", "")
            elif elem_id in elem_content:
                merged.update(elem_content[elem_id])

            # Overlay design data (position, size, style, animation …)
            # Drop slideId and updatedAt — redundant at this level
            for k, v in cl_data.items():
                if k not in ("slideId", "updatedAt"):
                    merged[k] = v

            elements.append(merged)

        elements.sort(key=lambda e: e.get("zIndex", 0))

        slides.append({
            "id":              slide_id,
            "order":           slide.get("order", 0),
            "layoutId":        slide.get("layoutId", "blank-canvas"),
            "backgroundColor": slide.get("backgroundColor", "#ffffff"),
            "elements":        elements,
        })

    return slides


async def create_deck_doc(
    outline_id: str,
    presentation_id: str,
    user_id: str,
    deck: dict,
    summary: dict,
) -> str:
    """
    Insert the final generated deck JSON into the decks collection.
    Stores both the raw deck (frontend-compatible) and a merged slides[]
    array where every element has its content and design data together.
    Returns the new deck document _id (as str).
    """
    from bson import ObjectId
    db  = _get_db()
    oid = ObjectId()
    await db.decks.insert_one({
        "_id":            oid,
        "outlineId":      outline_id,
        "presentationId": presentation_id,
        "userId":         user_id,
        "slides":         _build_slides(deck),
        "summary":        summary,
        "pptxPath":       None,
        "createdAt":      _now(),
    })
    return str(oid)


async def get_deck(deck_id: str) -> dict | None:
    """Fetch a deck document by its _id."""
    from bson import ObjectId
    db = _get_db()
    return await db.decks.find_one({"_id": ObjectId(deck_id)})


async def set_deck_pptx_path(deck_id: str, pptx_path: str) -> None:
    """Store the path to the generated .pptx file on disk."""
    from bson import ObjectId
    db = _get_db()
    await db.decks.update_one(
        {"_id": ObjectId(deck_id)},
        {"$set": {"pptxPath": pptx_path}},
    )
