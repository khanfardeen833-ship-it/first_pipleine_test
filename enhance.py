"""
Prompt enhancer — parallel generation for richer, longer output.

Fires 4 parallel API calls simultaneously:
  Thread 1 — Design system   (Title, Style, Colors, Typography)
  Thread 2 — Production      (Layout, Animation, Visual Requirements)
  Thread 3 — Slides Act I    (first half of slides)
  Thread 4 — Slides Act II + III + Final Instructions + META

Total output: ~4x more detailed than a single call.
All 4 threads run at the same time, so total time ≈ time of one call.

Usage:
    python enhance.py "coffee in Ethiopia"
    python enhance.py "AI market study" --slides 20 --style "data-driven cinematic"
"""

import os
import re
import time
import argparse
import datetime as _dt
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
load_dotenv()

from openai import AzureOpenAI, OpenAI


# ---------------------------------------------------------------------------
# Config — Azure
# ---------------------------------------------------------------------------
AZURE_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "https://admin-mjo8157d-eastus2.cognitiveservices.azure.com/")
AZURE_API_KEY  = os.environ.get("AZURE_OPENAI_API_KEY", "")
AZURE_MODEL    = os.environ.get("AZURE_OPENAI_MODEL", "gpt-4o")
AZURE_API_VER  = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")

# ---------------------------------------------------------------------------
# Config — Direct OpenAI
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL   = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Shared clients — created once, reused across all threads (thread-safe)
_openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
_azure_client  = AzureOpenAI(
    api_version=AZURE_API_VER,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
) if AZURE_API_KEY else None


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
ENHANCER_SYSTEM = """\
You are an ELITE AI Presentation Prompt Architect.

Your role: transform a short user topic into an ULTRA-CREATIVE, MAGICAL, CINEMATIC,
slide-by-slide presentation-generation prompt that another AI tool will use to render the deck.

Use the following as your style reference and quality standard:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STYLE REFERENCE EXAMPLE (UC Berkeley)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Style Direction: Magical Academic Wonderland + Playful Ivy League Adventure + Dreamy Campus Storytelling

Create an extremely beautiful, magical, playful presentation about University of California, Berkeley.

The presentation should feel like:
  a Pixar university movie, a dreamy academic fantasy, a magical student adventure,
  a cinematic campus exploration, mixed with playful storytelling and elite academic elegance.

The presentation must feel: inspiring, youthful, intelligent, artistic, adventurous, warm, emotional, visually magical.

This should NOT look like: a boring university presentation, a corporate academic slideshow, a traditional school deck.

It should feel like: entering a magical world of innovation, dreams, creativity, and student life.

Core Artistic Direction:
  Blend together: magical campus aesthetics, playful university storytelling, dreamy California atmosphere,
  animated student life, fantasy-inspired lighting, academic prestige, creative youthful energy.

Color Palette: Berkeley blue, golden yellow, sunset orange, warm cream, magical sky blue, soft glowing white, deep night blue.
  Add: glowing stars, golden sunlight, magical particles, dreamy gradients.

Typography: playful, elegant, youthful, inspiring.
  Use: cinematic serif titles, handwritten notebook-style notes, glowing magical text, oversized inspirational typography.

Layout System: magical scrapbook layouts, floating campus cards, notebook doodles, cinematic photography,
  animated clouds, paper textures, dreamy compositions, whimsical transitions.

Animation Style: soft, magical, cinematic, playful.
  Use: floating particles, glowing light trails, animated notebook sketches, flying paper airplanes,
  dreamy zoom transitions, moving clouds, golden sunlight movement, sparkling stars, magical campus glow.

Visual Requirements: cinematic campus visuals, magical sunsets, students studying, iconic buildings,
  libraries, innovation labs, notebook doodles, animated sketches, floating books, playful academic illustrations.

Slide-by-Slide Structure:
  Each slide has a unique design mood, composition, effects, and emotional atmosphere.
  Every slide should feel alive, immersive, and adventurous.

Final Quality: worthy of a Pixar university movie, Apple education keynote, magical campus documentary,
  premium university campaign, cinematic student experience showcase.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply the SAME level of magical, cinematic, ultra-creative quality to ANY topic the user gives you.

Adapt the style to the topic's domain:

  TECHNICAL (AI, cloud, cybersecurity, finance-tech):
    → architecture diagrams, dashboards, futuristic blueprint aesthetics, glowing neural networks,
      animated data flows, cinematic tech storytelling.

  CREATIVE / TRAVEL / LIFESTYLE / FOOD / CULTURE:
    → cinematic documentary pacing, emotional atmosphere, editorial luxury layouts,
      immersive photography, playful compositions, magical cultural storytelling.

  CORPORATE / FINANCE / INVESTOR:
    → investor-grade dashboards, KPI cards, elegant market charts, ecosystem diagrams,
      McKinsey/Bloomberg aesthetic with cinematic polish.

  EDUCATION / SCIENCE / MEDICAL:
    → magical diagrammatic teaching, floating equations, scientific illustrations,
      wonder-filled discovery atmosphere, cinematic educational storytelling.

  BRAND / PRODUCT:
    → respect the brand's actual color identity and cultural ecosystem,
      expand into its emotional world with cinematic energy.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUALITY BAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every prompt must feel worthy of:
  • Pixar-quality storytelling
  • Apple keynote events
  • Netflix documentary visuals
  • Behance featured projects
  • Luxury brand campaigns
  • Investor pitch competitions

NEVER produce: generic PowerPoint instructions, bullet-list-only slides,
  vague mood words, default chart aesthetics, clip-art references.

ALWAYS include for EVERY slide:
  • visual mood
  • layout composition
  • image / illustration / diagram style
  • typography placement
  • color usage
  • effects and animations
  • cinematic atmosphere
"""


