#!/usr/bin/env python3
"""Small shared helpers for the DIVELUX open graphics builds.

- render(svg, out, ...)  : SVG -> PNG with resvg (pip install resvg-py), no browser needed
- text_path(...)         : text -> SVG path data (fontTools), so SVG files do not depend on installed fonts
- PAL                    : the brand palette

Fonts (Bricolage Grotesque Bold, Inter Regular/SemiBold, SIL OFL 1.1) are looked up in $SAUNA_FONTS or ../../_fonts.
MIT License - DIVELUX, https://diveluxsaunahat.com
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _fonts_dir():
    for c in (os.environ.get('SAUNA_FONTS'), os.path.join(HERE, '..', '..', '_fonts'),
              os.path.join(HERE, '..', '..', '..', '_fonts'), os.path.join(HERE, 'fonts')):
        if c and os.path.isdir(c):
            return os.path.abspath(c)
    raise SystemExit('fonts not found: set SAUNA_FONTS to a folder with BricolageGrotesque-Bold.ttf and Inter-*.ttf')


FONT_FILES = {'display': 'BricolageGrotesque-Bold.ttf', 'text': 'Inter-Regular.ttf', 'semi': 'Inter-SemiBold.ttf'}
# family names as stored inside the font files (what a renderer matches on)
FAMILY = {'display': 'Bricolage Grotesque 96pt ExtraBold', 'text': 'Inter', 'semi': 'Inter SemiBold'}

PAL = {
    'paper': '#f6f3ee', 'paper2': '#efe9df', 'line': '#e3ddd3',
    'ink': '#1b1512', 'ink2': '#3a2a20', 'night': '#1c110b', 'muted': '#6f655c',
    'ember': '#f0762e', 'ember2': '#c9561a', 'glow': '#f7b27a',
    'wood1': '#ecd6b2', 'wood2': '#d9b683', 'wood3': '#b98a52', 'wood4': '#8a5f35',
    'felt1': '#c9c4bb', 'felt2': '#a39d94', 'felt3': '#7b756d',
    'stone1': '#8d867e', 'stone2': '#6a635c', 'stone3': '#4a443f',
    'water': '#a9c3c8', 'water2': '#7ea3ab', 'white': '#ffffff',
    'leaf': '#6f8f5a', 'leaf2': '#4f6f42',
}


def font_path(kind='display'):
    return os.path.join(_fonts_dir(), FONT_FILES[kind])


def render(svg, out=None, width=None, height=None, zoom=None, bg=None):
    """svg: markup string or path to .svg. Returns PNG bytes, writes `out` if given."""
    import resvg_py
    kw = dict(font_files=[font_path(k) for k in FONT_FILES], skip_system_fonts=True,
              font_family=FAMILY['text'], sans_serif_family=FAMILY['text'])
    if width:
        kw['width'] = int(width)
    if height:
        kw['height'] = int(height)
    if zoom:
        kw['zoom'] = float(zoom)
    if bg:
        kw['background'] = bg
    if svg.lstrip().startswith('<'):
        data = resvg_py.svg_to_bytes(svg_string=svg, **kw)
    else:
        data = resvg_py.svg_to_bytes(svg_path=svg, **kw)
    data = bytes(data)
    if out:
        with open(out, 'wb') as f:
            f.write(data)
    return data


_FONTS = {}


def _font(kind):
    if kind not in _FONTS:
        from fontTools.ttLib import TTFont
        t = TTFont(font_path(kind))
        _FONTS[kind] = (t, t.getGlyphSet(), t.getBestCmap(), t['head'].unitsPerEm, _kern_pairs(t))
    return _FONTS[kind]


def _kern_pairs(t):
    """Pair kerning from GPOS (PairPos formats 1 and 2), enough for headings."""
    pairs = {}
    try:
        gpos = t['GPOS'].table
        feats = [f for f in gpos.FeatureList.FeatureRecord if f.FeatureTag == 'kern']
        idx = sorted({i for f in feats for i in f.Feature.LookupListIndex})
        for i in idx:
            lk = gpos.LookupList.Lookup[i]
            for st in lk.SubTable:
                if st.LookupType == 9:
                    st = st.ExtSubTable
                if st.LookupType != 2:
                    continue
                cov = st.Coverage.glyphs
                if st.Format == 1:
                    for g1, ps in zip(cov, st.PairSet):
                        for pv in ps.PairValueRecord:
                            v = pv.Value1.XAdvance if pv.Value1 and hasattr(pv.Value1, 'XAdvance') else 0
                            if v:
                                pairs.setdefault((g1, pv.SecondGlyph), v)
                else:
                    c1, c2 = st.ClassDef1.classDefs, st.ClassDef2.classDefs
                    by2 = {}
                    for g, c in c2.items():
                        by2.setdefault(c, []).append(g)
                    for g1 in cov:
                        rec = st.Class1Record[c1.get(g1, 0)]
                        for ci, r in enumerate(rec.Class2Record):
                            v = r.Value1.XAdvance if r.Value1 and hasattr(r.Value1, 'XAdvance') else 0
                            if v and ci:
                                for g2 in by2.get(ci, []):
                                    pairs.setdefault((g1, g2), v)
    except Exception:
        pass
    return pairs


def text_width(text, size, kind='display', tracking=0.0):
    t, gs, cmap, upm, kern = _font(kind)
    w, prev = 0.0, None
    for ch in text:
        g = cmap.get(ord(ch), '.notdef')
        if prev:
            w += kern.get((prev, g), 0)
        w += gs[g].width + tracking * upm
        prev = g
    return (w - tracking * upm) * size / upm


def text_path(text, x, y, size, kind='display', anchor='start', tracking=0.0, nd=2):
    """Returns SVG path data for `text` with the baseline at y. anchor: start | middle | end."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    t, gs, cmap, upm, kern = _font(kind)
    s = size / upm
    w = text_width(text, size, kind, tracking)
    if anchor == 'middle':
        x -= w / 2
    elif anchor == 'end':
        x -= w
    fmt = lambda v: ('%.*f' % (nd, v)).rstrip('0').rstrip('.') or '0'
    pen = SVGPathPen(gs, ntos=fmt)
    cx, prev = 0.0, None
    for ch in text:
        g = cmap.get(ord(ch), '.notdef')
        if prev:
            cx += kern.get((prev, g), 0)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x + cx * s, y)))
        cx += gs[g].width + tracking * upm
        prev = g
    return pen.getCommands()


