"""Contact sheet of the compressed UI graphics in a pointer table (GBA 4bpp, OBJ 1D layout: 32x16 sprites).

python -X utf8 tools/gfxsheet.py TABLE COUNT OUT.png [--pal work/qa/gfx1/ppu_000090.pal.bin --pal-index 4 --obj]
Each block is decompressed (BIOS LZ77) and drawn as consecutive 32x16 sprites (4x2 tiles each), labelled.
"""
import argparse, struct, sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz

ROOT = Path(__file__).resolve().parents[1]


def pal_colors(pal, index):
    out = []
    for i in range(16):
        v = struct.unpack_from('<H', pal, (index * 16 + i) * 2)[0]
        out.append(((v & 31) * 8, (v >> 5 & 31) * 8, (v >> 10 & 31) * 8))
    return out


def tile_img(data, k, cols):
    im = Image.new('RGB', (8, 8))
    px = im.load()
    for y in range(8):
        for x in range(8):
            b = data[k * 32 + y * 4 + x // 2] if k * 32 + y * 4 + x // 2 < len(data) else 0
            px[x, y] = cols[(b >> (4 * (x & 1))) & 15]
    return im


def block_img(data, cols, sw=4, sh=2):
    nt = len(data) // 32
    per = sw * sh
    ns = max(1, nt // per)
    im = Image.new('RGB', (sw * 8 * ns, sh * 8), (255, 0, 255))
    for s in range(ns):
        for t in range(per):
            k = s * per + t
            if k < nt:
                im.paste(tile_img(data, k, cols), (s * sw * 8 + (t % sw) * 8, (t // sw) * 8))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('table', type=lambda s: int(s, 16))
    ap.add_argument('count', type=int)
    ap.add_argument('out')
    ap.add_argument('--pal', default=str(ROOT / 'work/qa/gfx1/ppu_000090.pal.bin'))
    ap.add_argument('--pal-index', type=int, default=4)
    ap.add_argument('--obj', action='store_true', help='palette from OBJ half of the dump')
    a = ap.parse_args()
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    pal = Path(a.pal).read_bytes()
    if a.obj:
        pal = pal[0x200:]
    cols = pal_colors(pal, a.pal_index)
    rows = []
    for i in range(a.count):
        p = struct.unpack_from('<I', rom, a.table + 4 * i)[0] - 0x08000000
        try:
            d, used = lz.decompress(rom, p)
        except Exception:
            continue
        rows.append((i, p, block_img(d, cols)))
    W = max(r[2].width for r in rows) * 2 + 80
    H = sum(r[2].height * 2 + 4 for r in rows)
    sheet = Image.new('RGB', (W, H), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    y = 0
    for i, p, im in rows:
        d.text((2, y + 4), '%d %06X' % (i, p), fill=(255, 255, 255))
        sheet.paste(im.resize((im.width * 2, im.height * 2), Image.NEAREST), (80, y))
        y += im.height * 2 + 4
    sheet.save(a.out)
    print(len(rows), 'blocks ->', a.out)


if __name__ == '__main__':
    main()
