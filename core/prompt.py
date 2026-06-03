"""
System prompt loader with dynamic skill routing.

Provides two modes:
1. build_system_prompt() - Legacy: loads all skills (backward compatible)
2. build_system_prompt_optimized() - New: loads only relevant skills based on request
"""

import time
from pathlib import Path
from typing import Set
from core.config import (
    CORE_SKILLS, ELEM_SKILLS, SKILLS_INDEX,
    CORE_SKILL_FILES, ELEMENT_SKILL_FILES, PROMPTS_DIR,
)
from core.router import route_skills, get_skill_display_names, get_excluded_skills
from core.schema_config import SchemaCompressionConfig


def build_compression_instructions() -> str:
    """
    Build schema compression instructions based on current mode.
    Returns empty string if compression disabled.
    """
    if not SchemaCompressionConfig.precompute_metadata():
        return ""

    phase1_instructions = """
## SCHEMA COMPRESSION (PHASE 1)

You are generating JSON with schema compression enabled. The client will inject certain fields
that do not require design reasoning. DO NOT generate these fields:

Fields the client will add automatically (don't generate):
- `id`: Element identifiers (e.g., "text-1", "shape-2") → client generates sequentially
- `uuid`: Unique identifiers → client generates via uuid.uuid4()
- `updatedAt`: Last modified timestamp → client adds batch timestamp
- `createdAt`: Creation timestamp → client adds batch timestamp
- `created`: Creation timestamp → client adds batch timestamp
- `formattedContent`: Always equals `content` → omit this duplicate
- `originalType`: Always equals `type` → omit this duplicate
- `version`: Fixed schema version → client adds to header only

IMPORTANT: These are NOT design decisions. Removing them saves ~5-10% output tokens
while preserving all design quality.

Design-critical fields you MUST generate:
- `content`, `text`: Slide content and messaging
- `type`: Element type (text, shape, image, chart, icon, etc.)
- All style fields: color, fontSize, fontFamily, fontWeight, backgroundColor, etc.
- All layout fields: position (x, y), size (width, height), rotation, zIndex
- Visual effects: shadow, blur, opacity, stroke, borderRadius
- Media: imageUrl, chartData, chartConfig, svgContent
- Relationships: groupId (only if grouped), parentId (for nested elements)

Generate all design fields normally. The schema compression is transparent to design quality.
"""

    if not SchemaCompressionConfig.compress_styles():
        return phase1_instructions.strip()

    phase2_instructions = """
## SCHEMA COMPRESSION (PHASE 2 — PRE-LOADED HELPERS)

The file `_helpers.py` has been pre-loaded in your working directory.
It already defines all required helper functions and containers:
- `nid()`, `make_text()`, `make_shape()`, `make_icon()`, `make_chart()`, `make_image()`
- `init_slide()`, `add_text()`, `add_shape()`, `add_icon()`, `add_chart()`, `add_image()`
- `save_deck(title)` — assembles and writes deck.json
- `NOW`, `COUNTER` — pre-set with correct batch timestamp and ID offset
- All container variables: `slides_content`, `changelog_slides`, etc.

Your build.py MUST:
1. Start with: `from _helpers import *`
2. Define your palette color constants
3. Write slide construction code using the pre-loaded helpers
4. End with: `save_deck("Your Presentation Title")`

DO NOT redefine nid(), make_text(), make_shape(), make_icon(), make_chart(),
make_image(), init_slide(), add_text(), add_shape(), add_icon(), add_chart(),
add_image(), save_deck(), or any containers.
DO NOT add boilerplate for counting elements or assembling the envelope — save_deck() handles it.

Example minimal build.py structure:
```python
from _helpers import *

# Palette
BG = "#0B1020"
ACCENT = "#3B82F6"
WHITE = "#F8FAFC"

# Slide 1
S1 = "slide-1"
init_slide(S1, 0, bg=BG)
add_text(S1, "Title Here", "title", 80, 200, 1000, 100, color=WHITE)
add_shape(S1, "rectangle", 0, 0, 1280, 720, fill=BG, opacity=1)

save_deck("My Presentation")
```

This saves ~200 lines of boilerplate per batch = ~1,000 tokens per batch saved.
"""

    if not SchemaCompressionConfig.use_layout_templates():
        return (phase1_instructions + phase2_instructions).strip()

    phase3_instructions = """
## SCHEMA COMPRESSION (PHASE 3 — LAYOUT MACROS)

`_helpers.py` also provides compact macro helpers for the most common slide patterns.
Use these instead of the verbose explicit calls — each saves 10-20 tokens.

### JetBrains Mono text (saves ~4 tokens per call):
```python
# Instead of:
add_text(S, text, type_, x, y, w, h, color=C, font_size=12, font_family="JetBrains Mono", ...)
# Use:
add_mono(S, text, type_, x, y, w, h, C, size=12, spacing=2, transform="uppercase")
```

### Eyebrow caption — top-left chapter label (saves ~18 tokens):
```python
# Instead of:
add_text(S, "CHAPTER 01", "caption", 80, 48, 400, 20, color=C, font_size=11,
         font_family="JetBrains Mono", letter_spacing=2, text_transform="uppercase")
# Use:
add_eyebrow(S, "CHAPTER 01", C)                       # x=80, y=48 defaults
add_eyebrow(S, "CHAPTER 01", C, x=80, y=48, size=11)  # explicit if needed
```

### Page number — bottom-right (saves ~14 tokens):
```python
# Instead of:
add_text(S, "03", "caption", 1180, 670, 60, 24, color=C, font_size=14,
         font_family="JetBrains Mono", font_weight=700, text_align="right")
# Use:
add_page_num(S, "03", C)
```

### Combined slide header — eyebrow + page number in one call (saves ~25 tokens):
```python
add_slide_header(S, "CHAPTER 01", "03", eyebrow_color=SILVER, num_color=AMBER)
add_slide_header(S, "CHAPTER 01", "03", SILVER, AMBER, rule=True, rule_color=NAVY)
```

### Background shapes (saves ~4-6 tokens per call):
```python
add_bg(S, OBSIDIAN)                     # full 1280×720 background
add_band(S, y=470, h=250, fill=NAVY, opacity=0.7)  # horizontal band
add_rule(S, y=80, color=CYAN, opacity=0.3)          # thin 1px divider
```

### Usage priority:
- ALWAYS use `add_eyebrow()` for chapter/section labels
- ALWAYS use `add_page_num()` for slide numbers
- PREFER `add_slide_header()` to combine both in one call
- USE `add_bg()` for full-canvas backgrounds
- USE `add_mono()` for any JetBrains Mono text with multiple kwargs
- Keep explicit `add_text()` / `add_shape()` for custom positions and unique elements
"""

    return (phase1_instructions + phase2_instructions + phase3_instructions).strip()


