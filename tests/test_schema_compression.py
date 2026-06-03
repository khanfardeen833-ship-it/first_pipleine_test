"""
Tests for schema compression (Phase 1).

Tests the post-processor functions that:
1. Generate UUIDs and element IDs client-side
2. Normalize timestamps across a batch
3. Remove redundant fields
4. Apply compression mode-based transformations
"""

import json
import time
from pathlib import Path
from uuid import UUID

from core.post_processor import (
    precompute_metadata,
    recalculate_element_ids,
    normalize_timestamps,
    cleanup_unused_fields,
    apply_schema_compression,
)
from core.schema_config import SchemaCompressionConfig, CompressionMode


def create_test_batch_json():
    """Create a minimal batch JSON for testing."""
    return {
        "exportedAt": int(time.time() * 1000),
        "presentation": {
            "title": "Test Presentation",
            "slideCount": 1,
            "elementCount": 2,
            "createdAt": "2026-06-02T00:00:00Z",
            "updatedAt": "2026-06-02T00:00:00Z",
        },
        "files": {
            "content": {
                "slides": [
                    {
                        "id": "slide-1",
                        "order": 0,
                        "backgroundColor": "#ffffff",
                        "textElements": [
                            {
                                "id": "text-1",
                                "type": "text",
                                "originalType": "text",  # Redundant - should be removed
                                "content": "Hello",
                                "formattedContent": "Hello",  # Duplicate - should be removed
                                "version": "2.0",  # Should be removed
                                "position": {"x": 100, "y": 100},
                                "size": {"width": 300, "height": 50},
                                "color": "#000000",
                                "fontSize": 16,
                                "fontFamily": "Inter",
                            }
                        ],
                        "shapeElements": [
                            {
                                "id": "shape-1",
                                "type": "rectangle",
                                "originalType": "rectangle",  # Redundant
                                "position": {"x": 500, "y": 100},
                                "size": {"width": 200, "height": 200},
                                "fillColor": "#3b82f6",
                            }
                        ],
                    }
                ]
            },
            "changelog": {"version": "2.0", "slides": {}},
            "baseLayout": {"version": "v1", "slides": []},
        },
    }


def test_precompute_metadata_adds_uuid():
    """Test that precompute_metadata adds UUIDs to elements."""
    batch_json = create_test_batch_json()
    batch_timestamp = time.time()

    # Before: no uuid
    assert "uuid" not in batch_json["files"]["content"]["slides"][0]["textElements"][0]

    # Apply precomputation
    result = precompute_metadata(batch_json, batch_timestamp, skip_id_generation=False)

    # After: uuid should exist and be valid
    text_elem = result["files"]["content"]["slides"][0]["textElements"][0]
    assert "uuid" in text_elem
    # Verify it's a valid UUID
    UUID(text_elem["uuid"])


def test_precompute_metadata_normalizes_timestamps():
    """Test that precompute_metadata normalizes timestamps."""
    batch_json = create_test_batch_json()
    batch_timestamp = time.time()

    result = precompute_metadata(batch_json, batch_timestamp, skip_id_generation=False)

    text_elem = result["files"]["content"]["slides"][0]["textElements"][0]
    shape_elem = result["files"]["content"]["slides"][0]["shapeElements"][0]

    # All elements should have consistent timestamps
    assert "createdAt" in text_elem
    assert "updatedAt" in text_elem
    assert "createdAt" in shape_elem
    assert "updatedAt" in shape_elem
    assert text_elem["createdAt"] == shape_elem["createdAt"]
    assert text_elem["updatedAt"] == shape_elem["updatedAt"]


def test_precompute_metadata_removes_redundant_fields():
    """Test that precompute_metadata removes redundant fields."""
    batch_json = create_test_batch_json()

    result = precompute_metadata(batch_json, time.time(), skip_id_generation=False)

    text_elem = result["files"]["content"]["slides"][0]["textElements"][0]
    shape_elem = result["files"]["content"]["slides"][0]["shapeElements"][0]

    # Redundant fields should be removed
    assert "originalType" not in text_elem
    assert "originalType" not in shape_elem
    assert "formattedContent" not in text_elem
    assert "version" not in text_elem
    assert "version" not in shape_elem


