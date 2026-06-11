"""
Presentation Generation API Server

Endpoints:
  POST   /api/presentations              - Submit a prompt, get run_id back
  GET    /api/presentations/:id          - Check status (pending/processing/done/failed)
  GET    /api/outlines/:id               - Get the generated outline (show on frontend)
  PUT    /api/outlines/:id               - Edit the outline before generating slides
  POST   /api/outlines/:id/generate      - Trigger full deck generation from outline
  GET    /api/outlines/:id/deck          - Fetch the final deck JSON
  GET    /api/outlines/:id/deck/download - Download deck as .json file (editor format)

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
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime, timezone

from core import storage
from core.worker import run_worker
from core.runner import run_deck_pipeline
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
    slides: int = Field(default=15)
    density: str = Field(default="Standard", description="Standard, Compact, Spacious")
    audience: str = Field(default="Executive Leadership")
    tone: str = Field(default="", description="e.g., formal, conversational, playful")
    fontFamily: str = Field(default="Trebuchet MS", description="Use system fonts from design guide")
    fontSize: str = Field(default="Medium", description="Small, Medium, Large")
    palette: str = Field(default="auto", description="Color palette name, or 'auto' to let the art director pick the best fit for the topic")
    imageSource: str = Field(default="pexels", description="Stock photos, Pexels, Unsplash, etc.")
    pageNumbers: bool = Field(default=True)


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
    # Explicitly apply defaults to ensure values are never None
    density = body.density or "Standard"
    audience = body.audience or "Executive Leadership"
    tone = body.tone if body.tone is not None else ""
    fontFamily = body.fontFamily or "Trebuchet MS"
    fontSize = body.fontSize or "Medium"
    palette = body.palette or "auto"
    imageSource = body.imageSource or "pexels"
    pageNumbers = body.pageNumbers if body.pageNumbers is not None else True

    pid = await storage.create_presentation(
        user_id=body.userId,
        prompt=body.prompt,
        slides=body.slides,
        density=density,
        audience=audience,
        tone=tone,
        fontFamily=fontFamily,
        fontSize=fontSize,
        palette=palette,
        imageSource=imageSource,
        pageNumbers=pageNumbers,
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
async def edit_outline(outline_id: str, body: EditOutlineRequest,
                       background_tasks: BackgroundTasks):
    """
    Frontend saves the reviewed/edited outline.
    Saves the outline content and automatically kicks off deck generation.
    Only allowed when status is 'pending'.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") not in ("pending",):
        raise HTTPException(409, f"Cannot update outline in status '{doc.get('status')}'")

    await storage.update_outline_content(outline_id, body.outline)
    background_tasks.add_task(run_deck_pipeline, outline_id)

    return {
        "message": "Outline saved — deck generation started",
        "outlineId": outline_id,
        "note": "Poll GET /api/outlines/{id} — status changes to 'done' when done (~2 min).",
    }


@app.post("/api/outlines/{outline_id}/generate")
async def generate_deck(outline_id: str, background_tasks: BackgroundTasks):
    """
    Manually trigger deck generation for an outline (optional — the worker
    triggers this automatically after outline creation).
    Deck generation takes ~2 minutes; poll GET /api/outlines/{id} for status.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") != "pending":
        raise HTTPException(409, f"Outline is already in status '{doc.get('status')}'")

    background_tasks.add_task(run_deck_pipeline, outline_id)

    return {
        "message": "Deck generation started",
        "outlineId": outline_id,
        "note": "Poll GET /api/outlines/{id} — status changes to 'done' when done (~2 min)."
    }


@app.get("/api/outlines/{outline_id}/deck")
async def get_deck(outline_id: str):
    """
    Fetch the final deck once status is 'done'.
    Returns slides[] — one entry per slide, each element has content + design together.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") != "done":
        raise HTTPException(409, f"Deck not ready yet — status is '{doc.get('status')}'")
    deck_doc = await storage.get_deck(str(doc["deckId"]))
    if not deck_doc:
        raise HTTPException(404, "Deck document not found")
    return JSONResponse(content={
        "slides":  deck_doc.get("slides"),
        "summary": deck_doc.get("summary"),
    })


@app.get("/api/outlines/{outline_id}/deck/download")
async def download_deck_json(outline_id: str):
    """
    Download the flat deck JSON as a .json file.
    This is the same format the editor uses — slides[].elements[] with all
    properties inline. Share this file with anyone who needs the deck data.
    """
    if not ObjectId.is_valid(outline_id):
        raise HTTPException(400, "Invalid outlineId")
    doc = await storage.get_outline(outline_id)
    if not doc:
        raise HTTPException(404, "Outline not found")
    if doc.get("status") != "done":
        raise HTTPException(409, f"Deck not ready yet — status is '{doc.get('status')}'")
    deck_doc = await storage.get_deck(str(doc["deckId"]))
    if not deck_doc:
        raise HTTPException(404, "Deck document not found")

    import json
    title = (doc.get("outline", {}).get("title") or "deck").replace(" ", "_")[:40]
    filename = f"{title}.json"
    payload = json.dumps({
        "outlineId":      outline_id,
        "presentationId": str(doc.get("presentationId", "")),
        "userId":         str(deck_doc.get("userId", "")),
        "slides":         deck_doc.get("slides", []),
    }, ensure_ascii=False, indent=2)

    return Response(
        content=payload,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/outlines")
async def list_outlines(limit: int = 20):
    """List recent outlines (without deck JSON)."""
    docs = await storage.list_outlines(limit=limit)
    return [_to_str_id(d) for d in docs]


# ── Deck download ─────────────────────────────────────────────────────────────

@app.get("/api/decks/{deck_id}/download")
async def download_deck_pptx(deck_id: str):
    """
    Download the generated .pptx file for a completed deck.
    Returns 404 if the deck doesn't exist or the PPTX hasn't been generated yet.
    """
    if not ObjectId.is_valid(deck_id):
        raise HTTPException(400, "Invalid deckId")
    deck = await storage.get_deck(deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    pptx_path_str = deck.get("pptxPath")
    if not pptx_path_str:
        raise HTTPException(404, "PPTX not ready yet — deck generation may still be running")
    from pathlib import Path
    pptx_path = Path(pptx_path_str)
    if not pptx_path.exists():
        raise HTTPException(404, "PPTX file not found on disk")
    return FileResponse(
        pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="presentation.pptx",
    )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"[server] starting on http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
