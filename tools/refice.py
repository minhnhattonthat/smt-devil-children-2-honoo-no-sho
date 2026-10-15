"""Reference English from rom/ref/ice_ref.gba (Book of Ice + someone's English proto patch). Reference only.

python -X utf8 tools/refice.py   -> work/ref_en.json {"M0123": "english", "F2BADFA": "name", ...}
Main table: same 5331-entry layout as Fire; a hint is kept only when the speaker/portrait/control skeleton of the
Ice English equals the Fire Japanese (same scene). Name fields: matched by record position (same tables, shifted).
"""
import json, re, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec as C

ROOT = Path(__file__).resolve().parents[1]
REF_T = 0x250344


def dec_en(d, p):
    out = []
    i = p
    while i < len(d) - 1:
        lo, hi = d[i], d[i + 1]
        u = lo | hi << 8
        i += 2
        if u < 0x100:
            name, n = C.CTRL.get(u, ('#%02X' % u, 0))
            args = []
            for _ in range(n):
                args.append(d[i] | d[i + 1] << 8)
                i += 2
            out.append('[%s%s]' % (name, ''.join(':%d' % x for x in args)))
            if u == 0xFF:
                break
        elif lo < 0x80:
            out.append(chr(lo))
            if hi != 0x7F:
                out.append(chr(hi))
        else:
            out.append(C.TBL.get(lo << 8 | hi, '[#%04X]' % (lo << 8 | hi)))
    return ''.join(out)


def skel(t):
    return re.findall(r'\[(?:name|face)[^\]]*\]', t)


def main():
    a = (ROOT / 'rom/honoo.gba').read_bytes()
    b = (ROOT / 'rom/ref/ice_ref.gba').read_bytes()
    out = {}
    for f in sorted((ROOT / 'script/main').glob('*.json')):
        for e in json.load(open(f, encoding='utf-8')):
            i = e['idx'][0]
            pb = struct.unpack_from('<I', b, REF_T + 4 * i)[0] - 0x08000000
            if pb < 0x800000:
                continue            # untranslated in the reference
            en = dec_en(b, pb)
            if skel(en) == skel(e['jp']) and 'In development' not in en and 'In Development' not in en:
                out[e['id']] = en
    # name fields: find the same 16-byte JP field in the reference ROM's first 8 MiB? It holds English now,
    # so match by offset delta of the record tables instead.
    fields = json.load(open(ROOT / 'script/names.json', encoding='utf-8'))
    for e in fields:
        off = int(e['off'], 16)
        for delta in (0x1A68,):        # Ice record tables sit 0x1A68 bytes later
            s = b[off + delta: off + delta + 16]
            if all(0x20 <= x < 0x7F for x in s.rstrip(b'\x00 ')) and s[:1].isalpha():
                out[e['id']] = s.decode('ascii').rstrip('\x00 ')
                break
    (ROOT / 'work').mkdir(exist_ok=True)
    json.dump(out, open(ROOT / 'work/ref_en.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0)
    print(len(out), 'hints')


if __name__ == '__main__':
    main()
