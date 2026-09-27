"""UtopiaOS-themed figures for the ElasticSkip post.

Reuses the drawing helpers from the GPT-from-scratch post. Numbers come from
the paper's macros.tex / story.md (nDCG@10, MS MARCO dev, prompt-free).
Run from this directory:  python3 make_figures.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scratchGPT", "images"))
import make_diagrams as base  # noqa: E402

base.HERE = HERE
base.POST = "elasticskip"
from make_diagrams import Svg, BG, PANEL, LINE, LINE1, FG, MUTED, G, GD, Y, C, M, V, R  # noqa: E402

# chart series colours: in-band steps of the theme's green/gold, validated on
# the dark surface #0c1011 (CVD dE 9.6, normal dE 17.5, contrast >= 6:1)
S_OURS, S_BASE = "#32a675", "#bf841d"
NEUTRAL = "#5c6b67"   # non-highlighted marks


# ─────────────────────────────────────────────────────────────────
# 1. Where to cut: which layers each strategy keeps (illustrative)
# ─────────────────────────────────────────────────────────────────
def where_to_cut():
    s = Svg(1000, 490, "where_to_cut.svg")
    N, cw, x0 = 28, 19, 250
    kept = {
        "middle-skip (ours)": set(range(0, 8)) | set(range(22, 28)),
        "importance ranking": {0, 1, 2, 3, 4, 5, 6, 8, 11, 13, 16, 19, 22, 26},
        "truncation (drop tail)": set(range(0, 14)),
        "prefix drop": set(range(14, 28)),
    }
    notes = {
        "middle-skip (ours)": ("6 / 6", G),
        "importance ranking": ("2 / 6", R),
        "truncation (drop tail)": ("0 / 6", R),
        "prefix drop": ("6 / 6", Y),
    }
    s.text(40, 66, "a 28-layer query encoder cut to 14 layers (illustrative layouts)",
           size=12, fill=MUTED, anchor="start")
    # final-six bracket
    fx = x0 + 22 * cw
    s.rect(fx - 3, 84, 6 * cw + 6, 334, fill=Y, fop=0.05, stroke=Y, sop=0.5, rx=6, dash="4 4")
    s.text(fx + 3 * cw, 100, "final 6 layers", size=11, fill=Y, weight=700)
    s.text(x0, 114, "layer 0", size=9.5, fill=MUTED, anchor="start")
    s.text(fx - 10, 114, "→ 27", size=9.5, fill=MUTED, anchor="end")
    s.text(x0 + N * cw + 46, 100, "final-6", size=10.5, fill=MUTED, anchor="start")
    s.text(x0 + N * cw + 46, 114, "kept", size=10.5, fill=MUTED, anchor="start")
    for r, (name, keep) in enumerate(kept.items()):
        y = 134 + r * 72
        ours = r == 0
        s.text(x0 - 16, y + 18, name, size=12.5, fill=G if ours else FG, anchor="end",
               weight=700 if ours else 400)
        for i in range(N):
            k = i in keep
            col = (G if ours else C) if k else LINE
            s.rect(x0 + i * cw, y, cw - 3, 26, fill=col, stroke=col if k else LINE1,
                   fop=0.55 if k else 0.35, sop=0.9 if k else 0.8, rx=3)
        txt, col = notes[name]
        s.text(x0 + N * cw + 46, y + 18, txt, size=13, fill=col, weight=700, anchor="start")
    s.text(500, 440, "the final 6 layers build the pooled query embedding; importance ranking removes most of them",
           size=11, fill=FG)
    s.text(500, 464, "importance rules score a layer as redundant when its input ≈ its output, "
           "but near the top that is the representation settling, not idling",
           size=11, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 2. Isolation: same recipe, only the removed layers change (dot plot)
# ─────────────────────────────────────────────────────────────────
def isolation():
    s = Svg(1000, 430, "isolation.svg")
    rows = ["middle-skip (ours)", "norm-ratio (HARNESS-LM)", "Block-Influence (ShortGPT)",
            "random (control)", "truncation (drop tail)", "prefix drop"]
    data = {"0.6B · keep 14 of 28": [37.44, 35.74, 35.94, 31.90, 30.72, 30.85],
            "4B · keep 16 of 36": [40.78, 39.56, 36.68, 39.75, 35.76, 31.36]}
    lx = 250                  # label column right edge
    panels = [(290, 580), (640, 930)]
    vmin, vmax = 29, 42
    s.text(40, 64, "nDCG@10 on MS MARCO dev, identical training recipe, only the cut differs",
           size=12.5, fill=FG, anchor="start", weight=700)
    for i, name in enumerate(rows):
        y = 128 + i * 42
        s.text(lx, y + 4, name, size=11.5, fill=G if i == 0 else FG, anchor="end", weight=700 if i == 0 else 400)
    for (p0, p1), (title, vals) in zip(panels, data.items()):
        px = lambda v: p0 + (v - vmin) / (vmax - vmin) * (p1 - p0)
        s.text((p0 + p1) / 2, 96, title, size=12, fill=FG, weight=700)
        for v in range(30, 43, 4):
            s.line(px(v), 108, px(v), 360, LINE1, sw=1, arrow=False)
            s.text(px(v), 378, str(v), size=10.5, fill=MUTED)
        for i, v in enumerate(vals):
            y = 128 + i * 42
            s.line(p0, y, p1, y, LINE1, sw=1, arrow=False, dash="1 5")
            ours = i == 0
            s.circle(px(v), y, 6, fill=S_OURS if ours else NEUTRAL, stroke=BG, sw=2)
            s.text(px(v) + 12, y + 4, f"{v:.2f}", size=11, fill=FG if ours else MUTED,
                   anchor="start", weight=700 if ours else 400)
    s.text(500, 408, "where you cut spans 6.7 / 9.4 points; the training recipe spans at most 2.0",
           size=11.5, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 3. ElasticSkip: one base, many depths
# ─────────────────────────────────────────────────────────────────
def architecture():
    s = Svg(1000, 600, "elasticskip.svg")
    # asymmetric retrieval strip
    s.rect(24, 50, 952, 92, fill=PANEL, stroke=LINE, rx=10)
    s.text(44, 74, "asymmetric retrieval", size=12, fill=FG, anchor="start", weight=700)
    s.text(44, 96, "documents", size=11, fill=MUTED, anchor="start")
    s.text(44, 124, "query", size=11, fill=MUTED, anchor="start")
    s.rect(140, 84, 230, 22, fill=V, stroke=V, fop=0.1, sop=0.7, rx=5)
    s.text(255, 99, "full encoder · offline · frozen index", size=10, fill=V)
    s.rect(140, 112, 230, 22, fill=G, stroke=G, fop=0.12, sop=0.8, rx=5)
    s.text(255, 127, "ElasticSkip · online, every request", size=10, fill=G)
    s.line(372, 95, 520, 108, MUTED, sw=1.2)
    s.line(372, 123, 520, 112, G, sw=1.2)
    s.circle(534, 110, 13, stroke=Y, glow=True)
    s.text(534, 115, "·", size=20, fill=Y, weight=700)
    s.text(556, 106, "one dot product", size=11, fill=Y, anchor="start", weight=700)
    s.text(556, 122, "only the query side is on the clock", size=10, fill=MUTED, anchor="start")

    # the layer stack
    x, w, lh = 120, 190, 11
    layers = 28
    L, K = 8, 14      # illustrative boundary and widest skip
    top = 170
    for i in range(layers):
        yy = top + (layers - 1 - i) * (lh + 1)
        if i < L:
            col, fop, sop = C, 0.35, 0.8
        elif i < L + K:
            col, fop, sop = LINE, 0.25, 0.6
        else:
            col, fop, sop = G, 0.4, 0.85
        s.rect(x, yy, w, lh, fill=col, stroke=col if col != LINE else LINE1, fop=fop, sop=sop, rx=2)
    y_tail = top
    y_mid = top + 6 * (lh + 1)
    y_pre = top + (layers - L) * (lh + 1)
    ybot = top + layers * (lh + 1)
    s.text(x - 14, y_tail + 38, "tail", size=12, fill=G, anchor="end", weight=700)
    s.text(x - 14, y_tail + 54, "kept", size=10, fill=MUTED, anchor="end")
    s.text(x - 14, (y_mid + y_pre) / 2 + 4, "middle", size=12, fill=MUTED, anchor="end", weight=700)
    s.text(x - 14, (y_mid + y_pre) / 2 + 20, "skip k", size=10, fill=MUTED, anchor="end")
    s.text(x - 14, (y_pre + ybot) / 2 + 4, "prefix", size=12, fill=C, anchor="end", weight=700)
    s.text(x - 14, (y_pre + ybot) / 2 + 20, "kept", size=10, fill=MUTED, anchor="end")
    s.text(x + w / 2, ybot + 22, "one base model", size=12, fill=FG, weight=700)
    # adapters
    s.rect(x + w + 20, y_tail, 150, 70, fill=M, stroke=M, fop=0.1, sop=0.8, rx=7)
    s.text(x + w + 95, y_tail + 30, "per-depth LoRA", size=11.5, fill=M, weight=700)
    s.text(x + w + 95, y_tail + 48, "one small adapter per k", size=9.5, fill=MUTED)
    s.rect(x + w + 20, y_pre + 10, 150, 70, fill=Y, stroke=Y, fop=0.1, sop=0.8, rx=7)
    s.text(x + w + 95, y_pre + 40, "shared LoRA", size=11.5, fill=Y, weight=700)
    s.text(x + w + 95, y_pre + 58, "active at every depth", size=9.5, fill=MUTED)
    s.path(f"M{x + w + 20},{y_tail + 35} L{x + w + 4},{y_tail + 35}", M, sw=1.3)
    s.path(f"M{x + w + 20},{y_pre + 45} L{x + w + 4},{y_pre + 45}", Y, sw=1.3)

    # depths on demand
    dx = 640
    s.text(dx, 184, "pick the depth at deploy time", size=12.5, fill=FG, anchor="start", weight=700)
    s.text(dx, 202, "merge its adapters, serve at a fixed depth", size=10, fill=MUTED, anchor="start")
    for j, (k, note) in enumerate([(4, "light load"), (10, "busy"), (14, "peak traffic")]):
        yy = 230 + j * 86
        depth = layers - k
        bw = 9
        for i in range(depth):
            col = C if i < L else G
            s.rect(dx + i * (bw + 2), yy, bw, 30, fill=col, stroke=col, fop=0.45, sop=0.85, rx=1.5)
        s.text(dx, yy + 50, f"k = {k}  →  {depth} layers", size=11.5, fill=FG, anchor="start", weight=700)
        s.text(dx + 180, yy + 50, note, size=10.5, fill=MUTED, anchor="start")
    s.path(f"M{x + w + 176},{(y_tail + ybot) / 2} C{560},{(y_tail + ybot) / 2} {580},{300} {dx - 14},{300}",
           GD, sw=1.4, dash="5 4")
    s.text(500, 578, "no retraining and no re-indexing per latency target: a new operating point is a cheap adapter",
           size=11.5, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 4. Cross-scale head-to-head: one ElasticSkip base vs per-depth HARNESS-LM
# ─────────────────────────────────────────────────────────────────
def crossscale():
    s = Svg(1000, 430, "crossscale.svg")
    panels = [
        ("0.6B (28 layers)", [24, 20, 18, 16, 14], [38.73, 38.56, 38.25, 37.89, 37.04],
         [38.73, 38.02, 37.87, 36.64, 35.95], 38.05, (35.5, 39.5)),
        ("4B (36 layers)", [32, 28, 24, 20, 16], [42.92, 42.61, 42.40, 41.77, 40.89],
         [42.28, 42.01, 41.81, 41.00, 39.24], 43.00, (38.5, 43.5)),
        ("8B (36 layers)", [32, 28, 24, 20, 16], [43.91, 43.80, 43.53, 43.11, 42.09],
         [43.07, 42.75, 42.67, 41.68, 41.35], 43.29, (40.5, 44.5)),
    ]
    s.text(40, 64, "nDCG@10 on MS MARCO dev vs executed layers: one ElasticSkip base against HARNESS-LM trained per depth",
           size=12, fill=FG, anchor="start", weight=700)
    for p, (title, depths, ours, hlm, full, (lo, hi)) in enumerate(panels):
        x0, x1 = 80 + p * 310, 80 + p * 310 + 250
        y0, y1 = 340, 110
        xmin, xmax = min(depths) - 1, max(depths) + 1
        px = lambda d: x0 + (d - xmin) / (xmax - xmin) * (x1 - x0)
        py = lambda v: y0 - (v - lo) / (hi - lo) * (y0 - y1)
        s.text((x0 + x1) / 2, 94, title, size=12, fill=FG, weight=700)
        step = 1.0
        v = lo + 0.5
        while v <= hi:
            s.line(x0, py(v), x1, py(v), LINE1, sw=1, arrow=False)
            s.text(x0 - 8, py(v) + 4, f"{v:.1f}".rstrip("0").rstrip("."), size=9.5, fill=MUTED, anchor="end")
            v += step
        for d in depths:
            s.text(px(d), y0 + 18, str(d), size=9.5, fill=MUTED)
        # uncompressed teacher reference
        s.path(f"M{x0},{py(full):.1f} L{x1},{py(full):.1f}", MUTED, sw=1.2, arrow=False, dash="2 4")
        s.text(x1, py(full) - 6, f"full {full:.2f}", size=9.5, fill=MUTED, anchor="end")
        for vals, col, dash, marker in [(hlm, S_BASE, "7 5", "sq"), (ours, S_OURS, None, "ci")]:
            d_ = " ".join(("M" if i == 0 else "L") + f"{px(d):.1f},{py(v):.1f}" for i, (d, v) in enumerate(zip(depths, vals)))
            s.path(d_, col, sw=2, arrow=False, dash=dash)
            for d, v in zip(depths, vals):
                if marker == "ci":
                    s.circle(px(d), py(v), 4.5, fill=col, stroke=BG, sw=1.8)
                else:
                    s.rect(px(d) - 4.5, py(v) - 4.5, 9, 9, fill=col, stroke=BG, sw=1.8)
        # label the most aggressive cut's gap
        dlast, g = depths[-1], ours[-1] - hlm[-1]
        s.text(px(dlast), py(ours[-1]) - 12, f"+{g:.2f}", size=10.5, fill=FG, weight=700)
    s.text(500, 380, "executed layers (fewer = faster)", size=10.5, fill=MUTED)
    # legend
    lx, ly = 250, 408
    for i, (name, col, dash, marker) in enumerate([("ElasticSkip (one base)", S_OURS, None, "ci"),
                                                   ("HARNESS-LM (one model per depth)", S_BASE, "7 5", "sq")]):
        xx = lx + i * 220
        s.path(f"M{xx},{ly} L{xx + 28},{ly}", col, sw=2, arrow=False, dash=dash)
        if marker == "ci":
            s.circle(xx + 14, ly, 4, fill=col, stroke=BG, sw=1.5)
        else:
            s.rect(xx + 10, ly - 4, 8, 8, fill=col, stroke=BG, sw=1.5)
        s.text(xx + 36, ly + 4, name, size=11, fill=FG, anchor="start")
    s.path(f"M{lx + 520},{ly} L{lx + 548},{ly}", MUTED, sw=1.2, arrow=False, dash="2 4")
    s.text(lx + 556, ly + 4, "uncompressed", size=11, fill=FG, anchor="start")
    s.render()


if __name__ == "__main__":
    where_to_cut()
    isolation()
    architecture()
    crossscale()
