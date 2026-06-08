"""
Bildory presentation JSON validator.

Checks structural correctness of a generated presentation export:
- Envelope completeness
- Version strings
- Slide count consistency
- ID synchronization between content and changelog
- zIndex uniqueness across the whole deck

Usage:
    python3 validate.py <path_to_json>

Exit codes:
    0 — validation passed
    1 — validation failed (problems printed to stdout)
    2 — usage error or file not found
"""

import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Individual checks — each returns a list of problem strings
# ---------------------------------------------------------------------------

def check_envelope(data):
    """Top-level keys and the three files sub-keys exist."""
    problems = []
    for key in ["exportedAt", "presentation", "files"]:
        if key not in data:
            problems.append(f"missing root key: {key}")
    if "files" in data:
        for key in ["content", "baseLayout", "changelog"]:
            if key not in data["files"]:
                problems.append(f"missing files.{key}")
    return problems


def check_versions(data):
    """changelog.version must be '2.0', baseLayout.version must be 'v1'."""
    problems = []
    cl_version = data["files"]["changelog"].get("version")
    if cl_version != "2.0":
        problems.append(f"changelog.version must be '2.0' (got: {cl_version!r})")
    bl_version = data["files"]["baseLayout"].get("version")
    if bl_version != "v1":
        problems.append(f"baseLayout.version must be 'v1' (got: {bl_version!r})")
    return problems


def check_slide_counts(data):
    """content, baseLayout, and presentation.slideCount must agree."""
    problems = []
    content_slides = data["files"]["content"].get("slides", [])
    base_slides = data["files"]["baseLayout"].get("slides", [])
    declared = data["presentation"].get("slideCount")

    n_content = len(content_slides)
    n_base = len(base_slides)

    if n_content != n_base:
        problems.append(
            f"slide count mismatch: content.slides={n_content}, "
            f"baseLayout.slides={n_base}"
        )
    if declared != n_content:
        problems.append(
            f"presentation.slideCount ({declared}) does not match "
            f"content.slides length ({n_content})"
        )

    # Check that slide IDs match between content and baseLayout, in order
    for i, (c, b) in enumerate(zip(content_slides, base_slides)):
        if c.get("id") != b.get("id"):
            problems.append(
                f"slide {i}: content.id={c.get('id')!r} != "
                f"baseLayout.id={b.get('id')!r}"
            )
        if c.get("order") != i:
            problems.append(
                f"slide {c.get('id')}: order={c.get('order')} does not match "
                f"index {i}"
            )

    # Check that every slide has a changelog entry
    changelog_slides = data["files"]["changelog"].get("slides", {})
    for slide in content_slides:
        sid = slide.get("id")
        if sid not in changelog_slides:
            problems.append(f"slide {sid} has no changelog entry")

    return problems


def check_text_id_sync(data):
    """Every text element ID in content must appear in changelog and vice versa."""
    problems = []
    content_slides = data["files"]["content"].get("slides", [])
    changelog_slides = data["files"]["changelog"].get("slides", {})

    for slide in content_slides:
        sid = slide.get("id")
        text_in_content = {t["id"] for t in slide.get("textElements", [])}
        text_in_changelog = {
            eid for eid in changelog_slides.get(sid, {}).get("elements", {})
            if eid.startswith("text-")
        }
        only_content = text_in_content - text_in_changelog
        only_changelog = text_in_changelog - text_in_content
        if only_content:
            problems.append(
                f"slide {sid}: text IDs in content but missing from changelog: "
                f"{sorted(only_content)}"
            )
        # Note: changelog-only text IDs are orphans — allowed when editing
        # existing decks, but suspicious in freshly generated ones. We flag
        # them as a warning.
        if only_changelog:
            problems.append(
                f"slide {sid}: orphan text IDs in changelog (no matching "
                f"content entry): {sorted(only_changelog)}"
            )

    return problems


