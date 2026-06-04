"""
MongoDB storage layer.

Collections:
  presentations  — frontend-created, one doc per request
                   { _id, userId, prompt, slides, status, createdAt, updatedAt }
                   status flow:  pending → processing → done | failed

  outlines       — pipeline-created, one doc per presentation
                   { _id, presentationId, userId, prompt, totalSlides,
                     status, outline, deck, summary, createdAt, updatedAt }
                   status flow:  pending → generating → complete | failed
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
) -> str:
    """
    Create a new presentation document. Always creates a fresh document
    with a new ID — same prompt submitted twice = two independent presentations.

    Returns the new presentation_id (str).
    """
    from bson import ObjectId
    db = _get_db()
    now = _now()
    result = await db.presentations.insert_one({
        "userId": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
        "prompt": prompt.strip(),
        "slides": slides,
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
) -> str:
    """
    Insert a new document into the outlines collection with status='pending'.
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
        "deck": None,
        "summary": None,
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
) -> None:
    """Store the finished deck JSON + summary into the outline document."""
    from bson import ObjectId
    db = _get_db()
    await db.outlines.update_one(
        {"_id": ObjectId(outline_id)},
        {"$set": {
            "status": "complete",
            "deck": deck,
            "summary": summary,
            "updatedAt": _now(),
        }},
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