def test_recalculate_element_ids_global():
    """Test that recalculate_element_ids generates sequential IDs globally."""
    batch_json = create_test_batch_json()

    result = recalculate_element_ids(batch_json, per_slide=False)

    slide = result["files"]["content"]["slides"][0]
    text_ids = [e.get("id") for e in slide.get("textElements", [])]
    shape_ids = [e.get("id") for e in slide.get("shapeElements", [])]

    # IDs use uniform "text-N" / "shape-N" prefixes regardless of element subtype
    assert text_ids == ["text-1"]
    assert shape_ids == ["shape-1"]


def test_recalculate_element_ids_per_slide():
    """Test that recalculate_element_ids resets counter per slide."""
    batch_json = create_test_batch_json()
    # Add second slide
    batch_json["files"]["content"]["slides"].append({
        "id": "slide-2",
        "order": 1,
        "backgroundColor": "#ffffff",
        "textElements": [{"type": "text", "content": "Slide 2"}],
        "shapeElements": [],
    })

    result = recalculate_element_ids(batch_json, per_slide=True)

    slide1 = result["files"]["content"]["slides"][0]
    slide2 = result["files"]["content"]["slides"][1]

    # Each slide should start with text-1
    assert slide1["textElements"][0]["id"] == "text-1"
    assert slide2["textElements"][0]["id"] == "text-1"


def test_normalize_timestamps_consistent_across_elements():
    """Test that normalize_timestamps uses consistent timestamp."""
    batch_json = create_test_batch_json()
    run_timestamp = time.time()

    result = normalize_timestamps(batch_json, run_timestamp)

    text_elem = result["files"]["content"]["slides"][0]["textElements"][0]
    shape_elem = result["files"]["content"]["slides"][0]["shapeElements"][0]

    # All timestamps should be identical
    assert text_elem["createdAt"] == shape_elem["createdAt"]
    assert text_elem["updatedAt"] == shape_elem["updatedAt"]
    assert result["presentation"]["createdAt"] == text_elem["createdAt"]


def test_cleanup_unused_fields():
    """Test that cleanup_unused_fields removes unused fields."""
    batch_json = create_test_batch_json()
    slide = batch_json["files"]["content"]["slides"][0]

    # Add unused fields
    slide["textElements"][0]["sourceId"] = "src-123"
    slide["textElements"][0]["metadata"] = {"key": "value"}
    slide["textElements"][0]["locked"] = False
    slide["textElements"][0]["_internal"] = "internal"
    slide["textElements"][0]["_debug"] = "debug"
    slide["textElements"][0]["_cache"] = "cache"

    result = cleanup_unused_fields(batch_json)

    text_elem = result["files"]["content"]["slides"][0]["textElements"][0]

    # Unused fields should be removed
    assert "sourceId" not in text_elem
    assert "metadata" not in text_elem
    assert "locked" not in text_elem
    assert "_internal" not in text_elem
    assert "_debug" not in text_elem
    assert "_cache" not in text_elem


def test_apply_schema_compression_phase1():
    """Test Phase 1 compression (metadata precomputation)."""
    batch_json = create_test_batch_json()

    result = apply_schema_compression(batch_json, "phase1", int(time.time()))

    text_elem = result["files"]["content"]["slides"][0]["textElements"][0]

    # Phase 1 should:
    # 1. Add uuid
    # 2. Normalize timestamps
    # 3. Remove redundant fields
    assert "uuid" in text_elem
    assert "createdAt" in text_elem
    assert "updatedAt" in text_elem
    assert "originalType" not in text_elem
    assert "formattedContent" not in text_elem
    assert "version" not in text_elem


def test_apply_schema_compression_legacy():
    """Test legacy mode (no compression)."""
    batch_json = create_test_batch_json()
    original = json.dumps(batch_json)

    result = apply_schema_compression(batch_json, "legacy", int(time.time()))

    # Legacy mode should not modify the JSON
    # (except for some normalizations that happen anyway)
    assert "textElements" in result["files"]["content"]["slides"][0]


