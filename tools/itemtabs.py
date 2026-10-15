"""Item-menu category tabs (OBJ, LZ77 block 0x132C28 via pointer 0x02391C): 6 tabs of 32x16 (4x2 tiles, 1D),
JP 回復 こうげき ほじょ そのた マソウ 化石 -> English in a hand-made 3x5 pixel font (tab text area is 19x9 px, so full
words only; flagged choices: Fight = attack items, Boost = support items, Gear = マソウ arcane gear).

gen() -> (pointer slot, LZ77 bytes). python -X utf8 tools/itemtabs.py preview OUT.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz

ROOT = Path(__file__).resolve().parents[1]
BLOCK, SLOTS = 0x132C28, (0x02391C, 0x0FAE50)
WORDS = ['HEAL', 'FIGHT', 'BOOST', 'OTHER', 'GEAR', 'FOSSIL']
F = {  # 3x5 (i, l narrower)
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'F': ['###', '#..', '##.', '#..', '#..'], 'G': ['.##', '#..', '#.#', '#.#', '.##'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'], 'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'a': ['...', '##.', '.##', '#.#', '.##'], 'e': ['...', '.#.', '###', '#..', '.##'],
    'g': ['...', '.##', '#.#', '.##', '##.'], 'h': ['#..', '#..', '##.', '#.#', '#.#'],
    'i': ['#', '.', '#', '#', '#'], 'l': ['#', '#', '#', '#', '#'], 'o': ['...', '.#.', '#.#', '#.#', '.#.'],
    'r': ['...', '#.#', '##.', '#..', '#..'], 's': ['...', '.##', '#..', '..#', '##.'],
    't': ['.#.', '###', '.#.', '.#.', '.##'],
    'E': ['###', '#..', '##.', '#..', '###'], 'L': ['#..', '#..', '#..', '#..', '###'], 'I': ['#', '#', '#', '#', '#'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'S': ['.##', '#..', '.#.', '..#', '##.'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
}


def word_pixels(w):
    cols = []
    for k, ch in enumerate(w):
        g = F[ch]
        for x in range(len(g[0])):
            cols.append([g[y][x] == '#' for y in range(5)])
        if k < len(w) - 1:
            cols.append([False] * 5)
    return cols


def gen():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d, _ = lz.decompress(rom, BLOCK)
    d = bytearray(d)

    def get(tab, x, y):
        t = (y // 8) * 4 + x // 8
        b = d[tab * 256 + t * 32 + (y % 8) * 4 + (x % 8) // 2]
        return (b >> (4 * (x & 1))) & 15

    def put(tab, x, y, v):
        t = (y // 8) * 4 + x // 8
        i = tab * 256 + t * 32 + (y % 8) * 4 + (x % 8) // 2
        sh = 4 * (x & 1)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for tab, w in enumerate(WORDS):
        for y in range(3, 14):
            for x in range(2, 23):
                put(tab, x, y, 7 if y % 2 == 0 else 6)
        cols = word_pixels(w)
        x0 = 3 + (19 - len(cols)) // 2
        for i, c in enumerate(cols):
            for y in range(5):
                if c[y]:
                    put(tab, x0 + i, 6 + y, 0xE)
                    if not (i + 1 < len(cols) and cols[i + 1][y]) and x0 + i + 1 < 22:
                        put(tab, x0 + i + 1, 6 + y, 1)
    return SLOTS, lz.compress(bytes(d))


BG_BLOCK, BG_SLOTS = 0x12E8F8, (0x223C58,)   # item-menu frame tiles: the unselected tabs, 32 tiles per row


def gen_bg():
    """Unselected tabs in the menu frame tileset: tab k spans x 48+24k .. +23, rows 0-15; text area x+1..x+22,
    rows 3-12 striped 7 (odd rows) / C (even rows); text colour F."""
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d, _ = lz.decompress(rom, BG_BLOCK)
    d = bytearray(d)

    def put(x, y, v):
        t = (y // 8) * 32 + x // 8
        i = t * 32 + (y % 8) * 4 + (x % 8) // 2
        sh = 4 * (x & 1)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for k, w in enumerate(WORDS):
        x0 = 48 + 24 * k
        for y in range(3, 13):
            for x in range(x0 + 1, x0 + 23):
                put(x, y, 7 if y % 2 else 0xC)
        cols = word_pixels(w)
        sx = x0 + 1 + (22 - len(cols)) // 2
        for i, c in enumerate(cols):
            for y in range(5):
                if c[y]:
                    put(sx + i, 5 + y, 0xF)
    return BG_SLOTS, lz.compress(bytes(d))


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'preview':
        from PIL import Image
        slots, blob = gen()
        d, _ = lz.decompress(blob, 0)
        pal = {0: (0, 0, 0), 1: (30, 30, 30), 5: (90, 60, 60), 6: (200, 120, 140), 7: (170, 90, 110), 8: (60, 30, 40),
               0xE: (255, 255, 255)}
        im = Image.new('RGB', (32, 16 * 6))
        for tab in range(6):
            for y in range(16):
                for x in range(32):
                    t = (y // 8) * 4 + x // 8
                    b = d[tab * 256 + t * 32 + (y % 8) * 4 + (x % 8) // 2]
                    im.putpixel((x, tab * 16 + y), pal.get((b >> (4 * (x & 1))) & 15, (255, 0, 255)))
        im.resize((32 * 6, 16 * 6 * 6), Image.NEAREST).save(sys.argv[2])
