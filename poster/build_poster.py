#!/usr/bin/env python3
"""Premium front-side QR profile poster for Muhangi Gaston / Gaston Software Solutions LLP.

Layout (top to bottom): brand mark, name, title, company, slogan, a row of three
service icons either side of the QR, the QR itself carrying the official GSS logo
in a white rounded square with a blue border, a navy CTA banner, and the footer.

Outputs: PNG (high-res), SVG (vector, text as outlines) and a true-A4 PDF.
"""
import base64
import io
import pathlib

import cairosvg
import segno
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE.parent / "qr_build"
URL = "https://donationsgsstec-dev.github.io/Muhangi-Gaston-/"

# ------------------------------------------------------------------ palette
NAVY_DEEP = "#050D1C"
NAVY = "#0A1B36"
NAVY_MID = "#102A50"
NAVY_LIGHT = "#173A6B"
ELECTRIC = "#1E7BE8"
CYAN = "#35C6F4"
CYAN_SOFT = "#7FDBFF"
WHITE = "#FFFFFF"
SILVER = "#C6D0DD"
SILVER_DIM = "#8496AE"

# ------------------------------------------------------------------ canvas
W, H = 1600, 2263                      # A4-ish portrait ratio
M = 58
CARD_X, CARD_Y = M, M
CARD_W, CARD_H = W - 2 * M, H - 2 * M
CARD_R = 34

