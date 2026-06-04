"""
Presentation Generation API Server

Endpoints:
  POST   /api/presentations              - Submit a prompt, get run_id back
  GET    /api/presentations/:id          - Check status (pending/processing/done/failed)
  GET    /api/outlines/:id               - Get the generated outline (show on frontend)
  PUT    /api/outlines/:id               - Edit the outline before generating slides
  POST   /api/outlines/:id/generate      - Trigger full deck generation from outline
  GET    /api/outlines/:id/deck          - Fetch the final deck JSON

Run:
  python server.py
  (or)  uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import os
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from bson import ObjectId
from datetime import datetime, timezone

from core import storage
from core.worker import run_worker
from core.runner import generate_from_outline
from core.config import preflight


# ---------------------------------------------------------------------------
# Startup: run the change-stream worker as a background task
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    preflight()
    # Start the worker in background — it will drain existing pending docs
    # and then watch the change stream for new ones
    worker_task = asyncio.create_task(run_worker())
    print("[server] worker started in background")
    yield
    worker_task.cancel()
    print("[server] worker stopped")


app = FastAPI(
    title="Presentation Generation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class CreatePresentationRequest(BaseModel):
    userId: str
    prompt: str
    slides: int = 15


class EditOutlineRequest(BaseModel):
    outline: dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _to_str_id(doc: dict) -> dict:
    """Convert ObjectId fields to strings for JSON serialization."""
    if not doc:
        return doc
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "ok", "service": "Presentation Generation API"}


@app.get("/health")
async def health():
    """Quick health check — also verifies MongoDB is reachable."""
    db = storage._get_db()
    await db.command("ping")
    return {"status": "ok", "db": "connected"}


# ── Presentations ────────────────────────────────────────────────────────────

@app.post("/api/presentations", status_code=201)
async def create_presentation(body: CreatePresentationRequest):
    """
    Submit a prompt to generate a presentation outline.
    Every submission creates a fresh presentation with a new unique ID.
    Same prompt submitted twice = two independent presentations, two outlines.
    """
    pid = await storage.create_presentation(
        user_id=body.userId,
        prompt=body.prompt,
        slides=body.slides,
    )
    return {
        "presentationId": pid,
        "status": "pending",
        "message": "Outline is being generated — poll GET /api/presentations/{id} for status.",
    }


@app.get("/api/presentations/{presentation_id}")
async def get_presentation(presentation_id: str):
    """
    Poll this to check whether the outline is ready.
    Returns status and outlineId once done.
    """
    if not ObjectId.is_valid(presentation_id):
        raise HTTPException(400, "Invalid presentationId")
    db = storage._get_db()
    doc = await db.presentations.find_one({"_id": ObjectId(presentation_id)})
    if not doc:
        raise HTTPException(404, "Presentation not found")
    return _to_str_id(doc)


# ── Outlines ─────────────────────────────────────────────────────────────────

@app.get("/api/outlines/{outline_id}")
async def get_outline(outline_id: str):
    """
    Get the generated slide outline.
    Frontend displays this for the user to review / edit before generating the deck.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    safe = _to_str_id({k: v for k, v in doc.items() if k != "deck"})
    return safe


@app.put("/api/outlines/{outline_id}")
async def edit_outline(outline_id: str, body: EditOutlineRequest):
    """
    User edits the outline on the frontend — save it here before generating.
    Only allowed when status is 'pending' (deck not yet generated).
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") not in ("pending",):
        raise HTTPException(409, f"Cannot edit outline in status '{doc.get('status')}'")

    await storage.update_outline_content(outline_id, body.outline)
    return {"message": "Outline updated", "outlineId": outline_id}


@app.post("/api/outlines/{outline_id}/generate")
async def generate_deck(outline_id: str, background_tasks: BackgroundTasks):
    """
    User approves the outline — start full deck generation in the background.
    Deck generation takes ~2 minutes; poll GET /api/outlines/{id} for status.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") != "pending":
        raise HTTPException(409, f"Outline is already in status '{doc.get('status')}'")

    # Fetch run_meta from presentations to get user_prompt + slide config
    db = storage._get_db()
    pres = await db.presentations.find_one(
        {"_id": ObjectId(doc["presentationId"])} if ObjectId.is_valid(str(doc["presentationId"])) else {"_id": doc["presentationId"]}
    )
    if not pres:
        raise HTTPException(404, "Parent presentation not found")

    # Build a run_id and run_meta.json so generate_from_outline can work
    import time, json
    from pathlib import Path
    from core.config import WORKSPACE

    run_id  = f"run-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id":      run_id,
        "user_prompt": pres.get("prompt", ""),
        "total_slides": pres.get("slides", 15),
        "batch_size":   5,
        "outline_id":   outline_id,
    }
    (run_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    outline_data = doc.get("outline", {})

    async def _generate():
        try:
            await storage.set_outline_generating(outline_id)
            await generate_from_outline(run_id, outline_data)
            # grab the saved deck from disk and store in MongoDB
            merged = run_dir / "merged_deck.json"
            if merged.exists():
                deck = json.loads(merged.read_text(encoding="utf-8"))
                summary_path = run_dir / "run_summary.json"
                summary_raw = json.loads(summary_path.read_text()) if summary_path.exists() else {}
                mongo_summary = {
                    "duration_seconds": summary_raw.get("run", {}).get("duration_seconds"),
                    "cost_usd":         summary_raw.get("cost", {}).get("sdk_reported"),
                    "tokens":           summary_raw.get("tokens", {}),
                    "validation_passed": summary_raw.get("output", {}).get("validation_passed"),
                }
                await storage.save_deck_to_outline(outline_id, deck, mongo_summary)
        except Exception as e:
            await storage.mark_outline_failed(outline_id, str(e))

    background_tasks.add_task(_generate)

    return {
        "message": "Deck generation started",
        "outlineId": outline_id,
        "runId": run_id,
        "note": "Poll GET /api/outlines/{id} — status changes to 'complete' when done (~2 min)."
    }


@app.get("/api/outlines/{outline_id}/deck")
async def get_deck(outline_id: str):
    """
    Fetch the final deck JSON once status is 'complete'.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") != "complete":
        raise HTTPException(409, f"Deck not ready yet — status is '{doc.get('status')}'")
    return JSONResponse(content={"deck": doc.get("deck"), "summary": doc.get("summary")})


@app.get("/api/outlines")
async def list_outlines(limit: int = 20):
    """List recent outlines (without deck JSON)."""
    docs = await storage.list_outlines(limit=limit)
    return [_to_str_id(d) for d in docs]


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"[server] starting on http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
