"""UtopiaOS-themed figures for the MOGIC post.

Reuses the drawing helpers from the GPT-from-scratch post so every diagram on
the site shares one style. Run from this directory:  python3 make_figures.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scratchGPT", "images"))
import make_diagrams as base  # noqa: E402

base.HERE = HERE  # write outputs next to this file
base.POST = "mogic"
from make_diagrams import (Svg, BG, PANEL, LINE, LINE1, FG, MUTED,  # noqa: E402
                           G, GD, Y, C, M, V, O, R)

# chart series colours: in-band steps of the theme's green/gold, validated
# (dark surface #0c1011): CVD dE 9.6, normal dE 17.5, contrast >= 6:1
S_MOGIC, S_ORACLE = "#32a675", "#bf841d"


def vec(s, x, y, cols, cw=13, ch=13):
    for i, col in enumerate(cols):
        s.rect(x + i * cw, y, cw - 1, ch, fill=col, stroke=col, fop=0.45, sop=0.9, rx=2)


def box(s, x, y, w, h, label, color, sub=None, size=12):
    s.rect(x, y, w, h, fill=color, stroke=color, fop=0.10, sop=0.85, rx=7)
    cy = y + h / 2 + (0 if sub else size * 0.35)
    s.text(x + w / 2, cy - (4 if sub else 0), label, size=size, fill=color, weight=700)
    if sub:
        s.text(x + w / 2, cy + 12, sub, size=9.5, fill=MUTED)


def text_input(s, x, y, w, parts):
    """A text input chip: [(text, colour), ...] joined by a ‖ separator."""
    s.rect(x, y, w, 26, fill=PANEL, stroke=LINE, rx=5)
    body = f' <tspan fill="{MUTED}">‖</tspan> '.join(
        f'<tspan fill="{col}">{base.esc(t)}</tspan>' for t, col in parts)
    s.text(x + 10, y + 17, body, size=11, anchor="start", raw=True)


# ─────────────────────────────────────────────────────────────────
# 1. Early vs late fusion
# ─────────────────────────────────────────────────────────────────
def fusion():
    s = Svg(1000, 470, "fusion.svg")
    for x0, title, col in [(30, "early fusion", Y), (515, "late fusion", G)]:
        s.rect(x0, 56, 455, 360, fill=PANEL, stroke=col, sop=0.55, rx=12, dash="7 6", fop=0.5)
        s.text(x0 + 16, 80, title, size=14, fill=col, anchor="start", weight=700)

    # early fusion: metadata pasted into the text
    s.text(46, 104, "metadata is concatenated into the input text", size=11, fill=MUTED, anchor="start")
    text_input(s, 46, 118, 423, [("grass court", FG), ("Tennis terminology", Y), ("Tennis court surfaces", Y)])
    s.line(257, 146, 257, 176, GD)
    s.trapezoid(172, 222, 170, 70, 40, "Transformer", "reads every token", color=Y)
    s.line(257, 258, 257, 280, GD)
    vec(s, 225, 284, [Y, G, C, M, Y])
    s.text(257, 318, "one fused embedding", size=10, fill=MUTED)
    for i, (mark, txt, col) in enumerate([("+", "very accurate with clean metadata", G),
                                          ("−", "long inputs → slow at serving time", R),
                                          ("−", "noisy metadata derails it", R)]):
        s.text(52, 348 + i * 20, f'<tspan fill="{col}" font-weight="700">{mark}</tspan>  {base.esc(txt)}',
               size=11.5, fill=FG, anchor="start", raw=True)

    # late fusion: embeddings blended at the end
    s.text(531, 104, "metadata embeddings are blended in afterwards", size=11, fill=MUTED, anchor="start")
    text_input(s, 531, 118, 110, [("grass court", FG)])
    s.line(586, 146, 586, 172, GD)
    box(s, 546, 176, 80, 40, "encoder", G, size=11)
    s.rect(700, 118, 150, 98, fill=Y, stroke=Y, fop=0.07, sop=0.7, rx=8)
    s.text(775, 138, "memory bank", size=11, fill=Y, weight=700)
    for i, (t, col) in enumerate([("Courts by type", G), ("Landforms", R), ("Grasslands", R)]):
        vec(s, 712, 150 + i * 20, [col] * 3, cw=10, ch=12)
        s.text(746, 160 + i * 20, t, size=10, fill=FG if col == G else MUTED, anchor="start")
    s.line(586, 216, 586, 258, GD)
    s.path("M775,216 L775,240 L660,240 L660,258", Y, sw=1.3)
    box(s, 546, 262, 150, 36, "combiner (cross-attn)", C, size=10.5)
    s.line(621, 298, 621, 312, GD)
    vec(s, 589, 312, [G, C, G, Y, G])
    s.text(621, 340, "enriched embedding", size=10, fill=MUTED)
    for i, (mark, txt, col) in enumerate([("+", "fast: metadata are precomputed vectors", G),
                                          ("+", "robust to noisy retrieved metadata", G),
                                          ("−", "lower accuracy ceiling", R)]):
        s.text(537, 364 + i * 20, f'<tspan fill="{col}" font-weight="700">{mark}</tspan>  {base.esc(txt)}',
               size=11.5, fill=FG, anchor="start", raw=True)

    s.text(500, 448, "MOGIC: train with the left, serve with the right",
           size=14, fill=Y, weight=700, glow=True)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 2. The MOGIC framework (themed redraw of the paper's Figure 1)
# ─────────────────────────────────────────────────────────────────
def framework():
    s = Svg(1000, 600, "mogic_framework.svg")
    # disciple panel
    s.rect(24, 50, 600, 238, fill=PANEL, stroke=G, sop=0.6, rx=12, dash="7 6", fop=0.55)
    s.text(40, 72, "disciple · OAK", size=13, fill=G, anchor="start", weight=700)
    s.text(162, 72, "trained · runs at inference", size=10.5, fill=MUTED, anchor="start")
    text_input(s, 40, 96, 150, [("Query: Gummy candy", FG)])
    text_input(s, 40, 222, 150, [("Label: Jelly bean", FG)])
    box(s, 222, 91, 70, 36, "E_θD", G, size=12)
    box(s, 222, 217, 70, 36, "E_θD", G, size=12)
    s.path("M257,127 L257,217", GD, sw=1.1, arrow=False, dash="3 3")
    s.text(264, 176, "shared", size=9.5, fill=MUTED, anchor="start")
    s.line(190, 109, 218, 109, GD)
    s.line(190, 235, 218, 235, GD)
    # memory bank + retrieved items
    s.rect(350, 60, 112, 44, fill=Y, stroke=Y, fop=0.08, sop=0.8, rx=7)
    s.text(406, 80, "memory bank", size=11, fill=Y, weight=700)
    s.text(406, 95, "metadata vectors", size=9, fill=MUTED)
    s.path("M205,109 L205,82 L346,82", GD)
    for i in range(3):
        vec(s, 476, 60 + i * 15, [[Y, G, C][i], M, [C, Y, G][i]], cw=10, ch=11)
    s.text(509, 58, "m_q", size=9, fill=MUTED, anchor="start")
    s.line(462, 82, 474, 82, Y, arrow=False)
    box(s, 544, 88, 44, 40, "C", C, size=14)
    s.path("M507,82 L524,82 L524,100 L540,100", Y)
    s.line(292, 112, 540, 116, GD)
    # label free parameter
    s.rect(330, 228, 96, 20, fill=V, stroke=V, fop=0.1, sop=0.7, rx=4)
    s.text(378, 242, "+ label params", size=9.5, fill=V)
    s.line(292, 235, 326, 238, GD)

    # oracle panel
    s.rect(24, 312, 600, 208, fill=PANEL, stroke=Y, sop=0.6, rx=12, dash="7 6", fop=0.55)
    s.text(40, 334, "oracle", size=13, fill=Y, anchor="start", weight=700)
    s.text(96, 334, "frozen · training only · sees ground-truth metadata", size=10.5, fill=MUTED, anchor="start")
    text_input(s, 40, 356, 330, [("Gummy candy", FG), ("Gummi candies", Y), ("Candy", Y)])
    text_input(s, 40, 470, 330, [("Jelly bean", FG), ("Gelatin desserts", Y)])
    box(s, 420, 351, 90, 36, "E_θO", Y, size=12)
    box(s, 420, 465, 90, 36, "E_θO", Y, size=12)
    s.line(370, 369, 416, 369, GD)
    s.line(370, 483, 416, 483, GD)
    s.path("M465,387 L465,465", Y, sw=1.1, arrow=False, dash="3 3")
    s.text(472, 430, "shared", size=9.5, fill=MUTED, anchor="start")

    # embedding nodes
    nx = 660
    nodes = {"xq": 102, "zl": 232, "xs": 363, "zs": 477}
    labels = {"xq": ("x_q", G), "zl": ("z_l", G), "xs": ("x*_q", Y), "zs": ("z*_l", Y)}
    for k, y in nodes.items():
        vec(s, nx, y, [G, C, G, Y, M] if k in ("xq", "zl") else [Y, G, C, M, Y])
        t, col = labels[k]
        s.text(nx - 8, y + 11, t, size=12, fill=col, anchor="end", weight=700, italic=True)
    s.line(588, 108, nx - 44, 108, G)
    s.line(430, 238, nx - 44, 238, G)
    s.line(510, 369, nx - 48, 369, Y)
    s.line(510, 483, nx - 48, 483, Y)

    # losses as arcs on the right
    ex = nx + 66
    def arc(y1, y2, off, col, dash=None):
        s.path(f"M{ex},{y1 + 6} C{ex + off},{y1 + 6} {ex + off},{y2 + 6} {ex},{y2 + 6}", col, sw=1.6,
               arrow=False, dash=dash)
    arc(nodes["xq"], nodes["zl"], 44, G)
    arc(nodes["xq"], nodes["xs"], 92, M, dash="6 4")
    arc(nodes["zl"], nodes["zs"], 92, M, dash="6 4")
    arc(nodes["xq"], nodes["zs"], 150, C, dash="2 4")
    arc(nodes["zl"], nodes["xs"], 128, C, dash="2 4")
    lx = 846
    for i, (name, col, dash, l1, l2) in enumerate([
            ("L_disciple", G, None, "triplet: the usual", "task loss"),
            ("L_matching", M, "6 4", "L2: copy the oracle's", "embeddings"),
            ("L_alignment", C, "2 4", "triplet across models:", "rank like the oracle")]):
        y = 150 + i * 120
        s.path(f"M{lx},{y - 4} L{lx + 26},{y - 4}", col, sw=2, arrow=False, dash=dash)
        s.text(lx + 32, y, name, size=12, fill=col, anchor="start", weight=700)
        s.text(lx, y + 18, l1, size=9.5, fill=MUTED, anchor="start")
        s.text(lx, y + 32, l2, size=9.5, fill=MUTED, anchor="start")

    s.text(500, 556, "L = L_disciple + α · L_alignment + β · L_matching",
           size=15, fill=Y, weight=700, glow=True)
    s.text(500, 582, "α = 1.0, β = 0.1 · at inference only the disciple runs, so there is no extra cost",
           size=11.5, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 3. Noise robustness (line chart)
# ─────────────────────────────────────────────────────────────────
def noise():
    s = Svg(1000, 456, "noise_robustness.svg")
    xs = [0, 20, 40, 60]
    series = [("MOGIC(OAK)", S_MOGIC, [36.94, 36.26, 35.62, 34.92], None, "circle"),
              ("Oracle", S_ORACLE, [47.63, 34.80, 26.75, 18.65], "7 5", "square")]
    x0, x1, y0, y1 = 110, 760, 360, 80   # plot box (y0 = bottom)
    vmin, vmax = 10, 50
    px = lambda v: x0 + (v - 0) / 60 * (x1 - x0)
    py = lambda v: y0 - (v - vmin) / (vmax - vmin) * (y0 - y1)
    s.text(40, 64, "P@1 on LF-WikiSeeAlsoTitles-320K as ground-truth metadata is corrupted",
           size=13, fill=FG, anchor="start", weight=700)
    for v in range(10, 51, 10):
        s.line(x0, py(v), x1, py(v), LINE1, sw=1, arrow=False)
        s.text(x0 - 12, py(v) + 4, str(v), size=11, fill=MUTED, anchor="end")
    s.line(x0, y0, x1, y0, LINE, sw=1.2, arrow=False)
    for x in xs:
        s.text(px(x), y0 + 22, f"{x}%", size=11, fill=MUTED)
    s.text((x0 + x1) / 2, y0 + 46, "metadata items replaced with irrelevant ones", size=11, fill=MUTED)
    s.add(f'<text x="0" y="0" font-size="11" fill="{MUTED}" text-anchor="middle" '
          f'transform="translate(56,{(y0 + y1) / 2}) rotate(-90)">P@1</text>')
    for name, col, vals, dash, marker in series:
        d = " ".join(("M" if i == 0 else "L") + f"{px(x):.1f},{py(v):.1f}" for i, (x, v) in enumerate(zip(xs, vals)))
        s.path(d, col, sw=2, arrow=False, dash=dash)
        for x, v in zip(xs, vals):
            if marker == "circle":
                s.circle(px(x), py(v), 5, fill=col, stroke=BG, sw=2)
            else:
                s.rect(px(x) - 5, py(v) - 5, 10, 10, fill=col, stroke=BG, sw=2)
        # selective labels: first and last value only
        s.text(px(0) + 12, py(vals[0]) - 10, f"{vals[0]:.2f}", size=11, fill=FG, anchor="start")
        s.text(px(60) + 12, py(vals[-1]) + 4, f"{vals[-1]:.2f}", size=11, fill=FG, anchor="start")
        s.text(px(60) + 62, py(vals[-1]) + 4, name, size=12, fill=FG, anchor="start", weight=700)
    # legend
    lx, ly = 800, 120
    for i, (name, col, _, dash, marker) in enumerate(series):
        yy = ly + i * 24
        s.path(f"M{lx},{yy} L{lx + 30},{yy}", col, sw=2, arrow=False, dash=dash)
        if marker == "circle":
            s.circle(lx + 15, yy, 4.5, fill=col, stroke=BG, sw=1.5)
        else:
            s.rect(lx + 10.5, yy - 4.5, 9, 9, fill=col, stroke=BG, sw=1.5)
        s.text(lx + 40, yy + 4, name, size=11.5, fill=FG, anchor="start")
    s.text(500, 440, "the oracle loses 29 points; MOGIC(OAK) loses 2", size=12, fill=FG)
    s.render()


if __name__ == "__main__":
    fusion()
    framework()
    noise()