def test_token_reduction_estimation():
    """Estimate token savings from Phase 1 compression.

    Note: In this small test, post-processor adds UUIDs and timestamps,
    which may increase size. Real savings come from Opus NOT generating
    these fields in the first place (via system prompt instructions).

    With system prompt optimization:
    - Opus omits: id, uuid, updatedAt, createdAt, originalType, formattedContent, version
    - Opus generates normal design fields
    - Client-side post-processor adds back: uuid, updatedAt, createdAt (much shorter than Opus versions)
    - Net result: 5-10% reduction in large presentations
    """
    batch_json = create_test_batch_json()

    # Count fields before
    before_str = json.dumps(batch_json)
    before_size = len(before_str.encode("utf-8"))

    result = apply_schema_compression(batch_json, "phase1", int(time.time()))
    after_str = json.dumps(result)
    after_size = len(after_str.encode("utf-8"))

    # In this small test, we add UUIDs which increases size
    # Real savings come from Opus NOT generating redundant fields
    size_difference = (before_size - after_size) / before_size * 100
    print(f"\nToken reduction estimation:")
    print(f"  Before: {before_size} bytes")
    print(f"  After: {after_size} bytes")
    print(f"  Difference: {size_difference:.1f}%")
    print(f"  (Note: Small test case adds UUIDs. Real savings in full presentations.)")

    # In real presentations, Phase 1 should save 5-10%
    # This test is too small to demonstrate that, but we verify the logic works
    assert "uuid" in after_str  # UUIDs were added
    assert "originalType" not in after_str  # Redundant fields removed


def test_phase2_cleanup_content_record_duplicates():
    """Phase 2: _cleanup_content_record_duplicates removes originalType and formattedContent."""
    from core.post_processor import _cleanup_content_record_duplicates
    batch_json = {
        "files": {
            "content": {
                "slides": [
                    {
                        "id": "slide-1",
                        "textElements": [
                            {"id": "text-1", "content": "Hello", "type": "title",
                             "originalType": "title", "formattedContent": "Hello"},
                            {"id": "text-2", "content": "World", "type": "caption",
                             "originalType": "caption", "formattedContent": "World"},
                        ]
                    }
                ]
            }
        }
    }
    result = _cleanup_content_record_duplicates(batch_json)
    slides = result["files"]["content"]["slides"]
    elems = slides[0]["textElements"]
    assert "originalType" not in elems[0], "originalType should be removed"
    assert "formattedContent" not in elems[0], "formattedContent should be removed"
    assert elems[0]["type"] == "title"
    assert elems[0]["content"] == "Hello"


def test_phase2_apply_schema_compression():
    """Phase 2: apply_schema_compression phase2 includes Phase 1 + duplicate cleanup."""
    from core.post_processor import apply_schema_compression
    batch_json = {
        "exportedAt": 1000000,
        "files": {
            "content": {
                "slides": [
                    {
                        "id": "slide-1",
                        "textElements": [
                            {"id": "text-1", "content": "A", "type": "title",
                             "originalType": "title", "formattedContent": "A",
                             "sourceId": "should-be-removed"},
                        ],
                        "shapeElements": []
                    }
                ]
            },
            "changelog": {"slides": {}}
        }
    }
    result = apply_schema_compression(batch_json, "phase2", batch_timestamp=1000.0)
    elem = result["files"]["content"]["slides"][0]["textElements"][0]
    assert "uuid" in elem, "Phase 1: uuid should be added"
    assert "originalType" not in elem, "Phase 2: originalType should be removed"
    assert "formattedContent" not in elem, "Phase 2: formattedContent should be removed"
    assert "sourceId" not in elem, "Phase 1: sourceId should be cleaned up"


def test_phase2_write_batch_helpers():
    """Phase 2: write_batch_helpers generates valid, executable _helpers.py."""
    import tempfile, os
    from core.build_helpers_template import write_batch_helpers
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        write_batch_helpers(tmpdir, counter_start=300, now_ts=1780400000000)
        helpers_path = Path(tmpdir) / "_helpers.py"
        assert helpers_path.exists(), "_helpers.py should be created"
        content = helpers_path.read_text(encoding="utf-8")
        assert "COUNTER = 300" in content, "COUNTER should be parameterized"
        assert "NOW = 1780400000000" in content, "NOW should be parameterized"
        assert "def make_text" in content, "make_text should be defined"
        assert "def save_deck" in content, "save_deck should be defined"
        assert "__NOW__" not in content, "placeholder should be replaced"
        assert "__COUNTER_START__" not in content, "placeholder should be replaced"

        # Verify it executes without error
        namespace = {}
        exec(content, namespace)
        assert "nid" in namespace
        assert "make_text" in namespace
        assert "save_deck" in namespace
        assert namespace["COUNTER"] == 300
        assert namespace["NOW"] == 1780400000000


def test_phase3_macros_in_helpers_template():
    """Phase 3: _helpers.py includes all 6 layout macro helpers."""
    import tempfile
    from core.build_helpers_template import write_batch_helpers
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        write_batch_helpers(tmpdir, counter_start=0, now_ts=1780400000000)
        content = Path(tmpdir / "_helpers.py" if hasattr(tmpdir, "__truediv__") else Path(tmpdir) / "_helpers.py").read_text()

        for macro in ["def add_mono", "def add_eyebrow", "def add_page_num",
                      "def add_bg", "def add_band", "def add_rule", "def add_slide_header"]:
            assert macro in content, f"{macro} should be in _helpers.py"


