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


# A second copy of the same six buttons, one LZ77 block each, palette rows 6/7 (table 0x223F00..0x223F14).
SINGLE = [(0x1280D0, 0x223F00), (0x1284DC, 0x223F04), (0x12893C, 0x223F08), (0x128CB0, 0x223F0C),
          (0x1292A0, 0x223F10), (0x12977C, 0x223F14)]   # かな カナ ABC もどる すすむ 決定 (WORDS order)


def draw(d, btn, word, odd, even):
    g = mkfont.load(ROOT / 'font/en8.txt', 8)

    def put(x, y, v):
        t = btn * 8 + (y // 8) * 4 + x // 8
        i = t * 32 + (y % 8) * 4 + (x % 8) // 2
        sh = 4 * (x & 1)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    for y in range(3, 14):
        for x in range(2, 30):
            put(x, y, odd if y % 2 else even)
    width = sum(g[ord(c)][0] for c in word) - 1
    x = 2 + (28 - width) // 2
    for c in word:
        cw, rows = g[ord(c)]
        for yy, r in enumerate(rows):
            for xx, ch in enumerate(r):
                if ch == '#' and 2 <= x + xx < 30:
                    put(x + xx, 4 + yy, 0xE)
        x += cw


def gen():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d = bytearray(lz.decompress(rom, BLOCK)[0])
    for btn, w in enumerate(WORDS):
        draw(d, btn, w, 2, 3)
    return SLOTS, lz.compress(bytes(d))


def gen_single():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    out = []
    for (blk, slot), w in zip(SINGLE, WORDS):
        d = bytearray(lz.decompress(rom, blk)[0])
        draw(d, 0, w, 6, 7)
        out.append(((slot,), lz.compress(bytes(d))))
    return out
