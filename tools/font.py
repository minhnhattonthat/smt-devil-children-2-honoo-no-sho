"""Game fonts: 1bpp tile sheets (8x8 tiles, row-major, `w` tiles wide) with a 16-byte header.

Header (little endian): u32 data size, u16 sheet width in tiles, u16 height in tiles, u16 glyphs per row,
u8 glyph width px, u8 glyph height px, u8 bpp.  Glyph index for code c (renderer 0x080C1DA0):
  c <= 0x80: index c;  else hi=c>>8, lo=c&0xFF: (hi-0x81 (-0x40 if hi>0x9F))*0xBC + lo-0x40 (-1 if lo>0x7F).
Usage: python -X utf8 tools/font.py render [out_dir]   -> work/font_<name>.png with a grid of glyph indexes.
"""
import struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = {"f12": 0x2DA2E0, "f8": 0x2DFB10, "f6": 0x2E21E0}
DATA = 0x10  # bitmap starts after the 16-byte header; tiles row-major, pixel x at bit (x&7) (LSB first)


def header(rom, off):
    size, w, h, cols, gw, gh, bpp = struct.unpack_from('<IHHHBBB', rom, off)
    return dict(size=size, w=w, h=h, cols=cols, gw=gw, gh=gh, bpp=bpp)


def code_to_index(c):
    if c <= 0x80:
        return c
    hi, lo = c >> 8, c & 0xFF
    r = hi - 0x81
    if hi > 0x9F:
        r -= 0x40
    return r * 0xBC + lo - 0x40 - (1 if lo > 0x7F else 0)


def index_to_code(i):
    r, k = divmod(i, 0xBC)
    lo = k + 0x40
    if lo >= 0x7F:
        lo += 1
    hi = r + 0x81
    if hi > 0x9F:
        hi += 0x40
    return hi << 8 | lo


def sheet_pixels(rom, off):
    """Return (W, H, get(x, y)) for the font sheet."""
    hd = header(rom, off)
    data = rom[off + DATA: off + DATA + hd['w'] * hd['h'] * 8]
    W = hd['w'] * 8

    def get(x, y):
        t = (y // 8) * hd['w'] + x // 8
        return data[t * 8 + y % 8] >> (x % 8) & 1
    return W, hd['h'] * 8, get


def glyph(rom, off, index):
    """Rows of bits for glyph `index` (list of lists)."""
    hd = header(rom, off)
    W, H, get = sheet_pixels(rom, off)
    gx, gy = (index % hd['cols']) * hd['gw'], (index // hd['cols']) * hd['gh']
    return [[get(gx + x, gy + y) for x in range(hd['gw'])] for y in range(hd['gh'])]


def render(out_dir):
    from PIL import Image, ImageDraw
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    for name, off in FONTS.items():
        hd = header(rom, off)
        W, H, get = sheet_pixels(rom, off)
        n = (W // hd['gw']) * (H // hd['gh'])
        z, lab = 3, 26
        cw, ch = hd['gw'] * z + lab, hd['gh'] * z + 4
        cols = 20
        im = Image.new('L', (cols * cw, (n // cols + 1) * ch), 255)
        d = ImageDraw.Draw(im)
        for i in range(n):
            g = glyph(rom, off, i)
            ox, oy = (i % cols) * cw, (i // cols) * ch
            d.text((ox, oy), '%d' % i, fill=128)
            for y, row in enumerate(g):
                for x, b in enumerate(row):
                    if b:
                        d.rectangle([ox + lab + x * z, oy + y * z, ox + lab + x * z + z - 1, oy + y * z + z - 1], fill=0)
        im.save(Path(out_dir) / f'font_{name}.png')
        print(name, hd, n, 'glyphs')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render(sys.argv[2] if len(sys.argv) > 2 else ROOT / 'work')
    else:
        print(__doc__)
