"""
Generate a deck DESIGN with GPT (OpenAI) instead of Claude slidegen — a quality
probe for when Anthropic credits are unavailable.

How it works: it monkeypatches core.slidegen._generate_one with a GPT
function-calling version that emits the SAME emit_slide spec, then reuses the
ENTIRE deterministic tail of the pipeline (archetype assignment, spec
expansion, merge, layout normalization, image resolution, PPTX export, HTML
preview). No Anthropic API calls are made — the run is forced onto the
all-offline slidegen path (layout-select off, mode=fast, visual-QA off).

The outline itself is also written by GPT (emit_outline), so the whole design
is GPT's.

Usage:
    python scripts/run_topic_gpt.py "luxury electric hypercar launch" --slides 8
"""

import argparse
import asyncio
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Force the all-offline slidegen path (no Anthropic) BEFORE anything reads env.
os.environ["SLIDEGEN_LAYOUT_SELECT"] = "0"   # OFF by default: library layouts crowd reasoning-off
# models (regen cascade costs more than the prefix-caching saves). Enable with --layout-select.
os.environ["SLIDEGEN_MODE"] = "fast"          # skip Anthropic art-director plan
os.environ["SLIDEGEN_VISUAL_QA"] = "0"        # base default; --qa (on by default below) flips it
# Settled QA-loop recipe: retry ANY sub-pass slide (<=6) up to 3 total tries.
os.environ.setdefault("SLIDEGEN_QA_SEVERE_MAX", "6")
os.environ.setdefault("SLIDEGEN_QA_MAX_ATTEMPTS", "3")

from dotenv import load_dotenv
load_dotenv()
from openai import AsyncOpenAI

import core.slidegen as sg
from core.slidegen import (SLIDE_TOOL, DESIGN_PLAN_TOOL, _slide_user_message,
                           expand_slide_spec)
from core.layouts import SELECT_TOOL, layout_index_text, fallback_selection
from core.config import WORKSPACE, VALIDATOR

# Layout keys understood by assign_archetypes / the archetype library.
LAYOUTS = ["title_only", "two_column", "three_column", "bullets",
           "chart", "timeline", "table", "quote", "closing"]

# Settled default generation model: terra is the value-optimal tier (luna gen
# drops quality; gpt-5.5 costs 2x for no gain under QA). Override with --model.
OPENAI_MODEL = os.environ.get("SLIDEGEN_GPT_MODEL", "gpt-5.6-terra")
_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


# OpenAI list prices per 1M tokens (input, output). Cached input ≈ 10% of input.
_RATES = {"gpt-5.5": (5, 30), "gpt-5.6-sol": (5, 30),
          "gpt-5.6-terra": (2.5, 15), "gpt-5.6-luna": (1, 6)}
_GEN = {"in": 0, "cached": 0, "out": 0}      # generation (+ design plan) usage
_JUDGE = {"in": 0, "cached": 0, "out": 0}    # QA vision-judge usage


def _cached_of(u):
    d = getattr(u, "prompt_tokens_details", None)
    if d is None:
        return 0
    return (getattr(d, "cached_tokens", None) or (d.get("cached_tokens", 0) if isinstance(d, dict) else 0)) or 0


def _tally(bucket, u):
    bucket["in"] += getattr(u, "prompt_tokens", 0) or 0
    bucket["cached"] += _cached_of(u)
    bucket["out"] += getattr(u, "completion_tokens", 0) or 0


def _real_cost(bucket, rate_in, rate_out):
    cached = bucket["cached"]
    uncached = max(0, bucket["in"] - cached)
    return (uncached * rate_in + cached * rate_in * 0.10 + bucket["out"] * rate_out) / 1e6


class _Usage:
    """Minimal shim so slidegen._price_usage (getattr-based) reads GPT tokens
    without crashing — cache fields are absent and default to 0."""
    def __init__(self, u):
        self.input_tokens = getattr(u, "prompt_tokens", 0) or 0
        self.output_tokens = getattr(u, "completion_tokens", 0) or 0


def _flatten_system(system) -> str:
    if isinstance(system, str):
        return system
    return "\n\n".join(b["text"] for b in system if b.get("text"))


