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


EN8_FROM_GAME = dict([(ord(c), 50 + i) for i, c in enumerate('0123456789')] +
                     [(ord(c), 60 + i) for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ')] +
                     [(ord(c), 86 + i) for i, c in enumerate('abcdefghijklmnopqrstuvwxyz')] +
                     [(ord('!'), 6), (ord('?'), 5), (ord(':'), 4), (ord('/'), 9), (ord('~'), 10), (ord('('), 11),
                      (ord(')'), 12), (ord('+'), 21), (ord('-'), 22), (ord('$'), 26), (ord('%'), 27), (ord('&'), 28),
                      (ord('*'), 29), (ord('@'), 30), (ord('['), 19), (ord(']'), 20)])
EN8_HAND = {  # 8 rows each; glyphs the game font lacks
    0x20: ['...'] * 8,
    0x2E: ['..', '..', '..', '..', '..', '..', '#.', '..'],
    0x2C: ['..', '..', '..', '..', '..', '#.', '#.', '..'],
    0x27: ['#.', '#.', '..', '..', '..', '..', '..', '..'],
    0x22: ['#.#.', '#.#.', '....', '....', '....', '....', '....', '....'],
    0x3B: ['..', '..', '#.', '..', '..', '#.', '#.', '..'],
    0x3D: ['....', '....', '###.', '....', '###.', '....', '....', '....'],
    0x3C: ['....', '..#.', '.#..', '#...', '.#..', '..#.', '....', '....'],
    0x3E: ['....', '#...', '.#..', '..#.', '.#..', '#...', '....', '....'],
    0x5F: ['....', '....', '....', '....', '....', '....', '....', '###.'],
    0x23: ['......', '.#.#..', '#####.', '.#.#..', '#####.', '.#.#..', '......', '......'],
    0x5E: ['.#..', '#.#.', '....', '....', '....', '....', '....', '....'],
    # condensed forms: status lists give a race 4 JP cells (32 px), "Monster" must fit
    0x2D: ['....', '....', '....', '###.', '....', '....', '....', '....'],
    0x4D: ['#...#.', '##.##.', '#.#.#.', '#.#.#.', '#...#.', '#...#.', '#...#.', '......'],
    0x72: ['....', '....', '#.#.', '##..', '#...', '#...', '#...', '....'],
}


def condense(rows):
    """Drop one ink column that repeats its right neighbour (the one nearest the middle) from glyphs >= 5 px ink:
    the game's 8 px Latin is ~1 px wider than the UI fields sized for 8 px kana."""
    ink = len(rows[0]) - 1
    if ink < 5:
        return rows
    cols = [''.join(r[x] for r in rows) for x in range(len(rows[0]))]
    cand = [x for x in range(ink - 1) if cols[x] == cols[x + 1] and '#' in cols[x]]
    if not cand:
        return rows
    del cols[min(cand, key=lambda c: abs(c - (ink - 1) / 2))]
    return [''.join(c[y] for c in cols) for y in range(len(rows))]


def gen_en8():
    sys.path.insert(0, str(ROOT / 'tools'))
    import font as F
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    out = []
    for c in range(0x20, 0x7F):
        if c in EN8_HAND:
            rows = EN8_HAND[c]
        elif c in EN8_FROM_GAME:
            g = F.glyph(rom, F.FONTS['f8'], EN8_FROM_GAME[c])
            cols = [x for x in range(8) if any(g[y][x] for y in range(8))]
            x0, x1 = (cols[0], cols[-1]) if cols else (0, 1)
            rows = condense([''.join('#' if g[y][x] else '.' for x in range(x0, x1 + 1)) + '.' for y in range(8)])
        else:
            rows = ['#.#.', '.#..', '#.#.', '....', '....', '....', '....', '....']   # placeholder
        out.append('= %02X %d' % (c, len(rows[0])))
        out += rows
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
    p.write_text({'en12': gen_en12, 'en8': gen_en8}[a.name](), encoding='utf-8', newline='\n')
    print('wrote', p)
