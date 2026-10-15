"""Build a first-guess glyph table by matching each 12px game glyph to MS Gothic 12px bitmaps of every
JIS X 0208 char (the game font is close to MS Gothic's embedded 12px strike).

python -X utf8 tools/ocr_font.py  -> tbl/jp_auto.tsv (index, code, char, score, runner-up, score)
Reviewed/fixed result lives in tbl/jp.tbl (tools/mktbl.py).
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font as F

ROOT = Path(__file__).resolve().parents[1]
S = 16


def candidates():
    out = []
    for hi in list(range(0x81, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                ch = bytes([hi, lo]).decode('cp932')
            except UnicodeDecodeError:
                continue
            out.append(ch)
    return out


def render(ch, fnt):
    im = Image.new('L', (S, S), 0)
    ImageDraw.Draw(im).text((2, 2), ch, font=fnt, fill=255)
    return (np.array(im) > 127).astype(np.float32)


def main():
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    off = F.FONTS['f12']
    fnt = ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc', 12)
    cands = candidates()
    R = np.stack([render(c, fnt) for c in cands]).reshape(len(cands), -1)
    Rs = R.sum(1)
    N = 1240
    M = np.zeros((N, len(cands)), np.float32)
    empty = []
    for i in range(N):
        g = np.array(F.glyph(rom, off, i), dtype=np.float32)
        if g.sum() == 0:
            empty.append(i)
            continue
        best = np.zeros(len(cands))
        for dy in range(0, 5):
            for dx in range(0, 5):
                c = np.zeros((S, S), np.float32)
                c[dy:dy + 12, dx:dx + 12] = g
                gs = c.reshape(-1)
                inter = R @ gs
                best = np.maximum(best, inter / np.maximum(Rs + gs.sum() - inter, 1))
        M[i] = best
    # Glyphs are mostly a subset of JIS in code order, with extras appended out of order: monotonic DP
    # alignment where a glyph may instead "skip" (take its independent best match) at a penalty.
    PEN = 0.25
    C = len(cands)
    # D[j] = best score of glyphs so far, with the last in-order glyph at candidate exactly j (or -inf)
    D = np.full(C, -1e9, np.float32)
    D0 = 0.0   # score with no in-order glyph yet
    hist = {}
    for i in range(1, N):
        if i in empty:
            continue
        pm = np.maximum.accumulate(np.maximum(D, -1e9))
        prev = np.concatenate([[D0], np.maximum(pm[:-1], D0)])   # best over j' < j
        take = prev + M[i]
        skip = D + M[i].max() - PEN
        hist[i] = (D.copy(), D0)
        D = np.maximum(take, skip)
        D0 = D0 + M[i].max() - PEN
    assign = {}
    j = int(np.argmax(D))
    cur = D[j]
    for i in range(N - 1, 0, -1):
        if i in empty:
            continue
        Dp, D0p = hist[i]
        if j < 0:
            assign[i] = int(np.argmax(M[i]))
            continue
        sk = Dp[j] + M[i].max() - PEN
        if abs(sk - cur) < 1e-4 and Dp[j] > -1e8:
            assign[i] = int(np.argmax(M[i]))
            cur = Dp[j]
            continue
        assign[i] = j
        target = cur - M[i, j]
        cands_prev = np.where(np.abs(Dp[:j] - target) < 1e-4)[0]
        if len(cands_prev):
            j = int(cands_prev[-1])
            cur = Dp[j]
        else:
            j = -1
            cur = D0p
    out = [(0, ' ', 1.0, '', 0.0)]
    for i in range(1, N):
        if i in empty:
            out.append((i, '', 0.0, '', 0.0))
            continue
        j = assign.get(i, int(np.argmax(M[i])))
        o = int(np.argmax(M[i]))
        out.append((i, cands[j], float(M[i, j]), cands[o], float(M[i, o])))
    p = ROOT / 'tbl/jp_auto.tsv'
    p.parent.mkdir(exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        for i, c, s, c2, s2 in out:
            f.write('%d\t%04X\t%s\t%.3f\t%s\t%.3f\n' % (i, F.index_to_code(i), c, s, c2, s2))
    low = [r for r in out if r[2] < 0.7 and r[1].strip()]
    print('written', p, 'low-score', len(low))


if __name__ == '__main__':
    main()
