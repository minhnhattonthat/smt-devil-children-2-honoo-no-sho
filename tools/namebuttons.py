"""Name-entry screen buttons (OBJ, LZ77 block 0x127B80; refs 0x035424, 0x100938): six 32x16 sprites (1D, 8 tiles
each): かな カナ ABC もどる すすむ 決定 -> Hira / Kata / ABC / Back / Next / OK (Hira/Kata: flagged short forms of
hiragana/katakana, the page switches). Background rows alternate colour 2 / 3 (x 2..29, y 3..13); text colour E,
drawn with the 8 px English font (font/en8.txt).
gen() -> (slots, LZ77 bytes)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz
import mkfont

ROOT = Path(__file__).resolve().parents[1]
BLOCK, SLOTS = 0x127B80, (0x035424, 0x100938)
WORDS = ['Hira', 'Kata', 'ABC', 'Back', 'Next', 'OK']


def gen():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d, _ = lz.decompress(rom, BLOCK)
    d = bytearray(d)
    g = mkfont.load(ROOT / 'font/en8.txt', 8)

    def put(btn, x, y, v):
        t = btn * 8 + (y // 8) * 4 + x // 8
        i = t * 32 + (y % 8) * 4 + (x % 8) // 2
        sh = 4 * (x & 1)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for btn, w in enumerate(WORDS):
        for y in range(3, 14):
            for x in range(2, 30):
                put(btn, x, y, 2 if y % 2 else 3)
        width = sum(g[ord(c)][0] for c in w) - 1
        x = 2 + (28 - width) // 2
        for c in w:
            cw, rows = g[ord(c)]
            for yy, r in enumerate(rows):
                for xx, ch in enumerate(r):
                    if ch == '#' and 2 <= x + xx < 30:
                        put(btn, x + xx, 4 + yy, 0xE)
            x += cw
    return SLOTS, lz.compress(bytes(d))
