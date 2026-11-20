#!/usr/bin/env python3
"""Renders preview.png: all wallpapers, phone and desktop, on one sheet."""
import glob, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfxlib as g
from build import WALLS
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, top = 1600, 186
dw, dh, pw, ph, gap = 304, 171, 106, 230, 14          # desktop and phone thumbnails
cell = dw + pw + gap
cols, rows = 3, 2
ch = ph + 62
H = top + rows * ch + 70
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{g.PAL["paper"]}"/>',
     f'<path d="{g.text_path("Sauna Wallpapers", 64, 100, 54, tracking=-0.01)}" fill="{g.PAL["ink"]}"/>',
     f'<text x="64" y="144" font-family="Inter" font-size="22" fill="{g.PAL["muted"]}">{len(WALLS)} vector wallpapers · phone 1290 × 2796 and desktop 3840 × 2160 · PNG + SVG · free under CC BY 4.0</text>']
pos = []
for k, (name, title, fn) in enumerate(WALLS):
    x = 64 + (k % cols) * ((W - 128 - cell) / (cols - 1))
    y = top + (k // cols) * ch
    pos.append((name, int(x), int(y)))
    o.append(f'<text x="{x:.0f}" y="{y + ph + 30}" font-family="Inter" font-size="15" fill="{g.PAL["muted"]}">{name}</text>')
o.append(f'<text x="{W - 64}" y="{H - 34}" font-family="Inter" font-size="18" fill="{g.PAL["muted"]}" text-anchor="end">Made by DIVELUX — diveluxsaunahat.com</text></svg>')
im = Image.open(io.BytesIO(g.render('\n'.join(o)))).convert('RGB')
for name, x, y in pos:
    d = Image.open(glob.glob(os.path.join(ROOT, 'desktop', name + '-*.png'))[0]).convert('RGB').resize((dw, dh), Image.LANCZOS)
    p = Image.open(glob.glob(os.path.join(ROOT, 'phone', name + '-*.png'))[0]).convert('RGB').resize((pw, ph), Image.LANCZOS)
    im.paste(d, (x, y + ph - dh)); im.paste(p, (x + dw + gap, y))
im.save(os.path.join(ROOT, 'preview.png'), optimize=True)
print('preview ok')