# ---------------------------------------------------------------------------
# Few-shot example
# ---------------------------------------------------------------------------
FEW_SHOT_USER = """\
Topic: coffee in Ethiopia
Slide count: 12
Style: cinematic documentary, editorial magazine
"""

FEW_SHOT_ASSISTANT = """\
## Presentation Title
**"Origin — A Cinematic Journey Through Ethiopian Coffee"**
Subtitle: *From the misty highlands of Yirgacheffe to the cup in your hand.*

## Style Direction
National Geographic documentary × Kinfolk magazine editorial × Aesop brand minimalism. Warm, earthy, sun-drenched. Every slide should feel like a still frame pulled from a 4K travel documentary, with the slow pacing of a long-form essay.

## Core Artistic Direction
- Full-bleed cinematic photography as the visual foundation
- Editorial typography overlays with generous whitespace
- Soft film-grain texture on every image (subtle, 8% opacity)
- Hand-drawn cartographic accents for origin maps
- Earthy paper-texture backgrounds on text slides

## Color Palette
- **Roasted Earth** `#3D2817` (primary dark)
- **Highland Mist** `#F4EDE4` (warm off-white)
- **Yirgacheffe Green** `#5C7548` (accent)
- **Sun-Dried Cherry** `#A0392E` (highlight)
- **Golden Hour** `#D4A574` (gradient stop)
- **Hero Gradient:** `linear-gradient(180deg, #D4A574 0%, #A0392E 100%)`

## Typography
- **Display:** Canela Deck — 96pt, italic for poetic moments
- **Headline:** GT Sectra — 56pt, weight 500
- **Body:** Söhne — 18pt, line-height 1.7
- **Captions:** Söhne Mono — 13pt, all-caps tracking 0.15em

## Layout System
- 8-column editorial grid with asymmetric image bleeds
- Full-bleed hero slides alternated with magazine-style text spreads
- 120px outer margins on text-heavy slides
- Captions placed in the lower-left margin, magazine-style

## Animation Style
- Slow Ken Burns push on photography (8s drift)
- Text fades in with subtle vertical lift (200ms, ease-out)
- Maps draw in with hand-drawn pen animation
- Transitions: cross-dissolve, 800ms

## Visual Requirements
- Cinematic photography of Ethiopian highlands, coffee cherries, farmers' hands
- Hand-drawn map of the coffee belt
- Timeline of the coffee ceremony
- Comparative flavor wheel diagram
- Macro shots of beans at each roast stage

## Slide-by-Slide Structure

### ACT I — THE ORIGIN

**Slide 1 — Cover**
Full-bleed photograph of dawn fog rolling over Yirgacheffe hills. Title in Canela Deck, lower-left.

**Slide 2 — The Birthplace of Coffee**
Editorial spread: large photo of an Ethiopian farmer holding cherries, three short paragraphs of poetic prose right.

**Slide 3 — The Coffee Belt Map**
Hand-drawn cartographic map of Ethiopia's six main coffee regions. Each region annotated with a single flavor descriptor.

**Slide 4 — Yirgacheffe**
Full-bleed macro of ripe red cherries. Single sentence overlay: *"Where coffee tastes like jasmine and bergamot."*

### ACT II — THE CRAFT

**Slide 5 — From Cherry to Bean**
Four-step process diagram: Harvest → Wash → Dry → Hull. Each step illustrated with a photograph.

**Slide 6 — The Coffee Ceremony**
Editorial photograph of the bunna ceremony. Body text on the right describing its cultural significance.

**Slide 7 — Roast Profiles**
Five macro shots of beans at light, medium-light, medium, medium-dark, dark roasts. Below each, a Söhne Mono caption with temperature and time.

**Slide 8 — The Flavor Wheel**
Custom circular flavor diagram with Ethiopian-coffee-specific notes: floral, citrus, berry, wine, chocolate.

### ACT III — THE CUP

**Slide 9 — Brewing Methods**
Three side-by-side photographs: pour-over, French press, traditional jebena. Captions describe ideal use case for each.

**Slide 10 — Tasting Notes**
Editorial quote-slide. Large italic text: *"On the palate: jasmine, lemon zest, a finish like dark honey."*

**Slide 11 — The People Behind the Cup**
Portrait photography grid of farmers. Names, regions, and one-line quotes underneath.

**Slide 12 — Closing**
Full-bleed sunset over a coffee field. Centered text: *"Every cup is a story. Drink slowly."*

## Final AI Instructions
Prioritize cinematic photography over information density. Use whitespace as a design element. Every image should feel sun-warmed and tactile. Avoid: generic stock photos, plain bullet lists, harsh shadows, oversaturated colors.

<!--META
slide_count: 12
audience: coffee enthusiasts, hospitality professionals, culture lovers
tone: cinematic-editorial, warm, poetic
key_sections: Origin, Craft, Cup
-->
"""


