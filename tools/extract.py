"""Extract all text to script/*.json. Never clobbers existing files unless --force (English lives there).

python -X utf8 tools/extract.py [--force]

Entry: {id, kind, dialect, off, end, cap, slots, idx, jp, en}
  kind  msg   u16 script stream ending [end]; relocated by the build, all `slots` (pointer words) repointed.
        str   byte string, 0-terminated; written in place when it fits `cap` bytes (incl. terminator), else
              relocated (needs slots).
        field fixed 16-byte name field in a data record, written in place.
  dialect (msg) dlg = field/event dialogue engine (EC/F5 take one arg), btl = battle-preprocessed (EC/F5 no arg).
"""
import argparse, json, struct, sys, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec as C
import catalog as K
from scan_ptrs import try_str

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'script'
STR_REGIONS = [(0x275000, 0x276A38), (0x276CAC, 0x277080), (0x106B40, 0x1074A0)]
FIELD_REGION = (0x2BA000, 0x2CE000)
BTL_TABLE = (0x276A74, 0x276CAC)


def is_btl_text(jp):
    import re
    return any(int(x) >= 0xE5 for x in re.findall(r'\[(?:ec|f5):(\d+)\]', jp))


def decode_str(rom, p, e):
    out = []
    i = p
    while i < e - 1:
        b = rom[i]
        if b == 0x0A:
            out.append('[lf]')
            i += 1
            continue
        c = b << 8 | rom[i + 1]
        out.append(C.TBL.get(c, '[#%04X]' % c))
        i += 2
    return ''.join(out)


def field_text(rom, p):
    s = []
    for i in range(p, p + 16, 2):
        c = rom[i] << 8 | rom[i + 1]
        if c == 0:
            break
        s.append(C.TBL[c])
    return ''.join(s).rstrip('　')


def scan_fields(rom):
    T = C.TBL
    res = []
    p, end = FIELD_REGION
    while p < end:
        c0 = rom[p] << 8 | rom[p + 1]
        ok = c0 in T and c0 != 0x8140 and (rom[p - 2] << 8 | rom[p - 1]) not in T
        if ok:
            z = False
            for i in range(p, p + 16, 2):
                c = rom[i] << 8 | rom[i + 1]
                if c == 0:
                    z = True
                elif z or c not in T:
                    ok = False
                    break
        if ok:
            res.append(p)
            p += 16
        else:
            p += 1
    return res


def build_entries(rom):
    cat = K.catalog(rom)
    main_idx = collections.defaultdict(list)
    for i in range(K.MAIN_N):
        p = struct.unpack_from('<I', rom, K.MAIN_T + 4 * i)[0] - 0x08000000
        main_idx[p].append(i)
    entries = {}
    # strings: sequential scan of str regions (catches array elements without pointers)
    starts = set()
    for s, e in STR_REGIONS:
        i = s
        while i < e:
            r = try_str(rom, i)
            if r and (i == s or rom[i - 1] == 0):
                starts.add(i)
                i = r[0]
            else:
                i += 1
    for t, d in cat.items():
        if d['kind'] == 'str':
            starts.add(t)
    for t in sorted(starts):
        r = try_str(rom, t)
        if not r:
            continue
        e = r[0]
        j = e
        while j < len(rom) and rom[j] == 0 and j - t < 0x200:
            j += 1
        cap = j - t
        slots = cat.get(t, {}).get('slots', [])
        entries[t] = dict(id='S%06X' % t, kind='str', off=t, end=e, cap=cap, slots=slots,
                          jp=decode_str(rom, t, e))
    for t, d in sorted(cat.items()):
        if d['kind'] != 'msg':
            continue
        jp = C.decode_units(rom, t)[0]
        idx = main_idx.get(t, [])
        btl = any(BTL_TABLE[0] <= s < BTL_TABLE[1] for s in d['slots']) or is_btl_text(jp)
        e = dict(id=('M%04d' % idx[0]) if idx else 'T%06X' % t, kind='msg', dialect='btl' if btl else 'dlg',
                 off=t, end=d['end'], slots=d['slots'], idx=idx, jp=jp)
        if btl:
            e['jp'] = decode_btl(rom, t)
        entries[t] = e
    for p in scan_fields(rom):
        entries[p] = dict(id='F%06X' % p, kind='field', off=p, end=p + 16, cap=16, slots=[], jp=field_text(rom, p))
    return entries


BTL_NOARG = {0xEC, 0xF5}


def decode_btl(rom, p):
    """Battle dialect: EC/F5 have no argument."""
    saved = {k: C.CTRL[k] for k in BTL_NOARG}
    try:
        for k in BTL_NOARG:
            C.CTRL[k] = (C.CTRL[k][0], 0)
        return C.decode_units(rom, p)[0]
    finally:
        C.CTRL.update(saved)


def group(e):
    o = e['off']
    if e['kind'] == 'field':
        return 'names'
    if e['kind'] == 'msg' and e.get('idx'):
        return 'main/%02d' % (e['idx'][0] // 200)
    if 0x106B40 <= o < 0x1074A0:
        return 'battle'
    if 0x276CAC <= o < 0x277080:
        return 'bank'
    if e['kind'] == 'str':
        return 'menu'
    return 'sys'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    entries = build_entries(rom)
    files = collections.defaultdict(list)
    for t in sorted(entries, key=lambda t: (entries[t].get('idx') or [99999])[0] * 0x1000000 + t):
        e = entries[t]
        g = group(e)
        e['en'] = ''
        e['slots'] = ['%06X' % s for s in e['slots']]
        e['off'] = '%06X' % e['off']
        e['end'] = '%06X' % e['end']
        files[g].append(e)
    n = 0
    for g, es in sorted(files.items()):
        p = SCRIPT / (g + '.json')
        if p.exists() and not a.force:
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(es, f, ensure_ascii=False, indent=1)
            f.write('\n')
        n += 1
    tot = collections.Counter(e['kind'] for e in entries.values())
    print('files written', n, 'of', len(files), dict(tot))


if __name__ == '__main__':
    main()
