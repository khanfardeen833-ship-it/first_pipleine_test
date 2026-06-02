"""
Bildory presentation generator using Claude Agent SDK with parallel batching.

Usage:
    python agent.py "Build me a 10-slide deck about coffee in Ethiopia" [total_slides] [batch_size]
"""

import sys
import anyio

from core.config import preflight
from core.runner import run_parallel_agent


def main():
    print("Bildory Presentation Agent")
    preflight()

    if len(sys.argv) < 2:
        print("\nusage:   python agent.py \"your presentation request\" [slides] [batch_size]")
        print("example: python agent.py \"coffee deck\" 10 5")
        sys.exit(2)

    prompt = " ".join(sys.argv[1:])
    total_slides = 10
    batch_size = 5

    # Parse optional arguments
    if len(sys.argv) >= 3:
        try:
            total_slides = int(sys.argv[-2])
            batch_size = int(sys.argv[-1])
            prompt = " ".join(sys.argv[1:-2])
        except (ValueError, IndexError):
            pass

    anyio.run(run_parallel_agent, prompt, total_slides, batch_size)


if __name__ == "__main__":
    main()
