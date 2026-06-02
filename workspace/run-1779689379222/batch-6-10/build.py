import json
import time

NOW = int(time.time() * 1000)

# ============================================================
# COUNTERS
# ============================================================
COUNTER = 300  # element ID counter starts at 300, first element = 301

def next_id():
    global COUNTER
    COUNTER += 1
    return COUNTER

# ============================================================
# PALETTE
# ============================================================
OBSIDIAN = "#0B1020"
NAVY = "#111A33"
AZURE = "#2F80FF"
CYAN = "#21D4FD"
VIOLET = "#8B5CF6"
GREEN = "#22C55E"
AMBER = "#F59E0B"
MINT = "#7DD3FC"
SILVER = "#D8DEE9"
WHITE = "#F8FAFC"
DARK_PANEL = "#0A0F1F"
GLASS = "#1A2240"

# ============================================================
# HELPERS
# ============================================================
def make_text(text_id, slide_id, text, type_, x, y, w, h, zidx, now,
              color="#1c1917", font_size=None, font_weight=None, line_height=None,
              text_align="left", letter_spacing=0, font_family="Space Grotesk"):
    DEFAULTS = {
        "title":      (60, 700, 1.05),
        "subtitle":   (40, 600, 1.35),
        "heading":    (32, 600, 1.30),
        "subheading": (26, 600, 1.30),
        "paragraph":  (22, 700, 1.50),
        "caption":    (18, 600, 1.30),
    }
    fs, fw, lh = DEFAULTS[type_]
    if font_size is not None:   fs = font_size
    if font_weight is not None: fw = font_weight
    if line_height is not None: lh = line_height

    content_record = {
        "id": text_id, "content": text, "type": type_,
        "originalType": type_, "groupId": None, "formattedContent": text
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0, "zIndex": zidx,
        "style": {
            "fontSize": fs, "fontFamily": font_family, "color": color,
            "textAlign": text_align, "lineHeight": lh, "letterSpacing": letter_spacing,
            "fontWeight": fw, "fontStyle": "normal", "textDecoration": "none",
            "textTransform": "none", "isCode": False, "listStyle": "none",
            "link": "", "backgroundColor": "transparent", "background": "none",
            "WebkitBackgroundClip": "unset", "WebkitTextFillColor": "unset",
            "backgroundClip": "unset", "listLevel": 1,
            "paragraphSpacingBefore": 0, "paragraphSpacingAfter": 0,
            "textOutlineColor": "#000000", "textOutlineWidth": 0,
            "textTransformEffect": "none", "textTransformRadius": 220,
            "textVerticalAlign": "baseline", "curveEnabled": False,
            "curveValue": 26, "shadowType": "none", "shadowOffset": 22,
            "shadowDirection": -45, "shadowBlur": 0,
            "shadowTransparency": 40, "shadowColor": "#000000"
        },
        "formattedContent": text,
        "animation": {"enter": "none", "exit": "fade", "duration": 550,
                      "delay": 0, "trigger": "both", "typewriterMode": "character"},
        "enterAnimation": "none", "exitAnimation": "fade",
        "animationEffect": "none", "animationDurationMs": 550,
        "animationDelayMs": 0, "animationTrigger": "both",
        "animationTypewriterMode": "character", "updatedAt": now
    }
    return content_record, changelog_record


def make_shape(shape_id, slide_id, shape_type, x, y, w, h, zidx, now,
               fill="#c67c3a", stroke=None, stroke_width=0, opacity=1):
    if stroke is None:
        stroke = fill
    content_record = {
        "id": shape_id, "slideId": slide_id, "groupId": None
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "opacity": opacity,
        "shapeType": shape_type,
        "fill": fill, "stroke": stroke, "strokeWidth": stroke_width,
        "updatedAt": now
    }
    return content_record, changelog_record


def make_image(image_id, slide_id, src, x, y, w, h, zidx, now,
               is_background=False, border_radius=0, opacity=1):
    content_record = {
        "id": image_id, "slideId": slide_id, "groupId": None,
        "src": src, "s3Key": None,
        "isBackground": is_background, "_smartDiagram": False
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": w, "height": h, "rotation": 0,
        "zIndex": zidx, "opacity": opacity,
        "borderRadius": border_radius,
        "shadow": {
            "enabled": False, "angle": 135, "color": "#000000",
            "opacity": 40, "distance": 8, "blur": 12, "size": 0, "spread": 0
        },
        "border": {"type": "none", "width": 4, "color": "#000000", "specialStyle": None},
        "cropRatio": "free",
        "cropRect": {"left": 0, "top": 0, "right": 0, "bottom": 0},
        "focusPoint": {"x": 50, "y": 50},
        "updatedAt": now
    }
    return content_record, changelog_record


def make_icon(icon_id, slide_id, icon_name, x, y, zidx, now,
              size=80, color="#c67c3a", opacity=1):
    content_record = {
        "id": icon_id, "slideId": slide_id, "groupId": None,
        "iconName": icon_name, "iconSource": "lucide"
    }
    changelog_record = {
        "slideId": slide_id,
        "position": {"x": x, "y": y},
        "width": size, "height": size, "rotation": 0,
        "zIndex": zidx, "color": color, "opacity": opacity,
        "updatedAt": now
    }
    return content_record, changelog_record


# ============================================================
# REGISTRY
# ============================================================
text_by_slide = {f"slide-{i}": [] for i in range(6, 11)}
shape_elements = []
image_elements = []
icon_elements = []
chart_elements = []
table_elements = []

changelog_slides = {f"slide-{i}": {"elements": {}} for i in range(6, 11)}


