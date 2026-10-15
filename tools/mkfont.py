"""Generate the editable English font files once (font/en12.txt). After that, edit the .txt by hand; build reads it.

python -X utf8 tools/mkfont.py en12 [--force]
Format: per glyph a header line `= XX w` (hex code, advance width px), then H rows of w chars ('#' ink, '.' blank).
"""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def gen_en12():
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf', 11, layout_engine=ImageFont.Layout.BASIC)
    out = []
    for c in range(0x20, 0x7F):
        ch = chr(c)
        im = Image.new('L', (24, 16), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = '1'
        d.text((4, -1), ch, font=f, fill=255)
        cols = [x for x in range(24) if any(im.getpixel((x, y)) > 127 for y in range(12))]
        if not cols:
            x0, w = 0, 3                      # space
        else:
            x0, w = cols[0], cols[-1] - cols[0] + 2   # ink + 1px gap
        out.append('= %02X %d' % (c, w))
        for y in range(12):
            out.append(''.join('#' if im.getpixel((x0 + x, y)) > 127 else '.' for x in range(w)))
    return '\n'.join(out) + '\n'


def load(path, h):
    """-> {code: (width, rows[list of str])}"""
    g = {}
    lines = Path(path).read_text(encoding='utf-8').split('\n')
    i = 0
    while i < len(lines):
        if lines[i].startswith('= '):
            _, code, w = lines[i].split()
            code, w = int(code, 16), int(w)
            rows = [lines[i + 1 + k].ljust(w, '.')[:w] for k in range(h)]
            g[code] = (w, rows)
            i += 1 + h
        else:
            i += 1
    return g


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    p = ROOT / 'font' / (a.name + '.txt')
    if p.exists() and not a.force:
        sys.exit('%s exists (hand-edited?); use --force to regenerate' % p)
    p.parent.mkdir(exist_ok=True)
    p.write_text({'en12': gen_en12}[a.name](), encoding='utf-8', newline='\n')
    print('wrote', p)
