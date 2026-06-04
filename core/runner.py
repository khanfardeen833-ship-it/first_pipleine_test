"""
Async agent loop, run directory setup, validation gate, run summary, and summary JSON.
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

from core.config import WORKSPACE, VALIDATOR
from core.tracker import Tracker
from core.renderer import render_message
from core.prompt import build_system_prompt
from core.pricing import fmt_money
from core.merger import merge_presentations
from core.planner import generate_outline, print_outline
from core import storage


# ---------------------------------------------------------------------------
# Validation runner
# ---------------------------------------------------------------------------
def run_validation(json_path: Path) -> tuple:
    result = subprocess.run(
        ["python", str(VALIDATOR), str(json_path)],
        capture_output=True, text=True
    )
    passed = result.returncode == 0
    output = result.stdout.strip()

    problems = []
    warnings = []
    for line in output.splitlines():
        if line.startswith("  ! "):
            warnings.append(line[4:])
        elif line.startswith("  - "):
            problems.append(line[4:])

    return passed, problems, warnings


def validate_run_outputs(run_dir: Path) -> tuple:
    json_files = [
        f for f in run_dir.glob("*.json")
        if f.name not in ("run_summary.json", "merged_deck.json")
    ]

    if not json_files:
        print("\n[validation] no JSON files found in run directory")
        return False, []

    all_passed = True
    results = []
    print(f"\n--- final validation ---")
    for json_file in json_files:
        passed, problems, warnings = run_validation(json_file)
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {json_file.name}")
        if warnings:
            for w in warnings:
                print(f"    ! {w}")
        if problems:
            all_passed = False
            for p in problems:
                print(f"    - {p}")
        results.append({
            "file": json_file.name,
            "passed": passed,
            "problems": problems,
            "warnings": warnings,
        })

    if all_passed:
        print(f"  all outputs valid")
    else:
        print(f"  validation failed — see errors above")

    return all_passed, results


# ---------------------------------------------------------------------------
# Run summary JSON
# ---------------------------------------------------------------------------
def write_run_summary(run_dir: Path, data: dict):
    summary_path = run_dir / "run_summary.json"
    with open(summary_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n  summary: {summary_path}")


# ---------------------------------------------------------------------------
# Single agent loop (used by each batch)
# ---------------------------------------------------------------------------
async def _run_single_agent(user_prompt: str, system_prompt: str, run_dir: Path, label: str) -> Tracker:
    model   = os.environ["ANTHROPIC_MODEL"]
    tracker = Tracker(model)

    # Write to file to avoid Windows 32KB CreateProcess command-line limit
    sp_file = run_dir / "_system_prompt.md"
    sp_file.write_text(system_prompt, encoding="utf-8")

    options = ClaudeAgentOptions(
        system_prompt={
            "type": "file",
            "path": str(sp_file),
            "cache_control": {"type": "ephemeral"}
        },
        allowed_tools=["Read", "Write", "Bash"],
        cwd=str(run_dir),
        permission_mode="acceptEdits",
    )

    print(f"\n  [{label}] starting in {run_dir.name}")

    try:
        async for message in query(prompt=user_prompt, options=options):
            render_message(message, tracker)
    except Exception as e:
        print(f"\n  [{label}] exception: {e}")
        tracker.last_error = str(e)

    return tracker


# ---------------------------------------------------------------------------
# Batch agent — generates a slice of the deck
# ---------------------------------------------------------------------------
async def run_batch_agent(
    user_prompt: str,
    slide_start: int,
    slide_end: int,
    total_slides: int,
    id_offset: int,
    batch_dir: Path,
    slide_plan: dict = None,
) -> tuple:
    batch_size = slide_end - slide_start + 1
    label = f"batch-{slide_start}-{slide_end}"

    batch_constraint = f"""
BATCH CONSTRAINT: Generate ONLY slides {slide_start}–{slide_end} of {total_slides} total.
  slideId values: "slide-{slide_start}" through "slide-{slide_end}"
  Element ID counter starts at {id_offset} (first text element = "text-{id_offset + 1}", etc.)
  zIndex values start at {id_offset + 1}
  slideCount in the envelope JSON = {batch_size} (this batch only, NOT {total_slides})
  The final merged deck will combine all batches; focus only on your assigned slides.