# ---------------------------------------------------------------------------
# GPT outline (emit_outline)
# ---------------------------------------------------------------------------
OUTLINE_TOOL = {
    "type": "function",
    "function": {
        "name": "emit_outline",
        "description": "Emit a presentation outline: a cinematic narrative arc "
                       "with one entry per slide.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
                "slides": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "slide_number": {"type": "integer"},
                            "layout": {"type": "string", "enum": LAYOUTS,
                                       "description": "vary these across the deck"},
                            "bg": {"type": "string", "enum": ["light", "dark"]},
                            "title": {"type": "string"},
                            "subtitle": {"type": "string"},
                            "bullets": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["slide_number", "layout", "bg", "title", "bullets"],
                    },
                },
            },
            "required": ["title", "subtitle", "slides"],
        },
    },
}


async def gpt_outline(topic: str, n: int) -> dict:
    sys_msg = (
        "You are a world-class presentation strategist. Design a premium, "
        "cinematic slide-by-slide outline. Open with a title_only cover, close "
        "with a closing slide, and VARY the layout of every middle slide "
        f"(use a spread across {', '.join(LAYOUTS)}). Keep bullets punchy "
        "(<=14 words). Return via emit_outline."
    )
    user = f"Topic: {topic}\nSlide count: {n}\nStyle: premium, cinematic, editorial."
    resp = await _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": sys_msg},
                  {"role": "user", "content": user}],
        tools=[OUTLINE_TOOL],
        tool_choice={"type": "function", "function": {"name": "emit_outline"}},
        max_completion_tokens=16000,
        reasoning_effort="none",  # required: gpt-5.6-* reject function tools + reasoning in chat/completions
    )
    outline = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
    # normalize
    for i, s in enumerate(outline.get("slides", []), start=1):
        s.setdefault("slide_number", i)
        if s.get("layout") not in LAYOUTS:
            s["layout"] = "bullets"
    return outline


# ---------------------------------------------------------------------------
# GPT slide generator — drop-in for slidegen._generate_one (same signature)
# ---------------------------------------------------------------------------
_SLIDE_FN_TOOL = {
    "type": "function",
    "function": {
        "name": SLIDE_TOOL["name"],
        "description": SLIDE_TOOL["description"],
        "parameters": SLIDE_TOOL["input_schema"],
    },
}


async def gpt_generate_one(client, model, system, outline, slide_entry, slide_number,
                           usage_acc, archetype, neighbors, plan_text=None, think=True,
                           qa_feedback=None, retry_log=None, phase="generate",
                           layout_in_prefix=False):
    system_text = _flatten_system(system)
    last_err = None
    feedback = ""
    for attempt in range(3):
        try:
            content = _slide_user_message(outline, slide_entry, slide_number,
                                          archetype, neighbors, plan_text,
                                          layout_in_prefix=layout_in_prefix)
            if feedback:
                content += f"\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED: {feedback}"
            resp = await _client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": system_text},
                          {"role": "user", "content": content}],
                tools=[_SLIDE_FN_TOOL],
                tool_choice={"type": "function", "function": {"name": "emit_slide"}},
                max_completion_tokens=16000,
                reasoning_effort="none",  # required for gpt-5.6-* function tools in chat/completions
            )
            usage_acc.append(_Usage(resp.usage))
            _tally(_GEN, resp.usage)
            msg = resp.choices[0].message
            if not msg.tool_calls:
                raise ValueError("GPT returned no emit_slide call")
            spec = json.loads(msg.tool_calls[0].function.arguments)
            # fail-fast validation (same probe slidegen uses)
            expand_slide_spec(spec, deck_title="probe", slide_number=slide_number,
                              deck_id="probe", timestamp=0)
            n_el = len(spec.get("elements", []))
            if n_el < 6 and attempt < 2:
                feedback = (f"only {n_el} elements — layer it richer (kicker chip, "
                            f"accent rules, panels, icon badges, dividers, page caption).")
                print(f"  [gpt slide-{slide_number}] attempt {attempt+1} thin "
                      f"({n_el} el) — regenerating")
                continue
            print(f"  [gpt slide-{slide_number}] {n_el} elements ✓")
            return spec
        except Exception as e:
            last_err = e
            print(f"  [gpt slide-{slide_number}] attempt {attempt+1} failed: {e}")
    raise RuntimeError(f"slide {slide_number} failed after retries: {last_err}")


# ---------------------------------------------------------------------------
# GPT-vision QA judge — drop-in for core.visual_qa._judge_one (same signature)
# ---------------------------------------------------------------------------
QA_MODEL = os.environ.get("QA_OPENAI_MODEL", "gpt-5.6-luna")  # cheap+fast vision judge


