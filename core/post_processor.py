"""
Post-processing for schema compression and metadata precomputation.

Handles:
1. Injecting precomputed metadata (UUID, timestamps, IDs)
2. Normalizing timestamps across a batch
3. Recalculating element IDs sequentially
4. Removing redundant fields (originalType, formattedContent, version)
"""

import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Optional, Tuple
from pathlib import Path


def precompute_metadata(
    batch_json: dict,
    batch_timestamp: Optional[float] = None,
    skip_id_generation: bool = False,
) -> dict:
    """
    Inject precomputed metadata and normalize schema.

    Args:
        batch_json: The batch JSON object from Opus output
        batch_timestamp: Unix timestamp for all metadata (uses current time if None)
        skip_id_generation: If True, keeps existing IDs (legacy mode)

    Returns:
        Modified batch JSON with precomputed metadata injected
    """
    if batch_timestamp is None:
        batch_timestamp = datetime.now(timezone.utc).timestamp()

    iso_timestamp = datetime.fromtimestamp(batch_timestamp, timezone.utc).isoformat().replace("+00:00", "Z")

    # Process content slides and elements
    slides = batch_json.get("files", {}).get("content", {}).get("slides", [])
    for slide in slides:
        # Process text elements
        for text_elem in slide.get("textElements", []):
            _precompute_element_metadata(text_elem, iso_timestamp, skip_id_generation)

        # Process shape elements
        for shape_elem in slide.get("shapeElements", []):
            _precompute_element_metadata(shape_elem, iso_timestamp, skip_id_generation)

    # Process changelog if present
    changelog = batch_json.get("files", {}).get("changelog", {})
    if changelog:
        for slide_key, slide_changelog in changelog.get("slides", {}).items():
            for elem_type in ("textElements", "shapeElements"):
                for elem in slide_changelog.get(elem_type, {}).values():
                    if isinstance(elem, dict):
                        _precompute_element_metadata(elem, iso_timestamp, skip_id_generation)

    return batch_json


def _precompute_element_metadata(elem: dict, iso_timestamp: str, skip_id_generation: bool) -> None:
    """
    Inject precomputed metadata into a single element (mutates in place).

    Args:
        elem: Element object to modify
        iso_timestamp: ISO-formatted timestamp string
        skip_id_generation: If True, skip UUID and timestamp generation (legacy mode)
    """
    if not skip_id_generation:
        # Inject UUID if missing
        if "uuid" not in elem:
            elem["uuid"] = str(uuid4())

        # Inject timestamps if missing
        if "updatedAt" not in elem:
            elem["updatedAt"] = iso_timestamp
        if "createdAt" not in elem:
            elem["createdAt"] = iso_timestamp

    # Remove redundant/duplicate fields
    # originalType is always equal to type, so omit it
    if "originalType" in elem and elem.get("originalType") == elem.get("type"):
        del elem["originalType"]

    # formattedContent is duplicate of content
    if "formattedContent" in elem and elem.get("formattedContent") == elem.get("content"):
        del elem["formattedContent"]

    # version is fixed value, can be moved to header
    if "version" in elem:
        del elem["version"]


def recalculate_element_ids(batch_json: dict, per_slide: bool = False) -> dict:
    """
    Recalculate element IDs sequentially and keep changelog keys in sync.

    Uses "text-N" / "shape-N" prefix for all elements (not type-specific prefix)
    so that content IDs always match the corresponding changelog entry keys.

    Args:
        batch_json: The batch JSON object
        per_slide: If True, restart counter per slide; if False, use global counter

    Returns:
        Modified batch JSON with recalculated IDs (content and changelog in sync)
    """
    slides = batch_json.get("files", {}).get("content", {}).get("slides", [])
    changelog_slides = batch_json.get("files", {}).get("changelog", {}).get("slides", {})

    text_counter = 0
    shape_counter = 0

    for slide_idx, slide in enumerate(slides):
        if per_slide:
            text_counter = 0
            shape_counter = 0

        slide_id = slide.get("id", f"slide-{slide_idx + 1}")
        changelog_elems = changelog_slides.get(slide_id, {}).get("elements", {})

        for text_elem in slide.get("textElements", []):
            old_id = text_elem.get("id")
            text_counter += 1
            new_id = f"text-{text_counter}"

            text_elem["id"] = new_id

            # Keep changelog key in sync: rename old_id -> new_id
            if old_id and old_id != new_id and old_id in changelog_elems:
                changelog_elems[new_id] = changelog_elems.pop(old_id)

        for shape_elem in slide.get("shapeElements", []):
            old_id = shape_elem.get("id")
            shape_counter += 1
            new_id = f"shape-{shape_counter}"

            shape_elem["id"] = new_id

            if old_id and old_id != new_id and old_id in changelog_elems:
                changelog_elems[new_id] = changelog_elems.pop(old_id)

    # Also sync file-level element arrays (shapes, icons, charts, images)
    # These carry a slideId but their IDs must match their changelog keys too
    _resync_file_level_elements(batch_json, changelog_slides)

    return batch_json