# ---------------------------------------------------------------------------
# Low-level API callers — shared clients, 4000 tokens each
# ---------------------------------------------------------------------------
def _raw_openai(messages: list) -> str:
    response = _openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_completion_tokens=1100,
    )
    return response.choices[0].message.content.strip()


def _raw_azure(messages: list) -> str:
    response = _azure_client.chat.completions.create(
        model=AZURE_MODEL,
        messages=messages,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def _staggered(fn, delay: float):
    """Wrap a zero-arg callable with a stagger delay to spread burst requests."""
    def wrapper():
        time.sleep(delay)
        return fn()
    return wrapper


def _messages(user_prompt: str) -> list:
    return [
        {"role": "system",    "content": ENHANCER_SYSTEM},
        {"role": "user",      "content": FEW_SHOT_USER},
        {"role": "assistant", "content": FEW_SHOT_ASSISTANT},
        {"role": "user",      "content": user_prompt},
    ]


# ---------------------------------------------------------------------------
# 8 section generators — compact bullet format for token efficiency
# ---------------------------------------------------------------------------
def _gen_title_style(topic: str, slides: int, style: str, raw_fn) -> str:
    return raw_fn(_messages(f"""\
Topic: {topic} | Slides: {slides} | Style: {style}

Output ONLY these 3 sections. Use tight bullet lists, not paragraphs. No preamble.

## Presentation Title
Bold title + italic subtitle (2 lines max)

## Style Direction
3-5 bullet points describing the cinematic/editorial feel. What it should feel like, what to avoid.

## Core Artistic Direction
6-8 tight bullets: photography style, typography approach, texture/effects, layout mood, color philosophy, animation energy.
"""))


def _gen_colors_type(topic: str, slides: int, style: str, raw_fn) -> str:
    return raw_fn(_messages(f"""\
Topic: {topic} | Slides: {slides} | Style: {style}

Output ONLY these 2 sections. Compact format. No preamble.

## Color Palette
8-10 named colors with hex codes. One line each: **Name** `#HEX` — usage note.

## Typography
5 font roles. Each line: **Role: Font Name** — size range, weight, usage context.
Include a short Hierarchy table (Hero / Section / Body / Caption sizes).
"""))


def _gen_layout_anim_visuals(topic: str, slides: int, style: str, raw_fn) -> str:
    return raw_fn(_messages(f"""\
Topic: {topic} | Slides: {slides} | Style: {style}

Output ONLY these 3 sections. Tight bullets. No preamble.

## Layout System
5-6 bullets: grid system, bleed rules, margin sizes, composition types used.

## Animation Style
5-6 bullets: transition type, entrance effects, speed/easing, specific motion ideas.

## Visual Requirements
5-6 bullets: photography style, illustration type, diagram aesthetic, texture/overlay notes.
"""))


def _gen_slides_chunk(topic: str, slides: int, style: str, raw_fn,
                      start: int, end: int, act_label: str) -> str:
    return raw_fn(_messages(f"""\
Topic: {topic} | Total slides: {slides} | Style: {style}

Output ONLY {act_label} — slides {start} to {end}. No preamble. No other sections.

### {act_label}

For each slide use this compact format:
**Slide N — [Evocative Title]**
- Mood: ...
- Layout: ...
- Visual: ...
- FX: ...
- Color: ...
- Type: ...
"""))


def _gen_final(topic: str, slides: int, style: str, raw_fn) -> str:
    return raw_fn(_messages(f"""\
Topic: {topic} | Slides: {slides} | Style: {style}

Output in pure markdown (no preamble):

## Final AI Instructions
8-10 tight bullets: what to avoid, what to achieve, quality bar for the renderer.

<!--META
slide_count: {slides}
audience: <who this is for>
tone: <cinematic-corporate / magical-editorial / investor-grade / etc>
key_sections: <comma-separated act names>
-->
"""))


# ---------------------------------------------------------------------------
# Parse / strip META block
# ---------------------------------------------------------------------------
def parse_meta(text: str) -> dict:
    meta = {}
    m = re.search(r"<!--META\s*(.*?)-->", text, re.DOTALL)
    if not m:
        return meta
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta


def strip_meta(text: str) -> str:
    return re.sub(r"<!--META.*?-->", "", text, flags=re.DOTALL).strip()


# ---------------------------------------------------------------------------
# Main enhance function — 8 parallel threads
# ---------------------------------------------------------------------------
def enhance(user_topic: str, slides: int = 15, style: str = "cinematic premium, editorial polish") -> str:
    if AZURE_API_KEY:
        provider, model, raw_fn = "Azure OpenAI", AZURE_MODEL, _raw_azure
    elif OPENAI_API_KEY:
        provider, model, raw_fn = "OpenAI", OPENAI_MODEL, _raw_openai
    else:
        raise RuntimeError("No API key found. Set AZURE_OPENAI_API_KEY or OPENAI_API_KEY in .env.")

    # Divide slides into 4 chunks across 4 threads
    c1_end = slides // 4
    c2_end = slides // 2
    c3_end = (slides * 3) // 4
    c4_end = slides

    print(f"[enhance] provider: {provider} | model: {model}")
    print(f"[enhance] topic: {user_topic} | slides: {slides} | style: {style}")
    print(f"[enhance] launching 8 parallel threads (1100 tokens each)...")

    # Stagger requests by 0.5s each — gentle ramp-up reduces throttling.
    sections = {
        "title_style":        _staggered(lambda: _gen_title_style(user_topic, slides, style, raw_fn),         0.0),
        "colors_type":        _staggered(lambda: _gen_colors_type(user_topic, slides, style, raw_fn),         0.5),
        "layout_anim_visuals":_staggered(lambda: _gen_layout_anim_visuals(user_topic, slides, style, raw_fn), 1.0),
        "slides_c1":          _staggered(lambda: _gen_slides_chunk(user_topic, slides, style, raw_fn, 1,        c1_end, "ACT I"),   1.5),
        "slides_c2":          _staggered(lambda: _gen_slides_chunk(user_topic, slides, style, raw_fn, c1_end+1, c2_end, "ACT II"),  2.0),
        "slides_c3":          _staggered(lambda: _gen_slides_chunk(user_topic, slides, style, raw_fn, c2_end+1, c3_end, "ACT III"), 2.5),
        "slides_c4":          _staggered(lambda: _gen_slides_chunk(user_topic, slides, style, raw_fn, c3_end+1, c4_end, "ACT IV"),  3.0),
        "final":              _staggered(lambda: _gen_final(user_topic, slides, style, raw_fn),                3.5),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(fn): name for name, fn in sections.items()}
        for future in as_completed(future_map):
            name = future_map[future]
            results[name] = future.result()
            print(f"[enhance]   + {name} done")

    # Merge in correct section order
    merged = "\n\n".join([
        results["title_style"],
        results["colors_type"],
        results["layout_anim_visuals"],
        "## Slide-by-Slide Structure\n\n"
            + results["slides_c1"] + "\n\n"
            + results["slides_c2"] + "\n\n"
            + results["slides_c3"] + "\n\n"
            + results["slides_c4"],
        results["final"],
    ])

    meta = parse_meta(merged)
    enhanced = strip_meta(merged)

    # Save to history
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(__file__).parent / "enhance-history" / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "original.txt").write_text(user_topic, encoding="utf-8")
    (run_dir / "enhanced.md").write_text(enhanced, encoding="utf-8")
    (run_dir / "meta.txt").write_text("\n".join([
        f"provider    : {provider}",
        f"model       : {model}",
        f"slide_count : {meta.get('slide_count', slides)}",
        f"audience    : {meta.get('audience', 'n/a')}",
        f"tone        : {meta.get('tone', 'n/a')}",
        f"key_sections: {meta.get('key_sections', 'n/a')}",
    ]), encoding="utf-8")
    print(f"[enhance] saved -> {run_dir}/")
    print(f"[enhance] done. enhanced prompt ({len(enhanced)} chars)")
    return enhanced


def main():
    parser = argparse.ArgumentParser(description="Parallel cinematic presentation prompt enhancer")
    parser.add_argument("topic", nargs="+", help="The topic to enhance")
    parser.add_argument("--slides", type=int, default=15, help="Suggested slide count")
    parser.add_argument("--style", type=str, default="cinematic premium, editorial polish",
                        help="Style direction")
    args = parser.parse_args()

    topic = " ".join(args.topic)
    enhanced = enhance(topic, slides=args.slides, style=args.style)

    print("\n--- enhanced prompt ---\n")
    print(enhanced)


if __name__ == "__main__":
    main()