async def gpt_judge_one(client, model, png_path, slide_number, total,
                        outline_entry, plan_text, usage_acc):
    from core.visual_qa import _JUDGE_SYSTEM, REVIEW_TOOL, PASS_SCORE
    b64 = base64.standard_b64encode(Path(png_path).read_bytes()).decode()
    context = f"Slide {slide_number} of {total}.\n"
    if outline_entry:
        context += f"\nINTENDED CONTENT (outline entry):\n{json.dumps(outline_entry, indent=2)}\n"
    if plan_text:
        context += f"\nART DIRECTOR PLAN:\n{plan_text}\n"
    context += "\nReview the screenshot and call emit_review."
    tool = {"type": "function", "function": {
        "name": REVIEW_TOOL["name"],
        "description": REVIEW_TOOL["description"],
        "parameters": REVIEW_TOOL["input_schema"],
    }}
    kwargs = {}
    if QA_MODEL.startswith("gpt-5.6"):
        kwargs["reasoning_effort"] = "none"  # 5.6 rejects function tools + reasoning
    resp = await _client.chat.completions.create(
        model=QA_MODEL,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user", "content": [
                {"type": "text", "text": context},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ]},
        ],
        tools=[tool],
        tool_choice={"type": "function", "function": {"name": "emit_review"}},
        max_completion_tokens=2000,
        **kwargs,
    )
    usage_acc.append(_Usage(resp.usage))
    _tally(_JUDGE, resp.usage)
    review = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
    has_high = any(p.get("severity") == "high" for p in review.get("problems", []))
    review["slide_number"] = slide_number
    review["pass"] = review["score"] >= PASS_SCORE and not has_high
    return review


# ---------------------------------------------------------------------------
# GPT art-director design plan — drop-in for core.slidegen._design_plan
# (director mode). Leans on the full visual-design guide already in `system`.
# ---------------------------------------------------------------------------
async def gpt_design_plan(client, model, system, outline, archetypes, usage_acc,
                          palette_auto=False, font_auto=False, on_entry=None):
    system_text = _flatten_system(system)
    listing = "\n".join(
        f'  slide {i}: [{s.get("layout","bullets")}] archetype "{a[0]}" — {s.get("title","")}'
        for i, (s, a) in enumerate(zip(outline.get("slides", []), archetypes), start=1)
    )
    auto = ""
    if palette_auto:
        auto += ("PALETTE IS AUTO: choose the ONE palette from the 14 in the visual "
                 "design guide whose MOOD fits this topic; name it + its exact hexes in "
                 "deck_notes; every slide uses only it.\n")
    if font_auto:
        auto += ("FONT IS AUTO: pick the heading/body pairing from the Typography "
                 "Pairings table that matches this topic; name both in deck_notes.\n")
    msg = (
        "You are the ART DIRECTOR for this deck. Use the visual-design guide, "
        "richness rules and motif/background system already in your system prompt. "
        "Design the whole deck as ONE coherent system, then call emit_design_plan once.\n\n"
        f"SLIDES AND ASSIGNED ARCHETYPES:\n{listing}\n\n"
        f"{auto}\n"
        "Decide the background system deck-wide (state it in deck_notes as "
        '"Background system: ..."). For EACH slide write a precise, executable '
        "60-140 word plan: composition skeleton with rough geometry, the oversized "
        "typographic anchor (what + size range), background + accent hexes from the "
        "chosen palette, image subject + overlay/filter treatment (or 'no image'), "
        "and the one distinctive touch vs its neighbours. Plan enough layered "
        "elements to land 18-30 per slide (hard floor 14): enumerate decorative "
        "layers (kicker chips, accent rules, corner ticks, offset panels, icon "
        "badges, stat ribbons, dividers). Keep ALL text inside the 48px safe zone "
        "(x 48-1232, y 48-672). Premium reads as RESTRAINT: whitespace, disciplined "
        "alignment, high contrast, one sharp accent used sparingly."
    )
    tool = {"type": "function", "function": {
        "name": DESIGN_PLAN_TOOL["name"],
        "description": DESIGN_PLAN_TOOL["description"],
        "parameters": DESIGN_PLAN_TOOL["input_schema"],
    }}
    kwargs = {}
    if OPENAI_MODEL.startswith("gpt-5.6"):
        kwargs["reasoning_effort"] = "none"
    resp = await _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": system_text},
                  {"role": "user", "content": msg}],
        tools=[tool],
        tool_choice={"type": "function", "function": {"name": "emit_design_plan"}},
        max_completion_tokens=16000,
        **kwargs,
    )
    usage_acc.append(_Usage(resp.usage))
    _tally(_GEN, resp.usage)
    plan = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
    notes = plan.get("deck_notes", "")
    if notes:
        print(f"  [gpt art-director] {notes[:160]}")
    plans = {int(e["slide_number"]): e["plan"]
             for e in plan.get("slides", []) if "plan" in e}
    # executors are launched by generate_deck_per_slide's catch-all after we return
    print(f"  [gpt art-director] planned {len(plans)}/{len(outline.get('slides', []))} slides")
    return plans


