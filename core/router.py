"""
Skill router: analyzes user requests and determines which skills to load.
Reduces system prompt size by excluding irrelevant skills.
"""

import re
from typing import Set

SKILL_KEYWORDS = {
    "06-chart-element.md": [
        "sales", "revenue", "growth", "metrics", "kpi", "analytics",
        "dashboard", "statistics", "trend", "forecast", "data",
        "monthly", "quarterly", "annual", "quarterly", "chart",
        "graph", "bar", "line", "pie", "visualization", "numbers",
        "analysis", "report"
    ],
    "07-table-element.md": [
        "comparison", "table", "matrix", "pricing", "benchmark",
        "comparison table", "data table", "spreadsheet"
    ],
    "04-image-element.md": [
        "travel", "tourism", "culture", "geography", "product",
        "showcase", "photography", "coffee", "food", "visual",
        "image", "photo", "picture", "landscape", "scene"
    ],
    "05-icon-element.md": [
        "benefits", "features", "advantages", "checklist", "summary",
        "highlights", "key points", "icons", "symbol", "mark"
    ],
    "03-shape-element.md": [
        "workflow", "process", "architecture", "pipeline", "lifecycle",
        "journey", "roadmap", "system design", "flow", "diagram",
        "structure", "framework", "layout"
    ],
    "02-text-element.md": []  # Always included, no keywords needed
}

# Map skill filenames to display names
SKILL_DISPLAY_NAMES = {
    "02-text-element.md": "text",
    "03-shape-element.md": "shape",
    "04-image-element.md": "image",
    "05-icon-element.md": "icon",
    "06-chart-element.md": "chart",
    "07-table-element.md": "table",
}


def route_skills(user_request: str) -> Set[str]:
    """
    Analyze user request and determine which skills to load.

    Args:
        user_request: The user's presentation topic/request

    Returns:
        Set of skill filenames to load (e.g., {'02-text-element.md', '04-image-element.md'})
        Always includes text element.
    """
    # Always include text element and core skills (handled separately)
    selected_skills = {"02-text-element.md"}

    # Normalize request for matching
    normalized_request = _normalize_text(user_request)
    keywords = _extract_keywords(normalized_request)

    # Match keywords against skill registry
    for skill_file, skill_keywords in SKILL_KEYWORDS.items():
        if skill_file == "02-text-element.md":
            continue  # Already included

        for keyword in keywords:
            if keyword in skill_keywords:
                selected_skills.add(skill_file)
                break  # Found match, add skill and move to next skill

    return selected_skills


def _normalize_text(text: str) -> str:
    """Convert text to lowercase and remove extra whitespace."""
    return " ".join(text.lower().split())


def _extract_keywords(text: str) -> Set[str]:
    """
    Extract meaningful keywords from text.
    Removes common words and splits by whitespace/punctuation.
    """
    # Remove common stop words
    stop_words = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "as", "is", "are", "was",
        "be", "been", "being", "have", "has", "do", "does", "will",
        "can", "could", "should", "would", "make", "me", "your", "my",
        "build", "create", "new", "10", "20", "30", "40", "50", "slides",
        "slide", "deck", "presentation", "about"
    }

    # Split by non-alphanumeric characters and convert to lowercase
    words = re.findall(r"\b[a-z0-9]+\b", text)

    # Filter out stop words and single characters
    keywords = {word for word in words if word not in stop_words and len(word) > 1}

    return keywords


def get_skill_display_names(skill_files: Set[str]) -> Set[str]:
    """Convert skill filenames to display names for logging."""
    return {SKILL_DISPLAY_NAMES[skill] for skill in skill_files if skill in SKILL_DISPLAY_NAMES}


def get_excluded_skills(selected_skills: Set[str]) -> Set[str]:
    """Return skills that were not selected."""
    all_optional_skills = set(SKILL_KEYWORDS.keys())
    excluded = all_optional_skills - selected_skills
    return excluded


def log_routing_decision(
    user_request: str,
    selected_skills: Set[str],
    prompt_size_bytes: int,
    full_prompt_size_bytes: int
) -> str:
    """
    Generate a formatted log message showing routing decision and metrics.
    """
    selected_names = get_skill_display_names(selected_skills)
    excluded_names = get_skill_display_names(get_excluded_skills(selected_skills))

    reduction_pct = (1 - prompt_size_bytes / full_prompt_size_bytes) * 100 if full_prompt_size_bytes > 0 else 0
    estimated_token_reduction = int((full_prompt_size_bytes - prompt_size_bytes) / 4.5)  # ~4.5 chars per token

    log_lines = [
        "[SKILL ROUTING]",
        f"Request: \"{user_request[:60]}{'...' if len(user_request) > 60 else ''}\"",
        f"Selected Skills: {', '.join(sorted(selected_names))}",
        f"Excluded Skills: {', '.join(sorted(excluded_names)) if excluded_names else '(none)'}",
        f"Prompt Size: {prompt_size_bytes:,} / {full_prompt_size_bytes:,} bytes ({reduction_pct:.1f}% reduction)",
        f"Estimated Token Reduction: ~{estimated_token_reduction} input tokens"
    ]

    return "\n".join(log_lines)
