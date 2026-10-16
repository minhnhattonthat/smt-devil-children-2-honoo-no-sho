"""ビッグ / スモール (LZ77 block 0x15B8EC, slots 0x0CA6F0 0x1059DC): 16 tiles = two 64x8 rows (normal, dimmed),
each "ビッグ" at x 0-31 and "スモール" at x 32-63, outlined 8px text: row 0 fill 6 outline 8, row 1 fill 2 outline 4.
gen() -> (slots, LZ77 bytes)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz
import mkfont

ROOT = Path(__file__).resolve().parents[1]
BLOCK, SLOTS = 0x15B8EC, (0x0CA6F0, 0x1059DC)
WORDS = ['Big', 'Small']


def gen():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d = bytearray(len(lz.decompress(rom, BLOCK)[0]))
    g = mkfont.load(ROOT / 'font/en8.txt', 8)

    def put(x, y, v):
        i = ((y // 8) * 8 + x // 8) * 32 + (y % 8) * 4 + (x % 8) // 2
        sh = 4 * (x & 1)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for row, (fill, edge) in enumerate(((6, 8), (2, 4))):
        for k, w in enumerate(WORDS):
            ink = set()
            x = k * 32 + 1
            for c in w:
                cw, rows = g[ord(c)]
                ink |= {(x + xx, yy) for yy, r in enumerate(rows[:7]) for xx, ch in enumerate(r) if ch == '#'}
                x += cw
            assert x <= k * 32 + 32, w
            for x, y in ink:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if 0 <= y + dy < 8 and k * 32 <= x + dx < k * 32 + 32 and (x + dx, y + dy) not in ink:
                            put(x + dx, row * 8 + y + dy, edge)
            for x, y in ink:
                put(x, row * 8 + y, fill)
    return SLOTS, lz.compress(bytes(d))
