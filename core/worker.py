"""
Background worker using MongoDB Change Streams.

Instead of polling every N seconds, the worker opens a change stream on the
presentations collection. MongoDB pushes an event the instant a document is
inserted or updated with status='pending' — zero delay, zero wasted queries.

Startup sequence:
  1. Drain any existing pending docs that arrived while the worker was offline.
  2. Open a change stream and wait for new inserts/updates in real time.

Flow per document:
  presentations.status: pending
        → atomic claim  (status = 'processing')
        → generate outline  (Haiku, ~15s)
        → insert into outlines  (status = 'pending', outline = {...})
        → presentations.status = 'done'  (+ outlineId reference)

Run with:
    python run_worker.py
"""

import asyncio
import sys

from dotenv import load_dotenv
load_dotenv()

from core import storage
from core.planner import generate_outline


# Change stream filter: fire on insert OR update that sets status='pending'
_PIPELINE = [
    {"$match": {
        "operationType": {"$in": ["insert", "update", "replace"]},
        "$or": [
            {"fullDocument.status": "pending"},            # insert with pending
            {"updateDescription.updatedFields.status": "pending"},  # update to pending
        ]
    }}
]


async def process_one(doc: dict) -> None:
    """
    Process a single presentation doc (already claimed as 'processing').
    Generates outline → saves to outlines → marks presentation 'done'.
    """
    raw_id = doc["_id"]
    pid    = str(raw_id)
    prompt = doc.get("prompt", "")
    slides = int(doc.get("slides", 15))
    uid    = str(doc.get("userId", ""))

    print(f"\n[worker] processing  {pid}")
    print(f"         prompt:  {prompt[:80]}")
    print(f"         slides:  {slides}")

    try:
        outline = await generate_outline(prompt, slides, run_dir=None)
        print(f"[worker] outline ready  ({len(outline.get('slides', []))} slides)")

        outline_id = await storage.create_outline_doc(
            presentation_id=pid,
            user_id=uid,
            outline=outline,
        )
        print(f"[worker] saved -> outlines/{outline_id}  status=pending")

        await storage.mark_presentation_done(raw_id, outline_id)
        print(f"[worker] presentations/{pid}  status=done  outlineId={outline_id}")

    except Exception as e:
        err = str(e)
        print(f"[worker] ERROR for {pid}: {err}")
        await storage.mark_presentation_failed(raw_id, err)


async def _drain_existing() -> int:
    """
    On startup, process any presentations that were already pending
    (arrived while the worker was offline).
    Returns the number of docs processed.
    """
    count = 0
    while True:
        doc = await storage.claim_pending_presentation()
        if not doc:
            break
        await process_one(doc)
        count += 1
    return count


async def run_worker() -> None:
    """
    Main entry point.
    1. Drain existing pending presentations.
    2. Watch the change stream for new ones in real time.
    """
    print("[worker] starting — using MongoDB Change Streams")
    print("[worker] watching: presentations  (status=pending)")
    print("[worker] writing:  outlines       (status=pending)")
    print()

    # Step 1: catch up on anything pending from before start
    drained = await _drain_existing()
    if drained:
        print(f"[worker] drained {drained} pending doc(s) from before startup")
    else:
        print("[worker] no backlog — ready")

    # Step 2: open change stream and react in real time
    db = storage._get_db()
    print("[worker] change stream open — waiting for new presentations...\n")

    async with db.presentations.watch(
        _PIPELINE,
        full_document="updateLookup",   # include full doc on updates too
    ) as stream:
        async for event in stream:
            op   = event["operationType"]
            full = event.get("fullDocument") or {}

            # The event fired but someone else may have already claimed it;
            # use the atomic claim so we never double-process.
            if full.get("status") == "pending":
                doc = await storage.claim_pending_presentation()
                if doc:
                    print(f"[worker] change stream event ({op}) → claimed {doc['_id']}")
                    asyncio.create_task(process_one(doc))
                # If claim returns None, another worker already took it — skip.
