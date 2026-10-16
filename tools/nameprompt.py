"""Name-entry frame tileset (BG, LZ77 block 0x126A3C; refs 0x034C18 0x03637C 0x1008F4 0x1009C0): tiles 12-23 + 24-35 hold
the prompt 名前を入力して下さい as a 96x16 strip (background 9, text E). Redrawn as English with font/en12.txt.
gen() -> (slots, LZ77 bytes)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz
import mkfont

ROOT = Path(__file__).resolve().parents[1]
BLOCK, SLOTS = 0x126A3C, (0x034C18, 0x03637C, 0x1008F4, 0x1009C0)
TEXT = 'Enter a name.'


def gen():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d, _ = lz.decompress(rom, BLOCK)
    d = bytearray(d)
    g = mkfont.load(ROOT / 'font/en12.txt', 12)

    def put(x, y, v):            # 96x16 strip: tiles 12-23 (top 8 rows), 24-35 (bottom 8 rows)
        t = (12 if y < 8 else 24) + x // 8
        i = t * 32 + (y % 8) * 4 + (x % 8) // 2
        sh = 4 * (x & 1)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for y in range(16):
        for x in range(96):
            put(x, y, 9)
    x = 2
    for c in TEXT:
        w, rows = g[ord(c)]
        for yy, r in enumerate(rows):
            for xx, ch in enumerate(r):
                if ch == '#' and x + xx < 96:
                    put(x + xx, 2 + yy, 0xE)
        x += w
    return SLOTS, lz.compress(bytes(d))
