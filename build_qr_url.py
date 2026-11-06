#!/usr/bin/env python3
"""Build the premium QR that opens the profile page.

Because the payload is a short URL, the symbol is a low QR version with plenty of
spare capacity, so error correction can be set to H (~30%) and the company logo
can sit safely in the centre without endangering decoding.

Usage:  python3 build_qr_url.py "https://your-permanent-url/"
"""
import base64
import io
import pathlib
import sys

import cairosvg
import segno
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "qr"
OUT.mkdir(exist_ok=True)

URL = sys.argv[1] if len(sys.argv) > 1 else "https://gss-tec.com/muhangi-gaston"
print(f"payload URL: {URL}")

NAVY_DEEP, NAVY, NAVY_LIGHT = "#081428", "#0C2242", "#14345E"
BLUE, SILVER, SILVER_DIM, WHITE = "#2E6FB7", "#C6D0DD", "#8A9AB0", "#FFFFFF"
ACCENT = "#9EC1E8"

W, H = 1200, 1500
M = 54
CARD_X, CARD_Y = M, M
CARD_W, CARD_H = W - 2 * M, H - 2 * M
CARD_R = 30

QR_MODULE, QR_QUIET, PLATE_PAD = 11, 4, 30

FONTS = {
    "title": HERE.parent / "qr_build/fonts/static/Montserrat-Bold.ttf",
    "slogan": HERE.parent / "qr_build/fonts/static/Montserrat-Medium.ttf",
    "label": HERE.parent / "qr_build/fonts/static/Inter-SemiBold.ttf",
    "body": HERE.parent / "qr_build/fonts/static/Inter-Regular.ttf",
    "foot": HERE.parent / "qr_build/fonts/static/Inter-Medium.ttf",
}
_loaded = {}
for k, p in FONTS.items():
    f = TTFont(str(p))
    _loaded[k] = (f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"], f.getGlyphSet())


def measure(key, text, size, ls=0.0):
    upm, cmap, hmtx, _ = _loaded[key]
    return sum(hmtx[cmap.get(ord(c))][0] * size / upm + ls for c in text) - (ls if text else 0)


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


def tspan(key, text, size, x, y, anchor="middle", ls=0.0, fill=WHITE):
    d, _ = text_path(key, text, size, x, y, anchor, ls)
    return f'<path d="{d}" fill="{fill}"/>'


# ------------------------------------------------------------------ QR symbol
qr = segno.make(URL, error="h", boost_error=False)
matrix = list(qr.matrix)
N = len(matrix)
qr_span = N * QR_MODULE
plate_w = qr_span + 2 * (QR_QUIET * QR_MODULE + PLATE_PAD)
plate_x = (W - plate_w) / 2
qr_x = plate_x + QR_QUIET * QR_MODULE + PLATE_PAD
print(f"EC=H | version={qr.version} | modules={N}x{N} | {len(URL)} chars")

# --- centre logo knocked out of the module grid ---------------------------
CLEAR = 3                      # modules cleared each side of the centre
c0, c1 = (N - CLEAR) // 2, (N - CLEAR) // 2 + CLEAR


def qr_path():
    parts = []
    for r, row in enumerate(matrix):
        c = 0
        while c < N:
            if row[c]:
                s = c
                while c < N and row[c]:
                    c += 1
                x, y = qr_x + s * QR_MODULE, qr_y + r * QR_MODULE
                w = (c - s) * QR_MODULE
                parts.append(f"M{x} {y}h{w}v{QR_MODULE}h-{w}z")
            else:
                c += 1
    return "".join(parts)


def qr_path_masked():
    """Dark modules, with the centre square removed for the logo."""
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
            x, y = qr_x + s * QR_MODULE, qr_y + r * QR_MODULE
            w = (c - s) * QR_MODULE
            parts.append(f"M{x} {y}h{w}v{QR_MODULE}h-{w}z")
    return "".join(parts)


# --- logo badge (centred in the cleared square) ---------------------------
# The source logo has a black background, which would merge into the dark
# modules. Key the background out and place the emblem on a white rounded
# badge so it reads as a clean brand mark.
CLEAR_PX = CLEAR * QR_MODULE
BADGE = CLEAR_PX + 24                 # badge side, slightly larger than the hole
_ss = 4                               # supersample factor
_bw_px = BADGE * _ss

_src = Image.open(HERE.parent / "qr_build" / "logo.png").convert("RGB")
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

_badge = Image.new("RGBA", (_bw_px, _bw_px), (0, 0, 0, 0))
_rad = int(_bw_px * 0.10)
_mask = Image.new("L", (_bw_px, _bw_px), 0)
ImageDraw.Draw(_mask).rounded_rectangle([0, 0, _bw_px - 1, _bw_px - 1],
                                        radius=_rad, fill=255)
_badge.paste(Image.new("RGBA", (_bw_px, _bw_px), (255, 255, 255, 255)), (0, 0), _mask)

# fit the emblem inside the badge with even padding on every side
_inner = int(BADGE * 0.76) * _ss
_scale = min(_inner / _keyed.width, _inner / _keyed.height)
_lw, _lh = max(1, round(_keyed.width * _scale)), max(1, round(_keyed.height * _scale))
_logo_rs = _keyed.resize((_lw, _lh), Image.LANCZOS)
_badge.alpha_composite(_logo_rs, ((_bw_px - _lw) // 2, (_bw_px - _lh) // 2))

_fr = ImageDraw.Draw(_badge)
_fw = max(2, int(_bw_px * 0.008))
_fr.rounded_rectangle([_fw // 2, _fw // 2, _bw_px - 1 - _fw // 2, _bw_px - 1 - _fw // 2],
                      radius=_rad, outline=(198, 208, 221, 255), width=_fw)
_badge.save(HERE / "logo_badge.png")
logo_b64 = base64.b64encode((HERE / "logo_badge.png").read_bytes()).decode()

# header mark: the same keyed emblem, transparent, for use on the dark card
_hw = 600
_hh = round(_hw * _keyed.height / _keyed.width)
_keyed.resize((_hw, _hh), Image.LANCZOS).save(HERE / "logo_header.png")
head_b64 = base64.b64encode((HERE / "logo_header.png").read_bytes()).decode()
HEAD_W = 300
HEAD_H = HEAD_W * _keyed.height / _keyed.width

LOGO_W = LOGO_H = BADGE
logo_x = plate_x + QR_QUIET * QR_MODULE + PLATE_PAD + (qr_span - BADGE) / 2

TITLE = "MUHANGI GASTON"
SUB = "FOUNDER | GASTON SOFTWARE SOLUTIONS LLP"
SLOGAN = "Innovation Today. Transformation Tomorrow."
SCAN = "SCAN TO VIEW MY PROFESSIONAL PROFILE"
NOTE = "Opens my full profile page — services, products and contact"
CONTACT = "info@gss-tec.com   |   +256 755 274 944"
WEB = "gss-tec.com   |   Kampala, Uganda"

title_sz = fit("title", TITLE, 62, CARD_W - 200, ls=6)
sub_sz = fit("label", SUB, 22, CARD_W - 200, ls=3.2)
slogan_sz = fit("slogan", SLOGAN, 24, CARD_W - 220, ls=1.2)
scan_sz = fit("label", SCAN, 25, CARD_W - 120, ls=4)
note_sz = fit("body", NOTE, 16, CARD_W - 80, ls=1.2)
contact_sz = fit("foot", CONTACT, 19, CARD_W - 120, ls=0.6)
web_sz = fit("body", WEB, 17, CARD_W - 120, ls=0.8)

logo_top = CARD_Y + 50
title_y = logo_top + HEAD_H + 86
rule_y = title_y + 26
sub_y = rule_y + 44
slogan_y = sub_y + 48
foot_top = CARD_Y + CARD_H - 118
plate_y = slogan_y + 60
qr_y = plate_y + QR_QUIET * QR_MODULE + PLATE_PAD
logo_y = plate_y + QR_QUIET * QR_MODULE + PLATE_PAD + (qr_span - LOGO_H) / 2
assert plate_y + plate_w + 108 < foot_top, "QR plate collides with the footer"

inner = f'''
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0" stop-color="{NAVY_DEEP}"/>
      <stop offset="0.45" stop-color="{NAVY}"/>
      <stop offset="1" stop-color="{NAVY_LIGHT}"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{NAVY}"/>
      <stop offset="0.5" stop-color="{SILVER}"/>
      <stop offset="1" stop-color="{NAVY}"/>
    </linearGradient>
    <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#9FB0C6"/>
      <stop offset="0.5" stop-color="{SILVER}"/>
      <stop offset="1" stop-color="#6E8098"/>
    </linearGradient>
    <linearGradient id="plate" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFFFF"/>
      <stop offset="1" stop-color="#F4F7FB"/>
    </linearGradient>
    <linearGradient id="topbar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{NAVY}"/>
      <stop offset="0.5" stop-color="{ACCENT}"/>
      <stop offset="1" stop-color="{NAVY}"/>
    </linearGradient>
  </defs>

  <rect x="{CARD_X}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="{CARD_R}"
        fill="url(#card)" stroke="url(#frame)" stroke-width="1.6"/>
  <rect x="{CARD_X + 12}" y="{CARD_Y + 12}" width="{CARD_W - 24}" height="{CARD_H - 24}"
        rx="{CARD_R - 10}" fill="none" stroke="{BLUE}" stroke-opacity="0.35" stroke-width="1"/>
  <rect x="{CARD_X + 60}" y="{CARD_Y}" width="{CARD_W - 120}" height="3" fill="url(#topbar)"/>

  <image x="{(W - HEAD_W) / 2:.1f}" y="{logo_top:.1f}" width="{HEAD_W}" height="{HEAD_H:.1f}"
         xlink:href="data:image/png;base64,{head_b64}"/>

  {tspan("title", TITLE, title_sz, W / 2, title_y, ls=6)}
  <rect x="{W / 2 - 190}" y="{rule_y}" width="380" height="2" fill="url(#rule)"/>
  {tspan("label", SUB, sub_sz, W / 2, sub_y, ls=3.2, fill=SILVER)}
  {tspan("slogan", SLOGAN, slogan_sz, W / 2, slogan_y, ls=1.2, fill=ACCENT)}

  <rect x="{plate_x}" y="{plate_y}" width="{plate_w}" height="{plate_w}" rx="18"
        fill="url(#plate)" stroke="url(#frame)" stroke-width="2"/>
  <path d="{qr_path_masked()}" fill="{NAVY_DEEP}"/>
  <image x="{logo_x:.1f}" y="{logo_y:.1f}" width="{LOGO_W}" height="{LOGO_H}"
         xlink:href="data:image/png;base64,{logo_b64}"/>

  {tspan("label", SCAN, scan_sz, W / 2, plate_y + plate_w + 58, ls=4, fill=SILVER)}
  {tspan("body", NOTE, note_sz, W / 2, plate_y + plate_w + 90, ls=1.2, fill=SILVER_DIM)}

  <rect x="{W / 2 - 210}" y="{foot_top}" width="420" height="1.4" fill="url(#rule)"/>
  {tspan("foot", CONTACT, contact_sz, W / 2, foot_top + 40, ls=0.6, fill=WHITE)}
  {tspan("body", WEB, web_sz, W / 2, foot_top + 74, ls=0.8, fill=SILVER_DIM)}
'''

design = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
          f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
          f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
          f'  <rect width="{W}" height="{H}" fill="{NAVY_DEEP}"/>\n{inner}\n</svg>\n')
(OUT / "muhangi-gaston-profile-qr.svg").write_text(design, encoding="utf-8")
cairosvg.svg2png(bytestring=design.encode(),
                 write_to=str(OUT / "muhangi-gaston-profile-qr.png"), output_width=2400)

A4W, A4H = 595.28 / 0.75, 841.89 / 0.75
margin = 29.33
sc = min((A4W - 2 * margin) / W, (A4H - 2 * margin) / H)
dw, dh = W * sc, H * sc
dx, dy = (A4W - dw) / 2, (A4H - dh) / 2
a4 = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
      f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="{A4W:.2f}" height="{A4H:.2f}" viewBox="0 0 {A4W:.2f} {A4H:.2f}">'
      f'<rect width="{A4W:.2f}" height="{A4H:.2f}" fill="#FFFFFF"/>'
      f'<g transform="translate({dx:.3f},{dy:.3f}) scale({sc:.6f})">{inner}</g></svg>')
cairosvg.svg2pdf(bytestring=a4.encode(),
                 write_to=str(OUT / "muhangi-gaston-profile-qr.pdf"))

(OUT / "qr-target.txt").write_text(URL + "\n", encoding="utf-8")
for p in sorted(OUT.iterdir()):
    print(f"  {p.name:38} {p.stat().st_size/1024:8.1f} KB")
