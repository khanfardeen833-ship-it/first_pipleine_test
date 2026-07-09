# Skill 09 — zIndex Rules

## What this is
zIndex controls the stacking order of elements. In Bildory, zIndex must be
**globally unique across the entire deck** — not just per slide.
Duplicates cause a validation failure.

## The rule

Every element in the deck gets its own unique integer zIndex.
Elements on slide 5 have higher zIndex values than elements on slide 1
(because IDs are assigned sequentially as you build the deck).

```
slide-1: text-1 (z=1), text-2 (z=2), shape-3 (z=3)
slide-2: text-4 (z=4), image-5 (z=5)
slide-3: shape-6 (z=6), text-7 (z=7)
...
```

## Counter pattern — use this in every build script

```python
ZIDX = 0

def nextz():
    global ZIDX
    ZIDX += 1
    return ZIDX
```

Then every time you create an element:
```python
c, cl = make_text("text-1", "slide-1", "Title", "title",
                   x=48, y=48, w=800, h=80, zidx=nextz(), now=NOW)
```

Never hardcode zIndex values. Never reuse a zIndex. Always call `nextz()`.

## Element ID numbering convention

IDs and zIndex should match — element `text-7` should have `zIndex: 7`.
This makes the deck easy to debug. Use the same counter for both:

```python
COUNTER = 0

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# Usage:
n = next_id()
text_id = f"text-{n}"
zidx = n   # same number for both ID and zIndex
```

## Stacking order within a slide

Lower zIndex = behind. Higher zIndex = in front.

Typical layer order for a slide:
1. Background shape or image (lowest z)
2. Accent shapes / decorative elements
3. Images
4. Icons
5. Charts / Tables
6. Text (highest z — always readable on top)

## Rules & gotchas

- zIndex lives in the **changelog** record, not the content record (except tables — see `07-table-element.md`)
- The validator checks `changelog.slides` for all zIndex values across all slides
- Starting counter at 1 (not 0) is conventional — `zIndex: 0` is valid but reserved-looking
- If you're adding elements to an existing deck, start your counter above the highest existing zIndex
