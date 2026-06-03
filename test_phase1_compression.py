#!/usr/bin/env python3
"""
Test Phase 1 Schema Compression against baseline.

Runs presentations with legacy mode and phase1 mode,
compares output tokens to verify 5-10% savings prediction.
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import preflight
import anyio


async def run_test_presentation(compression_mode: str, test_name: str):
    """Run presentation generator with specified compression mode."""
    os.environ["SCHEMA_COMPRESSION_MODE"] = compression_mode

    # Use a moderately-sized presentation prompt (8 slides)
    user_prompt = """Create a business presentation about sustainable practices.

Include these topics:
- Environmental impact introduction
- Current challenges
- Corporate responsibility
- Green technology solutions
- Renewable energy overview
- Carbon footprint reduction
- Impact metrics and goals
- Call to action

Style: Clean, professional, corporate design with earth-tone colors.
"""

    print(f"\n{'='*70}")
    print(f"Running {test_name} with SCHEMA_COMPRESSION_MODE={compression_mode}")
    print(f"{'='*70}")
    print(f"Prompt: {user_prompt[:100]}...")

    # Import here to get config with updated env var
    from core.runner import run_parallel_agent

    try:
        await run_parallel_agent(user_prompt)
        print(f"[OK] {test_name} completed")
        return True
    except Exception as e:
        print(f"[FAIL] {test_name} failed: {e}")
        return False


def get_latest_run_summary() -> dict:
    """Find and read the most recent run_summary.json file."""
    workspace = Path("workspace")
    if not workspace.exists():
        print("ERROR: workspace directory not found")
        return None

    # Find most recent run directory
    run_dirs = sorted(
        [d for d in workspace.iterdir() if d.is_dir() and d.name.startswith("run-")],
        key=lambda p: int(p.name.split("-")[1]),
        reverse=True
    )

    if not run_dirs:
        print("ERROR: No run directories found")
        return None

    latest_run = run_dirs[0]
    summary_file = latest_run / "run_summary.json"

    if not summary_file.exists():
        print(f"ERROR: {summary_file} not found")
        return None

    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    """Run comparison test."""
    print("\n" + "="*70)
    print("PHASE 1 COMPRESSION TEST - Token Savings Verification")
    print("="*70)

    preflight()

    results = {}

    # Test 1: Legacy mode (baseline)
    print("\n[1/2] Running BASELINE (legacy mode)...")
    baseline_success = await run_test_presentation("legacy", "BASELINE TEST")

    if baseline_success:
        baseline_summary = get_latest_run_summary()
        if baseline_summary:
            baseline_tokens = baseline_summary.get("tokens", {}).get("output", 0)
            baseline_run_id = baseline_summary.get("run", {}).get("id")
            results["baseline"] = {
                "run_id": baseline_run_id,
                "output_tokens": baseline_tokens,
                "compression_mode": baseline_summary.get("run", {}).get("schema_compression", "legacy"),
            }
            print(f"[OK] Baseline tokens: {baseline_tokens}")
        else:
            print("[FAIL] Failed to read baseline summary")
            sys.exit(1)
    else:
        print("[FAIL] Baseline test failed")
        sys.exit(1)

    # Small delay between tests
    time.sleep(2)

    # Test 2: Phase 1 mode
    print("\n[2/2] Running PHASE 1 (with compression)...")
    phase1_success = await run_test_presentation("phase1", "PHASE 1 TEST")

    if phase1_success:
        phase1_summary = get_latest_run_summary()
        if phase1_summary:
            phase1_tokens = phase1_summary.get("tokens", {}).get("output", 0)
            phase1_run_id = phase1_summary.get("run", {}).get("id")
            results["phase1"] = {
                "run_id": phase1_run_id,
                "output_tokens": phase1_tokens,
                "compression_mode": phase1_summary.get("run", {}).get("schema_compression", "phase1"),
            }
            print(f"[OK] Phase 1 tokens: {phase1_tokens}")
        else:
            print("[FAIL] Failed to read phase1 summary")
            sys.exit(1)
    else:
        print("[FAIL] Phase 1 test failed")
        sys.exit(1)

    # Calculate savings
    print("\n" + "="*70)
    print("RESULTS: Token Savings Analysis")
    print("="*70)

    baseline_output = results["baseline"]["output_tokens"]
    phase1_output = results["phase1"]["output_tokens"]

    token_reduction = baseline_output - phase1_output
    percent_reduction = (token_reduction / baseline_output) * 100 if baseline_output > 0 else 0

    print(f"\nBaseline (legacy):        {baseline_output:,} tokens")
    print(f"Phase 1 (compressed):     {phase1_output:,} tokens")
    print(f"\nToken reduction:          {token_reduction:,} tokens")
    print(f"Percent reduction:        {percent_reduction:.2f}%")

    print(f"\nBaseline run ID:          {results['baseline']['run_id']}")
    print(f"Phase 1 run ID:           {results['phase1']['run_id']}")

    # Verify against prediction
    print("\n" + "="*70)
    print("PREDICTION vs ACTUAL")
    print("="*70)
    print(f"Expected: 5-10% reduction")
    print(f"Actual:   {percent_reduction:.2f}% reduction")

    if 5 <= percent_reduction <= 10:
        print("[PASS] RESULT: Within expected range (5-10%)")
        status = "PASS"
    elif percent_reduction < 5:
        print("[MARGINAL] RESULT: Below expected range (< 5%)")
        print("   - Phase 1 may not be fully active")
        print("   - Check SCHEMA_COMPRESSION_MODE environment variable")
        status = "MARGINAL"
    elif percent_reduction > 10:
        print("[EXCELLENT] RESULT: Exceeds expected range (> 10%)")
        print("   - Savings are better than predicted!")
        status = "EXCELLENT"
    else:
        print("[FAIL] RESULT: Negative reduction (compression increased tokens)")
        print("   - Something is wrong - Phase 1 should never increase tokens")
        status = "FAIL"

    # Save results
    results_file = Path("phase1_compression_test_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "baseline": results["baseline"],
            "phase1": results["phase1"],
            "analysis": {
                "baseline_tokens": baseline_output,
                "phase1_tokens": phase1_output,
                "token_reduction": token_reduction,
                "percent_reduction": percent_reduction,
                "status": status,
            }
        }, f, indent=2)

    print(f"\n[OK] Results saved to: {results_file}")
    print("="*70 + "\n")

    return status


if __name__ == "__main__":
    result = anyio.run(main)
    if result == "FAIL":
        sys.exit(1)
