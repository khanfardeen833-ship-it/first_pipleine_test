"""One-time migrator: turn snapshotted archetypes into skills/layouts/<type>/*.md.

Body text is written verbatim from scripts/_archetypes_snapshot.json (soft-
wrapped for readability; core.layouts._flow rejoins wrap points to a space, so
the round-trip is byte-identical). One-line `description:` index entries are
hand-authored in DESCRIPTIONS below.

Usage:  python scripts/_migrate_layouts.py title_only [bullets ...]
        python scripts/_migrate_layouts.py --all
"""
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = json.loads((ROOT / "scripts/_archetypes_snapshot.json").read_text(encoding="utf-8"))
LAYOUTS = ROOT / "skills" / "layouts"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# Hand-authored one-line "when to use" index entries (~20 tokens each).
DESCRIPTIONS = {
    ("title_only", "full-bleed hero"):
        "Opening hero — full-bleed image or deep color field, kicker chip, "
        "58-72pt title on one side, bottom stat ribbon.",
    ("title_only", "split hero"):
        "Opening — left color panel (kicker + huge title) beside a full-height "
        "image with a floating stat chip on the seam.",
    ("title_only", "editorial masthead"):
        "Magazine-cover opener — ultra-large display title low-left on generous "
        "whitespace, metadata rule, hairline grid; imagery optional.",
    ("title_only", "centered monolith"):
        "Symmetric luxury opener — centered title on a deep field inside a "
        "hairline frame, small crest, no photo.",
    ("title_only", "circular cutout hero"):
        "Opening — huge two-line title left, subject photo cropped to a circle "
        "inside oversized decorative rings on the right.",
    ("title_only", "photo-card + offset panel"):
        "Opening — a photo card floating over a solid accent offset panel on the "
        "left, large 3-line title on a light field right.",
    ("title_only", "dual-photo band"):
        "Dark opener — nav pill chips up top, huge 3-line title center-left, and "
        "a bottom band of two overlapping photos.",
    ("title_only", "circular subject hero"):
        "Light opener — ultra-large two-tone title with a pill CTA, subject photo "
        "cropped to a circle over accent circles on the right.",

    # bullets
    ("bullets", "stat band"):
        "Numbers-forward — pull the figures out of the bullets into a band of 3-4 "
        "big 60-90pt stat blocks plus one supporting image or insight card.",
    ("bullets", "icon card grid"):
        "Each bullet becomes an icon-badge card in an asymmetric grid (one card "
        "larger) — good for feature/benefit lists.",
    ("bullets", "numbered editorial"):
        "Vertical numbered list (01/02/03 in the gutter), accent bars, heading + "
        "caption per row, full-height image on the right.",
    ("bullets", "split feature"):
        "Left full-height image with an overlaid stat; right, bullets as staggered "
        "mini-cards with icon badges.",
    ("bullets", "editorial index"):
        "Whitespace-forward contents-page feel — each bullet a full-width row with "
        "a right-aligned number and hairline rules, no cards.",
    ("bullets", "feature + sidebar"):
        "One dominant hero insight (60-90pt) on the left beside a hairline-ruled "
        "sidebar of 2-3 quieter secondary points.",
    ("bullets", "numbered card rail"):
        "A horizontal row of 3-4 equal number-medallion cards on a band, with the "
        "last card highlighted as a deep accent panel.",
    ("bullets", "contents card"):
        "Agenda on a pale field — one large translucent card holding centered "
        "heading and full-width numbered pill rows.",

    # two_column
    ("two_column", "dual panel"):
        "Two contrasting panels (tinted vs outlined) with column headers and icon "
        "badges; bullets split as aligned rows across a divider.",
    ("two_column", "versus split"):
        "Hard 50/50 split with opposing tones, mirrored rows, and a central "
        "circular VS/theme badge on the seam — for comparisons.",
    ("two_column", "indexed ledger"):
        "Editorial ledger — a heavy left label rail anchors two columns stacked as "
        "hairline-divided rows with letterspaced headers.",

    # three_column
    ("three_column", "three cards"):
        "Three equal icon-badge cards with the middle one elevated (taller or "
        "tinted) for rhythm.",
    ("three_column", "offset trio"):
        "Three columns at staggered vertical offsets with a connecting through-line "
        "and oversized 01/02/03 numerals behind each.",
    ("three_column", "ribbon trio"):
        "A continuous top ribbon spans three number/icon-led blocks divided by "
        "vertical rules; optional bottom photo strip.",
    ("three_column", "pill-header ghost trio"):
        "Three columns, each a filled pill header above a light body card, with a "
        "faint ghost number behind; middle column in the contrast accent.",
    ("three_column", "tri-circle overlap"):
        "A centered Venn-style overlap of three translucent icon circles with text "
        "blocks around them — for intersecting themes.",
    ("three_column", "connected process trio"):
        "Three steps linked left-to-right by a connector line, each a node with an "
        "icon, a pill label on the line, and a caption — for processes.",

    # timeline
    ("timeline", "horizontal timeline"):
        "Baseline connector with circle year-badges, labels alternating above/"
        "below, and an accent 'now' marker.",
    ("timeline", "vertical milestones"):
        "Left rail connector with year badges, each milestone a row card to the "
        "right; final milestone highlighted.",
    ("timeline", "stepped ascent"):
        "Milestones climb an ascending diagonal connector, each step higher than "
        "the last, final 'now' node enlarged — a rising-trajectory feel.",

    # chart
    ("chart", "chart + callout"):
        "Chart on one side with a big-stat headline callout card beside it and "
        "small supporting icon rows.",
    ("chart", "hero chart"):
        "Chart is the hero (70-80% width) on a tinted plot panel, with a ribbon of "
        "2-3 stat callouts along one edge.",
    ("chart", "split data story"):
        "Left half chart, right half a stacked narrative — one bold takeaway plus "
        "3 insight rows with icon badges.",

    # quote
    ("quote", "editorial quote"):
        "Oversized quotation glyph, italic quote on a layered offset panel, "
        "attribution with an initial-badge, muted image behind — a rich quote.",
    ("quote", "centered statement"):
        "No image — a huge centered statement on a deep field with tiny "
        "attribution; confidence through restraint and scale.",
    ("quote", "portrait quote"):
        "Left full-height portrait, right the quote on an offset panel with "
        "attribution and proof chips — quote with a face.",

    # table
    ("table", "framed table"):
        "Table inside a framed panel with a heading row and one key-number callout "
        "chip; accent header treatment.",
    ("table", "comparison matrix"):
        "Table as a comparison grid — accent header, zebra rows, and one "
        "highlighted winning column/row so the recommendation pops.",
    ("table", "scorecard grid"):
        "Table read as a scorecard — each cell pairs its value with an icon/rating "
        "dot/tier chip, plus a floating key-number chip.",

    # closing
    ("closing", "light art-panel close"):
        "Warm light close — large sign-off word low-left, contact caption, and a "
        "Bauhaus-style abstract art panel of layered shapes on the right.",
    ("closing", "dark glow close"):
        "Dark close — big light sign-off word center-left beside a moody image "
        "bleeding off the right edge with a faked ambient glow.",
    ("closing", "illustration card close"):
        "Light close — a rounded white card holds the sign-off and CTA; right, a "
        "product photo on a filled accent shape with decorative marks.",
    ("closing", "circular subject close"):
        "Light close mirroring a circular-subject opener — ultra-large sign-off "
        "with a pill CTA, subject photo in a circle over accent circles.",
}


def migrate(layout_type: str) -> int:
    entries = SNAP[layout_type]
    outdir = LAYOUTS / layout_type
    outdir.mkdir(parents=True, exist_ok=True)
    written = 0
    for order, (name, body) in enumerate(entries):
        desc = DESCRIPTIONS.get((layout_type, name))
        if not desc:
            raise SystemExit(f"missing DESCRIPTIONS entry for ({layout_type!r}, {name!r})")
        sid = slug(name)
        wrapped = textwrap.fill(body, width=88, break_long_words=False,
                                break_on_hyphens=False)
        fm = (f"---\n"
              f"id: {sid}\n"
              f"name: {name}\n"
              f"layout_type: {layout_type}\n"
              f"order: {order}\n"
              f"description: {desc}\n"
              f"---\n\n")
        path = outdir / f"{order:02d}-{sid}.md"
        path.write_text(fm + wrapped + "\n", encoding="utf-8")
        print(f"  wrote {path.relative_to(ROOT)}")
        written += 1
    return written


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    types = list(SNAP.keys()) if args == ["--all"] else args
    total = sum(migrate(t) for t in types)
    print(f"migrated {total} layout(s) across {len(types)} type(s): {', '.join(types)}")


if __name__ == "__main__":
    main()