def contact_sheet(cells, cols, cell_w, cell_h, title, subtitle, footer_left='', footer_right='Made by DIVELUX — diveluxsaunahat.com',
                  dark=False, width=1600, pad=64, label_size=13, grid_lines=True, cell_bg=None, footer_gap=56):
    """cells: list of (inner_svg_markup, label). inner markup is placed in a cell_w x cell_h box (origin top-left)."""
    bg, ink, mut, line = (PAL['night'], PAL['paper'], '#b9aea3', '#3a2a20') if dark else (PAL['paper'], PAL['ink'], PAL['muted'], PAL['line'])
    rows = (len(cells) + cols - 1) // cols
    top = 186
    gh = rows * cell_h
    height = top + gh + footer_gap + 40
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         f'<rect width="{width}" height="{height}" fill="{bg}"/>',
         f'<path d="{text_path(title, pad, 100, 54, tracking=-0.01)}" fill="{ink}"/>',
         f'<text x="{pad}" y="144" font-family="Inter" font-size="22" fill="{mut}">{subtitle}</text>']
    for i, (inner, label) in enumerate(cells):
        cx, cy = pad + (i % cols) * cell_w, top + (i // cols) * cell_h
        if cell_bg:
            o.append(f'<rect x="{cx}" y="{cy}" width="{cell_w}" height="{cell_h}" fill="{cell_bg}"/>')
        if grid_lines:
            o.append(f'<rect x="{cx + .5}" y="{cy + .5}" width="{cell_w}" height="{cell_h}" fill="none" stroke="{line}"/>')
        o.append(f'<g transform="translate({cx} {cy})" color="{ink}">{inner}</g>')
        if label:
            o.append(f'<text x="{cx + cell_w / 2}" y="{cy + cell_h - 20}" font-family="Inter" font-size="{label_size}" fill="{mut}" text-anchor="middle">{label}</text>')
    fy = top + gh + footer_gap
    o.append(f'<text x="{pad}" y="{fy}" font-family="Inter" font-size="18" fill="{mut}">{footer_left}</text>')
    o.append(f'<text x="{width - pad}" y="{fy}" font-family="Inter" font-size="18" fill="{mut}" text-anchor="end">{footer_right}</text>')
    o.append('</svg>')
    return '\n'.join(o)
