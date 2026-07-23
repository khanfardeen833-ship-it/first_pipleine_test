"""
Batch API proof-of-concept — measures whether routing the slide EXECUTORS
through Anthropic's Batch API is viable, using a real deck's saved outline+plan.

Answers the three questions that decide it:
  1. LATENCY  — submit->done wall-clock (the only real unknown; no tight SLA)
  2. COST     — batch bills at 50%; we sum usage and show standard vs batch
  3. QUALITY  — every returned emit_slide spec must expand cleanly (identical
                model+prompt => identical quality by construction)

Does NOT touch the production pipeline. Reconstructs the executor requests with
the same public helpers slidegen uses. Run:
    python scripts/_batch_poc.py workspace/run-topic-<id>
"""
import sys, os, json, time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

import core.slidegen as sg
from core.slidegen import (SLIDE_TOOL, DESIGN_PLAN_TOOL, MAX_TOKENS_PER_SLIDE,
                           build_slidegen_system, assign_archetypes,
                           _slide_user_message, expand_slide_spec)


def main(run_dir: str):
    run = Path(run_dir)
    outline = json.load(open(run / "outline.json", encoding="utf-8"))
    plans_raw = json.load(open(run / "design_plan.json", encoding="utf-8"))
    plans = {int(k): v for k, v in plans_raw.items()}  # keys may be str
    slides = outline.get("slides", [])
    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

    # Rebuild the executor prompts exactly as slidegen does (no layout-select
    # path => selected_layouts=None; archetypes via the same assigner).
    system = build_slidegen_system(outline, {}, None)
    archetypes = assign_archetypes(slides, seed=0)

    def neighbors_of(i):  # same shape slidegen builds: "slide N: <arch>"
        out = []
        if i > 1:
            out.append(f"slide {i-1}: {archetypes[i-2][0]}")
        if i < len(slides):
            out.append(f"slide {i+1}: {archetypes[i][0]}")
        return "; ".join(out) or "none"

    requests = []
    for i, entry in enumerate(slides, start=1):
        content = _slide_user_message(outline, entry, i, archetypes[i-1],
                                      neighbors_of(i), plans.get(i),
                                      layout_in_prefix=False)
        requests.append(Request(
            custom_id=f"slide-{i}",
            params=MessageCreateParamsNonStreaming(
                model=model, max_tokens=MAX_TOKENS_PER_SLIDE, system=system,
                tools=[SLIDE_TOOL, DESIGN_PLAN_TOOL],
                tool_choice={"type": "tool", "name": "emit_slide"},
                messages=[{"role": "user", "content": content}],
            ),
        ))

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    print(f"[batch-poc] submitting {len(requests)} executor slides "
          f"(model={model})...")
    t0 = time.time()
    batch = client.messages.batches.create(requests=requests)
    print(f"[batch-poc] batch id={batch.id}  status={batch.processing_status}")

    # 2. Poll until done — this wall-clock is the answer to the latency question
    while True:
        b = client.messages.batches.retrieve(batch.id)
        el = time.time() - t0
        if b.processing_status == "ended":
            print(f"[batch-poc] ENDED after {el:.0f}s "
                  f"({el/60:.1f} min)  counts={b.request_counts}")
            break
        print(f"[batch-poc] ...{el:.0f}s status={b.processing_status} "
              f"processing={b.request_counts.processing}")
        time.sleep(15)

    latency = time.time() - t0

    # 3. Collect results, sum usage, validate every spec
    agg = {"input": 0, "output": 0, "cw": 0, "cr": 0}
    ok = bad = 0
    for r in client.messages.batches.results(batch.id):
        if r.result.type != "succeeded":
            bad += 1
            print(f"  {r.custom_id}: {r.result.type}")
            continue
        u = r.result.message.usage
        agg["input"] += u.input_tokens or 0
        agg["output"] += u.output_tokens or 0
        agg["cw"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        agg["cr"] += getattr(u, "cache_read_input_tokens", 0) or 0
        spec = next((c.input for c in r.result.message.content
                     if c.type == "tool_use"), None)
        try:
            expand_slide_spec(spec, deck_title="poc", slide_number=1,
                              deck_id="poc", timestamp=0)
            ok += 1
        except Exception as e:
            bad += 1
            print(f"  {r.custom_id}: spec invalid — {e}")

    std = sg._price_flat(model, input_tokens=agg["input"],
                         output_tokens=agg["output"],
                         cache_write=agg["cw"], cache_read=agg["cr"]) or 0.0
    batch_cost = round(std * 0.5, 4)  # Batch API = 50% of standard

    print("\n===================== BATCH POC RESULT =====================")
    print(f"  slides submitted : {len(requests)}")
    print(f"  valid specs back : {ok}   (failed: {bad})")
    print(f"  LATENCY          : {latency:.0f}s  ({latency/60:.1f} min)")
    print(f"  tokens           : in={agg['input']:,} out={agg['output']:,} "
          f"cache_w={agg['cw']:,} cache_r={agg['cr']:,}")
    print(f"  cost @ standard  : ${std:.4f}")
    print(f"  cost @ batch(50%): ${batch_cost:.4f}   "
          f"(saves ${std-batch_cost:.4f} on this stage)")
    print("============================================================")
    print("  Quality note: batch uses the SAME model + prompts, so specs are")
    print("  identical to real-time. The only real trade is the latency above.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1
         else "workspace/run-topic-1784712166468")
