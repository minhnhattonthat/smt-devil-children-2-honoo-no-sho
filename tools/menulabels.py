"""Field-menu option labels (OBJ graphics): table 0x223BCC, one 64x16 label = 2 LZ77 blocks of 32x16 (4x2 tiles,
1D layout), palette index 1 = outline, 2-6 = fill shades (6 = brightest).

gen() -> {table index: LZ77 bytes}; tools/build.py writes them to free space and repoints the table.
python -X utf8 tools/menulabels.py preview OUT.png   (renders the English labels, zoomed)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz

ROOT = Path(__file__).resolve().parents[1]
TABLE = 0x223BCC
LABELS = [(0, 'Vinecom'), (2, 'Magic'), (4, 'Items'), (6, 'Settings'), (8, 'Save')]
W, H = 64, 16


def render(text):
    f = ImageFont.truetype(str(ROOT / 'font/LiberationSans-Bold.ttf'), 11)
    m = Image.new('L', (W + 8, H), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = '1'
    d.text((4, 1), text, font=f, fill=255)
    # italic: shear rows to the right towards the top
    ink = [[1 if m.getpixel((x, y)) > 127 else 0 for x in range(W + 8)] for y in range(H)]
    sh = [[0] * (W + 8) for _ in range(H)]
    for y in range(H):
        s = (H - 1 - y) // 4
        for x in range(W + 8):
            if ink[y][x] and x + s < W + 8:
                sh[y][x + s] = 1
    # crop/centre horizontally into W
    cols = [x for x in range(W + 8) if any(sh[y][x] for y in range(H))]
    x0 = cols[0] - max(0, (W - (cols[-1] - cols[0] + 1)) // 2) if cols else 0
    pix = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            sx = x + x0
            if 0 <= sx < W + 8 and sh[y][sx]:
                pix[y][x] = 6 if y < 8 else (5 if y < 11 else 4)
    out = [[pix[y][x] for x in range(W)] for y in range(H)]
    for y in range(H):
        for x in range(W):
            if pix[y][x] == 0 and any(0 <= y + dy < H and 0 <= x + dx < W and pix[y + dy][x + dx]
                                       for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                out[y][x] = 1
    return out


def to_blocks(pix):
    """64x16 indexes -> two 32x16 sprites, each 8 tiles (4 wide x 2 tall, 1D), 4bpp."""
    blocks = []
    for half in range(2):
        data = bytearray()
        for ty in range(2):
            for tx in range(4):
                for y in range(8):
                    for x in range(0, 8, 2):
                        px = half * 32 + tx * 8 + x
                        py = ty * 8 + y
                        data.append(pix[py][px] | pix[py][px + 1] << 4)
        blocks.append(bytes(data))
    return blocks


def gen():
    out = {}
    for idx, text in LABELS:
        a, b = to_blocks(render(text))
        out[idx] = lz.compress(a)
        out[idx + 1] = lz.compress(b)
    return out


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'preview':
        pal = {0: (0, 0, 160), 1: (20, 20, 20), 4: (200, 200, 120), 5: (230, 230, 170), 6: (255, 255, 255)}
        im = Image.new('RGB', (W, H * len(LABELS)))
        for k, (_, t) in enumerate(LABELS):
            p = render(t)
            for y in range(H):
                for x in range(W):
                    im.putpixel((x, k * H + y), pal.get(p[y][x], (255, 0, 0)))
        im.resize((W * 4, H * len(LABELS) * 4), Image.NEAREST).save(sys.argv[2])
        print('wrote', sys.argv[2])