def check_shape_id_sync(data):
    """Shape IDs in content.shapeElements must appear in changelog."""
    problems = []
    content_shapes = data["files"]["content"].get("shapeElements", [])
    changelog_slides = data["files"]["changelog"].get("slides", {})

    shape_ids_content = {s["id"] for s in content_shapes}
    shape_ids_changelog = set()
    for sid, body in changelog_slides.items():
        for eid in body.get("elements", {}):
            if eid.startswith("shape-"):
                shape_ids_changelog.add(eid)

    only_content = shape_ids_content - shape_ids_changelog
    only_changelog = shape_ids_changelog - shape_ids_content
    if only_content:
        problems.append(
            f"shape IDs in content but missing from changelog: "
            f"{sorted(only_content)}"
        )
    if only_changelog:
        problems.append(
            f"orphan shape IDs in changelog (no matching content entry): "
            f"{sorted(only_changelog)}"
        )

    # Verify slideId consistency: each shape's content slideId should match
    # the slide its changelog entry lives under.
    content_shape_by_id = {s["id"]: s for s in content_shapes}
    for sid, body in changelog_slides.items():
        for eid, el in body.get("elements", {}).items():
            if eid.startswith("shape-") and eid in content_shape_by_id:
                content_sid = content_shape_by_id[eid].get("slideId")
                changelog_sid = el.get("slideId")
                if content_sid != sid:
                    problems.append(
                        f"shape {eid}: content.slideId={content_sid!r} "
                        f"but lives under changelog slide {sid!r}"
                    )
                if changelog_sid != sid:
                    problems.append(
                        f"shape {eid}: changelog.slideId={changelog_sid!r} "
                        f"but lives under changelog slide {sid!r}"
                    )

    return problems


def check_image_id_sync(data):
    """Image IDs in content.imageElements must appear in changelog."""
    problems = []
    content_images = data["files"]["content"].get("imageElements", [])
    changelog_slides = data["files"]["changelog"].get("slides", {})

    img_ids_content = {i["id"] for i in content_images}
    img_ids_changelog = set()
    for sid, body in changelog_slides.items():
        for eid in body.get("elements", {}):
            if eid.startswith("image-"):
                img_ids_changelog.add(eid)

    only_content = img_ids_content - img_ids_changelog
    only_changelog = img_ids_changelog - img_ids_content
    if only_content:
        problems.append(
            f"image IDs in content but missing from changelog: "
            f"{sorted(only_content)}"
        )
    if only_changelog:
        problems.append(
            f"orphan image IDs in changelog: {sorted(only_changelog)}"
        )

    return problems


def check_icon_id_sync(data):
    """Icon IDs in content.iconElements must appear in changelog."""
    problems = []
    content_icons = data["files"]["content"].get("iconElements", [])
    changelog_slides = data["files"]["changelog"].get("slides", {})

    icon_ids_content = {i["id"] for i in content_icons}
    icon_ids_changelog = set()
    for sid, body in changelog_slides.items():
        for eid in body.get("elements", {}):
            if eid.startswith("icon-"):
                icon_ids_changelog.add(eid)

    only_content = icon_ids_content - icon_ids_changelog
    only_changelog = icon_ids_changelog - icon_ids_content
    if only_content:
        problems.append(
            f"icon IDs in content but missing from changelog: "
            f"{sorted(only_content)}"
        )
    if only_changelog:
        problems.append(
            f"orphan icon IDs in changelog: {sorted(only_changelog)}"
        )

    return problems


def check_chart_id_sync(data):
    """Chart IDs in content.chartElements must appear in changelog."""
    problems = []
    content_charts = data["files"]["content"].get("chartElements", [])
    changelog_slides = data["files"]["changelog"].get("slides", {})

    chart_ids_content = {c["id"] for c in content_charts}
    chart_ids_changelog = set()
    for sid, body in changelog_slides.items():
        for eid in body.get("elements", {}):
            if eid.startswith("chart-"):
                chart_ids_changelog.add(eid)

    only_content = chart_ids_content - chart_ids_changelog
    only_changelog = chart_ids_changelog - chart_ids_content
    if only_content:
        problems.append(
            f"chart IDs in content but missing from changelog: "
            f"{sorted(only_content)}"
        )
    if only_changelog:
        problems.append(
            f"orphan chart IDs in changelog: {sorted(only_changelog)}"
        )

    return problems