def add_text(slide_id, text, type_, x, y, w, h, **kwargs):
    n = next_id()
    tid = f"text-{n}"
    c, cl = make_text(tid, slide_id, text, type_, x, y, w, h, n, NOW, **kwargs)
    text_by_slide[slide_id].append(c)
    changelog_slides[slide_id]["elements"][tid] = cl
    return tid


def add_shape(slide_id, shape_type, x, y, w, h, **kwargs):
    n = next_id()
    sid = f"shape-{n}"
    c, cl = make_shape(sid, slide_id, shape_type, x, y, w, h, n, NOW, **kwargs)
    shape_elements.append(c)
    changelog_slides[slide_id]["elements"][sid] = cl
    return sid


def add_image(slide_id, src, x, y, w, h, **kwargs):
    n = next_id()
    iid = f"image-{n}"
    c, cl = make_image(iid, slide_id, src, x, y, w, h, n, NOW, **kwargs)
    image_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


def add_icon(slide_id, name, x, y, **kwargs):
    n = next_id()
    iid = f"icon-{n}"
    c, cl = make_icon(iid, slide_id, name, x, y, n, NOW, **kwargs)
    icon_elements.append(c)
    changelog_slides[slide_id]["elements"][iid] = cl
    return iid


# ============================================================
# SLIDE 6 — Container Image Hygiene: Build Once, Run Anywhere
# ============================================================
SID = "slide-6"

# Background
add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN, stroke_width=0)
# Subtle blueprint grid accent (left rail)
add_shape(SID, "rectangle", 0, 0, 6, 720, fill=CYAN, stroke_width=0, opacity=0.6)
# Top metadata strip
add_text(SID, "ACT II  //  CONTAINERIZATION  //  06", "caption",
         48, 40, 600, 22, color=MINT, font_size=12, font_family="JetBrains Mono",
         letter_spacing=3)
add_text(SID, "build · ship · run", "caption",
         1080, 40, 160, 22, color=SILVER, font_size=12, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# Hero title
add_text(SID, "Image Hygiene",
         "title", 48, 96, 1180, 80,
         color=WHITE, font_size=72, font_weight=700, line_height=1.05)
add_text(SID, "Build once. Promote everywhere. Trust nothing.",
         "subtitle", 48, 184, 1180, 50,
         color=CYAN, font_size=28, font_weight=400, line_height=1.3,
         font_family="Inter")

# Divider line
add_shape(SID, "rectangle", 48, 252, 80, 2, fill=AMBER, stroke_width=0)

# Body editorial copy (left column)
add_text(SID,
         "Container images are the contract between your code and the cluster. "
         "Keep them small, deterministic, and signed — every byte you ship is a byte you must defend.",
         "paragraph", 48, 280, 520, 110,
         color=SILVER, font_size=20, font_weight=400, line_height=1.55,
         font_family="Inter")

# Four principle cards (left column, stacked) — actually four pills below paragraph
pill_y = 408
pills = [
    ("01", "MULTI-STAGE BUILDS", "strip toolchains from runtime", CYAN),
    ("02", "DISTROLESS BASE", "no shell, no surface area", VIOLET),
    ("03", "SIGNED PROVENANCE", "cosign + SBOM at every push", GREEN),
    ("04", "PINNED DIGESTS", "@sha256, never :latest", AMBER),
]
for i, (num, title, sub, accent) in enumerate(pills):
    py = pill_y + i * 64
    add_shape(SID, "rectangle", 48, py, 520, 52, fill=GLASS, stroke_width=0, opacity=0.7)
    add_shape(SID, "rectangle", 48, py, 3, 52, fill=accent, stroke_width=0)
    add_text(SID, num, "caption", 64, py + 14, 30, 26,
             color=accent, font_size=14, font_family="JetBrains Mono",
             font_weight=600, letter_spacing=1)
    add_text(SID, title, "caption", 108, py + 10, 220, 22,
             color=WHITE, font_size=14, font_family="IBM Plex Sans",
             font_weight=600, letter_spacing=2)
    add_text(SID, sub, "caption", 108, py + 30, 400, 18,
             color=SILVER, font_size=12, font_family="Inter",
             font_weight=400, letter_spacing=0)

# RIGHT: dark-mode terminal code card
code_x, code_y, code_w, code_h = 624, 280, 608, 384
add_shape(SID, "rectangle", code_x, code_y, code_w, code_h,
          fill=DARK_PANEL, stroke_width=0, opacity=1)
# Top bar of terminal
add_shape(SID, "rectangle", code_x, code_y, code_w, 32, fill="#070B17", stroke_width=0)
# Three traffic lights
add_shape(SID, "circle", code_x + 16, code_y + 11, 10, 10, fill="#FF5F56", stroke_width=0)
add_shape(SID, "circle", code_x + 36, code_y + 11, 10, 10, fill="#FFBD2E", stroke_width=0)
add_shape(SID, "circle", code_x + 56, code_y + 11, 10, 10, fill="#27C93F", stroke_width=0)
add_text(SID, "Dockerfile  ·  multi-stage", "caption",
         code_x + 200, code_y + 8, 280, 18,
         color=SILVER, font_size=11, font_family="JetBrains Mono",
         letter_spacing=1, text_align="center")

# Code lines
code_lines = [
    ("01", "# ── build stage ─────────────────────────────", SILVER, 0.5),
    ("02", "FROM golang:1.22-alpine AS build", CYAN, 1),
    ("03", "WORKDIR /src", WHITE, 1),
    ("04", "COPY go.mod go.sum ./", WHITE, 1),
    ("05", "RUN go mod download", WHITE, 1),
    ("06", "COPY . .", WHITE, 1),
    ("07", "RUN CGO_ENABLED=0 go build -o /api ./cmd/api", GREEN, 1),
    ("08", "", WHITE, 1),
    ("09", "# ── runtime ────────────────────────────────", SILVER, 0.5),
    ("10", "FROM gcr.io/distroless/static:nonroot", VIOLET, 1),
    ("11", "COPY --from=build /api /api", WHITE, 1),
    ("12", "USER 65532:65532", AMBER, 1),
    ("13", 'ENTRYPOINT ["/api"]', WHITE, 1),
]
line_y = code_y + 50
for ln_num, ln_text, ln_color, ln_op in code_lines:
    add_text(SID, ln_num, "caption", code_x + 16, line_y, 24, 18,
             color=SILVER, font_size=11, font_family="JetBrains Mono",
             font_weight=400, letter_spacing=0)
    if ln_text:
        add_text(SID, ln_text, "caption", code_x + 48, line_y, 540, 18,
                 color=ln_color, font_size=12, font_family="JetBrains Mono",
                 font_weight=500, letter_spacing=0)
    line_y += 24

# Footer caption under code
add_text(SID, "→ final image: 6.4 MB  ·  0 CVEs  ·  signed",
         "caption", code_x, code_y + code_h + 12, code_w, 18,
         color=GREEN, font_size=12, font_family="JetBrains Mono",
         letter_spacing=2)

# ============================================================
# SLIDE 7 — From Container to Cluster: The Scheduler's Promise
# ============================================================
SID = "slide-7"

# Background
add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=NAVY, stroke_width=0)
# Subtle background grid (vertical lines at 1/4, 1/2, 3/4)
add_shape(SID, "rectangle", 320, 0, 1, 720, fill=WHITE, stroke_width=0, opacity=0.04)
add_shape(SID, "rectangle", 640, 0, 1, 720, fill=WHITE, stroke_width=0, opacity=0.04)
add_shape(SID, "rectangle", 960, 0, 1, 720, fill=WHITE, stroke_width=0, opacity=0.04)

