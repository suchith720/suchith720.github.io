"""Generate the UtopiaOS-themed diagrams for the "GPT from scratch" post.

Run from this directory:  python3 make_diagrams.py
Writes the *.svg diagrams (and thumbnail.svg) next to this file.
The post uses a PNG thumbnail (for social cards):
    rsvg-convert -w 1600 -h 1000 thumbnail.svg -o thumbnail.png && rm thumbnail.svg
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ── palette (matches assets/utopia.scss) ──────────────────────────
BG, PANEL, LINE1, LINE = "#0c1011", "#121819", "#1d2729", "#2a3739"
FG, MUTED = "#d3ddd8", "#7f8e89"
G, GD, Y, C, M, V, O, R = ("#3dff9a", "#1f9b5c", "#f5c542", "#5ad7ff",
                           "#ff7edb", "#a78bfa", "#ff9f5a", "#ff5f56")
EMB = [O, Y, G]  # colours of the embedding dimensions
FONT = "'JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"
TOK_IN = list("accou")
TOK_OUT = list("ccoun")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, w, h, filename, titlebar=True):
        self.w, self.h, self.filename, self.titlebar = w, h, filename, titlebar
        self.els = []

    def add(self, s):
        self.els.append(s)

    # primitives
    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.2, rx=0,
             fop=1.0, sop=1.0, dash=None, glow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        f = ' filter="url(#glow)"' if glow else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                 f'fill="{fill}" fill-opacity="{fop}" stroke="{stroke}" stroke-opacity="{sop}" '
                 f'stroke-width="{sw}"{d}{f}/>')

    def text(self, x, y, t, size=13, fill=FG, anchor="middle", weight=400,
             italic=False, op=1.0, glow=False, raw=False):
        st = ' font-style="italic"' if italic else ""
        f = ' filter="url(#glow)"' if glow else ""
        body = t if raw else esc(t)
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}" font-weight="{weight}" fill-opacity="{op}"{st}{f}>{body}</text>')

    def line(self, x1, y1, x2, y2, color=GD, sw=1.4, dash=None, arrow=True, op=1.0):
        self.path(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}", color, sw, dash, arrow, op)

    def path(self, d, color=GD, sw=1.4, dash=None, arrow=True, op=1.0, fill="none"):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mk = f' marker-end="url(#a{color[1:]})"' if arrow else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" '
                 f'stroke-opacity="{op}" stroke-linecap="round" stroke-linejoin="round"{da}{mk}/>')

    def circle(self, cx, cy, r, fill=BG, stroke=G, sw=1.4, glow=False):
        f = ' filter="url(#glow)"' if glow else ""
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{f}/>')

    def grid(self, x, y, rows, cols, cw, ch, color, fop=0.22, text=None, tsize=9, tcolor=FG):
        """color(r, c) -> colour or None; fop may be a float or f(r, c)."""
        for r in range(rows):
            for c in range(cols):
                col = color(r, c)
                if col is None:
                    continue
                op = fop(r, c) if callable(fop) else fop
                self.rect(x + c * cw, y + r * ch, cw, ch, fill=col, stroke=col, fop=op, sop=0.85, sw=1.1)
                if text:
                    t = text(r, c)
                    if t:
                        self.text(x + c * cw + cw / 2, y + r * ch + ch / 2 + tsize * 0.35, t,
                                  size=tsize, fill=tcolor if col != R else R)

    def pill(self, cx, cy, w, h, label, color, size=12, fop=0.12, sub=None):
        self.rect(cx - w / 2, cy - h / 2, w, h, fill=color, stroke=color, fop=fop, sop=0.9, rx=h / 2 if h < 34 else 8)
        if sub:
            self.text(cx, cy - 2, label, size=size, fill=color, weight=600)
            self.text(cx, cy + size, sub, size=size - 2, fill=MUTED)
        else:
            self.text(cx, cy + size * 0.35, label, size=size, fill=color, weight=600)

    def trapezoid(self, x, y_mid, w, h_left, h_right, label, sub, color=GD):
        pts = [(x, y_mid - h_left / 2), (x + w, y_mid - h_right / 2),
               (x + w, y_mid + h_right / 2), (x, y_mid + h_left / 2)]
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts) + " Z"
        self.add(f'<path d="{d}" fill="{PANEL}" stroke="{color}" stroke-width="1.4"/>')
        self.text(x + w / 2, y_mid - 2, label, size=13, fill=G, weight=700)
        self.text(x + w / 2, y_mid + 14, sub, size=10, fill=MUTED)

    def token(self, x, y, ch, color=FG, w=26, stroke=LINE, glow=False):
        self.rect(x, y, w, w, fill=PANEL, stroke=stroke, rx=4, glow=glow)
        self.text(x + w / 2, y + w / 2 + 5, ch, size=14, fill=color, weight=600)

    def render(self):
        markers = "".join(
            f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            for c in (G, GD, Y, C, M, V, O, R, MUTED, FG))
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" font-family="{FONT}" xml:space="preserve">'
                f'<defs>{markers}'
                '<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
                '<feGaussianBlur stdDeviation="2.4" result="b"/>'
                '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
                f'<pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">'
                f'<circle cx="1" cy="1" r="1" fill="{LINE1}"/></pattern></defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>'
                f'<rect width="{self.w}" height="{self.h}" fill="url(#dots)"/>')
        bar = ""
        if self.titlebar:
            bar = (f'<rect width="{self.w}" height="34" fill="{PANEL}"/>'
                   f'<line x1="0" y1="34" x2="{self.w}" y2="34" stroke="{LINE1}"/>'
                   f'<circle cx="20" cy="17" r="5.5" fill="{R}"/><circle cx="38" cy="17" r="5.5" fill="#ffbd2e"/>'
                   f'<circle cx="56" cy="17" r="5.5" fill="#27c93f"/>'
                   f'<text x="{self.w / 2}" y="21.5" font-size="12" fill="{MUTED}" text-anchor="middle">'
                   f'~/workshop/scratchGPT/{esc(self.filename)}</text>')
        svg = head + bar + "".join(self.els) + "</svg>\n"
        with open(os.path.join(HERE, self.filename), "w") as f:
            f.write(svg)
        print("wrote", self.filename)


def caption(s, x, y, t):
    s.text(x, y, t, size=11, fill=MUTED)


def name(s, x, y, t, color=Y):
    s.text(x, y, t, size=14, fill=color, weight=700, italic=True)


# ─────────────────────────────────────────────────────────────────
# 0. Bigram model: a lookup table of next-character logits
# ─────────────────────────────────────────────────────────────────
def bigram():
    s = Svg(1000, 500, "bigram.svg")
    sentence = "We are accounted poor citizens"
    cur, nxt = 3, 4  # the "a" and "r" of "are"
    tx0, tw = 170, 22
    s.text(tx0 - 14, 81, "input ›", size=12, fill=MUTED, anchor="end")
    for i, ch in enumerate(sentence):
        x = tx0 + i * tw
        if ch == " ":
            s.rect(x, 64, tw - 3, 22, fill=LINE1, rx=3, fop=0.6)
            continue
        col, stroke = (C, C) if i == cur else ((Y, Y) if i == nxt else (FG, LINE))
        s.rect(x, 64, tw - 3, 22, fill=PANEL, stroke=stroke, rx=3, glow=i in (cur, nxt))
        s.text(x + (tw - 3) / 2, 80, ch, size=13, fill=col, weight=700 if i in (cur, nxt) else 400)
    ax, rx_ = tx0 + cur * tw + 9.5, tx0 + nxt * tw + 9.5
    s.text(ax - 4, 108, "current", size=10, fill=C, anchor="end")

    vocab = list("eaorw")
    # the table
    tx, ty, cw = 130, 150, 40
    for j, ch in enumerate(vocab):
        s.text(tx + j * cw + 20, ty - 8, ch, size=12, fill=Y if ch == "r" else MUTED, weight=700 if ch == "r" else 400)
        s.text(tx - 16, ty + j * cw + 25, ch, size=12, fill=C if ch == "a" else MUTED, weight=700 if ch == "a" else 400)
    base = [[.3, .5, .2, .6, .4], [0, 0, 0, 0, 0], [.5, .2, .4, .7, .3], [.6, .4, .2, .3, .5], [.2, .6, .5, .1, .4]]
    s.grid(tx, ty, 5, 5, cw, cw, lambda r, c: C if r == 1 else G,
           fop=lambda r, c: 0.45 if r == 1 else 0.05 + 0.18 * base[r][c])
    s.rect(tx, ty + cw, 5 * cw, cw, stroke=C, sw=2, glow=True)
    s.text(tx + 100, ty + 226, "token_embedding_table", size=12, fill=G, weight=700)
    s.text(tx + 100, ty + 243, "(vocab × vocab)", size=11, fill=MUTED)
    # lookup: current char -> its row
    s.path(f"M{ax},90 L{ax},118 L96,118 L96,{ty + cw + 20} L{tx - 26},{ty + cw + 20}", C, dash="5 4")

    # the row = logits
    logits = [1.2, -0.3, 0.4, 2.1, -1.0]
    lx, ly = 430, ty + cw
    s.line(tx + 5 * cw + 8, ly + 20, lx - 10, ly + 20, C)
    s.text((tx + 5 * cw + lx) / 2, ly + 8, "row 'a'", size=11, fill=C)
    for j, ch in enumerate(vocab):
        s.text(lx + j * cw + 20, ly - 8, ch, size=12, fill=Y if ch == "r" else MUTED, weight=700 if ch == "r" else 400)
    s.grid(lx, ly, 1, 5, cw, cw, lambda r, c: Y if c == 3 else C,
           fop=lambda r, c: 0.12 + 0.12 * (logits[c] + 1.0), text=lambda r, c: f"{logits[c]:+.1f}", tsize=10)
    s.text(lx + 100, ly + 62, "logits", size=12, fill=C, weight=700)
    s.text(lx + 100, ly + 78, "unnormalised log-probs", size=10, fill=MUTED)

    # softmax -> probabilities
    ex = [math.exp(v) for v in logits]
    probs = [e / sum(ex) for e in ex]
    s.line(lx + 5 * cw + 8, ly + 20, 700, ly + 20, G)
    s.text(670, ly + 8, "softmax", size=11, fill=G)
    bx, basey, bw = 712, 350, 36
    s.text(bx, 150, "p( next char | 'a' )", size=12, fill=FG, anchor="start")
    s.line(bx - 8, basey, bx + 5 * 48, basey, LINE, arrow=False)
    for j, (ch, p) in enumerate(zip(vocab, probs)):
        x = bx + j * 48
        h = p * 250
        col = Y if ch == "r" else C
        s.rect(x, basey - h, bw, h, fill=col, stroke=col, fop=0.6 if ch == "r" else 0.22, sop=0.9, glow=ch == "r")
        s.text(x + bw / 2, basey - h - 6, f"{p:.2f}".lstrip("0"), size=9, fill=col)
        s.text(x + bw / 2, basey + 18, ch, size=12, fill=col if ch == "r" else MUTED, weight=700 if ch == "r" else 400)
    # target: the actual next char
    rbar = bx + 3 * 48 + bw / 2
    s.path(f"M{rx_},90 L{rx_},104 L{rbar},104 L{rbar},{basey - probs[3] * 250 - 22}", Y, dash="5 4")
    s.text(rx_ + 8, 100, "target", size=10, fill=Y, anchor="start")

    loss = -math.log(probs[3])
    s.text(500, 432, f"loss = −log p( 'r' | 'a' ) = −log {probs[3]:.2f} ≈ {loss:.2f}", size=15,
           fill=Y, weight=700, glow=True)
    s.text(500, 462, "the bigram model predicts the next character from the current one alone",
           size=12, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 1. Masked self-attention (one head)
# ─────────────────────────────────────────────────────────────────
def masked_attention():
    s = Svg(1000, 540, "masked_attention.svg")
    s.text(40, 72, '<tspan fill="%s">input ›</tspan> <tspan fill="%s">"We are </tspan>'
           '<tspan fill="%s" font-weight="700" text-decoration="underline">accou</tspan>'
           '<tspan fill="%s">nted poor citizens"</tspan>' % (MUTED, FG, G, FG), size=15, anchor="start", raw=True)
    s.text(960, 72, "context window  T = 5", size=12, fill=MUTED, anchor="end")

    cy, cw = 290, 18
    # X
    xx, xy = 70, cy - 45
    name(s, xx + 27, xy - 12, "X")
    s.grid(xx, xy, 5, 3, cw, cw, lambda r, c: EMB[c])
    for i, t in enumerate(TOK_IN):
        s.text(xx - 12, xy + i * cw + 13, t, size=12, fill=MUTED)
    caption(s, xx + 27, xy + 112, "embeddings")

    # Q, K, V projections
    proj = [("Q", "X·Wq", C, 130), ("K", "X·Wk", M, 245), ("V", "X·Wv", V, 360)]
    px = 210
    for nm, formula, col, y in proj:
        s.path(f"M{xx + 58},{cy} C{xx + 100},{cy} {px - 50},{y + 45} {px - 8},{y + 45}", GD)
        s.grid(px, y, 5, 2, cw, cw, lambda r, c, col=col: col, fop=lambda r, c: 0.18 + 0.1 * c)
        s.text(px + 44, y + 12, nm, size=14, fill=col, weight=700, anchor="start", italic=True)
        s.text(px + 44, y + 28, formula, size=10, fill=MUTED, anchor="start")

    # scores
    big = 26
    sx, sy = 330, cy - 65
    name(s, sx + 65, sy - 26, "Q·Kᵀ / √d", C)
    for j, t in enumerate(TOK_IN):
        s.text(sx + j * big + 13, sy - 6, t, size=11, fill=MUTED)
    for i, t in enumerate(TOK_IN):
        s.text(sx - 10, sy + i * big + 17, t, size=11, fill=MUTED)
    vals = [[.30, .55, .20, .70, .45], [.62, .25, .80, .35, .50], [.40, .75, .55, .20, .65],
            [.25, .45, .60, .85, .30], [.50, .35, .70, .40, .60]]
    s.grid(sx, sy, 5, 5, big, big, lambda r, c: C, fop=lambda r, c: 0.08 + 0.35 * vals[r][c])
    caption(s, sx + 65, sy + 150, "scores (T×T)")
    s.path(f"M{px + 38},{175} C{px + 80},{175} {sx - 50},{cy - 20} {sx - 22},{cy - 20}", C)
    s.path(f"M{px + 38},{290} C{px + 70},{290} {sx - 50},{cy + 15} {sx - 22},{cy + 15}", M)

    # masked
    mx = 530
    name(s, mx + 65, sy - 26, "masked_fill", R)
    s.grid(mx, sy, 5, 5, big, big, lambda r, c: C if c <= r else R,
           fop=lambda r, c: (0.08 + 0.35 * vals[r][c]) if c <= r else 0.10,
           text=lambda r, c: None if c <= r else "−∞", tsize=9)
    caption(s, mx + 65, sy + 150, "causal mask")
    s.line(sx + 136, cy, mx - 8, cy, R)
    # mini tril icon over the arrow
    for i in range(4):
        for j in range(i + 1):
            s.rect(sx + 150 + j * 7, cy - 42 + i * 7, 6, 6, fill=G, fop=0.7)
    s.text(sx + 164, cy - 50, "tril", size=10, fill=MUTED)

    # softmax weights
    wx = 730
    W = [[1.00], [.62, .38], [.21, .45, .34], [.15, .20, .30, .35], [.09, .31, .12, .22, .26]]
    name(s, wx + 65, sy - 26, "softmax", G)
    s.grid(wx, sy, 5, 5, big, big, lambda r, c: G if c <= r else LINE,
           fop=lambda r, c: (0.10 + 0.55 * W[r][c]) if c <= r else 0.25,
           text=lambda r, c: (f"{W[r][c]:.2f}".lstrip("0") if W[r][c] < 1 else "1") if c <= r else "0",
           tsize=8.5)
    caption(s, wx + 65, sy + 150, "attention weights")
    s.line(mx + 136, cy, wx - 8, cy, G)

    # @ V -> output
    ax = 900
    s.circle(ax, cy, 13, stroke=Y, glow=True)
    s.text(ax, cy + 5, "@", size=14, fill=Y, weight=700)
    s.line(wx + 136, cy, ax - 15, cy, Y)
    s.path(f"M{px + 38},{405} L{ax},{405} L{ax},{cy + 16}", V, dash="5 4")
    s.text(ax - 170, 398, "V", size=12, fill=V, weight=700, italic=True)
    ox = ax - 18
    s.grid(ox, 110, 5, 2, cw, cw, lambda r, c: [M, V][c], fop=lambda r, c: 0.25 + 0.1 * c)
    s.line(ax, cy - 15, ax, 110 + 94, Y)
    s.text(ox - 10, 124, "out", size=13, fill=Y, weight=700, anchor="end", italic=True)

    s.text(500, 470, "out = softmax( mask( Q·Kᵀ / √d ) ) · V", size=16, fill=Y, weight=700, glow=True)
    s.text(500, 500, "each character can only look at itself and the characters before it",
           size=12, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 2. Multi-head attention
# ─────────────────────────────────────────────────────────────────
def multi_head():
    s = Svg(1000, 480, "multi_head_attention.svg")
    cy, cw = 255, 18
    xx = 40
    s.grid(xx, cy - 27, 3, 5, cw, cw, lambda r, c: EMB[r])
    for j, t in enumerate(TOK_IN):
        s.text(xx + j * cw + 9, cy - 34, t, size=11, fill=MUTED)
    name(s, xx + 45, cy - 52, "X")
    caption(s, xx + 45, cy + 48, "embeddings")

    heads = [(C, 95), (M, 210), (Y, 325)]
    for k, (col, top) in enumerate(heads):
        hx, hw, hh = 190, 260, 100
        hc = top + hh / 2
        s.path(f"M{xx + 96},{cy} C{xx + 130},{cy} {hx - 40},{hc} {hx - 6},{hc}", GD)
        s.rect(hx, top, hw, hh, fill=PANEL, stroke=col, sop=0.6, rx=8)
        s.text(hx + 12, top + 18, f"head {k + 1}", size=11, fill=col, anchor="start", weight=700)
        s.grid(hx + 16, top + 28, 5, 5, 12, 12, lambda r, c, col=col: col if c <= r else LINE,
               fop=lambda r, c: 0.45 if c <= r else 0.3)
        s.text(hx + 108, top + 62, "→", size=16, fill=MUTED)
        s.grid(hx + 150, top + 32, 2, 5, cw, cw, lambda r, c, col=col: col, fop=lambda r, c: 0.18 + 0.14 * r)
        s.text(hx + 196, top + 88, "softmax(QKᵀ)V", size=9, fill=MUTED)
        # to concat
        s.path(f"M{hx + hw},{hc} C{hx + hw + 40},{hc} {560 - 50},{201 + 36 * k + 18} {556},{201 + 36 * k + 18}", col)

    # concat
    cx0 = 560
    rows = [C, C, M, M, Y, Y]
    s.grid(cx0, 201, 6, 5, cw, cw, lambda r, c: rows[r], fop=lambda r, c: 0.18 + 0.14 * (r % 2))
    name(s, cx0 + 45, 190, "concat", FG)
    caption(s, cx0 + 45, 330, "(T × n_heads·h)")

    s.trapezoid(680, cy, 100, 108, 54, "Linear", "proj")
    s.line(cx0 + 94, cy, 676, cy, GD)

    ox = 810
    s.grid(ox, cy - 27, 3, 5, cw, cw, lambda r, c: G, fop=lambda r, c: 0.15 + 0.12 * r)
    s.line(784, cy, ox - 6, cy, G)
    name(s, ox + 45, cy - 40, "out", G)
    caption(s, ox + 45, cy + 48, "(T × C)")

    s.text(500, 455, "several heads attend in parallel, each noticing different patterns — then one projection fuses them",
           size=12, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 3. Feed-forward
# ─────────────────────────────────────────────────────────────────
def feedforward():
    s = Svg(1000, 370, "feedforward.svg")
    cy, cw = 205, 18
    ox = 105
    s.grid(ox, cy - 27, 3, 5, cw, cw, lambda r, c: EMB[r])
    for j, t in enumerate(TOK_IN):
        s.text(ox + j * cw + 9, cy - 34, t, size=11, fill=MUTED)
    caption(s, ox + 45, 345, "x  (C)")

    s.trapezoid(ox + 115, cy, 90, 54, 216, "Linear", "C → 4C")
    s.line(ox + 94, cy, ox + 111, cy, GD, arrow=False)

    hx = ox + 225
    hid = [C, V, M]
    s.grid(hx, cy - 108, 12, 5, cw, cw, lambda r, c: hid[r % 3], fop=lambda r, c: 0.14 + 0.03 * ((r * 7 + c * 3) % 5))
    caption(s, hx + 45, 345, "hidden (4C)")

    s.pill(hx + 150, cy, 70, 28, "ReLU", Y)
    s.line(hx + 94, cy, hx + 112, cy, GD)
    s.trapezoid(hx + 205, cy, 90, 216, 54, "Linear", "4C → C")
    s.line(hx + 186, cy, hx + 201, cy, GD)
    s.pill(hx + 350, cy, 88, 28, "Dropout", V)
    s.line(hx + 296, cy, hx + 304, cy, GD, arrow=False)
    s.line(hx + 296, cy, hx + 303, cy, GD)

    fx = hx + 420
    s.grid(fx, cy - 27, 3, 5, cw, cw, lambda r, c: G, fop=lambda r, c: 0.15 + 0.12 * r)
    s.line(hx + 395, cy, fx - 6, cy, G)
    caption(s, fx + 45, 345, "out  (C)")
    s.text(500, 66, "the same small MLP is applied to every position independently", size=12, fill=MUTED)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 4. Transformer block (pre-norm, residual)
# ─────────────────────────────────────────────────────────────────
def block():
    s = Svg(1000, 640, "block.svg")
    cx, cw = 500, 18
    # frame
    s.rect(320, 140, 360, 380, fill=PANEL, stroke=GD, rx=16, dash="7 6", fop=0.6)
    s.text(664, 162, "Block", size=12, fill=G, anchor="end", weight=700)
    s.text(698, 330, "× n_layers", size=13, fill=Y, anchor="start", weight=700)
    s.path("M690,150 L690,510", MUTED, sw=1, arrow=False, dash="2 4")

    # input / output grids
    s.grid(cx - 45, 545, 3, 5, cw, cw, lambda r, c: EMB[r])
    caption(s, cx, 620, "x  (T × C)")
    s.grid(cx - 45, 64, 3, 5, cw, cw, lambda r, c: G, fop=lambda r, c: 0.15 + 0.12 * r)
    caption(s, cx + 90, 95, "out")

    # trunk (bottom → top)
    s.line(cx, 545, cx, 480, GD, arrow=False)
    s.circle(cx, 500, 3.5, fill=GD, stroke=GD)
    s.pill(cx, 466, 150, 26, "LayerNorm", V, size=11)
    s.line(cx, 479, cx, 479, GD, arrow=False)
    s.line(cx, 453, cx, 434, GD)
    s.pill(cx, 395, 220, 72, "Masked Multi-Head", C, size=13, sub="Attention (causal)")
    s.line(cx, 359, cx, 345, C)
    s.circle(cx, 332, 12, stroke=G, glow=True)
    s.text(cx, 337, "+", size=16, fill=G, weight=700)
    s.circle(cx, 305, 3.5, fill=GD, stroke=GD)
    s.line(cx, 320, cx, 290, GD)
    s.pill(cx, 276, 150, 26, "LayerNorm", V, size=11)
    s.line(cx, 263, cx, 246, GD)
    s.pill(cx, 212, 220, 64, "Feed-Forward", M, size=13, sub="MLP")
    s.line(cx, 180, cx, 172, M)
    s.circle(cx, 160, 12, stroke=G, glow=True)
    s.text(cx, 165, "+", size=16, fill=G, weight=700)
    s.line(cx, 148, cx, 124, G)

    # residual skips
    s.path(f"M{cx},500 L356,500 L356,332 L{cx - 14},332", GD, dash="5 4")
    s.path(f"M{cx},305 L356,305 L356,160 L{cx - 14},160", GD, dash="5 4")
    s.add(f'<text x="0" y="0" font-size="10" fill="{MUTED}" text-anchor="middle" transform="translate(348,420) rotate(-90)">residual</text>')
    s.add(f'<text x="0" y="0" font-size="10" fill="{MUTED}" text-anchor="middle" transform="translate(348,235) rotate(-90)">residual</text>')

    # code + annotations
    s.text(80, 336, "x = x + self.sa(self.ln1(x))", size=12, fill=Y, anchor="start")
    s.text(80, 164, "x = x + self.ff(self.ln2(x))", size=12, fill=Y, anchor="start")
    s.text(720, 390, "communication:", size=12, fill=C, anchor="start", weight=700)
    s.text(720, 408, "tokens exchange information", size=11, fill=MUTED, anchor="start")
    s.text(720, 208, "computation:", size=12, fill=M, anchor="start", weight=700)
    s.text(720, 226, "each token processes it alone", size=11, fill=MUTED, anchor="start")
    s.render()


# ─────────────────────────────────────────────────────────────────
# 5. Full GPT architecture
# ─────────────────────────────────────────────────────────────────
def architecture():
    s = Svg(1000, 690, "gpt_architecture.svg")
    cx = 440
    # tokens
    for i, t in enumerate(TOK_IN):
        s.token(cx - 105 + i * 42, 620, t)
    s.text(cx + 120, 638, "idx  (B, T)", size=11, fill=MUTED, anchor="start")

    s.pill(cx - 95, 572, 170, 34, "token_embedding", G, size=11)
    s.pill(cx + 95, 572, 170, 34, "position_embedding", Y, size=11)
    s.line(cx - 95, 616, cx - 95, 591, GD)
    s.path(f"M{cx + 95},616 L{cx + 95},591", Y, dash="3 3")
    s.text(cx + 190, 612, "0 1 2 3 4", size=10, fill=MUTED, anchor="start")
    s.path(f"M{cx - 95},555 L{cx - 95},528 L{cx - 14},528", GD)
    s.path(f"M{cx + 95},555 L{cx + 95},528 L{cx + 14},528", Y)
    s.circle(cx, 528, 12, stroke=G, glow=True)
    s.text(cx, 533, "+", size=16, fill=G, weight=700)
    s.text(cx + 190, 532, "(B, T, 384)", size=11, fill=MUTED, anchor="start")

    # decoder stack
    top, bot = 170, 505
    s.rect(cx - 170, top, 340, bot - top, fill=PANEL, stroke=GD, rx=16, dash="7 6", fop=0.6)
    s.text(cx - 156, top + 20, "decoder", size=12, fill=G, anchor="start", weight=700)
    s.line(cx, 516, cx, 486, GD)
    cols = [C, M, Y, V, O, G]
    for k in range(6):
        y = 452 - k * 46
        s.rect(cx - 140, y, 280, 30, fill=cols[k], stroke=cols[k], fop=0.12, sop=0.8, rx=6)
        s.text(cx, y + 20, f"Block {k + 1}  ·  MHA + FFN", size=12, fill=cols[k], weight=600)
        if k < 5:
            s.line(cx, y, cx, y - 14, GD)
    s.text(cx + 190, 340, "× 6  (n_layers)", size=12, fill=Y, anchor="start", weight=700)
    s.text(cx + 190, 358, "(B, T, 384)", size=11, fill=MUTED, anchor="start")

    s.line(cx, 222, cx, 146, GD)
    s.pill(cx, 133, 150, 26, "LayerNorm", V, size=11)
    s.line(cx, 120, cx, 102, GD)
    s.pill(cx, 88, 170, 28, "Linear  lm_head", G, size=11)
    s.line(cx, 74, cx, 60, G)
    s.text(cx, 52, "logits → softmax → p(next char)", size=13, fill=Y, weight=700, glow=True)
    s.text(cx + 190, 92, "(B, T, 65)", size=11, fill=MUTED, anchor="start")

    # hyper-parameter panel
    px, py = 790, 420
    s.rect(px - 16, py - 30, 200, 150, fill=PANEL, stroke=LINE, rx=8)
    s.text(px, py - 10, "# hyperparameters", size=11, fill=MUTED, anchor="start")
    for i, (k, v) in enumerate([("n_embed", "384"), ("n_heads", "6"), ("n_layers", "6"),
                                ("dropout", "0.2"), ("vocab", "65")]):
        s.text(px, py + 14 + i * 20, f'<tspan fill="{C}">{k:<9}</tspan><tspan fill="{MUTED}">= </tspan>'
               f'<tspan fill="{Y}">{v}</tspan>', size=12, anchor="start", raw=True)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 6. Training: next-character prediction + cross-entropy
# ─────────────────────────────────────────────────────────────────
def training():
    s = Svg(1000, 540, "training.svg")
    x0, step = 100, 46
    xs = [x0 + i * step + 13 for i in range(5)]
    # targets
    for i, t in enumerate(TOK_OUT):
        s.token(xs[i] - 13, 68, t, color=Y, stroke=Y if i == 4 else LINE, glow=(i == 4))
    s.text(x0 - 20, 86, "targets", size=11, fill=Y, anchor="end")
    # decoder
    s.rect(x0 - 20, 130, 5 * step + 22, 280, fill=PANEL, stroke=GD, rx=14, dash="7 6", fop=0.6)
    s.text(x0 + 5 * step - 6, 150, "GPT", size=12, fill=G, anchor="end", weight=700)
    for k, col in enumerate([C, M, Y]):
        s.rect(x0 - 6, 350 - k * 80, 5 * step - 6, 22, fill=col, stroke=col, fop=0.10, sop=0.6, rx=5)
        s.text(x0 + 5 * step / 2 - 16, 365 - k * 80, "Block", size=10, fill=col)
    # causal wiring
    for j in range(5):
        for i in range(j + 1):
            s.path(f"M{xs[i]},425 C{xs[i]},300 {xs[j]},260 {xs[j]},104", GD if i != j else G,
                   sw=1 if i != j else 1.4, arrow=(i == j), op=0.45 if i != j else 1)
    # inputs
    for i, t in enumerate(TOK_IN):
        s.token(xs[i] - 13, 428, t)
    s.text(x0 - 20, 446, "inputs", size=11, fill=MUTED, anchor="end")
    s.text(x0 + 100, 490, "targets = inputs shifted left by one", size=11, fill=MUTED)

    # distribution for the last position
    s.path(f"M{xs[4] + 16},81 C{xs[4] + 110},81 {440},110 {462},128", Y, dash="5 4")
    s.text(470, 140, "position 5 · context \"accou\" → predict next char", size=12, fill=FG, anchor="start")
    vocab = list("abcde") + ["…"] + list("lmnop") + ["…"] + ["u"]
    probs = [.03, .01, .02, .01, .05, None, .04, .06, .62, .02, .01, None, .03]
    bx, base, bw = 480, 350, 30
    s.line(bx - 10, base, bx + len(vocab) * 34, base, LINE, arrow=False)
    for i, (ch, p) in enumerate(zip(vocab, probs)):
        x = bx + i * 34
        if p is None:
            s.text(x + bw / 2, base - 8, "…", size=13, fill=MUTED)
        else:
            h = max(3, p * 250)
            col = Y if ch == "n" else C
            s.rect(x, base - h, bw, h, fill=col, stroke=col, fop=0.6 if ch == "n" else 0.25, sop=0.9,
                   glow=(ch == "n"))
            if p >= .04:
                s.text(x + bw / 2, base - h - 6, f"{p:.2f}".lstrip("0"), size=9, fill=col)
        s.text(x + bw / 2, base + 18, ch, size=12, fill=Y if ch == "n" else MUTED, weight=700 if ch == "n" else 400)
    s.text(bx, base + 44, "softmax over the 65-char vocabulary", size=11, fill=MUTED, anchor="start")

    s.text(480, 440, "loss = −log p( 'n' | 'accou' ) = −log 0.62 ≈ 0.48", size=15, fill=Y,
           anchor="start", weight=700, glow=True)
    s.text(480, 468, "averaged over every position in the batch → F.cross_entropy", size=12,
           fill=MUTED, anchor="start")
    s.render()


# ─────────────────────────────────────────────────────────────────
# 7. Autoregressive decoding
# ─────────────────────────────────────────────────────────────────
def decoding():
    s = Svg(1000, 490, "decoding.svg")
    steps = [("a", "c"), ("ac", "c"), ("acc", "o"), (None, None), ("accou", "n")]
    x = 40
    prev_pred = None
    for k, (ctx, pred) in enumerate(steps):
        if ctx is None:
            s.text(x + 22, 250, "· · ·", size=20, fill=MUTED)
            x += 60
            prev_pred = None
            continue
        pw = 170
        s.text(x + pw / 2, 58, f"step {k + 1 if k < 3 else len(ctx)}", size=11, fill=MUTED)
        s.rect(x, 110, pw, 230, fill=PANEL, stroke=GD, rx=12, dash="6 5", fop=0.6)
        for b, col in enumerate([C, M, Y]):
            s.rect(x + 12, 290 - b * 62, pw - 24, 16, fill=col, stroke=col, fop=0.08, sop=0.45, rx=4)
        n = len(ctx)
        gap = min(30, (pw - 20) / max(n, 1))
        tx = [x + pw / 2 - (n - 1) * gap / 2 + i * gap for i in range(n)]
        last = tx[-1]
        for i, ch in enumerate(ctx):
            new = (i == n - 1 and k > 0)
            s.token(tx[i] - 11, 355, ch, w=22, color=Y if new else FG, stroke=Y if new else LINE)
            s.path(f"M{tx[i]},352 C{tx[i]},260 {last},220 {last},96", G if i == n - 1 else GD,
                   sw=1.4 if i == n - 1 else 1, arrow=(i == n - 1), op=1 if i == n - 1 else 0.45)
        s.token(last - 13, 66, pred, color=Y, stroke=Y, glow=True)
        s.text(x + pw / 2, 428, f'"{ctx}" → "{pred}"', size=12, fill=FG)
        if prev_pred:
            px, py = prev_pred
            gx = x - 15
            s.path(f"M{px + 14},{py} L{gx},{py} L{gx},{396} L{last},{396} L{last},{381}",
                   Y, dash="4 4", sw=1.2, op=0.85)
        prev_pred = (last, 79)
        x += pw + 30
    s.text(500, 466, "predict → sample → append → repeat   (until max_new_tokens)", size=13, fill=Y, weight=700)
    s.render()


# ─────────────────────────────────────────────────────────────────
# 8. Thumbnail / social card
# ─────────────────────────────────────────────────────────────────
def thumbnail():
    s = Svg(800, 500, "thumbnail.svg", titlebar=False)
    s.add(f'<rect width="800" height="500" fill="#07090a" fill-opacity="0.55"/>')
    n, cw, x0, y0 = 10, 30, 50, 100
    for r in range(n):
        for c in range(n):
            if c <= r:
                w = (0.25 + 0.75 * math.exp(-0.35 * (r - c))) * (0.6 + 0.4 * ((r * 3 + c * 5) % 4) / 3)
                s.rect(x0 + c * cw, y0 + r * cw, cw - 3, cw - 3, fill=G, fop=0.12 + 0.6 * w, rx=3,
                       glow=(r == c))
            else:
                s.rect(x0 + c * cw, y0 + r * cw, cw - 3, cw - 3, fill=LINE1, fop=0.9, rx=3)
    s.text(x0, y0 - 22, "causal attention", size=13, fill=MUTED, anchor="start")
    s.text(430, 225, "GPT", size=120, fill=G, anchor="start", weight=800, glow=True)
    s.text(434, 285, "from scratch", size=38, fill=FG, anchor="start", weight=700)
    s.text(436, 335, "$ python train.py --char-level", size=15, fill=MUTED, anchor="start")
    s.text(436, 365, '<tspan fill="%s">6</tspan> layers · <tspan fill="%s">6</tspan> heads · '
           '<tspan fill="%s">384</tspan>-d' % (Y, Y, Y), size=15, fill=MUTED, anchor="start", raw=True)
    s.text(760, 60, "♛", size=30, fill=Y, anchor="end", glow=True)
    s.render()


if __name__ == "__main__":
    bigram()
    masked_attention()
    multi_head()
    feedforward()
    block()
    architecture()
    training()
    decoding()
    thumbnail()