def check_zindex_uniqueness(data):
    """Every zIndex across the whole deck must be unique."""
    problems = []
    changelog_slides = data["files"]["changelog"].get("slides", {})

    z_to_owner = {}  # zIndex -> list of (slide, element) using it
    for sid, body in changelog_slides.items():
        for eid, el in body.get("elements", {}).items():
            if "zIndex" in el:
                z = el["zIndex"]
                z_to_owner.setdefault(z, []).append((sid, eid))

    duplicates = {z: owners for z, owners in z_to_owner.items() if len(owners) > 1}
    if duplicates:
        # Cap reporting to first 5 to keep output sane
        for z, owners in list(duplicates.items())[:5]:
            owners_str = ", ".join(f"{s}/{e}" for s, e in owners)
            problems.append(f"zIndex {z} used by multiple elements: {owners_str}")
        if len(duplicates) > 5:
            problems.append(
                f"... and {len(duplicates) - 5} more duplicate zIndex values"
            )

    return problems


def check_element_count(data):
    """presentation.elementCount should equal the sum of all elements."""
    problems = []
    content = data["files"]["content"]

    total = 0
    for slide in content.get("slides", []):
        total += len(slide.get("textElements", []))
    total += len(content.get("imageElements", []))
    total += len(content.get("shapeElements", []))
    total += len(content.get("chartElements", []))
    total += len(content.get("tableElements", []))
    total += len(content.get("iconElements", []))
    total += len(content.get("embedElements", []))
    total += len(content.get("smartDiagramElements", []))
    total += len(content.get("groupElements", []))

    declared = data["presentation"].get("elementCount")
    if declared != total:
        problems.append(
            f"presentation.elementCount ({declared}) does not match "
            f"actual total ({total})"
        )

    return problems


def check_safe_zone(data):
    """Text elements should stay inside the 48px safe zone (warning only)."""
    warnings = []
    changelog_slides = data["files"]["changelog"].get("slides", {})

    SAFE_LEFT = 48
    SAFE_TOP = 48
    SAFE_RIGHT = 1232  # 1280 - 48
    SAFE_BOTTOM = 672  # 720 - 48

    for sid, body in changelog_slides.items():
        for eid, el in body.get("elements", {}).items():
            if not eid.startswith("text-"):
                continue
            pos = el.get("position", {})
            x = pos.get("x", 0)
            y = pos.get("y", 0)
            w = el.get("width", 0)
            h = el.get("height", 0)

            issues = []
            if x < SAFE_LEFT:
                issues.append(f"x={x} < {SAFE_LEFT}")
            if y < SAFE_TOP:
                issues.append(f"y={y} < {SAFE_TOP}")
            if x + w > SAFE_RIGHT:
                issues.append(f"x+width={x + w} > {SAFE_RIGHT}")
            if y + h > SAFE_BOTTOM:
                issues.append(f"y+height={y + h} > {SAFE_BOTTOM}")

            if issues:
                warnings.append(
                    f"text {eid} on {sid} outside safe zone: {', '.join(issues)}"
                )

    return warnings


# ---------------------------------------------------------------------------
# Main validation entry point
# ---------------------------------------------------------------------------

def validate(path):
    """Run all checks. Returns (problems, warnings) — both are lists of strings."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"file not found: {path}"], []
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"], []

    # If envelope is broken, downstream checks will crash — stop here.
    envelope_problems = check_envelope(data)
    if envelope_problems:
        return envelope_problems, []

    problems = []
    problems.extend(check_versions(data))
    problems.extend(check_slide_counts(data))
    problems.extend(check_text_id_sync(data))
    problems.extend(check_shape_id_sync(data))
    problems.extend(check_image_id_sync(data))
    problems.extend(check_icon_id_sync(data))
    problems.extend(check_chart_id_sync(data))
    problems.extend(check_zindex_uniqueness(data))
    problems.extend(check_element_count(data))

    warnings = check_safe_zone(data)

    return problems, warnings


def main():
    if len(sys.argv) < 2:
        print("usage: python3 validate.py <path_to_json>")
        sys.exit(2)

    path = sys.argv[1]
    problems, warnings = validate(path)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ! {w}")
        print()

    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print(f"  - {p}")
        print(f"\n{len(problems)} problem(s) found.")
        sys.exit(1)

    print(f"Validation: OK ({len(warnings)} warning(s))")
    sys.exit(0)


if __name__ == "__main__":
    main()
