# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An AI presentation-generation pipeline: a prompt goes in, a "Bildory" editor deck JSON (and optionally a .pptx) comes out. Python orchestrates Anthropic API calls; a small Node.js script (pptxgenjs) handles PPTX export.

## Commands

```bash
# Full CLI pipeline: Azure OpenAI prompt enhance → deck generation
python run.py "coffee in Ethiopia"

# API server (FastAPI on :8000) — starts the MongoDB change-stream worker in-process
python server.py

# Standalone worker (outline + deck generation from MongoDB queues)
python run_worker.py

# End-to-end slidegen test with a hand-written outline — no Azure, no MongoDB needed
python scripts/run_premium_test.py

# Validate a generated deck (structure, ID sync, zIndex uniqueness)
python validate.py workspace/<run-id>/merged_deck.json

# Render a deck to a standalone preview.html (mimics the editor, incl. features PPTX export lacks)
python scripts/render_html_preview.py workspace/<run-id>/merged_deck.json

# PPTX export directly (normally invoked via core/pptx_exporter.py)
node scripts/export_pptx.js <deck.json> <out.pptx>

npm install   # only needed for PPTX export / lucide icons (pptxgenjs, adm-zip, lucide-static)
```

There is no requirements.txt. Python deps in use: `anthropic`, `claude-agent-sdk`, `fastapi`, `uvicorn`, `motor`, `anyio`, `openai`, `python-dotenv`, `pydantic`, `bson`. (`.pytest_cache` references a `tests/` directory that no longer exists.)

### Environment variables (.env, loaded via python-dotenv)

- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` — required; `preflight()` in `core/config.py` exits if missing
- `ANTHROPIC_OUTLINE_MODEL` — outline model (default `claude-haiku-4-5`)
- `DECK_ENGINE` — `slidegen` (default) or `agent` (legacy)
- `SLIDEGEN_MODE` — `fast` | `premium` | `director` (default `director`)
- `MONGODB_URI` — required for server/worker paths only
- `AZURE_OPENAI_*` / `OPENAI_API_KEY` — only for the prompt enhancer (`enhance.py`)
- `PRESENTATION_BATCH_SIZE` — slides per batch, legacy agent engine only (default 8)

## Architecture

### Two entry paths into one pipeline

1. **CLI** (`run.py`): `enhance.py` (4 parallel Azure OpenAI calls produce a rich brief) → `core/runner.run_parallel_agent`.
2. **API** (`server.py` + `core/worker.py`): MongoDB change streams drive a two-stage queue across three collections (`core/storage.py`):
   - `presentations` (status `pending → processing → done`) — worker picks up a prompt, generates an outline via `core/planner.py` (Haiku, ~15s)
   - `outlines` (status `pending → generating → done`) — `POST /api/outlines/:id/generate` flips status, worker generates the full deck (~2 min)
   - `decks` — final result in a merged per-slide format (each element carries content + design together)

### Two deck engines (selected in `core/runner.run_deck_pipeline`)

- **slidegen** (`core/slidegen.py`, default): one direct Anthropic API call per slide, run in parallel, returning a compact "slide spec" via schema-enforced tool call. All slides share a cached system prefix (skills + brief + outline) — slide 1 warms the prompt cache, the rest hit it. `director` mode adds a deck-wide design-plan call (palette choice when `palette: "auto"`, per-slide archetypes) that runs concurrently with a cache-warmer. Specs are expanded deterministically in-process by `deck_builder.Deck`. Each slide owns a 100-wide element-ID/zIndex band (`ID_OFFSET_PER_SLIDE`) so `core/merger.py` can concatenate without renumbering.
- **agent** (legacy): `claude-agent-sdk` parallel batch agents that write `build.py` scripts in the workspace.

Both write artifacts to `workspace/<run-id>/` and produce `merged_deck.json`, which is gated through `validate.py` before storage/export.

### The Bildory deck format — invariants enforced by validate.py

A deck has three files under `files`: `content`, `baseLayout`, `changelog`. The two structural rules that everything revolves around:

- **Dual records**: every element appears twice — a minimal record in `content` and a full geometry/style record in `changelog`, with synced IDs (see `skills/core/08-changelog-sync.md`).
- **Global zIndex**: zIndex values must be unique across the entire deck, not per slide (see `skills/core/09-zindex-rules.md`).

`deck_builder.py` exists so generation code never hand-assembles this format — it keeps both records in sync automatically.

### skills/ is prompt content, not documentation

The markdown files in `skills/` (and `prompts/`) are injected verbatim into the LLM system prompt (`core/prompt.py` for the agent engine, `build_slidegen_system` in `core/slidegen.py` for slidegen). Editing them changes what the model generates. `core/config.py` keeps explicit file lists (`CORE_SKILL_FILES`, `ELEMENT_SKILL_FILES`) — adding a skill file requires registering it there or it won't be loaded (and preflight checks the lists, so removing a file without updating them fails startup).

### PPTX export

`core/pptx_exporter.py` shells out to `scripts/export_pptx.js` (pptxgenjs), which maps the full deck structure — changelog geometry included — to PowerPoint. `scripts/render_html_preview.py` is the higher-fidelity reference for features the PPTX mapping doesn't cover yet (ellipse crops, CSS filters, blend modes).

## Notes

- Windows console: entry points call `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` — keep that in new entry points or Unicode output crashes.
- Cost/token tracking lives in `core/tracker.py` + `core/pricing.py`; unknown model IDs silently disable cost tracking.