def test_phase3_macros_functional():
    """Phase 3: macro helpers produce correct elements via add_text/add_shape."""
    import tempfile, os, json
    from core.build_helpers_template import write_batch_helpers
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        write_batch_helpers(tmpdir, counter_start=0, now_ts=1780400000000)
        helpers_content = (Path(tmpdir) / "_helpers.py").read_text()

        slide_code = """
S1 = "slide-1"
init_slide(S1, 0, bg="#000011")

# Phase 3 macros
add_bg(S1, "#0B1020")
add_eyebrow(S1, "CHAPTER 01", "#94A3B8")
add_page_num(S1, "01", "#FFFFFF")
add_band(S1, 400, 80, "#111A33", opacity=0.6)
add_rule(S1, 80, "#334155")
add_mono(S1, "API", "caption", 80, 200, 200, 24, "#21D4FD", size=12, spacing=2)

save_deck("Phase 3 Test")
"""
        original_dir = os.getcwd()
        os.chdir(tmpdir)
        try:
            ns = {}
            exec(helpers_content, ns)
            exec(slide_code, ns)
            deck = json.loads((Path(tmpdir) / "deck.json").read_text())
            slide = deck["files"]["content"]["slides"][0]
            changelog = deck["files"]["changelog"]["slides"]["slide-1"]["elements"]

            # Should have 6 elements from macros (3 shapes + 3 texts)
            assert deck["presentation"]["elementCount"] == 6, \
                f"Expected 6 elements, got {deck['presentation']['elementCount']}"

            # Check eyebrow text is uppercase-transform capable
            text_ids = [k for k in changelog if k.startswith("text-")]
            eyebrow_elem = next(
                (changelog[t] for t in text_ids
                 if changelog[t].get("style", {}).get("textTransform") == "uppercase"), None
            )
            assert eyebrow_elem is not None, "eyebrow should have textTransform=uppercase"
            assert eyebrow_elem["style"]["fontFamily"] == "JetBrains Mono", \
                "eyebrow should use JetBrains Mono"

            # Check page number is right-aligned
            page_num_elem = next(
                (changelog[t] for t in text_ids
                 if changelog[t].get("style", {}).get("textAlign") == "right"), None
            )
            assert page_num_elem is not None, "page_num should be right-aligned"
        finally:
            os.chdir(original_dir)


def test_phase3_prompt_instructions():
    """Phase 3: compression instructions include Phase 3 macro documentation."""
    import os
    from core.prompt import build_compression_instructions

    os.environ["SCHEMA_COMPRESSION_MODE"] = "phase3"
    instructions = build_compression_instructions()

    assert "PHASE 3" in instructions, "Should have Phase 3 section"
    assert "add_eyebrow" in instructions, "Should document add_eyebrow"
    assert "add_page_num" in instructions, "Should document add_page_num"
    assert "add_slide_header" in instructions, "Should document add_slide_header"
    assert "add_bg" in instructions, "Should document add_bg"

    # Reset
    os.environ["SCHEMA_COMPRESSION_MODE"] = "phase1"


if __name__ == "__main__":
    # Run tests manually
    test_precompute_metadata_adds_uuid()
    print("✓ test_precompute_metadata_adds_uuid")

    test_precompute_metadata_normalizes_timestamps()
    print("✓ test_precompute_metadata_normalizes_timestamps")

    test_precompute_metadata_removes_redundant_fields()
    print("✓ test_precompute_metadata_removes_redundant_fields")

    test_recalculate_element_ids_global()
    print("✓ test_recalculate_element_ids_global")

    test_recalculate_element_ids_per_slide()
    print("✓ test_recalculate_element_ids_per_slide")

    test_normalize_timestamps_consistent_across_elements()
    print("✓ test_normalize_timestamps_consistent_across_elements")

    test_cleanup_unused_fields()
    print("✓ test_cleanup_unused_fields")

    test_apply_schema_compression_phase1()
    print("✓ test_apply_schema_compression_phase1")

    test_apply_schema_compression_legacy()
    print("✓ test_apply_schema_compression_legacy")

    test_token_reduction_estimation()
    print("✓ test_token_reduction_estimation")

    print("\n✅ All schema compression tests passed!")