def load_core_skills() -> tuple[str, int]:
    """
    Load core skills (always required).
    Returns: (content: str, size_bytes: int)
    """
    sections = []
    sections.append("### SKILLS INDEX\n" + SKILLS_INDEX.read_text(encoding="utf-8"))

    for fname in CORE_SKILL_FILES:
        content = (CORE_SKILLS / fname).read_text(encoding="utf-8")
        sections.append(f"### {fname}\n{content}")

    skills_content = "\n\n---\n\n".join(sections)
    return skills_content, len(skills_content.encode("utf-8"))


def load_selected_skills(selected_skill_files: Set[str]) -> tuple[str, int]:
    """
    Load only specified element skills.

    Args:
        selected_skill_files: Set of skill filenames (e.g., {"02-text-element.md", "04-image-element.md"})

    Returns:
        (content: str, size_bytes: int)
    """
    sections = []

    for fname in selected_skill_files:
        if fname.startswith("02-") or fname.startswith("03-") or fname.startswith("04-") or \
           fname.startswith("05-") or fname.startswith("06-") or fname.startswith("07-"):
            file_path = ELEM_SKILLS / fname
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                sections.append(f"### {fname}\n{content}")

    # Sort sections by filename for consistency
    sections.sort()
    skills_content = "\n\n---\n\n".join(sections)
    return skills_content, len(skills_content.encode("utf-8"))