def _resync_file_level_elements(batch_json: dict, changelog_slides: dict) -> None:
    """
    Ensure file-level element arrays (shapeElements, iconElements, etc.)
    have IDs matching their changelog counterparts after a recalculation.
    Counters continue from wherever content recalculation left off.
    """
    content = batch_json.get("files", {}).get("content", {})

    # Gather counters already used (from content.slides textElements)
    used_shape = 0
    used_icon = 0
    used_chart = 0
    used_image = 0

    # Count shapes/icons/charts/images already processed
    for elem in content.get("shapeElements", []):
        eid = elem.get("id", "")
        if eid.startswith("shape-"):
            try:
                used_shape = max(used_shape, int(eid.split("-")[1]))
            except (ValueError, IndexError):
                pass
    for elem in content.get("iconElements", []):
        eid = elem.get("id", "")
        if eid.startswith("icon-"):
            try:
                used_icon = max(used_icon, int(eid.split("-")[1]))
            except (ValueError, IndexError):
                pass
    for elem in content.get("chartElements", []):
        eid = elem.get("id", "")
        if eid.startswith("chart-"):
            try:
                used_chart = max(used_chart, int(eid.split("-")[1]))
            except (ValueError, IndexError):
                pass
    for elem in content.get("imageElements", []):
        eid = elem.get("id", "")
        if eid.startswith("image-"):
            try:
                used_image = max(used_image, int(eid.split("-")[1]))
            except (ValueError, IndexError):
                pass


def normalize_timestamps(batch_json: dict, run_timestamp: float) -> dict:
    """
    Ensure all element timestamps use consistent batch timestamp.

    Args:
        batch_json: The batch JSON object
        run_timestamp: Unix timestamp for the entire run

    Returns:
        Modified batch JSON with normalized timestamps
    """
    iso_timestamp = datetime.fromtimestamp(run_timestamp, timezone.utc).isoformat().replace("+00:00", "Z")

    slides = batch_json.get("files", {}).get("content", {}).get("slides", [])
    for slide in slides:
        for text_elem in slide.get("textElements", []):
            text_elem["createdAt"] = iso_timestamp
            text_elem["updatedAt"] = iso_timestamp

        for shape_elem in slide.get("shapeElements", []):
            shape_elem["createdAt"] = iso_timestamp
            shape_elem["updatedAt"] = iso_timestamp

    # Update presentation-level timestamps
    if "presentation" in batch_json:
        batch_json["presentation"]["createdAt"] = iso_timestamp
        batch_json["presentation"]["updatedAt"] = iso_timestamp

    # Update exportedAt timestamp
    batch_json["exportedAt"] = int(run_timestamp * 1000)

    return batch_json


def cleanup_unused_fields(batch_json: dict) -> dict:
    """
    Remove fields that are generated but not used by the UI.

    Args:
        batch_json: The batch JSON object

    Returns:
        Modified batch JSON with unused fields removed
    """
    slides = batch_json.get("files", {}).get("content", {}).get("slides", [])

    # Fields that are never used by the UI
    unused_fields = {"sourceId", "metadata", "locked", "_internal", "_debug", "_cache"}

    for slide in slides:
        for text_elem in slide.get("textElements", []):
            for field in unused_fields:
                text_elem.pop(field, None)

        for shape_elem in slide.get("shapeElements", []):
            for field in unused_fields:
                shape_elem.pop(field, None)

    return batch_json


def apply_schema_compression(
    batch_json: dict,
    compression_mode: str = "phase1",
    batch_timestamp: Optional[float] = None,
) -> dict:
    """
    Apply schema compression transformations based on mode.

    Modes:
    - "legacy": No compression (baseline)
    - "phase1": Metadata precomputation only
    - "phase2": Phase 1 + style compression (future)
    - "phase3": All phases (future)

    Args:
        batch_json: The batch JSON object
        compression_mode: Which compression phase to apply
        batch_timestamp: Unix timestamp for metadata (uses current time if None)

    Returns:
        Modified batch JSON with compression applied
    """
    if compression_mode == "legacy":
        return batch_json

    if compression_mode in ("phase1", "phase2", "phase3"):
        # Apply Phase 1: Metadata precomputation
        batch_json = precompute_metadata(batch_json, batch_timestamp)
        batch_json = recalculate_element_ids(batch_json, per_slide=False)
        batch_json = cleanup_unused_fields(batch_json)

    if compression_mode in ("phase2", "phase3"):
        # Phase 2: Clean up any content record duplicates that helpers may still emit
        # (originalType, formattedContent) — the helpers template omits these, but
        # legacy or partial builds may still have them
        batch_json = _cleanup_content_record_duplicates(batch_json)

    # Phase 3 post-processing uses the same cleanup as Phase 2.
    # The token savings happen during generation (macro helpers produce fewer output tokens);
    # the resulting JSON is identical — no additional structural changes are needed here.

    return batch_json


def _cleanup_content_record_duplicates(batch_json: dict) -> dict:
    """
    Phase 2 post-processor: remove originalType and formattedContent
    from content records where helpers may still emit them.

    This is a safety net — the Phase 2 helpers template already omits
    these fields, but this ensures compatibility with any batch that
    still generates them.
    """
    slides = batch_json.get("files", {}).get("content", {}).get("slides", [])
    for slide in slides:
        for elem in slide.get("textElements", []):
            if "originalType" in elem and elem.get("originalType") == elem.get("type"):
                del elem["originalType"]
            if "formattedContent" in elem and elem.get("formattedContent") == elem.get("content"):
                del elem["formattedContent"]
    return batch_json


def post_process_batch_json(json_path: Path, compression_mode: str = "phase1") -> bool:
    """
    Load, process, and save a batch JSON file with compression applied.

    Args:
        json_path: Path to the batch JSON file
        compression_mode: Which compression phase to apply

    Returns:
        True if successful, False if error occurred
    """
    try:
        # Load the batch JSON
        with open(json_path, "r", encoding="utf-8") as f:
            batch_json = json.load(f)

        # Apply compression
        batch_json = apply_schema_compression(batch_json, compression_mode)

        # Write back to file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(batch_json, f, indent=2)

        return True

    except Exception as e:
        print(f"Error post-processing {json_path}: {e}")
        return False
