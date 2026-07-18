"""
Background worker using MongoDB Change Streams.

Watches two collections:
  presentations — status=pending  → generate outline → outlines status=pending
  outlines      — status=processing → generate deck  → outlines status=done

Flow:
  1. Frontend submits prompt
     presentations.status: pending
           → worker claims it (status=processing)
           → generates outline (~15s)
           → saves to outlines (status=pending)
           → presentations.status=done

  2. Frontend shows outline to user, user approves
     Frontend sets outlines.status=processing in the database
           → worker detects this via change stream
           → claims it (status=generating)
           → generates full deck (~2 min)
           → saves to decks collection
           → outlines.status=done
"""

import asyncio

from dotenv import load_dotenv
load_dotenv()

from core import storage
from core.planner import generate_outline
from core.runner import run_deck_pipeline


# ── Change stream filters ─────────────────────────────────────────────────────

_PRESENTATIONS_PIPELINE = [
    {"$match": {
        "operationType": {"$in": ["insert", "update", "replace"]},
        "$or": [
            {"fullDocument.status": "pending"},
            {"updateDescription.updatedFields.status": "pending"},
        ]
    }}
]

_OUTLINES_PIPELINE = [
    {"$match": {
        "operationType": {"$in": ["insert", "update", "replace"]},
        "$or": [
            {"fullDocument.status": "processing"},
            {"updateDescription.updatedFields.status": "processing"},
        ]
    }}
]


# ── Outline generation (Stage 1) ──────────────────────────────────────────────

async def process_presentation(doc: dict) -> None:
    """Claim a presentation, generate its outline, save to outlines collection."""
    raw_id = doc["_id"]
    pid    = str(raw_id)
    prompt = doc.get("prompt", "")
    slides = int(doc.get("slides", 15))
    uid    = str(doc.get("userId", ""))

    # Extract configuration fields (with defaults for backward compatibility)
    config = {
        "density": doc.get("density", "Standard"),
        "audience": doc.get("audience", "Executive Leadership"),
        "tone": doc.get("tone", ""),
        "fontFamily": doc.get("fontFamily", "Trebuchet MS"),
        "fontSize": doc.get("fontSize", "Medium"),
        "palette": doc.get("palette") or "auto",
        "imageSource": doc.get("imageSource", "pexels"),
        "pageNumbers": doc.get("pageNumbers", True),
    }

    print(f"\n[worker] processing presentation  {pid}")
    print(f"         prompt:  {prompt[:80]}")
    print(f"         slides:  {slides}")

    try:
        outline = await generate_outline(prompt, slides, run_dir=None)
        print(f"[worker] outline ready  ({len(outline.get('slides', []))} slides)")

        # Dump the outline locally for inspection (paired with deck.json later)
        try:
            from core.local_dump import dump_outline
            dump_outline(pid, prompt, outline)
        except Exception as dump_err:
            print(f"[worker] local outline dump failed (non-fatal): {dump_err}")

        outline_id = await storage.create_outline_doc(
            presentation_id=pid,
            user_id=uid,
            outline=outline,
            **config,
        )
        print(f"[worker] saved -> outlines/{outline_id}  status=pending")

        await storage.mark_presentation_done(raw_id, outline_id)
        print(f"[worker] presentations/{pid}  status=done  outlineId={outline_id}")
        print(f"[worker] waiting for frontend to approve -> outlines/{outline_id}")

    except Exception as e:
        err = str(e)
        print(f"[worker] ERROR for {pid}: {err}")
        await storage.mark_presentation_failed(raw_id, err)


# ── Deck generation (Stage 2) ─────────────────────────────────────────────────

async def process_outline(outline_id: str) -> None:
    """
    Frontend set outlines.status=processing — claim it and generate the deck.
    Uses atomic claim to prevent double-processing by concurrent workers.
    """
    from bson import ObjectId
    db = storage._get_db()

    # Atomic claim: only proceed if still 'processing' (not already grabbed)
    doc = await db.outlines.find_one_and_update(
        {"_id": ObjectId(outline_id), "status": "processing"},
        {"$set": {"status": "generating"}},
        return_document=False,
    )
    if not doc:
        return  # Another worker already claimed it

    print(f"\n[worker] outline approved by frontend  {outline_id}")
    print(f"[worker] starting deck generation...")

    try:
        await run_deck_pipeline(outline_id)
    except Exception as e:
        print(f"[worker] deck generation failed for {outline_id}: {e}")


# ── Startup backlog drain ─────────────────────────────────────────────────────

async def _drain_pending_presentations() -> int:
    count = 0
    while True:
        doc = await storage.claim_pending_presentation()
        if not doc:
            break
        await process_presentation(doc)
        count += 1
    return count


async def _drain_processing_outlines() -> int:
    """Pick up any outlines the frontend already set to processing before startup."""
    from bson import ObjectId
    db = storage._get_db()
    count = 0
    async for doc in db.outlines.find({"status": "processing"}):
        outline_id = str(doc["_id"])
        print(f"[worker] backlog: outline {outline_id} was processing — starting deck generation")
        asyncio.create_task(process_outline(outline_id))
        count += 1
    return count


# ── Main entry point ──────────────────────────────────────────────────────────

async def run_worker() -> None:
    print("[worker] starting — using MongoDB Change Streams")
    print("[worker] watching: presentations  (status=pending)    → outline generation")
    print("[worker] watching: outlines       (status=processing)  → deck generation")
    print()

    drained_pres = await _drain_pending_presentations()
    drained_out  = await _drain_processing_outlines()

    if drained_pres or drained_out:
        print(f"[worker] drained {drained_pres} presentation(s), {drained_out} outline(s) from backlog")
    else:
        print("[worker] no backlog — ready")

    db = storage._get_db()
    print("[worker] change streams open — waiting...\n")

    async def watch_presentations():
        async with db.presentations.watch(
            _PRESENTATIONS_PIPELINE,
            full_document="updateLookup",
        ) as stream:
            async for event in stream:
                full = event.get("fullDocument") or {}
                if full.get("status") == "pending":
                    doc = await storage.claim_pending_presentation()
                    if doc:
                        print(f"[worker] new presentation → {doc['_id']}")
                        asyncio.create_task(process_presentation(doc))

    async def watch_outlines():
        async with db.outlines.watch(
            _OUTLINES_PIPELINE,
            full_document="updateLookup",
        ) as stream:
            async for event in stream:
                full = event.get("fullDocument") or {}
                if full.get("status") == "processing":
                    outline_id = str(full["_id"])
                    print(f"[worker] outline approved → {outline_id}")
                    asyncio.create_task(process_outline(outline_id))

    await asyncio.gather(watch_presentations(), watch_outlines())