def build_system_prompt(extra: str = "") -> str:
    """
    Legacy: Load all skills (backward compatible).
    Use build_system_prompt_optimized() for better performance.
    """
    sections = []
    sections.append("### SKILLS INDEX\n" + SKILLS_INDEX.read_text(encoding="utf-8"))

    for fname in CORE_SKILL_FILES:
        content = (CORE_SKILLS / fname).read_text(encoding="utf-8")
        sections.append(f"### {fname}\n{content}")

    for fname in ELEMENT_SKILL_FILES:
        content = (ELEM_SKILLS / fname).read_text(encoding="utf-8")
        sections.append(f"### {fname}\n{content}")

    skills_content = "\n\n---\n\n".join(sections)

    prompt_file = PROMPTS_DIR / "system_prompt.md"
    template = prompt_file.read_text(encoding="utf-8")

    # Replace compression instructions
    compression_instructions = build_compression_instructions()
    result = template.replace("{{SKILLS_CONTENT}}", skills_content)
    result = result.replace("{{SCHEMA_COMPRESSION_INSTRUCTIONS}}", compression_instructions)

    if extra:
        result += "\n\n" + extra
    return result


def build_system_prompt_optimized(user_request: str, extra: str = "") -> tuple[str, dict]:
    """
    Load system prompt with selective skill loading based on user request.

    Args:
        user_request: The user's presentation topic/request
        extra: Optional extra content to append (batch constraints, etc.)

    Returns:
        (system_prompt: str, metadata: dict)
        where metadata contains: {
            "selected_skills": set of skill filenames,
            "prompt_size_bytes": total size,
            "reduction_pct": percentage reduction vs full prompt
        }
    """
    build_start = time.time()

    # Load core skills (always required)
    core_start = time.time()
    core_content, core_size = load_core_skills()
    core_elapsed = (time.time() - core_start) * 1000

    # Route to determine which optional skills to load
    routing_start = time.time()
    selected_skills = route_skills(user_request)
    routing_elapsed = (time.time() - routing_start) * 1000

    # Load selected skills
    loading_start = time.time()
    optional_content, optional_size = load_selected_skills(selected_skills)
    loading_elapsed = (time.time() - loading_start) * 1000

    # Combine core and optional
    combine_start = time.time()
    skills_content = core_content
    if optional_content:
        skills_content += "\n\n---\n\n" + optional_content
    combine_elapsed = (time.time() - combine_start) * 1000

    # Build full prompt
    template_start = time.time()
    prompt_file = PROMPTS_DIR / "system_prompt.md"
    template = prompt_file.read_text(encoding="utf-8")
    result = template.replace("{{SKILLS_CONTENT}}", skills_content)

    # Replace compression instructions
    compression_instructions = build_compression_instructions()
    result = result.replace("{{SCHEMA_COMPRESSION_INSTRUCTIONS}}", compression_instructions)

    if extra:
        result += "\n\n" + extra
    template_elapsed = (time.time() - template_start) * 1000

    # Calculate metrics
    calc_start = time.time()
    prompt_size_bytes = len(result.encode("utf-8"))
    full_prompt = build_system_prompt()
    full_prompt_size = len(full_prompt.encode("utf-8"))
    reduction_pct = (1 - prompt_size_bytes / full_prompt_size) * 100 if full_prompt_size > 0 else 0
    calc_elapsed = (time.time() - calc_start) * 1000

    build_total_elapsed = (time.time() - build_start) * 1000

    metadata = {
        "selected_skills": selected_skills,
        "selected_skill_names": get_skill_display_names(selected_skills),
        "excluded_skills": get_excluded_skills(selected_skills),
        "excluded_skill_names": get_skill_display_names(get_excluded_skills(selected_skills)),
        "prompt_size_bytes": prompt_size_bytes,
        "full_prompt_size_bytes": full_prompt_size,
        "reduction_pct": reduction_pct,
        # Performance instrumentation
        "timing": {
            "skill_routing_ms": round(routing_elapsed, 1),
            "skill_loading_ms": round(loading_elapsed, 1),
            "core_skills_load_ms": round(core_elapsed, 1),
            "content_combine_ms": round(combine_elapsed, 1),
            "template_building_ms": round(template_elapsed, 1),
            "metrics_calc_ms": round(calc_elapsed, 1),
            "total_prompt_building_ms": round(build_total_elapsed, 1),
        }
    }

    return result, metadata
