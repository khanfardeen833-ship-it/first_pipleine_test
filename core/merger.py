"""
Merges parallel batch JSONs into a single Bildory presentation JSON.
Each batch generates non-overlapping slide IDs and element ID ranges,
so the merge is a straight concatenation with no renumbering.
"""

import json
import time
from pathlib import Path


# Element arrays that live at files.content level (not inside slides)
_CONTENT_ARRAY_KEYS = [
    "imageElements",
    "shapeElements",
    "chartElements",
    "tableElements",
    "iconElements",
    "embedElements",
    "smartDiagramElements",
    "groupElements",
]


def _count_elements(content: dict) -> int:
    total = sum(len(s.get("textElements", [])) for s in content.get("slides", []))
    for key in _CONTENT_ARRAY_KEYS:
        total += len(content.get(key, []))
    return total


def merge_presentations(batch_json_paths: list) -> dict:
    batches = []
    for p in batch_json_paths:
        with open(p, encoding="utf-8") as f:
            batches.append(json.load(f))

    if not batches:
        raise ValueError("No batch JSONs to merge")

    first = batches[0]
    merged_content   = first["files"]["content"]
    merged_layout    = first["files"]["baseLayout"]
    merged_changelog = first["files"]["changelog"]
    merged_pres      = first["presentation"]

    for batch in batches[1:]:
        c  = batch["files"]["content"]
        bl = batch["files"]["baseLayout"]
        cl = batch["files"]["changelog"]

        merged_content["slides"].extend(c.get("slides", []))

        for key in _CONTENT_ARRAY_KEYS:
            if key not in merged_content:
                merged_content[key] = []
            merged_content[key].extend(c.get(key, []))

        if "slides" in bl:
            merged_layout["slides"].extend(bl["slides"])

        # changelog.slides is a dict keyed by slide ID — no conflicts by design
        if "slides" in cl:
            if "slides" not in merged_changelog:
                merged_changelog["slides"] = {}
            merged_changelog["slides"].update(cl["slides"])

    # order must match array index exactly
    for i, slide in enumerate(merged_content["slides"]):
        slide["order"] = i

    slide_count   = len(merged_content["slides"])
    element_count = _count_elements(merged_content)
    merged_pres["slideCount"]   = slide_count
    merged_pres["elementCount"] = element_count
    first["exportedAt"]          = int(time.time() * 1000)

    return first
