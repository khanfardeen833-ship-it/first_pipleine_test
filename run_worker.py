"""
Entry point for the outline generation worker.

Usage:
    python run_worker.py

The worker polls MongoDB presentations collection for status='pending' documents,
generates a slide outline for each using Claude Haiku, stores the outline in the
outlines collection, then marks the presentation as 'done'.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import anyio
from core.config import preflight
from core.worker import run_worker

if __name__ == "__main__":
    preflight()
    anyio.run(run_worker)
