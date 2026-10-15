"""Recon: find every aligned u32 in the ROM that points at decodable text, and classify the target.

python -X utf8 tools/scan_ptrs.py [--out work/ptrscan.tsv]
Kinds: msg = u16 script stream ending in [end] (FF 00); str = byte string (2-byte glyph codes, 0x0A) ending in 00.
"""
import argparse, struct, sys, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec as C

ROOT = Path(__file__).resolve().parents[1]
T = C.TBL


def try_msg(a, p, maxlen=6000):
    i, chars = p, 0
    while i < p + maxlen and i + 1 < len(a):
        u = a[i] | a[i + 1] << 8
        i += 2
        if u < 0x100:
            if u not in C.CTRL:
                return None
            if u == 0xFF:
                return (i, chars) if chars or i - p > 2 else None
            i += 2 * C.CTRL[u][1]
        else:
            if (a[i - 2] << 8 | a[i - 1]) not in T:
                return None
            chars += 1
    return None


def try_str(a, p, maxlen=400):
    i, chars = p, 0
    while i < p + maxlen and i < len(a):
        b = a[i]
        if b == 0:
            return (i + 1, chars) if chars else None
        if b == 0x0A:
            i += 1
            continue
        if b >= 0x81 and i + 1 < len(a) and (b << 8 | a[i + 1]) in T:
            chars += 1
            i += 2
            continue
        return None
    return None


def scan(a):
    res = {}
    refs = collections.defaultdict(list)
    for o in range(0, len(a) - 3, 4):
        v = struct.unpack_from('<I', a, o)[0]
        if 0x08000000 <= v < 0x08000000 + len(a):
            refs[v - 0x08000000].append(o)
    for t, rs in refs.items():
        if t in res:
            continue
        m = try_msg(a, t) if t % 2 == 0 else None
        s = try_str(a, t)
        if m and m[1] >= 1:
            res[t] = ('msg', m[0], m[1])
        elif s:
            res[t] = ('str', s[0], s[1])
    return res, refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT / 'work/ptrscan.tsv'))
    a = ap.parse_args()
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    res, refs = scan(rom)
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        for t in sorted(res):
            k, e, n = res[t]
            txt = C.decode_units(rom, t)[0] if k == 'msg' else ''
            if k == 'str':
                txt = ''.join(T.get(rom[i] << 8 | rom[i + 1], '?') for i in range(t, e - 1, 2))
            f.write('%06X\t%s\t%06X\t%d\t%s\t%s\n' % (t, k, e, n, ','.join('%06X' % r for r in refs[t][:6]), txt[:80]))
    c = collections.Counter((k, t >> 16) for t, (k, e, n) in res.items())
    for (k, b), n in sorted(c.items(), key=lambda x: (x[0][1], x[0][0])):
        print(k, hex(b << 16), n)


if __name__ == '__main__':
    main()
