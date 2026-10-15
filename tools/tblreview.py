"""Review sheet: game glyph (left) next to the table's char drawn in MS Gothic (right), for checking tbl/jp.tbl.

python -X utf8 tools/tblreview.py TSV OUT.png [--from N --to M] [--below SCORE]
TSV = tbl/jp_auto.tsv-style rows (index, code, char, score ...).
"""
import argparse, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font as F

ROOT = Path(__file__).resolve().parents[1]

ap = argparse.ArgumentParser()
ap.add_argument('tsv'); ap.add_argument('out')
ap.add_argument('--from', dest='lo', type=int, default=0); ap.add_argument('--to', dest='hi', type=int, default=9999)
ap.add_argument('--below', type=float, default=9)
a = ap.parse_args()
rom = (ROOT / 'rom/honoo.gba').read_bytes()
rows = []
for line in open(a.tsv, encoding='utf-8'):
    p = line.rstrip('\n').split('\t')
    i = int(p[0])
    if a.lo <= i <= a.hi and (len(p) < 4 or float(p[3]) < a.below):
        rows.append((i, p[2]))
fnt = ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc', 24)
lab = ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc', 11)
z, cols, cw, ch = 2, 12, 90, 34
im = Image.new('L', (cols * cw, (len(rows) + cols - 1) // cols * ch + 2), 255)
d = ImageDraw.Draw(im)
for k, (i, c) in enumerate(rows):
    ox, oy = (k % cols) * cw, (k // cols) * ch
    d.text((ox, oy), str(i), font=lab, fill=120)
    g = F.glyph(rom, F.FONTS['f12'], i)
    for y, r in enumerate(g):
        for x, b in enumerate(r):
            if b:
                d.rectangle([ox + 26 + x * z, oy + 4 + y * z, ox + 27 + x * z, oy + 5 + y * z], fill=0)
    d.text((ox + 56, oy + 4), c, font=fnt, fill=0)
im.save(a.out)
print(len(rows), 'rows ->', a.out)
