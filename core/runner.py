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
from core.prompt import build_system_prompt, build_system_prompt_optimized
from core.pricing import fmt_money
from core.merger import merge_presentations
from core.planner import plan_presentation
from core.post_processor import apply_schema_compression
from core.schema_config import SchemaCompressionConfig
from core.build_helpers_template import write_batch_helpers


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
async def _run_single_agent(user_prompt: str, system_prompt: str, run_dir: Path, label: str, model_override: str = None, phase: str = None) -> Tracker:
    model   = model_override or os.environ["ANTHROPIC_MODEL"]
    tracker = Tracker(model)
    tracker.batch_name = label
    tracker.batch_start_time = time.time()

    # Track phase if specified
    if phase:
        tracker.start_phase(phase)

    # Write to file to avoid Windows 32KB CreateProcess command-line limit
    sp_file = run_dir / "_system_prompt.md"
    sp_file.write_text(system_prompt, encoding="utf-8")

    options = ClaudeAgentOptions(
        model=model,
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

    # API timing instrumentation
    api_call_start = time.time()
    first_response_received = False
    first_response_time = None
    turn_start_times = {}
    final_response_time = None
    api_call_input_tokens = 0
    api_call_output_tokens = 0

    try:
        async for message in query(prompt=user_prompt, options=options):
            current_time = time.time()

            # Track first token latency
            if not first_response_received and type(message).__name__ == "AssistantMessage":
                first_response_received = True
                first_response_time = current_time
                first_token_latency = first_response_time - api_call_start
                tracker.perf.record_stage("first_token_latency", first_token_latency, {
                    "milliseconds": round(first_token_latency * 1000, 1)
                })
                print(f"    [latency] first token: {first_token_latency*1000:.0f}ms")

                # Capture token counts at first token
                if hasattr(message, 'usage') and message.usage:
                    api_call_input_tokens = getattr(message.usage, 'input_tokens', 0) or 0
                    api_call_output_tokens = getattr(message.usage, 'output_tokens', 0) or 0

            # Track per-turn timing
            if type(message).__name__ == "AssistantMessage":
                turn_num = tracker.turns + 1
                if turn_num not in turn_start_times:
                    turn_start_times[turn_num] = current_time

            render_message(message, tracker)

            # Record per-turn timing after rendering
            if type(message).__name__ == "AssistantMessage":
                current_turn = tracker.turns
                if current_turn in turn_start_times and current_turn not in [t["turn"] for t in tracker.perf.turns]:
                    turn_duration = current_time - turn_start_times[current_turn]
                    usage = getattr(message, "usage", {}) or {}
                    tokens_in = usage.get("input_tokens", 0) or 0
                    tokens_out = usage.get("output_tokens", 0) or 0
                    tracker.perf.record_turn(current_turn, turn_duration * 1000, tokens_in, tokens_out, len(tracker.tool_calls))

            # Track final response time
            if type(message).__name__ == "ResultMessage":
                final_response_time = current_time

    except Exception as e:
        print(f"\n  [{label}] exception: {e}")
        tracker.last_error = str(e)
    finally:
        # Record API call timing
        if first_response_time and final_response_time:
            api_duration = final_response_time - api_call_start
            first_token_latency = first_response_time - api_call_start
            stream_duration = final_response_time - first_response_time
            tracker.perf.record_api_call(
                api_call_start,
                first_response_time,
                final_response_time,
                tracker.input_tokens,
                tracker.output_tokens
            )
            tracker.perf.record_stage("total_api_call", api_duration, {
                "first_token_latency_ms": round(first_token_latency * 1000, 1),
                "stream_duration_s": round(stream_duration, 2)
            })

        # Record batch timing
        batch_duration = time.time() - tracker.batch_start_time
        tracker.perf.record_batch(
            label,
            batch_duration,
            tracker.input_tokens,
            tracker.output_tokens,
            len(system_prompt.encode("utf-8"))
        )

        if phase:
            tracker.end_phase()

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
    model_override: str = None,
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

    # If slide plan provided (from Haiku planning phase), inject as context
    design_context = ""
    if slide_plan:
        batch_slides = [s for s in slide_plan.get("slides", [])
                       if slide_start <= s.get("slide_number", 0) <= slide_end]
        if batch_slides:
            design_context = f"""
CONTENT PLAN FROM PLANNING PHASE:
Use this detailed content plan as guidance for visual design decisions.
{json.dumps(batch_slides, indent=2)}

You are the visual design phase. Use the content plan above to create visually compelling
design decisions that align with the content and layout hints provided.

"""

    # Use optimized prompt builder with skill routing
    extra_content = design_context + batch_constraint
    prompt_build_start = time.time()
    system_prompt, routing_metadata = build_system_prompt_optimized(
        user_request=user_prompt,
        extra=extra_content
    )
    prompt_build_elapsed = time.time() - prompt_build_start

    batch_dir.mkdir(parents=True, exist_ok=True)

    # Phase 2: Pre-inject helpers template before agent starts
    if SchemaCompressionConfig.is_enabled(2):
        now_ts = int(time.time() * 1000)
        write_batch_helpers(batch_dir, counter_start=id_offset, now_ts=now_ts)

    tracker = await _run_single_agent(user_prompt, system_prompt, batch_dir, label, model_override=model_override, phase="design")

    # Store routing metadata in tracker
    tracker.skill_routing = routing_metadata

    # Record prompt building timing
    if "timing" in routing_metadata:
        tracker.perf.record_stage("prompt_building", prompt_build_elapsed, routing_metadata["timing"])
    else:
        tracker.perf.record_stage("prompt_building", prompt_build_elapsed, {"prompt_size_bytes": routing_metadata.get("prompt_size_bytes", 0)})

    return batch_dir, tracker


# ---------------------------------------------------------------------------
# Parallel runner — splits deck into batches, gathers, merges
# ---------------------------------------------------------------------------
async def run_parallel_agent(user_prompt: str, total_slides: int = 15, batch_size: int = 5, skip_planning: bool = False):
    model   = os.environ["ANTHROPIC_MODEL"]
    run_id  = f"run-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n--- run starting (parallel) ---")
    print(f"  prompt:     {user_prompt[:120]}")
    print(f"  run dir:    {run_dir}")
    print(f"  slides:     {total_slides} total, {batch_size} per batch")
    if skip_planning:
        print(f"  optimization: skipping haiku planning phase (speed over cost)")

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

    start_time = time.time()

    # PHASE 1: Haiku Planning (optional, disabled by default for speed)
    phase1_elapsed = 0
    planning_tracker = None
    slide_plan = None

    if skip_planning is False and False:  # Disabled: hybrid approach slower than all-Opus
        print(f"\n--- phase 1: haiku planning ---")
        phase1_start = time.time()
        try:
            from core.tracker import Tracker
            planning_tracker = Tracker("claude-haiku-4-5")
            slide_plan = await plan_presentation(user_prompt, total_slides, tracker=planning_tracker)
            phase1_elapsed = time.time() - phase1_start
            print(f"  planning complete in {phase1_elapsed:.1f}s")
        except Exception as e:
            print(f"  planning failed: {e}")
            print(f"  continuing with opus-only design phase")
            slide_plan = None
            phase1_elapsed = 0

    if slide_plan is None:
        print(f"\n--- phase 1: skipped (pure opus for speed) ---")

    # PHASE 2: Opus Design (per-batch in parallel)
    print(f"\n--- phase 2: opus design (parallel) ---")
    phase2_start = time.time()

    tasks = [
        run_batch_agent(
            user_prompt, s, e, total_slides, off, bd,
            slide_plan=slide_plan,
            model_override="claude-opus-4-7"
        )
        for s, e, off, bd in batches
    ]
    results = await asyncio.gather(*tasks)

    phase2_elapsed = time.time() - phase2_start
    elapsed_gen = time.time() - start_time
    print(f"\n--- all batches done in {phase2_elapsed:.1f}s (phase 2 only) ---")

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
    merge_duration = 0
    if len(batch_json_paths) == len(batches):
        print(f"\n--- merging {len(batch_json_paths)} batch JSONs ---")
        merge_start = time.time()
        try:
            merged = merge_presentations(batch_json_paths)
            write_start = time.time()
            with open(merged_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2)
            write_duration = time.time() - write_start

            # Apply schema compression if enabled
            compression_mode = SchemaCompressionConfig.get_compression_mode_string()
            if compression_mode != "legacy":
                compress_start = time.time()
                with open(merged_path, "r", encoding="utf-8") as f:
                    merged = json.load(f)
                merged = apply_schema_compression(merged, compression_mode, int(time.time()))
                with open(merged_path, "w", encoding="utf-8") as f:
                    json.dump(merged, f, indent=2)
                compress_duration = time.time() - compress_start
                print(f"  schema compression ({compression_mode}): {compress_duration*1000:.0f}ms")

            merge_duration = time.time() - merge_start
            print(f"  merged -> {merged_path.name}  "
                  f"({merged_path.stat().st_size:,} bytes)")
            print(f"  merge time: {merge_duration:.2f}s (write: {write_duration*1000:.0f}ms)")
            merge_ok = True
        except Exception as e:
            print(f"  merge failed: {e}")
            merge_duration = time.time() - merge_start
    else:
        missing = len(batches) - len(batch_json_paths)
        print(f"\n--- merge skipped: {missing} batch(es) produced no JSON ---")

    # Validate merged deck
    validation_passed = False
    validation_results = []
    validation_duration = 0
    if merge_ok:
        print(f"\n--- validating merged deck ---")
        validation_start = time.time()
        passed, problems, warnings = run_validation(merged_path)
        validation_duration = time.time() - validation_start
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {merged_path.name} ({validation_duration:.2f}s)")
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

    # Extract skill routing metadata (same for all batches)
    skill_routing = None
    if all_trackers and all_trackers[0].skill_routing:
        sr = all_trackers[0].skill_routing
        skill_routing = {
            "selected_skills": list(sr.get("selected_skill_names", set())),
            "excluded_skills": list(sr.get("excluded_skill_names", set())),
            "prompt_size_bytes": sr.get("prompt_size_bytes", 0),
            "full_prompt_size_bytes": sr.get("full_prompt_size_bytes", 0),
            "reduction_percent": round(sr.get("reduction_pct", 0), 1),
        }

    # Determine if using hybrid pipeline
    using_hybrid = slide_plan is not None

    # Get compression mode
    compression_mode = SchemaCompressionConfig.get_compression_mode_string()

    summary = {
        "run": {
            "id": run_id,
            "timestamp": int(time.time() * 1000),
            "prompt": user_prompt,
            "model": model,
            "duration_seconds": round(elapsed, 2),
            "success": validation_passed and not any(t.last_error for t in all_trackers),
            "batches": len(batches),
            "hybrid_pipeline": using_hybrid,
            "schema_compression": compression_mode,
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

    if skill_routing:
        summary["skill_optimization"] = skill_routing

    # Add comprehensive performance instrumentation data
    performance = {
        "timing": {
            "total_seconds": round(elapsed, 2),
            "preflight_seconds": 0.0,
            "planning_seconds": phase1_elapsed,
            "design_seconds": round(phase2_elapsed, 2),
            "merge_seconds": round(merge_duration, 2),
            "validation_seconds": round(validation_duration, 2),
        },
        "batches": [t.perf.to_dict()["batches"][0] if t.perf.batches else {} for t in all_trackers],
        "api_calls": {
            "total_calls": sum(len(t.perf.api_calls) for t in all_trackers),
            "total_first_token_latency_seconds": round(sum(
                c.get("first_token_latency_seconds", 0) for t in all_trackers for c in t.perf.api_calls
            ), 2),
            "average_first_token_latency_seconds": round(
                sum(c.get("first_token_latency_seconds", 0) for t in all_trackers for c in t.perf.api_calls) /
                max(1, sum(len(t.perf.api_calls) for t in all_trackers)), 2
            ),
        },
        "bottleneck_analysis": _analyze_bottlenecks(elapsed, phase1_elapsed, phase2_elapsed, merge_duration, validation_duration),
    }

    # Collect per-turn timing data
    all_turns = []
    for tracker in all_trackers:
        if tracker.perf.turns:
            all_turns.extend(tracker.perf.turns)
    if all_turns:
        performance["turns"] = {
            "total": len(all_turns),
            "average_duration_ms": round(sum(t["duration_ms"] for t in all_turns) / len(all_turns), 1),
            "details": all_turns[:20]  # First 20 turns for analysis
        }

    summary["performance"] = performance

    # Add phase timing if using hybrid pipeline
    if using_hybrid and phase1_elapsed > 0:
        phases_data = {
            "planning": {
                "model": "claude-haiku-4-5",
                "duration_seconds": round(phase1_elapsed, 2),
            },
            "design": {
                "model": "claude-opus-4-7",
                "duration_seconds": round(phase2_elapsed, 2),
            },
            "total": {
                "duration_seconds": round(elapsed, 2),
            },
        }

        # Add token and cost breakdown from planning tracker if available
        if planning_tracker:
            planning_breakdown = planning_tracker.get_total_breakdown()
            phases_data["planning"]["tokens_input"] = planning_tracker.input_tokens
            phases_data["planning"]["tokens_output"] = planning_tracker.output_tokens
            if planning_breakdown.get("total") is not None:
                phases_data["planning"]["cost"] = round(planning_breakdown["total"], 6)

        # Add design phase tokens (aggregated from all batch trackers)
        design_input = sum(t.input_tokens for t in all_trackers if t.phase == "design" or "design" in t.phases)
        design_output = sum(t.output_tokens for t in all_trackers if t.phase == "design" or "design" in t.phases)
        if design_input > 0 or design_output > 0:
            phases_data["design"]["tokens_input"] = design_input
            phases_data["design"]["tokens_output"] = design_output

        summary["phases"] = phases_data

    write_run_summary(run_dir, summary)

    # Print summary
    print(f"\n--- run summary ---")
    print(f"  duration:        {elapsed:.1f}s  (generation: {elapsed_gen:.1f}s)")
    print(f"  batches:         {len(batches)}")
    print(f"  assistant turns: {agg['turns']}")
    print(f"  tool calls:      {agg['tool_calls']}")
    print(f"  files written:   {len(agg['files_written'])}")
    print(f"  cost (sdk):      {fmt_money(agg['sdk_cost'])}")

    # Print bottleneck analysis
    if performance.get("bottleneck_analysis"):
        print(f"\n--- bottleneck analysis ---")
        for bottleneck in performance["bottleneck_analysis"]:
            print(f"  {bottleneck['stage']:12} {bottleneck['seconds']:7.2f}s  ({bottleneck['percentage']:5.1f}%)")

    # Print per-API-call timing
    if performance["api_calls"]["total_calls"] > 0:
        print(f"\n--- api timing ---")
        print(f"  total api calls:          {performance['api_calls']['total_calls']}")
        print(f"  avg first-token latency:  {performance['api_calls']['average_first_token_latency_seconds']:.3f}s")

    print(f"\n  run directory: {run_dir}")
    print(f"\n--- done ---")


def _analyze_bottlenecks(total_seconds: float, planning_seconds: float, design_seconds: float, merge_seconds: float, validation_seconds: float) -> list:
    """Identify and rank bottlenecks by time spent."""
    stages = [
        ("design", design_seconds),
        ("validation", validation_seconds),
        ("merge", merge_seconds),
        ("planning", planning_seconds),
    ]

    # Filter out zero-time stages
    stages = [(name, duration) for name, duration in stages if duration > 0.1]

    # Calculate percentages
    bottlenecks = []
    for stage_name, duration in sorted(stages, key=lambda x: x[1], reverse=True):
        percentage = (duration / total_seconds * 100) if total_seconds > 0 else 0
        bottlenecks.append({
            "stage": stage_name,
            "seconds": round(duration, 2),
            "percentage": round(percentage, 1),
        })

    return bottlenecks


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
