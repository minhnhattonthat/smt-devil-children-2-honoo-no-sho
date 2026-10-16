"""Contact sheets of the dialogue-box area of msgtour shots, labelled with the shot name, for review.

python -X utf8 tools/debug/boxsheet.py [--src work/qa/msgs] [--out work/qa/boxsheets] [--per 48]
Crops y 92..160 of each shot, drops a page identical to the previous page of the same message.
"""
import argparse, glob, os, re
from PIL import Image, ImageChops, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('--src', default='work/qa/msgs')
ap.add_argument('--out', default='work/qa/boxsheets')
ap.add_argument('--per', type=int, default=48)
a = ap.parse_args()
fs = sorted(glob.glob(os.path.join(a.src, 'j*', 'm*.png')), key=lambda f: os.path.basename(f))
crops, prev = [], (None, None)
for f in fs:
    mid = re.match(r'm(\d+)_', os.path.basename(f)).group(1)
    c = Image.open(f).convert('RGB').crop((0, 92, 240, 160))
    if prev[0] == mid and not ImageChops.difference(c, prev[1]).getbbox():
        continue
    prev = (mid, c)
    crops.append((os.path.basename(f)[:-4], c))
os.makedirs(a.out, exist_ok=True)
COLS, TW, TH = 4, 240, 68 + 10
for s in range(0, len(crops), a.per):
    part = crops[s:s + a.per]
    rows = (len(part) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * (TW + 4), rows * TH), (40, 0, 40))
    d = ImageDraw.Draw(sheet)
    for i, (name, c) in enumerate(part):
        x, y = (i % COLS) * (TW + 4), (i // COLS) * TH
        d.text((x + 2, y), name, fill=(255, 255, 0))
        sheet.paste(c, (x, y + 10))
    sheet.save(os.path.join(a.out, 'sheet_%03d.png' % (s // a.per)))
print(len(crops), 'crops,', (len(crops) + a.per - 1) // a.per, 'sheets in', a.out)
