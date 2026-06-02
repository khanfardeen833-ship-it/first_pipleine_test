"""
Environment loading, path constants, and pre-flight checks.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from core.pricing import get_pricing, fmt_money

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_DIR  = Path(__file__).parent.parent.resolve()
SKILLS_DIR   = PROJECT_DIR / "skills"
CORE_SKILLS  = SKILLS_DIR / "core"
ELEM_SKILLS  = SKILLS_DIR / "elements"
SKILLS_INDEX = SKILLS_DIR / "00-index.md"
WORKSPACE    = PROJECT_DIR / "workspace"
VALIDATOR    = PROJECT_DIR / "validate.py"
PROMPTS_DIR  = PROJECT_DIR / "prompts"

CORE_SKILL_FILES = [
    "01-envelope.md",
    "08-changelog-sync.md",
    "09-zindex-rules.md",
    "10-design-rules.md",
]

ELEMENT_SKILL_FILES = [
    "02-text-element.md",
    "03-shape-element.md",
    "04-image-element.md",
    "05-icon-element.md",
    "06-chart-element.md",
    "07-table-element.md",
]


# ---------------------------------------------------------------------------
# Pre-flight
# ---------------------------------------------------------------------------
def preflight():
    problems = []

    for var in ["ANTHROPIC_MODEL", "ANTHROPIC_API_KEY"]:
        if not os.environ.get(var, "").strip():
            problems.append(f"missing or empty env var: {var}")

    if not SKILLS_INDEX.exists():
        problems.append(f"skills index not found: {SKILLS_INDEX}")

    for fname in CORE_SKILL_FILES:
        fpath = CORE_SKILLS / fname
        if not fpath.exists():
            problems.append(f"core skill missing: {fpath}")

    for fname in ELEMENT_SKILL_FILES:
        fpath = ELEM_SKILLS / fname
        if not fpath.exists():
            problems.append(f"element skill missing: {fpath}")

    if not VALIDATOR.exists():
        problems.append(f"validator not found: {VALIDATOR}")

    if not PROMPTS_DIR.exists():
        problems.append(f"prompts directory not found: {PROMPTS_DIR}")

    if problems:
        print("PRE-FLIGHT FAILED:")
        for p in problems:
            print(f"  {p}")
        sys.exit(1)

    WORKSPACE.mkdir(exist_ok=True)

    model = os.environ["ANTHROPIC_MODEL"]
    rates, is_known = get_pricing(model)

    print("pre-flight OK")
    print(f"  model:     {model}")
    print(f"  api:       anthropic (direct)")
    print(f"  workspace: {WORKSPACE}")
    print(f"  core skills:    {len(CORE_SKILL_FILES)} files")
    print(f"  element skills: {len(ELEMENT_SKILL_FILES)} files")
    if is_known:
        print(f"  pricing:   in ${rates['input']}/M  out ${rates['output']}/M  "
              f"cache-write ${rates['cache_write_1h']}/M  cache-read ${rates['cache_read']}/M")
    else:
        print(f"  pricing:   no schema found for {model!r} — cost tracking disabled")
