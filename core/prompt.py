"""
System prompt loader. Reads all skill .md files at startup and injects
their content directly into the system prompt. Eliminates Read tool calls
for skill files, saving 8-10 Bedrock round-trips (~70s) per run.
"""

from pathlib import Path
from core.config import (
    CORE_SKILLS, ELEM_SKILLS, SKILLS_INDEX,
    CORE_SKILL_FILES, ELEMENT_SKILL_FILES, PROMPTS_DIR, DECK_BUILDER_API,
)


def build_system_prompt(extra: str = "") -> str:
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
    result = template.replace("{{SKILLS_CONTENT}}", skills_content)
    result += "\n\n---\n\n" + DECK_BUILDER_API.read_text(encoding="utf-8")
    if extra:
        result += "\n\n" + extra
    return result
