"""Title logo (8 OBJ sprites, 8bpp, 1D, at screen x 32..256 y 0..128): 真・女神転生 / デビルチルドレン / 炎の書.
Each sprite is one LZ77 block; slots: pairs in the literal pool at 0x0072D8.. (stride 8) and table 0x0F98C0.. (stride 4).
Palette: OBJ palette (256 colours) from a title VRAM dump (work/qa/title/title.pal.bin) - only used for previews.

python -X utf8 tools/titlelogo.py dump OUT.png      original logo as an indexed PNG (palette from the dump)
python -X utf8 tools/titlelogo.py preview OUT.png   English logo
gen() -> list of (slots, LZ77 bytes)
"""
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz

ROOT = Path(__file__).resolve().parents[1]
X0 = 32                      # canvas x 0 = screen x 32
# (block, slots, canvas x, y, w, h)
SPRITES = [
    (0x0FCF98, (0x0072D8, 0x0F98C0), 0, 0, 64, 64),
    (0x0FD694, (0x0072E0, 0x0F98C4), 64, 0, 64, 64),
    (0x0FDF9C, (0x0072E8, 0x0F98C8), 128, 0, 64, 64),
    (0x0FE4E8, (0x0072F0, 0x0F98CC), 192, 0, 32, 64),
    (0x0FE5E4, (0x0072F8, 0x0F98D0), 0, 64, 64, 64),
    (0x0FE8F8, (0x007300, 0x0F98D4), 64, 64, 64, 64),
    (0x0FECDC, (0x007308, 0x0F98D8), 128, 64, 64, 64),
    (0x0FEFB4, (0x007310, 0x0F98DC), 192, 64, 32, 64),
]
W, H = 224, 128


def palette():
    import struct
    pal = (ROOT / 'work/qa/title/title.pal.bin').read_bytes()[0x200:0x400]
    out = []
    for i in range(256):
        c = struct.unpack_from('<H', pal, 2 * i)[0]
        out += [(c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3]
    return out


def load():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    im = Image.new('P', (W, H), 0)
    for blk, _, x0, y0, w, h in SPRITES:
        d, _ = lz.decompress(rom, blk)
        tw = w // 8
        for t in range(tw * (h // 8)):
            for y in range(8):
                for x in range(8):
                    im.putpixel((x0 + (t % tw) * 8 + x, y0 + (t // tw) * 8 + y), d[t * 64 + y * 8 + x])
    if (ROOT / 'work/qa/title/title.pal.bin').exists():     # preview colours only; the build needs indices
        im.putpalette(palette())
    return im


def save_blocks(im):
    out = []
    for _, slots, x0, y0, w, h in SPRITES:
        tw = w // 8
        d = bytearray(w * h)
        for t in range(tw * (h // 8)):
            for y in range(8):
                for x in range(8):
                    d[t * 64 + y * 8 + x] = im.getpixel((x0 + (t % tw) * 8 + x, y0 + (t // tw) * 8 + y))
        out.append((slots, lz.compress(bytes(d))))
    return out


FONTS = 'C:/Windows/Fonts/'
ORB = (87, 74, 12.5)          # pentagram orb in the banner (centre x, y, radius): kept when the title is erased
OUTLINE, CLEAR = 33, 0
GOLD = [58, 57, 55, 54, 53, 51, 48, 46, 45]           # DEVIL CHILDREN fill, top -> bottom (as the katakana)
RED = [41, 40, 39, 38, 37, 37]                         # SHIN MEGAMI TENSEI fill, outline white
WHITE = 60


def mask(text, font, size, box_w, box_h, scale=4):
    """Text rendered big, squeezed into box_w x box_h, thresholded -> set of (x, y)."""
    from PIL import ImageDraw, ImageFont
    f = ImageFont.truetype(FONTS + font, size * scale)
    l, t, r, b = f.getbbox(text)
    m = Image.new('L', (r - l, b - t), 0)
    ImageDraw.Draw(m).text((-l, -t), text, font=f, fill=255)
    m = m.resize((box_w, box_h), Image.LANCZOS)
    return {(x, y) for x in range(box_w) for y in range(box_h) if m.getpixel((x, y)) >= 110}


def grow(px, n):
    out = set(px)
    for _ in range(n):
        out |= {(x + dx, y + dy) for x, y in out for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    return out


def make():
    """English logo from the original: SHIN MEGAMI TENSEI / DEVIL CHILDREN / Book of Fire (banner and orb kept)."""
    im = load()
    ox, oy, rr = ORB
    for y in range(64):                  # erase the JP title above the banner, keep the orb
        for x in range(W):
            if (x - ox) ** 2 + (y - oy) ** 2 > rr ** 2:
                im.putpixel((x, y), CLEAR)
    for y in range(69, 81):              # erase 炎の書 on the red banner
        for x in range(100, 164):
            im.putpixel((x, y), 37)

    def paint(px, x0, y0, fill, edge, n):
        h = max(y for _, y in px) + 1
        for x, y in grow(px, n):
            if 0 <= x0 + x < W and 0 <= y0 + y < H:
                im.putpixel((x0 + x, y0 + y), edge)
        for x, y in px:
            im.putpixel((x0 + x, y0 + y), fill[min(len(fill) - 1, y * len(fill) // h)])

    # canvas x 88 = screen centre (the banner is centred there too)
    top = mask('SHIN MEGAMI TENSEI', 'ariblk.ttf', 12, 124, 11)
    paint(top, 88 - 62, 3, RED, WHITE, 1)
    main = mask('DEVIL CHILDREN', 'impact.ttf', 40, 172, 34)
    mx = 88 - 86
    # drop shadow (outline colour, 2 px down-right), then outline + gold fill
    shadow = {(x + 2, y + 2) for x, y in grow(main, 2)}
    for x, y in shadow:
        if 0 <= mx + x < W and 0 <= 19 + y < H:
            im.putpixel((mx + x, 19 + y), OUTLINE)
    paint(main, mx, 19, GOLD, OUTLINE, 2)
    sub = mask('Book of Fire', 'tahomabd.ttf', 11, 58, 9)
    for x, y in sub:
        im.putpixel((103 + x, 70 + y), WHITE)
    return im


def english():
    return make()


def gen():
    return save_blocks(english())


if __name__ == '__main__':
    cmd, out = sys.argv[1], sys.argv[2]
    im = load() if cmd == 'dump' else english()
    im.save(out)
    if out.endswith('.png'):
        im.convert('RGB').resize((W * 3, H * 3), Image.NEAREST).save(out[:-4] + '_x3.png')