"""

    # Inject the pre-approved outline for this batch's slides as design guidance
    outline_context = ""
    if slide_plan:
        batch_slides = [
            s for s in slide_plan.get("slides", [])
            if slide_start <= s.get("slide_number", 0) <= slide_end
        ]
        if batch_slides:
            outline_context = (
                "\n\nSLIDE OUTLINE (pre-approved structure — follow this plan):\n"
                + json.dumps(batch_slides, indent=2)
                + "\n\nUse the title, type, headline, key_points, and visual hint from "
                "each slide entry as your design brief. You may enrich the visuals "
                "but must preserve the content direction.\n"
            )

    system_prompt = build_system_prompt(extra=batch_constraint + outline_context)
    batch_dir.mkdir(parents=True, exist_ok=True)

    tracker = await _run_single_agent(user_prompt, system_prompt, batch_dir, label)
    return batch_dir, tracker


# ---------------------------------------------------------------------------
# Step 1: Create run + generate outline only (frontend shows this for editing)
# ---------------------------------------------------------------------------
async def create_outline(
    user_prompt: str,
    total_slides: int = 15,
    batch_size: int = 5,
) -> dict:
    """
    Phase 1 of the two-step pipeline.

    Creates the run directory, generates a slide-by-slide outline using
    Haiku (~15s), saves it to outline.json, and returns:
      {
        "run_id":     "run-1234567890",
        "run_dir":    "/path/to/workspace/run-...",
        "outline":    { "title": ..., "slides": [...] },
        "total_slides": 15,
        "batch_size": 5,
      }

    The frontend shows the outline to the user. When the user approves
    (with or without edits), pass the returned run_id + edited outline
    to generate_from_outline().
    """
    run_id  = f"run-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n--- run created ---")
    print(f"  run_id:  {run_id}")
    print(f"  prompt:  {user_prompt[:120]}")
    print(f"  slides:  {total_slides}")

    outline = None
    try:
        outline = await generate_outline(user_prompt, total_slides, run_dir)
        print_outline(outline)
    except Exception as e:
        print(f"\n  [planner] outline failed ({e})")

    # Persist to MongoDB
    try:
        await storage.save_outline(run_id, user_prompt, total_slides, batch_size, outline)
        print(f"  [mongo] outline saved -> presentations/{run_id}")
    except Exception as e:
        print(f"  [mongo] save_outline failed ({e}) — continuing")

    # Persist run metadata so generate_from_outline can resume without re-reading config
    meta = {
        "run_id": run_id,
        "user_prompt": user_prompt,
        "total_slides": total_slides,
        "batch_size": batch_size,
        "outline_generated": outline is not None,
    }
    (run_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "outline": outline,
        "total_slides": total_slides,
        "batch_size": batch_size,
    }


# ---------------------------------------------------------------------------
# Step 2: Generate slides from an (optionally edited) outline
# ---------------------------------------------------------------------------
async def generate_from_outline(run_id: str, outline: dict) -> None:
    """
    Phase 2 of the two-step pipeline.

    Accepts a run_id (from create_outline) and an outline dict — which may
    have been edited by the user on the frontend. Fires the parallel Opus
    batches using the outline as the design brief, then merges and validates.

    The edited outline is re-saved to outline.json so the final run
    directory always reflects what was actually used for generation.
    """
    run_dir = WORKSPACE / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    # Load original metadata
    meta_path = run_dir / "run_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"run_meta.json missing in {run_dir}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    user_prompt  = meta["user_prompt"]
    total_slides = meta["total_slides"]
    batch_size   = meta["batch_size"]

    # Persist the (possibly edited) outline back to disk and MongoDB
    (run_dir / "outline.json").write_text(
        json.dumps(outline, indent=2), encoding="utf-8"
    )
    try:
        await storage.update_outline(run_id, outline)
        await storage.set_generating(run_id)
        print(f"  [mongo] outline updated, status -> generating")
    except Exception as e:
        print(f"  [mongo] update_outline failed ({e}) — continuing")

    print(f"\n--- generating slides from outline ---")
    print(f"  run_id:  {run_id}")
    print(f"  slides:  {total_slides}  |  batch_size: {batch_size}")
    print(f"  outline: {len(outline.get('slides', []))} slides defined")

    batches = []
    slide_num = 1
    batch_idx = 0
    while slide_num <= total_slides:
        end = min(slide_num + batch_size - 1, total_slides)
        id_offset = batch_idx * 300
        batch_dir = run_dir / f"batch-{slide_num}-{end}"
        batches.append((slide_num, end, id_offset, batch_dir))
        slide_num = end + 1
        batch_idx += 1

    await _run_batches_and_merge(run_id, run_dir, user_prompt, total_slides,
                                  batches, outline)


# ---------------------------------------------------------------------------
# Parallel runner — splits deck into batches, gathers, merges
# (kept for one-shot use; internally calls create_outline + generate_from_outline)
# ---------------------------------------------------------------------------
async def run_parallel_agent(user_prompt: str, total_slides: int = 15, batch_size: int = 5):
    """
    One-shot runner: outline → (no pause) → generate → merge → validate.
    Use create_outline() + generate_from_outline() for the two-step flow
    where the frontend can review and edit the outline before generation.
    """
    run_id  = f"run-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n--- run starting (parallel) ---")
    print(f"  prompt:     {user_prompt[:120]}")
    print(f"  run dir:    {run_dir}")
    print(f"  slides:     {total_slides} total, {batch_size} per batch")

    batches = []
    slide_num = 1
    batch_idx = 0
    while slide_num <= total_slides:
        end = min(slide_num + batch_size - 1, total_slides)
        id_offset = batch_idx * 300
        batch_dir = run_dir / f"batch-{slide_num}-{end}"
        batches.append((slide_num, end, id_offset, batch_dir))
        slide_num = end + 1
        batch_idx += 1

    # ── Step 1: Generate slide outline (Haiku, ~10-20s) ──────────────────────
    outline = None
    try:
        outline = await generate_outline(user_prompt, total_slides, run_dir)
        print_outline(outline)
    except Exception as e:
        print(f"\n  [planner] outline generation failed ({e}) — continuing without outline")

    # ── Step 2: Parallel Opus batch generation ────────────────────────────────
    await _run_batches_and_merge(run_id, run_dir, user_prompt, total_slides,
                                  batches, outline)


# ---------------------------------------------------------------------------
# Internal: run batches + merge + validate + write summary
# ---------------------------------------------------------------------------
async def _run_batches_and_merge(
    run_id: str,
    run_dir: Path,
    user_prompt: str,
    total_slides: int,
    batches: list,
    outline,          # dict | None
) -> None:
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-7")
    start_time = time.time()

    tasks = [
        run_batch_agent(user_prompt, s, e, total_slides, off, bd,
                        slide_plan=outline)
        for s, e, off, bd in batches
    ]
    results = await asyncio.gather(*tasks)

    elapsed_gen = time.time() - start_time
    print(f"\n--- all batches done in {elapsed_gen:.1f}s ---")

    # Merge batch outputs
    batch_json_paths = []
    all_trackers = []
    for batch_dir, tracker in results:
        all_trackers.append(tracker)
        json_files = [
            f for f in batch_dir.glob("*.json")
            if f.name not in ("run_summary.json",)
        ]
        if json_files:
            # Pick the most recently written JSON as the batch output
            batch_json_paths.append(max(json_files, key=lambda f: f.stat().st_mtime))

    merged_path = run_dir / "merged_deck.json"
    merge_ok = False
    if len(batch_json_paths) == len(batches):
        print(f"\n--- merging {len(batch_json_paths)} batch JSONs ---")
        try:
            merged = merge_presentations(batch_json_paths)
            with open(merged_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2)
            print(f"  merged -> {merged_path.name}  "
                  f"({merged_path.stat().st_size:,} bytes)")
            merge_ok = True
        except Exception as e:
            print(f"  merge failed: {e}")
    else:
        missing = len(batches) - len(batch_json_paths)
        print(f"\n--- merge skipped: {missing} batch(es) produced no JSON ---")

    # Validate merged deck
    validation_passed = False
    validation_results = []
    if merge_ok:
        print(f"\n--- validating merged deck ---")
        passed, problems, warnings = run_validation(merged_path)
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {merged_path.name}")
        if warnings:
            for w in warnings:
                print(f"    ! {w}")
        if problems:
            for p in problems:
                print(f"    - {p}")
        validation_passed = passed
        validation_results = [{"file": merged_path.name, "passed": passed,
                                "problems": problems, "warnings": warnings}]

    # Aggregate tracker stats
    elapsed = time.time() - start_time
    agg = _aggregate_trackers(all_trackers)

    # Write summary
    output_files = [
        {"name": f.name, "size_bytes": f.stat().st_size}
        for f in sorted(run_dir.iterdir())
        if f.is_file() and f.name not in ("run_summary.json",)
    ]

    summary = {
        "run": {
            "id": run_id,
            "timestamp": int(time.time() * 1000),
            "prompt": user_prompt,
            "model": model,
            "duration_seconds": round(elapsed, 2),
            "success": validation_passed and not any(t.last_error for t in all_trackers),
            "batches": len(batches),
        },
        "output": {
            "files": output_files,
            "validation_passed": validation_passed,
            "validation_results": validation_results,
        },
        "tokens": {
            "input": agg["input_tokens"],
            "output": agg["output_tokens"],
            "cache_write": agg["cache_write"],
            "cache_read": agg["cache_read"],
        },
        "cost": {
            "sdk_reported": agg["sdk_cost"],
            "calculated": agg["calc_cost"],
        },
        "agent": {
            "turns": agg["turns"],
            "tool_calls": agg["tool_calls"],
            "files_written": agg["files_written"],
            "bash_commands_count": agg["bash_commands"],
            "thinking_chars": agg["thinking_chars"],
            "last_error": next((t.last_error for t in all_trackers if t.last_error), None),
            "permission_denials": [d for t in all_trackers for d in t.permission_denials],
        },
    }
    write_run_summary(run_dir, summary)

    # Persist final deck + summary to MongoDB
    try:
        mongo_summary = {
            "duration_seconds": round(elapsed, 2),
            "cost_usd": agg["sdk_cost"],
            "tokens": {
                "output": agg["output_tokens"],
                "input": agg["input_tokens"],
                "cache_write": agg["cache_write"],
                "cache_read": agg["cache_read"],
            },
            "validation_passed": validation_passed,
            "batches": len(batches),
        }
        deck_json = None
        if merge_ok and merged_path.exists():
            with open(merged_path, "r", encoding="utf-8") as f:
                deck_json = json.load(f)
        await storage.save_deck(run_id, deck_json, mongo_summary)
        print(f"  [mongo] deck saved -> presentations/{run_id}  (status: complete)")
    except Exception as e:
        print(f"  [mongo] save_deck failed ({e})")
        try:
            await storage.save_failed(run_id, str(e))
        except Exception:
            pass

    # Print summary
    print(f"\n--- run summary ---")
    print(f"  duration:        {elapsed:.1f}s  (generation: {elapsed_gen:.1f}s)")
    print(f"  batches:         {len(batches)}")
    print(f"  assistant turns: {agg['turns']}")
    print(f"  tool calls:      {agg['tool_calls']}")
    print(f"  files written:   {len(agg['files_written'])}")
    print(f"  cost (sdk):      {fmt_money(agg['sdk_cost'])}")
    print(f"\n  run directory: {run_dir}")
    print(f"\n--- done ---")


def _aggregate_trackers(trackers: list) -> dict:
    agg = {
        "input_tokens": 0, "output_tokens": 0,
        "cache_write": 0, "cache_read": 0,
        "sdk_cost": 0.0, "calc_cost": 0.0,
        "turns": 0, "tool_calls": 0,
        "files_written": [], "bash_commands": 0,
        "thinking_chars": 0,
    }
    for t in trackers:
        agg["input_tokens"]  += t.input_tokens
        agg["output_tokens"] += t.output_tokens
        agg["cache_write"]   += t.get_total_breakdown().get("cache_write_tok", 0)
        agg["cache_read"]    += t.cache_read
        agg["sdk_cost"]      += t.sdk_reported_cost
        agg["calc_cost"]     += t.get_total_breakdown().get("total", 0.0)
        agg["turns"]         += t.turns
        agg["tool_calls"]    += len(t.tool_calls)
        agg["files_written"] += t.files_written
        agg["bash_commands"] += len(t.bash_commands)
        agg["thinking_chars"]+= t.thinking_total_chars
    return agg


# ---------------------------------------------------------------------------
# Legacy single-agent loop (kept for backwards compat / debugging)
# ---------------------------------------------------------------------------
async def run_agent(user_prompt: str):
    system_prompt = build_system_prompt()
    model   = os.environ["ANTHROPIC_MODEL"]
    tracker = Tracker(model)

    run_id  = f"run-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    sp_file = run_dir / "_system_prompt.md"
    sp_file.write_text(system_prompt, encoding="utf-8")

    options = ClaudeAgentOptions(
        system_prompt={
            "type": "file",
            "path": str(sp_file),
            "cache_control": {"type": "ephemeral"}
        },
        allowed_tools=["Read", "Write", "Bash"],
        cwd=str(run_dir),
        permission_mode="acceptEdits",
    )

    print(f"\n--- run starting ---")
    print(f"  prompt:  {user_prompt[:120]}")
    print(f"  run dir: {run_dir}")

    try:
        async for message in query(prompt=user_prompt, options=options):
            render_message(message, tracker)
    except Exception as e:
        print(f"\n[exception] {e}")
        tracker.last_error = str(e)

    validation_passed, validation_results = validate_run_outputs(run_dir)

    elapsed   = time.time() - tracker.start
    breakdown = tracker.get_total_breakdown()

    output_files = [
        {"name": f.name, "size_bytes": f.stat().st_size}
        for f in sorted(run_dir.iterdir())
        if f.is_file() and f.name != "run_summary.json"
    ]

    summary = {
        "run": {
            "id": run_id,
            "timestamp": int(time.time() * 1000),
            "prompt": user_prompt,
            "model": model,
            "duration_seconds": round(elapsed, 2),
            "success": validation_passed and not tracker.last_error,
        },
        "output": {
            "files": output_files,
            "validation_passed": validation_passed,
            "validation_results": validation_results,
        },
        "tokens": {
            "input": tracker.input_tokens,
            "output": tracker.output_tokens,
            "cache_write": breakdown["cache_write_tok"],
            "cache_read": tracker.cache_read,
        },
        "cost": {
            "sdk_reported": tracker.sdk_reported_cost,
            "calculated": breakdown["total"],
        },
        "agent": {
            "turns": tracker.turns,
            "tool_calls": len(tracker.tool_calls),
            "files_written": tracker.files_written,
            "bash_commands_count": len(tracker.bash_commands),
            "thinking_chars": tracker.thinking_total_chars,
            "last_error": tracker.last_error,
            "permission_denials": tracker.permission_denials,
        },
    }
    write_run_summary(run_dir, summary)

    print(f"\n--- run summary ---")
    print(f"  duration:        {elapsed:.1f}s")
    print(f"  assistant turns: {tracker.turns}")
    print(f"  tool calls:      {len(tracker.tool_calls)}")
    print(f"  files written:   {len(tracker.files_written)}")
    for f in tracker.files_written:
        print(f"    {f}")
    print(f"  bash commands:   {len(tracker.bash_commands)}")
    print(f"  thinking:        {tracker.thinking_total_chars:,} chars")
    print(f"\n--- done ---")