# ---------------------------------------------------------------------------
# GPT layout selection — drop-in for core.layouts.select_layouts.
# Picks one library layout per slide; the pipeline then inlines ONLY those
# specs into the CACHED system prefix (layout_in_prefix=True), so per-slide
# messages shrink and the specs are billed once at cache-write, not per call.
# ---------------------------------------------------------------------------
async def gpt_select_layouts(outline, lib, *, core_rules="", model=None,
                             usage_acc=None):
    slides = outline.get("slides", [])
    if not slides:
        return {}, "fallback"
    system = ("You are the ART DIRECTOR picking the composition layout for each "
              "slide of ONE presentation deck.\n\n"
              "LAYOUT LIBRARY INDEX  (format: id [type]: when to use)\n"
              f"{layout_index_text(lib)}\n")
    if core_rules:
        system += "\n---\n\nCORE DESIGN RULES\n" + core_rules
    listing = "\n".join(
        f"  slide {s.get('slide_number', i)}: [{s.get('layout','bullets')}] "
        f"{s.get('title','')}" for i, s in enumerate(slides, start=1))
    msg = (
        f"DECK: {outline.get('title','')} — {outline.get('subtitle','')}\n\n"
        f"SLIDES ({len(slides)}):\n{listing}\n\n"
        "For EACH slide choose the ONE best layout_id from the index whose "
        "'when to use' fits the slide's content and its [type] hint.\n"
        "RULES:\n"
        "- Prefer a layout whose [type] matches the slide's type hint; choose a "
        "different type only when it clearly fits better.\n"
        "- ADJACENT SLIDES MUST NOT SHARE A LAYOUT, and vary the skeleton across "
        "the deck so nothing repeats back-to-back.\n"
        "- Aim for a varied set (typically 8-15 distinct layouts).\n"
        "- Return exactly one entry per slide, covering every slide number.\n"
        "Emit your choices via the select_layouts tool."
    )
    tool = {"type": "function", "function": {
        "name": SELECT_TOOL["name"],
        "description": SELECT_TOOL["description"],
        "parameters": SELECT_TOOL["input_schema"],
    }}
    kwargs = {}
    if OPENAI_MODEL.startswith("gpt-5.6"):
        kwargs["reasoning_effort"] = "none"
    try:
        resp = await _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": msg}],
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": "select_layouts"}},
            max_completion_tokens=2048,
            **kwargs,
        )
        _tally(_GEN, resp.usage)
        if usage_acc is not None:
            usage_acc.append(_Usage(resp.usage))
        payload = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
        chosen = {}
        for e in payload.get("slides", []):
            n = int(e["slide_number"])
            lid = str(e["layout_id"]).strip()
            if lid not in lib:
                raise ValueError(f"slide {n}: unknown layout_id {lid!r}")
            chosen[n] = lid
        missing = [i for i in range(1, len(slides) + 1) if i not in chosen]
        if missing:
            raise ValueError(f"selection missed slide(s) {missing}")
        print(f"  [gpt layouts] selected {len(set(chosen.values()))} distinct "
              f"layouts across {len(slides)} slides")
        return chosen, "selected"
    except Exception as e:
        print(f"  [gpt layouts] selection failed ({e}); seed=0 fallback")
        return fallback_selection(outline, lib, seed=0), "fallback"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "density": "Standard", "audience": "Executive Leadership",
    "tone": "confident, premium, cinematic", "fontFamily": "auto",
    "fontSize": "Medium", "palette": "auto", "imageSource": "pexels",
    "pageNumbers": True,
}


