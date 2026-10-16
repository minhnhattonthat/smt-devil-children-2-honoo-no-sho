"""Screen-title plates (OBJ 64x32, 1D, 4bpp, one LZ77 block each, see docs/re/graphics.md).
Style A (Dismiss / Reorder ally screens): flat plate rows 9-31 striped D/E, text colour 1 -> redrawn with font/en12.txt.
Style B (gfx table 0x223D2C..0x223D44): italic shaded plate rows 1-15 striped C/E -> Tahoma Bold italic
  (tools/menulabels.render), fill A, shadow B.
gen() -> list of (slots, LZ77 bytes);  python -X utf8 tools/headers.py preview OUT.png
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz
import menulabels
import mkfont

ROOT = Path(__file__).resolve().parents[1]
STYLE_A = [(0x12EEF0, (0x01B1F8, 0x0FAA60), 'Reorder'), (0x131294, (0x0183A8, 0x0FA924), 'Dismiss')]
STYLE_B = [(0x1282BC, (0x223D2C,), 'Status'), (0x12859C, (0x223D30,), 'Dismiss'), (0x128A28, (0x223D34,), 'DemiDex'),
           (0x128D9C, (0x223D38,), 'Reorder'), (0x129380, (0x223D3C,), 'Options'), (0x129860, (0x223D40,), 'Set'),
           (0x12DBFC, (0x223D44,), 'Access')]


class Sprite:
    def __init__(self, data):
        self.d = bytearray(data)

    def at(self, x, y):
        return ((y // 8) * 8 + x // 8) * 32 + (y % 8) * 4 + (x % 8) // 2, 4 * (x & 1)

    def get(self, x, y):
        i, sh = self.at(x, y)
        return (self.d[i] >> sh) & 15

    def put(self, x, y, v):
        i, sh = self.at(x, y)
        self.d[i] = (self.d[i] & ~(15 << sh)) | (v << sh)

    def erase(self, x0, y0, x1, y1, ink):
        for y in range(y0, y1):
            bg = Counter(self.get(x, y) for x in range(x0, x1) if self.get(x, y) not in ink).most_common(1)[0][0]
            for x in range(x0, x1):
                if self.get(x, y) in ink:
                    self.put(x, y, bg)


def style_a(data, text):
    s = Sprite(data)
    s.erase(0, 16, 47, 27, (1,))
    g = mkfont.load(ROOT / 'font/en12.txt', 12)
    w = sum(g[ord(c)][0] for c in text) - 1
    assert w <= 44, (text, w)
    x = 1 + (46 - w) // 2
    for c in text:
        cw, rows = g[ord(c)]
        for yy, r in enumerate(rows):
            for xx, ch in enumerate(r):
                if ch == '#':
                    s.put(x + xx, 15 + yy, 1)
        x += cw
    return bytes(s.d)


def style_b(data, text):
    s = Sprite(data)
    s.erase(5, 3, 60, 14, (0x9, 0xA, 0xB, 0xD, 0xF))     # plate border (B) is column 60
    pix = menulabels.render(text)           # 64x16: 0 none, 1 outline, 4-6 fill (centred in 64)
    for y in range(16):
        for x in range(64):
            if pix[y][x] >= 4 and 3 <= y < 14 and 5 <= x < 56:
                s.put(x, y, 0xA)
                if pix[min(15, y + 1)][min(63, x + 1)] < 4 and y + 1 < 14 and x + 1 < 56:
                    s.put(x + 1, y + 1, 0xB)
    return bytes(s.d)


def gen():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    out = []
    for blk, slots, text in STYLE_A:
        out.append((slots, lz.compress(style_a(lz.decompress(rom, blk)[0], text))))
    for blk, slots, text in STYLE_B:
        out.append((slots, lz.compress(style_b(lz.decompress(rom, blk)[0], text))))
    return out


if __name__ == '__main__' and sys.argv[1:2] == ['preview']:
    from PIL import Image
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    items = [(style_a(lz.decompress(rom, b)[0], t)) for b, _, t in STYLE_A] + \
            [(style_b(lz.decompress(rom, b)[0], t)) for b, _, t in STYLE_B]
    im = Image.new('L', (64 * 3, 32 * 3))
    for k, d in enumerate(items):
        s = Sprite(d)
        for y in range(32):
            for x in range(64):
                im.putpixel(((k % 3) * 64 + x, (k // 3) * 32 + y), s.get(x, y) * 17)
    im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(sys.argv[2])