# Top strip
add_text(SID, "ACT II  //  TRANSITION  //  07", "caption",
         48, 40, 500, 22, color=MINT, font_size=12, font_family="JetBrains Mono",
         letter_spacing=3)
add_text(SID, "from container to cluster", "caption",
         960, 40, 280, 22, color=SILVER, font_size=12, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# Title — left aligned, oversized
add_text(SID, "A container is",
         "title", 48, 88, 1180, 80,
         color=SILVER, font_size=64, font_weight=400, line_height=1.05,
         font_family="Space Grotesk")
add_text(SID, "a unit of trust.",
         "title", 48, 158, 1180, 80,
         color=WHITE, font_size=64, font_weight=700, line_height=1.05)
add_text(SID, "A cluster is a system of agreements.",
         "subtitle", 48, 232, 1180, 50,
         color=CYAN, font_size=28, font_weight=400,
         font_family="Inter", line_height=1.3)

# Three columns — the journey from one container to many
col_y = 320
col_w = 360
gap = 28
cols = [
    {
        "num": "ONE",
        "label": "THE CONTAINER",
        "title": "Predictable",
        "body": "Same artifact, every environment. Code, runtime, and dependencies sealed inside an immutable image.",
        "icon": "Package",
        "color": CYAN,
    },
    {
        "num": "MANY",
        "label": "THE FLEET",
        "title": "Replicated",
        "body": "Identical replicas distributed across nodes. No snowflakes. Failure of one is invisible to the rest.",
        "icon": "Boxes",
        "color": VIOLET,
    },
    {
        "num": "ONE+MANY",
        "label": "THE CLUSTER",
        "title": "Orchestrated",
        "body": "Declared desired state. The control plane converges reality toward intent — continuously, autonomously.",
        "icon": "Network",
        "color": GREEN,
    },
]
for i, col in enumerate(cols):
    cx = 48 + i * (col_w + gap)
    # Card panel
    add_shape(SID, "rectangle", cx, col_y, col_w, 320, fill=GLASS, stroke_width=0, opacity=0.55)
    # Top accent bar
    add_shape(SID, "rectangle", cx, col_y, col_w, 2, fill=col["color"], stroke_width=0)
    # Number / phase
    add_text(SID, col["num"], "caption", cx + 24, col_y + 24, 200, 18,
             color=col["color"], font_size=11, font_family="JetBrains Mono",
             font_weight=600, letter_spacing=4)
    # Icon
    add_icon(SID, col["icon"], cx + 24, col_y + 60, size=44, color=col["color"])
    # Label
    add_text(SID, col["label"], "caption", cx + 24, col_y + 124, 280, 18,
             color=SILVER, font_size=11, font_family="IBM Plex Sans",
             font_weight=600, letter_spacing=3)
    # Title
    add_text(SID, col["title"], "heading", cx + 24, col_y + 150, 320, 40,
             color=WHITE, font_size=34, font_weight=600, line_height=1.1,
             font_family="Space Grotesk")
    # Body
    add_text(SID, col["body"], "paragraph", cx + 24, col_y + 204, col_w - 48, 100,
             color=SILVER, font_size=15, font_weight=400, line_height=1.55,
             font_family="Inter")

# Connector arrows between columns
arrow_y = col_y + 80
for i in range(2):
    ax = 48 + (i + 1) * col_w + i * gap
    # Tiny dot trail
    for j in range(3):
        add_shape(SID, "circle", ax + 6 + j * 6, arrow_y, 3, 3,
                  fill=AMBER, stroke_width=0, opacity=0.8)

# Footer pull-quote
add_shape(SID, "rectangle", 48, 668, 4, 28, fill=AMBER, stroke_width=0)
add_text(SID, "The cluster is the smallest unit of resilience.",
         "caption", 64, 670, 800, 24,
         color=WHITE, font_size=16, font_weight=400, line_height=1.3,
         font_family="Inter")
add_text(SID, "07 / 15", "caption", 1180, 672, 60, 18,
         color=SILVER, font_size=11, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# ============================================================
# SLIDE 8 — The Orchestration Constellation
# ============================================================
SID = "slide-8"

# Background
add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN, stroke_width=0)

# Subtle violet glow center
add_shape(SID, "circle", 440, 240, 400, 240, fill=VIOLET, stroke_width=0, opacity=0.06)

# Top strip
add_text(SID, "ACT III  //  ORCHESTRATION  //  08", "caption",
         48, 40, 500, 22, color=MINT, font_size=12, font_family="JetBrains Mono",
         letter_spacing=3)
add_text(SID, "kubernetes · service mesh · autoscale", "caption",
         860, 40, 380, 22, color=SILVER, font_size=12, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# Title — top-left cinematic
add_text(SID, "The Orchestration",
         "title", 48, 88, 1180, 80,
         color=WHITE, font_size=60, font_weight=700, line_height=1.0)
add_text(SID, "Constellation.",
         "title", 48, 152, 1180, 80,
         color=CYAN, font_size=60, font_weight=700, line_height=1.0)

# Left rail editorial thesis
add_shape(SID, "rectangle", 48, 244, 2, 120, fill=AMBER, stroke_width=0)
add_text(SID, "THESIS", "caption", 64, 244, 200, 18,
         color=AMBER, font_size=11, font_family="JetBrains Mono",
         font_weight=600, letter_spacing=4)
add_text(SID,
         "Declare what should be.\nThe scheduler converges to it — node by node, pod by pod, packet by packet.",
         "paragraph", 64, 270, 320, 100,
         color=SILVER, font_size=16, font_weight=400, line_height=1.55,
         font_family="Inter")

# === Architecture diagram (right side, but spans wider) ===
diag_x = 412
diag_y = 256
diag_w = 820
diag_h = 280

# Diagram backdrop panel
add_shape(SID, "rectangle", diag_x, diag_y, diag_w, diag_h,
          fill=GLASS, stroke_width=0, opacity=0.4)

# Layer labels along left of diagram
layers = [
    ("USERS", 280),
    ("INGRESS", 320),
    ("MESH", 380),
    ("PODS", 440),
    ("NODES", 500),
]

# Users node (far left in diagram)
ux = diag_x + 24
add_icon(SID, "Users", ux, diag_y + 20, size=32, color=WHITE)
add_text(SID, "users", "caption", ux - 8, diag_y + 56, 60, 16,
         color=SILVER, font_size=11, font_family="JetBrains Mono",
         letter_spacing=1, text_align="center")

# Ingress
ix = diag_x + 130
add_shape(SID, "rectangle", ix, diag_y + 22, 100, 32, fill=NAVY,
          stroke=CYAN, stroke_width=1)
add_text(SID, "INGRESS", "caption", ix, diag_y + 30, 100, 18,
         color=CYAN, font_size=11, font_family="JetBrains Mono",
         font_weight=600, letter_spacing=2, text_align="center")

# Connector users -> ingress
add_shape(SID, "line", ux + 32, diag_y + 38, ix - (ux + 32), 1,
          fill=CYAN, stroke=CYAN, stroke_width=1, opacity=0.7)

# Service mesh band (3 services)
mesh_y = diag_y + 90
mesh_x = diag_x + 280
services = [
    ("svc-auth", VIOLET),
    ("svc-api", CYAN),
    ("svc-orders", VIOLET),
]
for j, (sname, scol) in enumerate(services):
    sx = mesh_x + j * 130
    add_shape(SID, "rectangle", sx, mesh_y, 110, 30, fill=NAVY,
              stroke=scol, stroke_width=1, opacity=1)
    add_text(SID, sname, "caption", sx, mesh_y + 8, 110, 16,
             color=scol, font_size=10, font_family="JetBrains Mono",
             font_weight=600, letter_spacing=1, text_align="center")

# Connector ingress -> mesh
add_shape(SID, "line", ix + 100, diag_y + 38, mesh_x - (ix + 100), 1,
          fill=CYAN, stroke=CYAN, stroke_width=1, opacity=0.6)
add_shape(SID, "line", mesh_x + 55, diag_y + 50, 1, 40,
          fill=CYAN, stroke=CYAN, stroke_width=1, opacity=0.4)

# Mesh label
add_text(SID, "service mesh", "caption", mesh_x, mesh_y - 22, 360, 16,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=2, text_align="center")

# Pods row (under mesh services) — 3 groups of 3 pods
pod_y = mesh_y + 56
for j in range(3):
    sx = mesh_x + j * 130
    for k in range(3):
        px = sx + 8 + k * 32
        add_shape(SID, "circle", px, pod_y, 18, 18,
                  fill=services[j][1], stroke_width=0, opacity=0.75)
    # connector mesh service to pods
    add_shape(SID, "line", sx + 55, mesh_y + 30, 1, 26,
              fill=services[j][1], stroke=services[j][1], stroke_width=1, opacity=0.4)

add_text(SID, "pods × replicas", "caption", mesh_x, pod_y + 28, 360, 16,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=2, text_align="center")

# Node row at bottom (3 nodes)
node_y = diag_y + 220
for j in range(3):
    nx = mesh_x + j * 130
    add_shape(SID, "rectangle", nx, node_y, 110, 24,
              fill=NAVY, stroke=MINT, stroke_width=1)
    add_text(SID, f"node-{j+1}", "caption", nx, node_y + 4, 110, 14,
             color=MINT, font_size=10, font_family="JetBrains Mono",
             letter_spacing=1, text_align="center")

# YAML floating snippet (right of diagram)
yaml_x = mesh_x + 420
yaml_y = diag_y + 30
add_shape(SID, "rectangle", yaml_x, yaml_y, 220, 180,
          fill=DARK_PANEL, stroke=CYAN, stroke_width=1, opacity=0.95)
add_text(SID, "deployment.yaml", "caption",
         yaml_x + 12, yaml_y + 8, 200, 16,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=1)
yaml_lines = [
    ("apiVersion:", "apps/v1", CYAN),
    ("kind:", "Deployment", WHITE),
    ("spec:", "", SILVER),
    ("  replicas:", "3", GREEN),
    ("  resources:", "", SILVER),
    ("    requests:", "", SILVER),
    ("      cpu:", "200m", AMBER),
    ("      memory:", "256Mi", AMBER),
    ("  readinessProbe:", "/healthz", VIOLET),
]
ly = yaml_y + 32
for k, v, col in yaml_lines:
    add_text(SID, k, "caption", yaml_x + 12, ly, 120, 14,
             color=SILVER, font_size=10, font_family="JetBrains Mono", letter_spacing=0)
    if v:
        add_text(SID, v, "caption", yaml_x + 130, ly, 80, 14,
                 color=col, font_size=10, font_family="JetBrains Mono",
                 font_weight=600, letter_spacing=0)
    ly += 16

# === Bottom strip: 3 principle cards ===
strip_y = 568
strip_h = 108
principles = [
    ("Declarative State",  "Desired state, version-controlled.",  "FileCode2",    CYAN),
    ("Self-Healing",       "Failed pods rescheduled automatically.", "Activity", VIOLET),
    ("Horizontal Scale",   "HPA reacts to load in seconds.",       "TrendingUp",   GREEN),
]
card_w = 384
gap = 16
for i, (title, sub, ico, col) in enumerate(principles):
    cx = 48 + i * (card_w + gap)
    add_shape(SID, "rectangle", cx, strip_y, card_w, strip_h, fill=GLASS,
              stroke_width=0, opacity=0.7)
    add_shape(SID, "rectangle", cx, strip_y, 3, strip_h, fill=col, stroke_width=0)
    add_icon(SID, ico, cx + 20, strip_y + 22, size=32, color=col)
    add_text(SID, f"0{i+1}", "caption", cx + card_w - 60, strip_y + 16, 40, 16,
             color=col, font_size=11, font_family="JetBrains Mono",
             font_weight=600, letter_spacing=2, text_align="right")
    add_text(SID, title, "subheading", cx + 64, strip_y + 22, 280, 28,
             color=WHITE, font_size=20, font_weight=600, line_height=1.2,
             font_family="Space Grotesk")
    add_text(SID, sub, "caption", cx + 64, strip_y + 56, 300, 36,
             color=SILVER, font_size=13, font_family="Inter",
             font_weight=400, letter_spacing=0)

# Footer
add_text(SID, "08 / 15", "caption", 1180, 696, 60, 16,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# ============================================================
# SLIDE 9 — Microservices Without the Chaos
# ============================================================
SID = "slide-9"

# Background
add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=NAVY, stroke_width=0)

# Top strip
add_text(SID, "ACT III  //  MICROSERVICES  //  09", "caption",
         48, 40, 500, 22, color=MINT, font_size=12, font_family="JetBrains Mono",
         letter_spacing=3)
add_text(SID, "bounded contexts · loose coupling", "caption",
         900, 40, 340, 22, color=SILVER, font_size=12, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# Title across top
add_text(SID, "Microservices",
         "title", 48, 88, 800, 80,
         color=WHITE, font_size=60, font_weight=700, line_height=1.0)
add_text(SID, "without the chaos.",
         "title", 48, 152, 1100, 80,
         color=CYAN, font_size=60, font_weight=700, line_height=1.0)

# Subtitle / kicker
add_text(SID, "Domain-aligned services · async events · contracts that hold.",
         "subtitle", 48, 228, 1180, 36,
         color=SILVER, font_size=22, font_weight=400, line_height=1.3,
         font_family="Inter")

# === LEFT: monolith fading ===
mono_x = 48
mono_y = 296
mono_w = 320
mono_h = 320

# Monolith outer block (faded)
add_shape(SID, "rectangle", mono_x, mono_y, mono_w, mono_h,
          fill="#6B7280", stroke_width=0, opacity=0.18)
# Inner messy crisscross - fake "tangled" overlay using lines
crack_color = "#6B7280"
# horizontal divisions inside monolith
for y_off in [60, 110, 170, 220, 270]:
    add_shape(SID, "rectangle", mono_x + 16, mono_y + y_off, mono_w - 32, 1,
              fill=crack_color, stroke_width=0, opacity=0.35)
# vertical divisions
for x_off in [80, 160, 240]:
    add_shape(SID, "rectangle", mono_x + x_off, mono_y + 16, 1, mono_h - 32,
              fill=crack_color, stroke_width=0, opacity=0.35)

# Crack diagonals (red anti-pattern)
add_shape(SID, "line", mono_x + 40, mono_y + 40, 240, 240,
          fill="#7F1D1D", stroke="#7F1D1D", stroke_width=2, opacity=0.6)
add_shape(SID, "line", mono_x + 280, mono_y + 40, -200, 200,
          fill="#7F1D1D", stroke="#7F1D1D", stroke_width=2, opacity=0.4)

# Monolith label
add_text(SID, "BEFORE", "caption", mono_x, mono_y - 24, mono_w, 18,
         color="#94A3B8", font_size=11, font_family="JetBrains Mono",
         font_weight=600, letter_spacing=4)
add_text(SID, "the monolith", "subheading", mono_x, mono_y + mono_h + 16, mono_w, 30,
         color="#94A3B8", font_size=22, font_weight=600,
         font_family="Space Grotesk")
add_text(SID, "one heartbeat. one outage. one deploy that scares everyone.",
         "caption", mono_x, mono_y + mono_h + 48, mono_w, 36,
         color="#64748B", font_size=12, font_family="Inter",
         font_weight=400, line_height=1.4)

# Arrow / transition between halves
arrow_x = mono_x + mono_w + 16
arrow_y = mono_y + mono_h // 2 - 20
add_shape(SID, "rectangle", arrow_x, arrow_y + 18, 32, 2, fill=AMBER, stroke_width=0)
add_text(SID, "→", "caption", arrow_x, arrow_y, 32, 40,
         color=AMBER, font_size=32, font_family="Inter",
         font_weight=400, text_align="center")

# === RIGHT: clean microservice ecosystem ===
ms_x = 432
ms_y = 296
ms_w = 800
ms_h = 320

# AFTER label
add_text(SID, "AFTER", "caption", ms_x, ms_y - 24, ms_w, 18,
         color=CYAN, font_size=11, font_family="JetBrains Mono",
         font_weight=600, letter_spacing=4)

# Backdrop
add_shape(SID, "rectangle", ms_x, ms_y, ms_w, ms_h,
          fill=GLASS, stroke_width=0, opacity=0.45)

# API Gateway at top
gw_x = ms_x + ms_w / 2 - 90
gw_y = ms_y + 20
add_shape(SID, "rectangle", gw_x, gw_y, 180, 36, fill=NAVY,
          stroke=CYAN, stroke_width=1)
add_icon(SID, "DoorOpen", gw_x + 8, gw_y + 6, size=24, color=CYAN)
add_text(SID, "API GATEWAY", "caption", gw_x + 36, gw_y + 10, 144, 18,
         color=CYAN, font_size=11, font_family="JetBrains Mono",
         font_weight=600, letter_spacing=3)

# 5 service cards in a row
svc_y = ms_y + 96
svc_w = 140
svc_h = 100
svc_gap = 12
total_svc_w = 5 * svc_w + 4 * svc_gap
start_x = ms_x + (ms_w - total_svc_w) / 2

services_def = [
    ("Auth", "ShieldCheck", VIOLET, "/v1/sessions"),
    ("Catalog", "Boxes", CYAN, "/v1/products"),
    ("Payments", "CreditCard", GREEN, "/v1/charges"),
    ("Orders", "ShoppingCart", AMBER, "/v1/orders"),
    ("Notify", "Bell", MINT, "/v1/events"),
]
for j, (sname, ico, col, route) in enumerate(services_def):
    sx = start_x + j * (svc_w + svc_gap)
    add_shape(SID, "rectangle", sx, svc_y, svc_w, svc_h, fill=DARK_PANEL,
              stroke_width=0, opacity=0.95)
    add_shape(SID, "rectangle", sx, svc_y, svc_w, 2, fill=col, stroke_width=0)
    add_icon(SID, ico, sx + 12, svc_y + 14, size=24, color=col)
    add_text(SID, sname, "subheading", sx + 12, svc_y + 44, svc_w - 24, 24,
             color=WHITE, font_size=16, font_weight=600, line_height=1.2,
             font_family="Space Grotesk")
    add_text(SID, route, "caption", sx + 12, svc_y + 70, svc_w - 24, 16,
             color=col, font_size=10, font_family="JetBrains Mono",
             letter_spacing=0)
    # Connector from gateway down to service
    cx_center = sx + svc_w / 2
    add_shape(SID, "line", cx_center, gw_y + 36, 1, svc_y - (gw_y + 36),
              fill=col, stroke=col, stroke_width=1, opacity=0.4)

# Event bus at bottom of right diagram
bus_y = svc_y + svc_h + 28
add_shape(SID, "rectangle", ms_x + 24, bus_y, ms_w - 48, 24,
          fill=NAVY, stroke=AMBER, stroke_width=1)
add_text(SID, "▸ event bus  ·  orders.created  →  payments  →  notify  →  catalog",
         "caption", ms_x + 24, bus_y + 4, ms_w - 48, 16,
         color=AMBER, font_size=11, font_family="JetBrains Mono",
         font_weight=500, letter_spacing=1, text_align="center")

# Async event particles between services
for j in range(4):
    px = start_x + (j + 1) * svc_w + j * svc_gap - 6
    add_shape(SID, "circle", px, svc_y + svc_h + 10, 4, 4,
              fill=AMBER, stroke_width=0, opacity=0.9)

# === Bottom row: 3 small annotations ===
ann_y = 644
ann = [
    ("BOUNDED CONTEXTS", "Each service owns its data and its words.", CYAN),
    ("INDEPENDENT DEPLOY", "Ship one. Don't redeploy the world.", VIOLET),
    ("LOOSE COUPLING", "Async by default. Fail without a chain reaction.", GREEN),
]
ann_w = 384
for i, (title, body, col) in enumerate(ann):
    ax = 48 + i * (ann_w + 16)
    add_shape(SID, "rectangle", ax, ann_y, 3, 48, fill=col, stroke_width=0)
    add_text(SID, title, "caption", ax + 14, ann_y, 360, 16,
             color=col, font_size=11, font_family="JetBrains Mono",
             font_weight=600, letter_spacing=3)
    add_text(SID, body, "caption", ax + 14, ann_y + 22, 360, 22,
             color=SILVER, font_size=14, font_family="Inter",
             font_weight=400, line_height=1.3)

add_text(SID, "09 / 15", "caption", 1180, 696, 60, 16,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# ============================================================
# SLIDE 10 — Serverless: Architecture That Breathes
# ============================================================
SID = "slide-10"

# Background
add_shape(SID, "rectangle", 0, 0, 1280, 720, fill=OBSIDIAN, stroke_width=0)
# Soft violet glow
add_shape(SID, "circle", 240, 360, 480, 360, fill=VIOLET, stroke_width=0, opacity=0.08)
add_shape(SID, "circle", 880, 360, 360, 240, fill=CYAN, stroke_width=0, opacity=0.06)

# Top strip
add_text(SID, "ACT III  //  SERVERLESS  //  10", "caption",
         48, 40, 500, 22, color=MINT, font_size=12, font_family="JetBrains Mono",
         letter_spacing=3)
add_text(SID, "event-driven · stateless · elastic", "caption",
         900, 40, 340, 22, color=SILVER, font_size=12, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# Title — centered serif feel, oversized
add_text(SID, "Architecture",
         "title", 48, 88, 1184, 80,
         color=WHITE, font_size=64, font_weight=400, line_height=1.0,
         text_align="center", font_family="Space Grotesk")
add_text(SID, "that breathes.",
         "title", 48, 156, 1184, 80,
         color=VIOLET, font_size=64, font_weight=700, line_height=1.0,
         text_align="center")

add_text(SID, "Idle costs nothing. Demand summons compute. Scale is a side effect.",
         "subtitle", 48, 232, 1184, 36,
         color=SILVER, font_size=20, font_weight=400, text_align="center",
         font_family="Inter", line_height=1.3)

# === Central event-driven flow diagram ===
flow_y = 304
flow_h = 200
flow_x = 48
flow_w = 880

# Pillars: Event Source → Queue → Function → Managed Service → Monitor
nodes = [
    {"label": "EVENT SOURCE", "sub": "S3 / API / Cron", "icon": "Zap", "color": CYAN},
    {"label": "QUEUE / TOPIC", "sub": "SQS · EventBridge", "icon": "Inbox", "color": MINT},
    {"label": "FUNCTION", "sub": "λ handler", "icon": "Code2", "color": VIOLET},
    {"label": "MANAGED STORE", "sub": "DynamoDB · S3", "icon": "Database", "color": GREEN},
    {"label": "OBSERVE", "sub": "metrics + traces", "icon": "Activity", "color": AMBER},
]

node_w = 156
node_h = 156
total_nodes_w = 5 * node_w + 4 * 25
start_x = flow_x + (flow_w - total_nodes_w) / 2

for j, n in enumerate(nodes):
    nx = start_x + j * (node_w + 25)
    # node card
    add_shape(SID, "rectangle", nx, flow_y, node_w, node_h, fill=GLASS,
              stroke=n["color"], stroke_width=1, opacity=0.6)
    # outer halo for function node
    if j == 2:
        add_shape(SID, "circle", nx - 16, flow_y - 16, node_w + 32, node_h + 32,
                  fill=VIOLET, stroke_width=0, opacity=0.12)
    # icon
    add_icon(SID, n["icon"], nx + node_w / 2 - 22, flow_y + 24, size=44, color=n["color"])
    # label
    add_text(SID, n["label"], "caption", nx, flow_y + 84, node_w, 18,
             color=n["color"], font_size=11, font_family="JetBrains Mono",
             font_weight=600, letter_spacing=2, text_align="center")
    # sub
    add_text(SID, n["sub"], "caption", nx, flow_y + 108, node_w, 18,
             color=SILVER, font_size=11, font_family="Inter",
             font_weight=400, letter_spacing=0, text_align="center")
    # phase number
    add_text(SID, f"0{j+1}", "caption", nx + 12, flow_y + 12, 30, 14,
             color=SILVER, font_size=10, font_family="JetBrains Mono",
             font_weight=500, letter_spacing=1)

# Flow connector dots between nodes (event particles)
for j in range(4):
    cx_start = start_x + (j + 1) * node_w + j * 25
    for k in range(3):
        add_shape(SID, "circle", cx_start + 4 + k * 6, flow_y + node_h / 2 - 2,
                  4, 4, fill=AMBER if k == 1 else MINT, stroke_width=0,
                  opacity=0.9 if k == 1 else 0.5)

# === RIGHT vertical pattern stack ===
pat_x = 952
pat_y = 304
pat_w = 280
pat_h = 200

add_shape(SID, "rectangle", pat_x, pat_y, pat_w, pat_h,
          fill=GLASS, stroke_width=0, opacity=0.55)
add_text(SID, "PATTERN NOTES", "caption", pat_x + 16, pat_y + 16, 248, 16,
         color=AMBER, font_size=10, font_family="JetBrains Mono",
         font_weight=600, letter_spacing=3)

patterns = [
    ("Event Trigger", CYAN),
    ("Stateless Function", VIOLET),
    ("Managed Service", GREEN),
    ("Pay-per-Use", AMBER),
]
py = pat_y + 44
for name, col in patterns:
    add_shape(SID, "circle", pat_x + 18, py + 6, 6, 6, fill=col, stroke_width=0)
    add_text(SID, name, "paragraph", pat_x + 36, py, 240, 22,
             color=WHITE, font_size=15, font_weight=500, line_height=1.2,
             font_family="Inter")
    py += 32

# === Bottom: dark code console ===
con_x = 48
con_y = 528
con_w = 1184
con_h = 144

add_shape(SID, "rectangle", con_x, con_y, con_w, con_h,
          fill=DARK_PANEL, stroke_width=0)
add_shape(SID, "rectangle", con_x, con_y, con_w, 28, fill="#070B17", stroke_width=0)
add_shape(SID, "circle", con_x + 16, con_y + 9, 10, 10, fill="#FF5F56", stroke_width=0)
add_shape(SID, "circle", con_x + 36, con_y + 9, 10, 10, fill="#FFBD2E", stroke_width=0)
add_shape(SID, "circle", con_x + 56, con_y + 9, 10, 10, fill="#27C93F", stroke_width=0)
add_text(SID, "handler.js  ·  serverless function", "caption",
         con_x + 540, con_y + 6, 280, 16,
         color=SILVER, font_size=11, font_family="JetBrains Mono",
         letter_spacing=1, text_align="center")

code_lines_2 = [
    ("// invoked per-event · ephemeral · stateless", SILVER, 0.6),
    ("export const handler = async (event) => {", CYAN, 1),
    ("  const order = JSON.parse(event.body);", WHITE, 1),
    ("  await ddb.put({ TableName: 'orders', Item: order }).promise();", VIOLET, 1),
    ("  return { statusCode: 202, body: JSON.stringify({ ok: true }) };", GREEN, 1),
    ("};", CYAN, 1),
]
ly = con_y + 40
for ln_text, ln_color, _op in code_lines_2:
    add_text(SID, ln_text, "caption", con_x + 24, ly, con_w - 48, 16,
             color=ln_color, font_size=13, font_family="JetBrains Mono",
             font_weight=500, letter_spacing=0)
    ly += 18

# Dashboard widgets in bottom-right of console (cold-start / concurrency)
widget_x = con_x + con_w - 280
widget_y = con_y + 36
add_shape(SID, "rectangle", widget_x, widget_y, 256, 92,
          fill="#070B17", stroke=GLASS, stroke_width=1)
# split into two
add_text(SID, "COLD START", "caption", widget_x + 16, widget_y + 12, 100, 14,
         color=SILVER, font_size=9, font_family="JetBrains Mono",
         font_weight=500, letter_spacing=2)
add_text(SID, "82ms", "heading", widget_x + 16, widget_y + 30, 110, 32,
         color=CYAN, font_size=26, font_weight=600,
         font_family="Space Grotesk")
add_text(SID, "p95", "caption", widget_x + 16, widget_y + 66, 100, 14,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=1)

add_text(SID, "CONCURRENCY", "caption", widget_x + 140, widget_y + 12, 110, 14,
         color=SILVER, font_size=9, font_family="JetBrains Mono",
         font_weight=500, letter_spacing=2)
add_text(SID, "1,420", "heading", widget_x + 140, widget_y + 30, 110, 32,
         color=GREEN, font_size=26, font_weight=600,
         font_family="Space Grotesk")
add_text(SID, "live", "caption", widget_x + 140, widget_y + 66, 100, 14,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=1)

# Footer page indicator
add_text(SID, "10 / 15", "caption", 1180, 696, 60, 16,
         color=SILVER, font_size=10, font_family="JetBrains Mono",
         letter_spacing=2, text_align="right")

# ============================================================
# ASSEMBLE FILES
# ============================================================
slides_content = []
slides_baselayout = []
for i in range(6, 11):
    sid = f"slide-{i}"
    slides_content.append({
        "id": sid,
        "order": i - 6,  # within batch ordering 0..4
        "layoutId": "blank-canvas",
        "backgroundColor": OBSIDIAN if i in (6, 8, 10) else NAVY,
        "textElements": text_by_slide[sid],
    })
    slides_baselayout.append({
        "id": sid,
        "layoutId": "blank-canvas",
        "imageElements": [],
        "shapeElements": [],
        "chartElements": [],
        "iconElements": [],
        "embedElements": [],
    })

content_file = {
    "slides": slides_content,
    "imageElements": image_elements,
    "shapeElements": shape_elements,
    "chartElements": chart_elements,
    "tableElements": table_elements,
    "iconElements": icon_elements,
    "embedElements": [],
    "smartDiagramElements": [],
    "groupElements": [],
}

baselayout_file = {
    "version": "v1",
    "slides": slides_baselayout,
    "imageElements": [],
    "shapeElements": [],
    "chartElements": [],
    "iconElements": [],
    "embedElements": [],
}

changelog_file = {
    "version": "2.0",
    "slides": changelog_slides,
}

# Element count
element_count = (
    sum(len(s["textElements"]) for s in slides_content)
    + len(image_elements)
    + len(shape_elements)
    + len(chart_elements)
    + len(table_elements)
    + len(icon_elements)
)

envelope = {
    "exportedAt": NOW,
    "presentation": {
        "_id": f"deck-cloud-arch-batch-6-10-{NOW}",
        "title": "Cloud Architecture Best Practices — Slides 6–10",
        "description": "",
        "thumbnailUrl": None,
        "isPublic": False,
        "slideCount": 5,
        "elementCount": element_count,
        "createdAt": "2026-05-25T00:00:00.000Z",
        "updatedAt": "2026-05-25T00:00:00.000Z",
        "s3Key": None,
        "s3Url": None,
    },
    "files": {
        "content": content_file,
        "baseLayout": baselayout_file,
        "changelog": changelog_file,
    },
}

OUT = "deck.json"
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(envelope, f, indent=2, ensure_ascii=False)

print(f"OK -> {OUT}")
print(f"slideCount   = 5")
print(f"elementCount = {element_count}")
print(f"  text   = {sum(len(s['textElements']) for s in slides_content)}")
print(f"  shape  = {len(shape_elements)}")
print(f"  image  = {len(image_elements)}")
print(f"  icon   = {len(icon_elements)}")
print(f"  chart  = {len(chart_elements)}")
print(f"  table  = {len(table_elements)}")
