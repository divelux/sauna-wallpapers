#!/usr/bin/env python3
"""Builds the Sauna Wallpapers: six vector compositions, each as phone (1290 x 2796) and desktop (3840 x 2160) SVG + PNG.

Every wallpaper is a function of the canvas size, so other sizes are one line away (see SIZES).
Needs: pip install resvg-py fonttools pillow
License: artwork CC BY 4.0, script MIT - DIVELUX, https://diveluxsaunahat.com
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfxlib as g

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = g.PAL
SIZES = {'phone': (1290, 2796), 'desktop': (3840, 2160)}


def f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def rect(x, y, w, h, c, rx=0, extra=''):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{c}"{extra}/>'


def line(d, c, w, extra=''):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def wisp_d(x, y, h, amp, n):
    seg = h / n
    d = f'M{f(x)} {f(y)}'
    for i in range(n):
        y0 = y - i * seg
        s = 1 if i % 2 == 0 else 1
        d += f' C{f(x + s * amp)} {f(y0 - seg * .33)} {f(x - s * amp)} {f(y0 - seg * .66)} {f(x)} {f(y0 - seg)}'
    return d


def sign(W, H, color, portrait):
    """A tiny wordmark, low contrast."""
    u = min(W, H) / 100
    size = 1.5 * u if not portrait else 1.9 * u
    if portrait:
        return f'<path d="{g.text_path("DIVELUX", W / 2, H - 9 * u, size, kind="semi", anchor="middle", tracking=0.42)}" fill="{color}"/>'
    return f'<path d="{g.text_path("DIVELUX", W - 4 * u, H - 3.6 * u, size, kind="semi", anchor="end", tracking=0.42)}" fill="{color}"/>'


# ---------------------------------------------------------------- wallpapers
def heat_ladder(W, H, portrait):
    """Bench tiers: every step up is warmer, the top one is ember."""
    cols = ['#1c110b', '#261710', '#33211a', '#4a3020', '#6b4a2b', '#8a5f35', '#b98a52', '#d9925a', P['ember']]
    parts = [24, 17, 13.5, 11, 9, 7.5, 6.5, 6, 5.5]
    o, y = [], H
    for c, p in zip(cols, parts):
        h = H * p / 100
        y -= h
        o.append(rect(0, y - 1, W, h + 1, c))
    return o, '#4a3020'


def steam(W, H, portrait):
    u = min(W, H) / 100
    o = [rect(0, 0, W, H, P['paper2'])]
    rnd = random.Random(3)
    n = 5 if portrait else 9
    for i in range(n):
        x = W * (i + .5) / n + rnd.uniform(-2, 2) * u
        base = H * rnd.uniform(.72, .9)
        top = H * rnd.uniform(.16, .34)
        c = [P['white'], P['paper'], P['white'], '#e6dfd3'][i % 4]
        o.append(line(wisp_d(x, base, base - top, (5.5 if portrait else 4.2) * u * (1 if i % 2 else -1), 3), c, (3.4 if i % 2 else 2.4) * u))
    return o, '#cfc6b8'


def planks(W, H, portrait):
    u = min(W, H) / 100
    rnd = random.Random(8)
    n = 7 if portrait else 16
    w = W / n
    shades = ['#ecd6b2', '#e7cfa6', '#efdcbc', '#e3c898', '#ead3ad', '#e9d2ac', '#e5cb9f']
    o = []
    for i in range(n):
        x = i * w
        o.append(rect(x, 0, w + 1, H, shades[(i * 3 + i // 4) % len(shades)]))
        for k in range(3):
            gx = x + w * (0.22 + 0.28 * k) + rnd.uniform(-.4, .4) * u
            a = rnd.uniform(.25, .8) * u * rnd.choice((-1, 1))
            ph = rnd.uniform(0, 6.28)
            pts = ' '.join(f'{f(gx + a * math.sin(yy / H * 6.28 * rnd.choice((1, 1.5)) + ph))} {f(yy)}' for yy in [H * t / 16 for t in range(17)])
            o.append(line('M' + pts, P['wood2'], .16 * u, ' opacity=".8"'))
        jy = H * ((0.17 + i * 0.37) % 1)
        o.append(line(f'M{f(x)} {f(jy)}h{f(w)}', P['wood3'], .18 * u))
        if i % 3 == 1:
            ky = H * ((0.55 + i * 0.23) % 1)
            kx = x + w * .55
            o.append(f'<ellipse cx="{f(kx)}" cy="{f(ky)}" rx="{f(.9 * u)}" ry="{f(1.5 * u)}" fill="{P["wood3"]}"/>')
            o.append(f'<ellipse cx="{f(kx)}" cy="{f(ky)}" rx="{f(1.8 * u)}" ry="{f(2.8 * u)}" fill="none" stroke="{P["wood2"]}" stroke-width="{f(.16 * u)}"/>')
    for i in range(1, n):
        o.append(line(f'M{f(i * w)} 0V{H}', P['wood3'], .18 * u))
    return o, P['wood3']


def bell_hat(cx, top, s):
    q = lambda x, y: f'{f(cx + x * s)} {f(top + y * s)}'
    o = [f'<path d="M{q(0, 0)}C{q(-64, 6)} {q(-84, 96)} {q(-108, 196)}H{f(cx + 108 * s)}C{q(84, 96)} {q(64, 6)} {q(0, 0)}z" fill="{P["felt1"]}"/>',
         f'<path d="M{q(0, 0)}C{q(64, 6)} {q(84, 96)} {q(108, 196)}H{f(cx + 30 * s)}C{q(30, 120)} {q(22, 60)} {q(0, 0)}z" fill="{P["felt2"]}" opacity=".45"/>',
         line(f'M{q(0, 2)}C{q(-22, 60)} {q(-34, 120)} {q(-36, 190)}', P['felt2'], 4 * s),
         line(f'M{q(0, 2)}C{q(22, 60)} {q(30, 120)} {q(30, 190)}', P['felt3'], 4 * s, ' opacity=".7"'),
         line(f'M{q(0, 2)}c{f(-12 * s)} {f(-14 * s)} {f(-10 * s)} {f(-30 * s)} 0 {f(-34 * s)} {f(10 * s)} {f(4 * s)} {f(12 * s)} {f(20 * s)} 0 {f(34 * s)}z', P['felt3'], 5 * s),
         rect(cx - 120 * s, top + 184 * s, 240 * s, 34 * s, P['felt3'], 17 * s),
         rect(cx + 62 * s, top + 193 * s, 26 * s, 16 * s, P['ember'], 3 * s)]
    return ''.join(o)


def hat(W, H, portrait):
    """A felt hat resting on the bench in a dark sauna."""
    u = min(W, H) / 100
    o = [rect(0, 0, W, H, P['night'])]
    bw = (W / 5) if portrait else (W / 14)
    for i in range(0, int(W / bw) + 1, 2):
        o.append(rect(i * bw, 0, bw, H, '#22150d'))
    by = H * (0.70 if portrait else 0.74)
    cx = W / 2 if portrait else W * 0.68
    s = (0.27 if portrait else 0.17) * u
    hat_top = by - 256 * s
    for dx, hh, a in ((-7, 20, 1), (2, 26, -1), (10, 17, 1)):
        o.append(line(wisp_d(cx + dx * u, hat_top - 4 * u, hh * u, 1.8 * u * a, 3), '#2e1d13', 1.3 * u))
    o.append(rect(0, by, W, 4.2 * u, P['wood4']))
    o.append(rect(0, by + 4.2 * u, W, 1.4 * u, '#5c3f23'))
    o.append(rect(0, by + 5.6 * u, W, H, '#150c08'))
    o.append(bell_hat(cx, by - 218 * s, s))
    return o, '#4a3020'


def stones(W, H, portrait):
    """Water on the stones: one ember drop above a bed of stove stones."""
    u = min(W, H) / 100
    rnd = random.Random(12)
    o = [rect(0, 0, W, H, P['ink'])]
    top = H * (0.70 if portrait else 0.66)
    cols = [P['stone1'], P['stone2'], P['stone3'], '#5a544e', P['stone2'], P['stone3']]
    pts = []
    for _ in range(4000):
        r = rnd.uniform(3.2, 6.5) * u
        x = rnd.uniform(-r, W + r)
        y = rnd.uniform(top, H + r)
        # the bed is a low mound: no stones above the mound line
        mound = top + (H - top) * 0.22 * (1 - math.cos((x / W - 0.5) * 2 * math.pi)) / 2 + r * .6
        if y < mound:
            continue
        if all(math.hypot(x - a, y - b) > r + c + .5 * u for a, b, c in pts):
            pts.append((x, y, r))
    pts.sort(key=lambda t: t[1])
    for k, (x, y, r) in enumerate(pts):
        o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(r)}" ry="{f(r * rnd.uniform(.7, .86))}" fill="{cols[k % len(cols)]}" transform="rotate({f(rnd.uniform(-30, 30))} {f(x)} {f(y)})"/>')
    cx, cy, s = W / 2, H * (0.44 if portrait else 0.36), 1.0 * u
    o.append(f'<path d="M{f(cx)} {f(cy - 9 * s)}c{f(5.4 * s)} {f(6.6 * s)} {f(8.4 * s)} {f(10.8 * s)} {f(8.4 * s)} {f(15 * s)}a{f(8.4 * s)} {f(8.4 * s)} 0 0 1 {f(-16.8 * s)} 0c0 {f(-4.2 * s)} {f(3 * s)} {f(-8.4 * s)} {f(8.4 * s)} {f(-15 * s)}z" fill="{P["ember"]}"/>')
    return o, '#4a443f'


def lake(W, H, portrait):
    """Evening by the lake: sun, far shore, pines, a small sauna cabin and its dock."""
    u = min(W, H) / 100
    hz = H * (0.60 if portrait else 0.62)
    o = [rect(0, 0, W, H, P['paper2'])]
    sx, sy, sr = (W * .68, hz - 30 * u, 9 * u) if portrait else (W * .70, hz - 26 * u, 8 * u)
    o.append(f'<circle cx="{f(sx)}" cy="{f(sy)}" r="{f(sr)}" fill="{P["ember"]}"/>')
    # far shore
    o.append(f'<path d="M0 {f(hz - 8 * u)}C{f(W * .2)} {f(hz - 22 * u)} {f(W * .38)} {f(hz - 20 * u)} {f(W * .52)} {f(hz - 9 * u)}C{f(W * .68)} {f(hz - 21 * u)} {f(W * .86)} {f(hz - 19 * u)} {W} {f(hz - 7 * u)}V{f(hz + 1)}H0z" fill="{P["felt1"]}"/>')

    def pine(x, h, c):
        w = h * .42
        return (f'<path d="M{f(x)} {f(hz - h)}l{f(w * .55)} {f(h * .42)}h{f(-w * .2)}l{f(w * .5)} {f(h * .36)}h{f(-w * 1.7)}l{f(w * .5)} {f(-h * .36)}h{f(-w * .2)}z" fill="{c}"/>'
                + rect(x - h * .03, hz - h * .24, h * .06, h * .24, P['wood4']))
    rnd = random.Random(2)
    xs = [(.04, 26), (.12, 19), (.2, 14), (.86, 24), (.95, 17), (.78, 13)] if portrait else [(.03, 24), (.07, 17), (.12, 21), (.17, 13), (.84, 22), (.89, 15), (.94, 20), (.985, 14), (.56, 11)]
    for k, (fx, h) in enumerate(xs):
        o.append(pine(W * fx, h * u, P['leaf2'] if k % 2 == 0 else P['leaf']))
    # cabin
    cw, chh = 22 * u, 12.5 * u
    cx0 = W * (0.30 if portrait else 0.30) - cw / 2
    o.append(rect(cx0 + cw * .68, hz - chh - 9.5 * u, 3 * u, 7 * u, P['ink2'], .3 * u))
    o.append(rect(cx0, hz - chh, cw, chh, P['wood2']))
    for k in (1, 2, 3):
        o.append(line(f'M{f(cx0)} {f(hz - chh + chh * k / 4)}h{f(cw)}', P['wood3'], .3 * u))
    o.append(f'<path d="M{f(cx0 - 3 * u)} {f(hz - chh + .8 * u)}L{f(cx0 + cw / 2)} {f(hz - chh - 10 * u)}L{f(cx0 + cw + 3 * u)} {f(hz - chh + .8 * u)}h{f(-3 * u)}L{f(cx0 + cw / 2)} {f(hz - chh - 7.6 * u)}L{f(cx0)} {f(hz - chh + .8 * u)}z" fill="{P["ink"]}"/>')
    o.append(f'<path d="M{f(cx0)} {f(hz - chh + .8 * u)}L{f(cx0 + cw / 2)} {f(hz - chh - 7.6 * u)}L{f(cx0 + cw)} {f(hz - chh + .8 * u)}z" fill="{P["wood3"]}"/>')
    o.append(rect(cx0 + 3.4 * u, hz - 8.4 * u, 5.6 * u, 8.4 * u, P['wood4'], .4 * u))
    o.append(rect(cx0 + 12.6 * u, hz - 8.2 * u, 6 * u, 4.8 * u, P['ink2'], .4 * u))
    o.append(rect(cx0 + 13.3 * u, hz - 7.5 * u, 4.6 * u, 3.4 * u, P['glow'], .2 * u))
    o.append(line(wisp_d(cx0 + cw * .68 + 1.5 * u, hz - chh - 10.5 * u, 13 * u, 1.6 * u, 3), P['white'], 1.4 * u))
    # shore line and water
    o.append(rect(0, hz - .2 * u, W, 1.6 * u, P['wood3']))
    o.append(rect(0, hz + 1.3 * u, W, H, P['water']))
    # dock
    dx0 = cx0 + cw - 2 * u
    o.append(rect(dx0, hz + .1 * u, 17 * u, 1.5 * u, P['wood2'], .2 * u))
    for k in (2.2, 8, 13.8):
        o.append(rect(dx0 + k * u, hz + .1 * u, 1.1 * u, 5 * u, P['wood4'], .2 * u))
    # sun glitter and ripples
    for k, (dw, dy) in enumerate(((11, 7), (15, 11), (8, 15), (12, 19.5), (6, 24))):
        o.append(rect(sx - dw * u / 2 + (k % 2) * 1.5 * u, hz + dy * u, dw * u, 1.1 * u, P['ember'], .55 * u, ' opacity=".55"'))
    for _ in range(9 if portrait else 12):
        rx, ry, rw = rnd.uniform(.04, .9) * W, hz + rnd.uniform(5, (H - hz) / u - 12) * u, rnd.uniform(5, 11) * u
        if abs(rx + rw / 2 - sx) < 14 * u:
            continue
        o.append(rect(rx, ry, rw, .7 * u, P['white'], .35 * u, ' opacity=".7"'))
    return o, P['water2']


WALLS = [
    ('heat-ladder', 'Heat ladder', heat_ladder),
    ('steam', 'Steam', steam),
    ('planks', 'Planks', planks),
    ('hat-on-the-bench', 'Hat on the bench', hat),
    ('water-on-stones', 'Water on the stones', stones),
    ('lake-evening', 'Lake evening', lake),
]


def main():
    only = [a for a in sys.argv[1:]]
    for kind, (W, H) in SIZES.items():
        os.makedirs(os.path.join(ROOT, kind), exist_ok=True)
        for name, title, fn in WALLS:
            if only and name not in only:
                continue
            body, sig = fn(W, H, H > W)
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                   f'<title>{title} - DIVELUX sauna wallpaper</title><clipPath id="c"><rect width="{W}" height="{H}"/></clipPath>'
                   f'<g clip-path="url(#c)">{"".join(body)}{sign(W, H, sig, H > W)}</g></svg>\n')
            base = os.path.join(ROOT, kind, f'{name}-{kind}-{W}x{H}')
            open(base + '.svg', 'w', encoding='utf-8').write(svg)
            g.render(svg, base + '.png')
            print(f'{name:18} {kind:8} {W}x{H}  png {os.path.getsize(base + ".png") // 1024} KB  svg {os.path.getsize(base + ".svg") // 1024} KB')


if __name__ == '__main__':
    main()