# ------------------------------------------------------------------ fonts
FONTS = {
    "title": BUILD / "fonts/static/Montserrat-Bold.ttf",
    "semi": BUILD / "fonts/static/Montserrat-SemiBold.ttf",
    "slogan": BUILD / "fonts/static/Montserrat-Medium.ttf",
    "label": BUILD / "fonts/static/Inter-SemiBold.ttf",
    "body": BUILD / "fonts/static/Inter-Regular.ttf",
    "foot": BUILD / "fonts/static/Inter-Medium.ttf",
}
_loaded = {}
for k, p in FONTS.items():
    f = TTFont(str(p))
    _loaded[k] = (f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"], f.getGlyphSet())


def measure(key, text, size, ls=0.0):
    upm, cmap, hmtx, _ = _loaded[key]
    if not text:
        return 0.0
    return sum(hmtx[cmap.get(ord(c))][0] * size / upm + ls for c in text) - ls


def fit(key, text, size, max_w, ls=0.0):
    while size > 8 and measure(key, text, size, ls) > max_w:
        size -= 0.5
    return size


def text_path(key, text, size, x, y, anchor="start", ls=0.0):
    upm, cmap, hmtx, gs = _loaded[key]
    scale = size / upm
    glyphs, total = [], 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        adv = hmtx[name][0] if name else 0
        glyphs.append((name, adv))
        total += adv * scale + ls
    if text:
        total -= ls
    if anchor == "middle":
        x -= total / 2
    elif anchor == "end":
        x -= total
    parts, cx = [], x
    for name, adv in glyphs:
        if name:
            pen = SVGPathPen(gs)
            gs[name].draw(TransformPen(pen, Transform(scale, 0, 0, -scale, cx, y)))
            c = pen.getCommands()
            if c:
                parts.append(c)
        cx += adv * scale + ls
    return " ".join(parts), total


def tspan(key, text, size, x, y, anchor="middle", ls=0.0, fill=WHITE, op=1.0):
    d, _ = text_path(key, text, size, x, y, anchor, ls)
    o = f' fill-opacity="{op}"' if op != 1.0 else ""
    return f'<path d="{d}" fill="{fill}"{o}/>'


# ------------------------------------------------------------------ QR symbol
qr = segno.make(URL, error="h", boost_error=False)
matrix = list(qr.matrix)
N = len(matrix)
print(f"QR: version {qr.version}, {N}x{N} modules, EC=H, {len(URL)} chars")

# ------------------------------------------------------------------ logo
# Preserve the original logo exactly: only the flat black background is keyed
# out so the mark sits cleanly on white. Colours and shapes are untouched.
_src = Image.open(BUILD / "logo.png").convert("RGB")
_sx, _sy = _src.size
_keyed = Image.new("RGBA", (_sx, _sy), (0, 0, 0, 0))
_p, _q = _src.load(), _keyed.load()
for y in range(_sy):
    for x in range(_sx):
        r, g, b = _p[x, y]
        lum = max(r, g, b)
        a = 0 if lum < 30 else (255 if lum > 64 else int((lum - 30) / 34 * 255))
        _q[x, y] = (r, g, b, a)
_keyed = _keyed.crop(_keyed.getbbox())
AR = _keyed.width / _keyed.height
print(f"logo: keyed to {_keyed.size}, aspect {AR:.3f}")

# ------------------------------------------------------------------ geometry
# Two icon columns flank the QR; the QR sits on the vertical centre line.
COL_W = 300                            # width of each icon column
GUT = 30                               # gutter between column and plate
QR_TARGET = 940                        # target QR plate side
qr_span = QR_TARGET - 68
QR_MODULE = qr_span // N
qr_span = QR_MODULE * N
plate_w = qr_span + 68
qr_side = plate_w

CLEAR = 3                              # modules cleared at the centre for the logo
c0, c1 = (N - CLEAR) // 2, (N - CLEAR) // 2 + CLEAR


def qr_path():
    parts = []
    for r, row in enumerate(matrix):
        c = 0
        while c < N:
            if not row[c] or (c0 <= r < c1 and c0 <= c < c1):
                c += 1
                continue
            s = c
            while c < N and row[c] and not (c0 <= r < c1 and c0 <= c < c1):
                c += 1
            x = s * QR_MODULE
            y = r * QR_MODULE
            w = (c - s) * QR_MODULE
            parts.append(f"M{x} {y}h{w}v{QR_MODULE}h-{w}z")
    return "".join(parts)


# --- logo badge: white rounded square, blue border, original mark inside
BADGE = CLEAR * QR_MODULE + 22
_ss = 4
_bpx = BADGE * _ss
_badge = Image.new("RGBA", (_bpx, _bpx), (0, 0, 0, 0))
_brad = int(_bpx * 0.14)
_bmask = Image.new("L", (_bpx, _bpx), 0)
ImageDraw.Draw(_bmask).rounded_rectangle([0, 0, _bpx - 1, _bpx - 1], radius=_brad, fill=255)
_badge.paste(Image.new("RGBA", (_bpx, _bpx), (255, 255, 255, 255)), (0, 0), _bmask)
_inner = int(BADGE * 0.78) * _ss
_scale = min(_inner / _keyed.width, _inner / _keyed.height)
_lw, _lh = max(1, round(_keyed.width * _scale)), max(1, round(_keyed.height * _scale))
_badge.alpha_composite(_keyed.resize((_lw, _lh), Image.LANCZOS),
                       ((_bpx - _lw) // 2, (_bpx - _lh) // 2))
_bdr = ImageDraw.Draw(_badge)
_bw = max(3, int(_bpx * 0.012))
_bdr.rounded_rectangle([_bw // 2, _bw // 2, _bpx - 1 - _bw // 2, _bpx - 1 - _bw // 2],
                       radius=_brad, outline=(30, 123, 232, 255), width=_bw)
_badge.save(HERE / "logo_badge.png")
badge_b64 = base64.b64encode((HERE / "logo_badge.png").read_bytes()).decode()

# --- header mark: original logo, transparent, on the navy card
_hw = 760
_head = _keyed.resize((_hw, max(1, round(_hw / AR))), Image.LANCZOS)
_head.save(HERE / "logo_header.png")
head_b64 = base64.b64encode((HERE / "logo_header.png").read_bytes()).decode()
HEAD_W = 330
HEAD_H = HEAD_W / AR

# ------------------------------------------------------------------ icons
def icon(name, cx, cy, s, color=CYAN):
    """Minimal line icons, 24x24 design grid scaled by s, centred on (cx, cy)."""
    def P(x, y):
        return (cx + (x - 12) * s, cy + (y - 12) * s)

    sw = s * 1.05
    st = f'fill="none" stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    g = [f'<g {st}>']
    if name == "ai":                       # neural node
        for (x, y) in [(6.5, 6), (17.5, 6), (6.5, 18), (17.5, 18), (12, 12)]:
            p = P(x, y)
            g.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{s*1.35:.1f}"/>')
        for (a, b) in [((6.5, 6), (12, 12)), ((17.5, 6), (12, 12)), ((6.5, 18), (12, 12)),
                       ((17.5, 18), (12, 12)), ((6.5, 6), (17.5, 6)), ((6.5, 18), (17.5, 18)),
                       ((6.5, 6), (6.5, 18)), ((17.5, 6), (17.5, 18))]:
            p1, p2 = P(*a), P(*b)
            g.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"/>')
    elif name == "code":                   # code brackets
        for pts in [[(9.5, 6.5), (4, 12), (9.5, 17.5)], [(14.5, 6.5), (20, 12), (14.5, 17.5)]]:
            d = " ".join(f'{"M" if i == 0 else "L"}{P(*pt)[0]:.1f} {P(*pt)[1]:.1f}'
                         for i, pt in enumerate(pts))
            g.append(f'<path d="{d}"/>')
        g.append(f'<line x1="{P(12,4.5)[0]:.1f}" y1="{P(12,4.5)[1]:.1f}" '
                 f'x2="{P(12,19.5)[0]:.1f}" y2="{P(12,19.5)[1]:.1f}"/>')
    elif name == "cloud":                  # cloud + upload arrow
        g.append(f'<path d="M{P(6.8,17)[0]:.1f} {P(6.8,17)[1]:.1f} '
                 f'a{s*3.5:.1f} {s*3.5:.1f} 0 0 1 {s*0.5:.1f} -{s*6.9:.1f} '
                 f'a{s*4.3:.1f} {s*4.3:.1f} 0 0 1 {s*8.4:.1f} {s*0.7:.1f} '
                 f'a{s*3.1:.1f} {s*3.1:.1f} 0 0 1 -{s*0.7:.1f} {s*6.2:.1f}"/>')
        g.append(f'<line x1="{P(12,16.5)[0]:.1f}" y1="{P(12,16.5)[1]:.1f}" '
                 f'x2="{P(12,9.5)[0]:.1f}" y2="{P(12,9.5)[1]:.1f}"/>')
        g.append(f'<path d="M{P(9.2,12.2)[0]:.1f} {P(9.2,12.2)[1]:.1f} '
                 f'L{P(12,9.5)[0]:.1f} {P(12,9.5)[1]:.1f} '
                 f'L{P(14.8,12.2)[0]:.1f} {P(14.8,12.2)[1]:.1f}"/>')
    elif name == "bulb":                   # innovation
        g.append(f'<path d="M{P(8.4,10.4)[0]:.1f} {P(8.4,10.4)[1]:.1f} '
                 f'a{s*3.6:.1f} {s*3.6:.1f} 0 1 1 {s*7.2:.1f} 0 '
                 f'a{s*3.6:.1f} {s*3.6:.1f} 0 0 1 -{s*2.3:.1f} {s*3.1:.1f} '
                 f'L{P(10.7,16.2)[0]:.1f} {P(10.7,16.2)[1]:.1f} '
                 f'L{P(13.3,16.2)[0]:.1f} {P(13.3,16.2)[1]:.1f} '
                 f'L{P(13.3,13.5)[0]:.1f} {P(13.3,13.5)[1]:.1f}"/>')
        g.append(f'<line x1="{P(10.4,18.2)[0]:.1f}" y1="{P(10.4,18.2)[1]:.1f}" '
                 f'x2="{P(13.6,18.2)[0]:.1f}" y2="{P(13.6,18.2)[1]:.1f}"/>')
        g.append(f'<line x1="{P(11.2,20.4)[0]:.1f}" y1="{P(11.2,20.4)[1]:.1f}" '
                 f'x2="{P(12.8,20.4)[0]:.1f}" y2="{P(12.8,20.4)[1]:.1f}"/>')
    elif name == "handshake":              # partnership
        g.append(f'<path d="M{P(2.5,11.5)[0]:.1f} {P(2.5,11.5)[1]:.1f} '
                 f'L{P(7.5,11.5)[0]:.1f} {P(7.5,11.5)[1]:.1f} '
                 f'L{P(11,8.6)[0]:.1f} {P(11,8.6)[1]:.1f} '
                 f'L{P(13.8,11.2)[0]:.1f} {P(13.8,11.2)[1]:.1f}"/>')
        g.append(f'<path d="M{P(21.5,11.5)[0]:.1f} {P(21.5,11.5)[1]:.1f} '
                 f'L{P(16.5,11.5)[0]:.1f} {P(16.5,11.5)[1]:.1f} '
                 f'L{P(13.4,14.4)[0]:.1f} {P(13.4,14.4)[1]:.1f} '
                 f'L{P(10.6,11.8)[0]:.1f} {P(10.6,11.8)[1]:.1f}"/>')
        g.append(f'<line x1="{P(7.5,11.5)[0]:.1f}" y1="{P(7.5,11.5)[1]:.1f}" '
                 f'x2="{P(10.6,11.8)[0]:.1f}" y2="{P(10.6,11.8)[1]:.1f}"/>')
        g.append(f'<line x1="{P(12,14.6)[0]:.1f}" y1="{P(12,14.6)[1]:.1f}" '
                 f'x2="{P(12,16.6)[0]:.1f}" y2="{P(12,16.6)[1]:.1f}"/>')
    elif name == "africa":                 # globe / continent
        g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s*8.6:.1f}"/>')
        g.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{s*3.7:.1f}" ry="{s*8.6:.1f}"/>')
        g.append(f'<line x1="{cx - s*8.6:.1f}" y1="{cy:.1f}" x2="{cx + s*8.6:.1f}" y2="{cy:.1f}"/>')
        g.append(f'<line x1="{cx - s*7.4:.1f}" y1="{cy - s*4.4:.1f}" '
                 f'x2="{cx + s*7.4:.1f}" y2="{cy - s*4.4:.1f}"/>')
        g.append(f'<line x1="{cx - s*7.4:.1f}" y1="{cy + s*4.4:.1f}" '
                 f'x2="{cx + s*7.4:.1f}" y2="{cy + s*4.4:.1f}"/>')
    g.append("</g>")
    return "".join(g)


def icon_chip(cx, cy, side):
    """Rounded chip that sits behind an icon."""
    x, y = cx - side / 2, cy - side / 2
    r = side * 0.28
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{side}" height="{side}" rx="{r:.1f}" '
            f'fill="{ELECTRIC}" fill-opacity="0.16" stroke="{CYAN}" stroke-opacity="0.45" '
            f'stroke-width="1.4"/>')


LEFT = [("ai", "AI &amp; Machine", "Learning"),
        ("code", "Software", "Development"),
        ("cloud", "Cloud", "Solutions")]
RIGHT = [("bulb", "Digital", "Innovation"),
         ("handshake", "Strategic", "Partnerships"),
         ("africa", "Tech for a", "Better Africa")]

# ------------------------------------------------------------------ text
TITLE = "MUHANGI GASTON"
ROLE = "Founder &amp; Software Engineer"
COMPANY = "GASTON SOFTWARE SOLUTIONS LLP"
SLOGAN = "Innovation Today. Transformation Tomorrow."
CTA = "SCAN TO VIEW MY FULL PROFILE"
FOOT = [("Kampala, Uganda", "gss-loc"),
        ("info@gss-tec.com", "gss-mail"),
        ("+256 755 274 944", "gss-tel"),
        ("www.gss-tec.com", "gss-web")]

title_sz = fit("title", TITLE, 96, CARD_W - 240, ls=7)
role_sz = fit("semi", "Founder & Software Engineer", 34, CARD_W - 420, ls=2.2)
comp_sz = fit("label", "GASTON SOFTWARE SOLUTIONS LLP", 24, CARD_W - 300, ls=5)
slogan_sz = fit("slogan", SLOGAN, 30, CARD_W - 260, ls=1.2)
cta_sz = fit("title", CTA, 42, plate_w - 90, ls=4.5)
foot_sz = 20
lab_sz = 17.5

# ------------------------------------------------------------------ vertical rhythm
# Blocks are laid out top-down; whatever space is left over is distributed
# across the gaps so the composition fills the card instead of leaving a hole.
top = CARD_Y + 62
bot = CARD_Y + CARD_H - 92

head_h = HEAD_H
title_h = title_sz
rule_h = 2.4
role_h = role_sz * 1.45
comp_h = comp_sz * 1.45
slogan_h = slogan_sz * 1.45
cta_h = 100

blocks = head_h + title_h + rule_h + role_h + comp_h + slogan_h + qr_side + cta_h
BASE_GAPS = [86, 34, 54, 50, 64, 74, 80]      # 7 gaps between the 8 blocks
spare = (bot - top) - blocks - sum(BASE_GAPS)
assert spare >= 0, f"content overflows by {-spare:.0f} units"
extra = spare / len(BASE_GAPS)
gaps = [g + extra for g in BASE_GAPS]
print(f"layout: blocks={blocks:.0f} gaps={sum(gaps):.0f} spare={spare:.0f} "
      f"(+{extra:.0f}/gap) qr={plate_w}px module={QR_MODULE}")

y = top
head_y = y
y += head_h + gaps[0]
title_y = y + title_h
y += title_h + gaps[1]
rule_y = y
y += rule_h + gaps[2]
role_y = y + role_h * 0.78
y += role_h + gaps[3]
comp_y = y + comp_h * 0.78
y += comp_h + gaps[4]
slogan_y = y + slogan_h * 0.78
y += slogan_h + gaps[5]
qr_top = y
plate_y = qr_top
y += qr_side + gaps[6]
cta_top = y
foot_top = CARD_Y + CARD_H - 60

# icon rows are centred on the QR
icons_top = qr_top + (qr_side - 3 * 132) / 2
icon_row_h = 132

plate_x = (W - plate_w) / 2

# icon column x centres
left_cx = plate_x - GUT - COL_W / 2
right_cx = plate_x + plate_w + GUT + COL_W / 2

# ------------------------------------------------------------------ SVG body
def icon_rows(items, cx):
    out = []
    for i, (ic, l1, l2) in enumerate(items):
        y = icons_top + i * icon_row_h + icon_row_h / 2
        chip_cy = y - 30
        out.append(icon_chip(cx, chip_cy, 78))
        out.append(icon(ic, cx, chip_cy, 1.52))
        out.append(tspan("label", l1, lab_sz, cx, y + 26, ls=0.4, fill=WHITE))
        out.append(tspan("label", l2, lab_sz, cx, y + 50, ls=0.4, fill=WHITE))
    return "\n  ".join(out)


inner = f'''
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="0.4" y2="1">
      <stop offset="0" stop-color="{NAVY_DEEP}"/>
      <stop offset="0.38" stop-color="{NAVY}"/>
      <stop offset="0.78" stop-color="{NAVY_MID}"/>
      <stop offset="1" stop-color="{NAVY_LIGHT}"/>
    </linearGradient>
    <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.85"/>
      <stop offset="0.5" stop-color="{ELECTRIC}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{SILVER}" stop-opacity="0.75"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{NAVY_MID}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{CYAN}"/>
      <stop offset="1" stop-color="{NAVY_MID}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="cta" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{NAVY}"/>
      <stop offset="0.5" stop-color="{ELECTRIC}"/>
      <stop offset="1" stop-color="{NAVY}"/>
    </linearGradient>
    <linearGradient id="plate" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="1" stop-color="#EFF5FC"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.42" r="0.62">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.20"/>
      <stop offset="0.55" stop-color="{ELECTRIC}" stop-opacity="0.08"/>
      <stop offset="1" stop-color="{NAVY_DEEP}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="topbar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{NAVY_MID}"/>
      <stop offset="0.28" stop-color="{CYAN}"/>
      <stop offset="0.72" stop-color="{CYAN}"/>
      <stop offset="1" stop-color="{NAVY_MID}"/>
    </linearGradient>
  </defs>

  <rect x="{CARD_X}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="{CARD_R}"
        fill="url(#card)" stroke="url(#frame)" stroke-width="2"/>
  <rect x="{CARD_X + 13}" y="{CARD_Y + 13}" width="{CARD_W - 26}" height="{CARD_H - 26}"
        rx="{CARD_R - 11}" fill="none" stroke="{CYAN}" stroke-opacity="0.28" stroke-width="1"/>
  <rect x="{CARD_X + 90}" y="{CARD_Y}" width="{CARD_W - 180}" height="4" fill="url(#topbar)"/>
  <rect x="{CARD_X}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="{CARD_R}"
        fill="url(#glow)"/>

  <image x="{(W - HEAD_W) / 2:.1f}" y="{head_y:.1f}" width="{HEAD_W}" height="{HEAD_H:.1f}"
         xlink:href="data:image/png;base64,{head_b64}"/>

  {tspan("title", TITLE, title_sz, W / 2, title_y, ls=7)}
  <rect x="{W / 2 - 300}" y="{rule_y}" width="600" height="2.4" fill="url(#rule)"/>
  {tspan("semi", "Founder &amp; Software Engineer", role_sz, W / 2, role_y, ls=2.2, fill=CYAN_SOFT)}
  {tspan("label", "GASTON SOFTWARE SOLUTIONS LLP", comp_sz, W / 2, comp_y, ls=5, fill=SILVER)}
  {tspan("slogan", SLOGAN, slogan_sz, W / 2, slogan_y, ls=1.2, fill=WHITE)}

  {icon_rows(LEFT, left_cx)}
  {icon_rows(RIGHT, right_cx)}

  <rect x="{plate_x}" y="{plate_y}" width="{plate_w}" height="{plate_w}" rx="22"
        fill="url(#plate)" stroke="url(#frame)" stroke-width="2"/>
  <g transform="translate({plate_x + 34},{plate_y + 34})">
    <path d="{qr_path()}" fill="{NAVY_DEEP}"/>
  </g>
  <image x="{plate_x + 34 + (qr_span - BADGE) / 2:.1f}" y="{plate_y + 34 + (qr_span - BADGE) / 2:.1f}"
         width="{BADGE}" height="{BADGE}" xlink:href="data:image/png;base64,{badge_b64}"/>

  <rect x="{plate_x}" y="{cta_top}" width="{plate_w}" height="{cta_h}" rx="16" fill="url(#cta)"/>
  {tspan("title", CTA, cta_sz, W / 2, cta_top + cta_h / 2 + 14, ls=4.5)}

  <rect x="{CARD_X + 150}" y="{foot_top - 34}" width="{CARD_W - 300}" height="1.6" fill="url(#rule)"/>
'''

# footer: four items across two rows, each with a tiny cyan glyph
fy1 = foot_top + 24
fy2 = foot_top + 66
sep = "  |  "
left_line = "Kampala, Uganda   |   info@gss-tec.com"
right_line = "+256 755 274 944   |   www.gss-tec.com"
foot_lines = [
    tspan("foot", "Kampala, Uganda", foot_sz, W / 2, fy1, ls=0.6, fill=SILVER),
    tspan("foot", "info@gss-tec.com", foot_sz, W / 2, fy2, ls=0.6, fill=WHITE),
]
# single centred line, with separators, is cleaner and stays readable
foot_all = "Kampala, Uganda    |    info@gss-tec.com    |    +256 755 274 944    |    www.gss-tec.com"
foot_all_sz = fit("foot", foot_all, 22, CARD_W - 120, ls=0.4)
inner += f'''
  {tspan("foot", foot_all, foot_all_sz, W / 2, foot_top + 30, ls=0.4, fill=SILVER)}
'''

design = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
          f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
          f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
          f'  <rect width="{W}" height="{H}" fill="{NAVY_DEEP}"/>\n{inner}\n</svg>\n')

(HERE / "muhangi-gaston-qr-poster.svg").write_text(design, encoding="utf-8")
cairosvg.svg2png(bytestring=design.encode(),
                 write_to=str(HERE / "muhangi-gaston-qr-poster.png"), output_width=3200)

A4W, A4H = 595.28 / 0.75, 841.89 / 0.75
margin = 28
sc = min((A4W - 2 * margin) / W, (A4H - 2 * margin) / H)
dw, dh = W * sc, H * sc
dx, dy = (A4W - dw) / 2, (A4H - dh) / 2
a4 = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
      f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="{A4W:.2f}" height="{A4H:.2f}" viewBox="0 0 {A4W:.2f} {A4H:.2f}">'
      f'<rect width="{A4W:.2f}" height="{A4H:.2f}" fill="#FFFFFF"/>'
      f'<g transform="translate({dx:.3f},{dy:.3f}) scale({sc:.6f})">{inner}</g></svg>')
cairosvg.svg2pdf(bytestring=a4.encode(),
                 write_to=str(HERE / "muhangi-gaston-qr-poster.pdf"))

for p in sorted(HERE.glob("muhangi-gaston-qr-poster.*")):
    print(f"  {p.name:40} {p.stat().st_size/1024:8.1f} KB")