async def main():
    global OPENAI_MODEL
    ap = argparse.ArgumentParser(description="Generate a deck design with GPT (no Anthropic).")
    ap.add_argument("topic")
    ap.add_argument("--slides", type=int, default=8)
    ap.add_argument("--tone", default=None)
    ap.add_argument("--palette", default=None)
    ap.add_argument("--model", default=OPENAI_MODEL,
                    help=f"generation model (default {OPENAI_MODEL}); e.g. gpt-5.6-luna, gpt-5.5")
    ap.add_argument("--no-qa", dest="qa", action="store_false",
                    help="disable the GPT-vision QA loop (on by default)")
    ap.add_argument("--layout-select", action="store_true",
                    help="GPT picks library layouts + caches specs in the prefix. OFF by default: "
                         "richer layouts crowd reasoning-off models and cost MORE via regen cascade.")
    ap.add_argument("--premium", action="store_true",
                    help="director mode: GPT art-director design plan (cohesive palette/font + "
                         "per-slide creative direction) + QA loop. The full Claude pipeline.")
    ap.set_defaults(qa=True)  # settled recipe: QA loop ON by default
    args = ap.parse_args()
    if args.premium:
        args.qa = True  # premium implies the QA loop
    OPENAI_MODEL = args.model

    config = dict(DEFAULT_CONFIG)
    if args.tone:
        config["tone"] = args.tone
    if args.palette:
        config["palette"] = args.palette

    # Monkeypatch: every slidegen slide call now goes to GPT.
    sg._generate_one = gpt_generate_one
    # GPT layout selection (opt-in) -> layout specs ride in the CACHED system prefix.
    if args.layout_select:
        os.environ["SLIDEGEN_LAYOUT_SELECT"] = "1"
        sg.select_layouts = gpt_select_layouts
        print("[gpt] layout-select ON (library layouts, specs cached in prefix)")

    # Premium/director mode: GPT art-director design plan feeds per-slide creative
    # direction into every slide (cohesive palette/font chosen deck-wide).
    deck_mode = "fast"
    if args.premium:
        deck_mode = "director"
        sg._design_plan = gpt_design_plan
        print("[gpt] PREMIUM (director) mode ON — GPT art-director design plan")

    # Optional: GPT-vision QA loop (screenshot -> judge -> regenerate failures).
    if args.qa:
        os.environ["SLIDEGEN_VISUAL_QA"] = "1"
        import core.visual_qa as vqa
        vqa._judge_one = gpt_judge_one        # judge on GPT vision, not Anthropic
        print(f"[gpt] QA loop ON — judge model: {QA_MODEL}")

    run_id = f"run-gpt-{int(time.time() * 1000)}"
    run_dir = WORKSPACE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[gpt] model: {OPENAI_MODEL}  run dir: {run_dir}")

    print(f"[gpt] writing {args.slides}-slide outline...")
    outline = await gpt_outline(args.topic, args.slides)
    (run_dir / "outline.json").write_text(json.dumps(outline, indent=2), encoding="utf-8")
    print(f"[gpt] outline: {outline.get('title')!r} — "
          f"{[s.get('layout') for s in outline.get('slides', [])]}")

    print(f"[gpt] designing {len(outline['slides'])} slides with GPT...")
    deck, stats = await sg.generate_deck_per_slide(outline, config, run_dir=run_dir,
                                                   mode=deck_mode)
    print(f"[gpt] stats: {json.dumps(stats, indent=2)}")

    merged = run_dir / "merged_deck.json"
    result = subprocess.run([sys.executable, str(VALIDATOR), str(merged)],
                            capture_output=True, text=True)
    print(result.stdout)
    print(f"[gpt] validation: {'PASS' if result.returncode == 0 else 'FAIL'}")

    from core.pptx_exporter import export_slides_to_pptx
    pptx_path = run_dir / "deck.pptx"
    await export_slides_to_pptx(deck, pptx_path)
    print(f"[gpt] pptx: {pptx_path}  ({pptx_path.stat().st_size:,} bytes)")

    preview = subprocess.run([sys.executable, "scripts/render_html_preview.py", str(merged)],
                             capture_output=True, text=True)
    print(preview.stdout.strip())
    print(f"[gpt] preview: {run_dir / 'preview.html'}")

    # Real cache-adjusted cost (cached prefix billed at ~10% of input rate).
    gri, gro = _RATES.get(OPENAI_MODEL, (5, 30))
    qri, qro = _RATES.get(QA_MODEL, (1, 6))
    gen_cost = _real_cost(_GEN, gri, gro)
    judge_cost = _real_cost(_JUDGE, qri, qro)
    print(f"\n[cost] generation ({OPENAI_MODEL}): in {_GEN['in']:,} "
          f"(cached {_GEN['cached']:,}) / out {_GEN['out']:,} -> ${gen_cost:.3f}")
    print(f"[cost] QA judge ({QA_MODEL}):   in {_JUDGE['in']:,} "
          f"(cached {_JUDGE['cached']:,}) / out {_JUDGE['out']:,} -> ${judge_cost:.3f}")
    print(f"[cost] REAL TOTAL: ${gen_cost + judge_cost:.3f}   time: {stats.get('total_seconds')}s")


if __name__ == "__main__":
    asyncio.run(main())
