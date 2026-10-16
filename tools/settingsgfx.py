"""Settings screen (START > Settings): BG picture, tiles LZ77 0x1318B4 (slot 0x223C48, -> VRAM 0), map LZ77 0x134620
(slot 0x223C94, 30x20 u16). Button plates carry the labels in colour F on stripes; each label (an ink cluster inside a
band) is erased to its row's stripe colour and redrawn with font/en12.txt. Unchanged map; tiles must be unshared.
gen() -> (slots, LZ77 bytes);  python -X utf8 tools/settingsgfx.py preview OUT.png
"""
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz
import mkfont

ROOT = Path(__file__).resolve().parents[1]
TILES, MAP, SLOTS = 0x1318B4, 0x134620, (0x223C48,)
INK = 0xF
# (band x0, y0, x1, y1), words left to right
BANDS = [((0, 31, 240, 47), ['Message', 'Fast', 'Normal', 'Slow']),
         ((0, 60, 240, 79), ['Animation', 'On', 'Off']),
         ((0, 91, 50, 103), ['Position'])]


def gen_data():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    d = bytearray(lz.decompress(rom, TILES)[0])
    m = lz.decompress(rom, MAP)[0]
    ent = [struct.unpack_from('<H', m, 2 * i)[0] for i in range(600)]
    uses = Counter(e & 0x3FF for e in ent)
    touched = set()

    def at(x, y):
        e = ent[(y // 8) * 30 + x // 8]
        sx = 7 - x % 8 if e & 0x400 else x % 8
        sy = 7 - y % 8 if e & 0x800 else y % 8
        return (e & 0x3FF) * 32 + sy * 4 + sx // 2, 4 * (sx & 1), e & 0x3FF

    def get(x, y):
        i, sh, _ = at(x, y)
        return (d[i] >> sh) & 15

    def put(x, y, v):
        i, sh, t = at(x, y)
        touched.add(t)
        d[i] = (d[i] & ~(15 << sh)) | (v << sh)

    g = mkfont.load(ROOT / 'font/en12.txt', 12)
    for (bx0, by0, bx1, by1), words in BANDS:
        cols = sorted({x for x in range(bx0, bx1) for y in range(by0, by1) if get(x, y) == INK})
        clusters = [[cols[0], cols[0]]]
        for x in cols[1:]:
            if x - clusters[-1][1] > 8:
                clusters.append([x, x])
            else:
                clusters[-1][1] = x
        assert len(clusters) == len(words), (words, clusters)
        ys = [y for y in range(by0, by1) for x in range(bx0, bx1) if get(x, y) == INK]
        top = (min(ys) + max(ys)) // 2 - 5          # one baseline per band; en12 caps ~ rows 1..9
        for (cx0, cx1), word in zip(clusters, words):
            for y in range(by0, by1):
                row = Counter(get(x, y) for x in range(cx0 - 2, cx1 + 3) if get(x, y) != INK)
                bg = row.most_common(1)[0][0]
                for x in range(cx0 - 2, cx1 + 3):
                    if get(x, y) == INK:
                        put(x, y, bg)
            w = sum(g[ord(c)][0] for c in word) - 1
            x = (cx0 + cx1 + 1 - w) // 2
            for c in word:
                cw, rows = g[ord(c)]
                for yy, r in enumerate(rows):
                    for xx, ch in enumerate(r):
                        if ch == '#':
                            put(x + xx, top + yy, INK)
                x += cw
    shared = [t for t in touched if uses[t] > 1]
    assert not shared, 'edited tiles used elsewhere in the map: %s' % shared
    return bytes(d), ent


def gen():
    return SLOTS, lz.compress(gen_data()[0])


if __name__ == '__main__' and sys.argv[1:2] == ['preview']:
    from PIL import Image
    d, ent = gen_data()
    im = Image.new('L', (240, 160))
    for y in range(160):
        for x in range(240):
            e = ent[(y // 8) * 30 + x // 8]
            sx = 7 - x % 8 if e & 0x400 else x % 8
            sy = 7 - y % 8 if e & 0x800 else y % 8
            im.putpixel((x, y), ((d[(e & 0x3FF) * 32 + sy * 4 + sx // 2] >> (4 * (sx & 1))) & 15) * 17)
    im.resize((720, 480), Image.NEAREST).save(sys.argv[2])
