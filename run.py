"""
Full pipeline: enhance a short prompt with Azure OpenAI, then run agent.py
to generate the presentation JSON.

Usage:
    python3 run.py "coffee in Ethiopia"
    python3 run.py "quarterly sales review for SaaS startup"

Steps
-----
1. enhance.py  — Azure OpenAI rewrites the short prompt into a rich brief
2. agent.py    — Claude agent generates & validates the presentation JSON
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import anyio

from enhance import enhance
from core.config import preflight
from core.runner import run_parallel_agent


def main():
    if len(sys.argv) < 2:
        print("usage:   python3 run.py \"your short idea\"")
        print("example: python3 run.py \"coffee in Ethiopia\"")
        sys.exit(2)

    user_prompt = " ".join(sys.argv[1:])

    # ── Step 1: enhance ──────────────────────────────────────────────────
    print("\n=== STEP 1: Enhance prompt (Azure OpenAI) ===")
    enhanced_prompt = enhance(user_prompt)

    # ── Step 2: agent ────────────────────────────────────────────────────
    print("\n=== STEP 2: Generate presentation (Claude agent) ===")
    preflight()
    anyio.run(run_parallel_agent, enhanced_prompt)


if __name__ == "__main__":
    main()
