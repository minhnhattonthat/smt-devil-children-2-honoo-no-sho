"""Catalogue every pointer-reached string in the ROM (trusted referrers only) and report coverage gaps.

python -X utf8 tools/catalog.py [--gaps]
Trusted referrers: code + code-bank tables (< 0x110000) and the known text pointer tables (TABLES).
Each target: kind msg (u16 script stream) or str (byte string), dialect dlg/btl for msgs.
"""
import argparse, struct, sys, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec as C
from scan_ptrs import try_msg, try_str

ROOT = Path(__file__).resolve().parents[1]
MAIN_T, MAIN_N = 0x24EC68, 5331
TABLES = [  # (start, end) of pointer tables outside the code bank that point at text
    (0x22D324, 0x22D4A4),   # bank menu strings
    (MAIN_T, MAIN_T + 4 * MAIN_N),
    (0x276A38, 0x276A54),   # small str table
    (0x276A74, 0x276CAC),   # battle msgs/strs
]
CODE_END = 0x110000
# text regions that must be fully covered (start, end)
REGIONS = [(0x106B40, 0x1074A0), (0x22D4B0, MAIN_T), (MAIN_T + 4 * MAIN_N, 0x27A9F0)]


def trusted(o):
    return o < CODE_END or any(s <= o < e for s, e in TABLES)


def catalog(rom):
    refs = collections.defaultdict(list)
    for o in range(0, len(rom) - 3, 4):
        if not trusted(o):
            continue
        v = struct.unpack_from('<I', rom, o)[0]
        if 0x08000000 <= v < 0x08000000 + len(rom):
            refs[v - 0x08000000].append(o)
    out = {}
    for t, rs in refs.items():
        m = try_msg(rom, t) if t % 2 == 0 else None
        s = try_str(rom, t)
        if m and m[1] >= 1:
            out[t] = dict(kind='msg', end=m[0], slots=rs)
        elif s:
            out[t] = dict(kind='str', end=s[0], slots=rs)
    return out


def gaps(rom, cat):
    cov = bytearray(len(rom))
    for t, d in cat.items():
        for i in range(t, d['end']):
            cov[i] = 1
    res = []
    for s, e in REGIONS:
        i = s
        while i < e:
            if not cov[i] and rom[i] not in (0, 0xFF):
                j = i
                while j < e and not cov[j]:
                    j += 1
                res.append((i, j))
                i = j
            else:
                i += 1
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gaps', action='store_true')
    a = ap.parse_args()
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    cat = catalog(rom)
    c = collections.Counter((d['kind'], t >> 16) for t, d in cat.items())
    print(sorted(c.items()))
    if a.gaps:
        for s, e in gaps(rom, cat):
            txt = C.decode_units(rom, s, e)[0] if s % 2 == 0 else rom[s:e].hex()
            print('%06X-%06X %d %s' % (s, e, e - s, txt[:100]))


if __name__ == '__main__':
    main()
