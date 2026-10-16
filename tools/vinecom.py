"""Vinecom screen (START > Vinecom): full-screen BG picture, 4bpp tiles in LZ77 block 0x12BFAC (slot 0x223C44,
decompresses to VRAM 0; BG3 map at VRAM 0xF800 is linear: screen tile (tx, ty) -> tile ty*32 + tx, row 0 -> tx + 1).
Seven label plates hold katakana in colour F (E = shading) on rows striped 2/4. Each plate's text is erased to its
stripe colour and redrawn in English with font/en8.txt, centred in the plate.
gen() -> (slots, LZ77 bytes);  python -X utf8 tools/vinecom.py preview OUT.png
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz
import mkfont

ROOT = Path(__file__).resolve().parents[1]
BLOCK, SLOTS = 0x12BFAC, (0x223C44,)
# screen rects (x0, y0, x1, y1) of each plate interior, English label (initials match the star: A D O W N S C)
# (わかれる = Dismiss, as in the Vine Center list)
LABELS = [((2, 42, 47, 53), 'Access'), ((10, 66, 54, 77), 'DemiDex'), ((18, 90, 64, 101), 'Options'),
          ((170, 26, 213, 37), 'Dismiss'), ((193, 50, 238, 61), 'Reorder'), ((193, 74, 238, 85), 'Status'),
          ((178, 98, 219, 109), 'Card')]


# selected-label highlight: OBJ 64x16 (two 32x16 sprites, 1D, one LZ77 block each; slots 0x223CF4 + 8k, +4),
# a copy of the plate with text colours B/C; sprite screen origin per label (same order as LABELS)
HL_BLOCKS = [(0x136C28, 0x136CC4), (0x136D28, 0x136DD8), (0x136E48, 0x136EF4), (0x136F68, 0x13700C),
             (0x137080, 0x13713C), (0x1371B4, 0x137248), (0x1372C4, 0x137340)]
HL_ORIGIN = [(0, 40), (8, 64), (16, 88), (168, 24), (192, 48), (192, 72), (176, 96)]


def tile_of(x, y):
    tx, ty = x // 8, y // 8
    return tx + 1 if ty == 0 else ty * 32 + tx


def relabel(get, put, rect, text, ink, x_off=0, y_off=0):
    """Erase colours `ink` inside rect (screen coords) to each row's stripe colour, draw text in ink[1].
    get/put take coordinates already shifted by (x_off, y_off)."""
    g = mkfont.load(ROOT / 'font/en8.txt', 8)
    x0, y0, x1, y1 = rect[0] - x_off, rect[1] - y_off, rect[2] - x_off, rect[3] - y_off
    top = min(y for y in range(y0, y1) for x in range(x0, x1) if get(x, y) in ink)
    for y in range(y0, y1):
        bg = Counter(get(x, y) for x in range(x0, x1) if get(x, y) not in ink).most_common(1)[0][0]
        for x in range(x0, x1):
            if get(x, y) in ink:
                put(x, y, bg)
    w = sum(g[ord(c)][0] for c in text) - 1
    assert w <= x1 - x0, (text, w)
    x = x0 + (x1 - x0 - w) // 2
    for c in text:
        cw, rows = g[ord(c)]
        for yy, r in enumerate(rows):
            for xx, ch in enumerate(r):
                if ch == '#':
                    put(x + xx, top + yy, ink[1])
        x += cw


def nib(d, i, sh):
    return (d[i] >> sh) & 15


def gen_data():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d = bytearray(lz.decompress(rom, BLOCK)[0])

    def at(x, y):
        return tile_of(x, y) * 32 + (y % 8) * 4 + (x % 8) // 2, 4 * (x & 1)

    def put(x, y, v):
        i, sh = at(x, y)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for rect, text in LABELS:
        relabel(lambda x, y: nib(d, *at(x, y)), put, rect, text, (0xE, 0xF))
    return bytes(d)


def gen_hl():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    out = []
    for k, ((b0, b1), (ox, oy), (rect, text)) in enumerate(zip(HL_BLOCKS, HL_ORIGIN, LABELS)):
        d = bytearray(lz.decompress(rom, b0)[0] + lz.decompress(rom, b1)[0])

        def at(x, y):
            s, lx = x // 32, x % 32
            return (s * 8 + (y // 8) * 4 + lx // 8) * 32 + (y % 8) * 4 + (lx % 8) // 2, 4 * (lx & 1)

        def put(x, y, v):
            i, sh = at(x, y)
            d[i] = (d[i] & ~(15 << sh)) | (v << sh)

        relabel(lambda x, y: nib(d, *at(x, y)), put, rect, text, (0xB, 0xC), ox, oy)
        out.append(((0x223CF4 + 8 * k,), lz.compress(bytes(d[:256]))))
        out.append(((0x223CF8 + 8 * k,), lz.compress(bytes(d[256:]))))
    return out


def gen():
    return [(SLOTS, lz.compress(gen_data()))] + gen_hl()


if __name__ == '__main__' and sys.argv[1:2] == ['preview']:
    from PIL import Image
    d = gen_data()
    im = Image.new('L', (240, 112))
    for y in range(112):
        for x in range(240):
            i = tile_of(x, y) * 32 + (y % 8) * 4 + (x % 8) // 2
            im.putpixel((x, y), ((d[i] >> (4 * (x & 1))) & 15) * 17)
    im.resize((960, 448), Image.NEAREST).save(sys.argv[2])
