#!/usr/bin/env python3
"""
Test Phase 1 Schema Compression speed increase.

Measures total runtime (wall-clock time) for presentation generation
with legacy mode vs phase1 mode to see if fewer tokens = faster generation.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.config import preflight
import anyio


async def run_presentation(compression_mode: str, test_name: str):
    """Run presentation generator with specified compression mode."""
    os.environ["SCHEMA_COMPRESSION_MODE"] = compression_mode

    # Simpler prompt for faster testing
    user_prompt = """Create a 5-slide tech company pitch deck about AI productivity.

Slides:
1. Title slide with company vision
2. Problem statement
3. Solution overview
4. Market opportunity
5. Closing call to action

Style: Modern, minimalist, tech company aesthetic.
"""

    print(f"\n{test_name} (SCHEMA_COMPRESSION_MODE={compression_mode})")
    print("-" * 60)

    from core.runner import run_parallel_agent

    start_time = time.time()
    try:
        await run_parallel_agent(user_prompt)
        elapsed = time.time() - start_time
        print(f"[OK] Completed in {elapsed:.1f} seconds")
        return elapsed, True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[FAIL] Failed after {elapsed:.1f}s: {str(e)[:100]}")
        return elapsed, False


def get_latest_summary() -> dict:
    """Get most recent run_summary.json"""
    workspace = Path("workspace")
    run_dirs = sorted(
        [d for d in workspace.iterdir() if d.is_dir() and d.name.startswith("run-")],
        key=lambda p: int(p.name.split("-")[1]),
        reverse=True
    )
    if not run_dirs:
        return None

    summary_file = run_dirs[0] / "run_summary.json"
    if not summary_file.exists():
        return None

    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    print("\n" + "="*60)
    print("PHASE 1 SPEED TEST - Runtime Comparison")
    print("="*60)

    preflight()

    results = {}

    # Test 1: Baseline
    print("\n[1/2] BASELINE (no compression)...")
    baseline_time, baseline_ok = await run_presentation("legacy", "BASELINE")

    if baseline_ok:
        baseline_summary = get_latest_summary()
        baseline_tokens = baseline_summary.get("tokens", {}).get("output", 0) if baseline_summary else 0
        baseline_duration = baseline_summary.get("run", {}).get("duration_seconds", 0) if baseline_summary else 0
        results["baseline"] = {
            "wall_clock_seconds": baseline_time,
            "reported_seconds": baseline_duration,
            "output_tokens": baseline_tokens,
        }
    else:
        print("[FAIL] Baseline test failed")
        sys.exit(1)

    # Short delay
    time.sleep(3)

    # Test 2: Phase 1
    print("\n[2/2] PHASE 1 (with metadata compression)...")
    phase1_time, phase1_ok = await run_presentation("phase1", "PHASE 1")

    if phase1_ok:
        phase1_summary = get_latest_summary()
        phase1_tokens = phase1_summary.get("tokens", {}).get("output", 0) if phase1_summary else 0
        phase1_duration = phase1_summary.get("run", {}).get("duration_seconds", 0) if phase1_summary else 0
        results["phase1"] = {
            "wall_clock_seconds": phase1_time,
            "reported_seconds": phase1_duration,
            "output_tokens": phase1_tokens,
        }
    else:
        print("[FAIL] Phase 1 test failed")
        sys.exit(1)

    # Analysis
    print("\n" + "="*60)
    print("SPEED ANALYSIS")
    print("="*60)

    baseline_wall = results["baseline"]["wall_clock_seconds"]
    phase1_wall = results["phase1"]["wall_clock_seconds"]
    time_saved = baseline_wall - phase1_wall
    time_percent = (time_saved / baseline_wall) * 100 if baseline_wall > 0 else 0

    baseline_reported = results["baseline"]["reported_seconds"]
    phase1_reported = results["phase1"]["reported_seconds"]

    baseline_tokens = results["baseline"]["output_tokens"]
    phase1_tokens = results["phase1"]["output_tokens"]
    token_saved = baseline_tokens - phase1_tokens
    token_percent = (token_saved / baseline_tokens) * 100 if baseline_tokens > 0 else 0

    print(f"\nWall-Clock Time:")
    print(f"  Baseline:      {baseline_wall:.1f} seconds")
    print(f"  Phase 1:       {phase1_wall:.1f} seconds")
    print(f"  Time saved:    {time_saved:.1f} seconds ({time_percent:+.1f}%)")

    if time_saved > 0:
        speedup = baseline_wall / phase1_wall
        print(f"  Speedup:       {speedup:.2f}x faster")

    print(f"\nReported Duration (from run_summary.json):")
    print(f"  Baseline:      {baseline_reported:.1f} seconds")
    print(f"  Phase 1:       {phase1_reported:.1f} seconds")
    if baseline_reported > 0:
        print(f"  Difference:    {baseline_reported - phase1_reported:.1f} seconds")

    print(f"\nOutput Tokens:")
    print(f"  Baseline:      {baseline_tokens:,} tokens")
    print(f"  Phase 1:       {phase1_tokens:,} tokens")
    print(f"  Saved:         {token_saved:,} tokens ({token_percent:+.1f}%)")

    print(f"\nToken Efficiency (tokens per second):")
    baseline_efficiency = baseline_tokens / baseline_wall if baseline_wall > 0 else 0
    phase1_efficiency = phase1_tokens / phase1_wall if phase1_wall > 0 else 0
    print(f"  Baseline:      {baseline_efficiency:.0f} tokens/sec")
    print(f"  Phase 1:       {phase1_efficiency:.0f} tokens/sec")

    # Interpretation
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)

    if time_percent > 5:
        print(f"[EXCELLENT] Phase 1 is {time_percent:.1f}% faster")
        print("  Fewer tokens = faster Opus generation")
    elif time_percent > 0:
        print(f"[GOOD] Phase 1 is {time_percent:.1f}% faster")
        print("  Modest speedup from reduced token generation")
    elif time_percent > -5:
        print(f"[NEUTRAL] Times are similar ({time_percent:+.1f}%)")
        print("  Speed improvement may be within test variance")
    else:
        print(f"[CONCERN] Phase 1 is {abs(time_percent):.1f}% slower")
        print("  Unexpected - Phase 1 should not be slower")

    # Save results
    with open("phase1_speed_test_results.json", "w") as f:
        json.dump({
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results,
            "analysis": {
                "wall_clock_baseline": baseline_wall,
                "wall_clock_phase1": phase1_wall,
                "time_saved_seconds": time_saved,
                "time_saved_percent": time_percent,
                "speedup_multiplier": baseline_wall / phase1_wall if phase1_wall > 0 else 0,
                "tokens_baseline": baseline_tokens,
                "tokens_phase1": phase1_tokens,
                "tokens_saved": token_saved,
                "tokens_saved_percent": token_percent,
            }
        }, f, indent=2)

    print(f"\n[OK] Results saved to phase1_speed_test_results.json")
    print("="*60 + "\n")


if __name__ == "__main__":
    anyio.run(main)
