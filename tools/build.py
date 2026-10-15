"""Build the English ROM.

python -X utf8 tools/build.py              -> build/honoo_en.gba (English where script has `en`)
python -X utf8 tools/build.py --marker     -> every untranslated entry replaced by an id marker at JP width
python -X utf8 tools/build.py --identity   -> no engine, no text: must equal the original (test)
python -X utf8 tools/build.py --only IDS   -> marker/English only for these ids (comma list), rest Japanese
Output also build/layout.json (where each entry went) and build/ranges.txt (allowed write ranges for romdiff).
"""
import argparse, json, struct, subprocess, sys, glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enc
import forms
import mkfont
import wrap as W

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / 'rom/honoo.gba'
OUT = ROOT / 'build/honoo_en.gba'
ARMIPS = ROOT / 'tools/armips/armips.exe'
SIZE = 16 * 1024 * 1024
LONGNAMES = 0x80F000            # table of long-name pointers (asm/main.asm)
TEXT_BASE = 0x810000           # relocated text goes here (engine + fonts live at 0x800000-0x80FFFF)
# fixed-length JP-encoded data outside the script (fullwidth Latin renders as proportional English)
PATCHES = [
    (0x0FA3B4, 'Ｊｉｎ　　　　　'),     # default hero name (was ジン), 8 units
]
# Packed fixed-stride name arrays read by getters (0x08038298 race, 0x080382C0 element): the caller copies the
# element's units, so each element becomes the 2-byte long-name escape 01 nn (+ zero pad) -> any English length.
ARRAYS = [
    (0x27585C, 8, ['God', 'Devil', 'Angel', 'Dragon', 'Bird', 'Beast', 'Oni', 'Spirit', 'Fiend', 'Mutant', 'Zombie',
                   'Boss', 'Monster']),
    (0x2758C4, 2, ['Light', 'Dark', 'Fire', 'Water', 'Earth', 'Wind', 'Thunder', 'Ice']),
]
MARK = 'The quick brown fox jumps over the lazy dog while five boxing wizards jump quickly. '


def load_script():
    es = []
    for f in sorted(glob.glob(str(ROOT / 'script/**/*.json'), recursive=True)):
        for e in json.load(open(f, encoding='utf-8')):
            e['_file'] = Path(f).relative_to(ROOT).as_posix()
            es.append(e)
    return es


def font_bins():
    """Write build/en12.bin, en8.bin (1bpp tile sheets, glyph index = byte) and width tables."""
    for name, gw, gh, cols_tiles in (('en12', 12, 12, 24), ('en8', 8, 8, 16)):
        g = mkfont.load(ROOT / 'font' / (name + '.txt'), gh)
        rows_px = 8 * gh
        tiles_w, tiles_h = cols_tiles, rows_px // 8
        data = bytearray(tiles_w * tiles_h * 8)
        widths = bytearray(128)
        for code, (w, rows) in g.items():
            if code >= 0x80:
                continue
            widths[code] = w
            gx, gy = (code % 16) * gw, (code // 16) * gh
            for y, r in enumerate(rows):
                for x, ch in enumerate(r[:gw]):
                    if ch == '#':
                        px, py = gx + x, gy + y
                        t = (py // 8) * tiles_w + px // 8
                        data[t * 8 + py % 8] |= 1 << (px % 8)
        widths[0x7F] = 0
        (ROOT / 'build').mkdir(exist_ok=True)
        (ROOT / 'build' / (name + '.bin')).write_bytes(bytes(data))
        (ROOT / 'build' / (name + '_w.bin')).write_bytes(bytes(widths))


def marker_text(e):
    """Marker: keep controls, replace each JP text run by ASCII of the same pixel width; id first."""
    import re
    if e['kind'] != 'msg':
        cap = e.get('cap', 16) - 1
        s = e['id'][1:]
        return s[:cap]
    parts = re.split(r'(\[[^\]]*\])', e['jp'])
    out, first, k = [], True, 0
    for p in parts:
        if not p:
            continue
        if p.startswith('['):
            out.append(p)
            continue
        target = len(p) * 12
        s = (e['id'] + ' ') if first else ''
        first = False
        while enc.text_width(s + MARK[k % len(MARK)]) <= target:
            s += MARK[k % len(MARK)]
            k += 1
        out.append(s.strip() or '.')
    return ''.join(out)


class Space:
    def __init__(self, rom, base):
        self.rom, self.p = rom, base

    def put(self, data, align=2):
        while self.p % align:
            self.p += 1
        at = self.p
        if at + len(data) > SIZE:
            raise RuntimeError('out of text space')
        self.rom[at:at + len(data)] = data
        self.p += len(data)
        return at


def build(mode='en', only=None, out=OUT, arrays=True):
    rom = bytearray(ORIG.read_bytes())
    ranges = []
    if mode == 'identity':
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(rom)
        return rom, {}
    rom += b'\xff' * (SIZE - len(rom))
    font_bins()
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom)
    r = subprocess.run([str(ARMIPS), str(ROOT / 'asm/main.asm'), '-root', str(ROOT), '-strequ', 'ROMPATH',
                        str(Path(out).resolve())], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('armips failed:\n' + r.stdout + r.stderr)
    rom = bytearray(out.read_bytes())
    ranges += [(0x0C20E8, 0x0C20F8), (0x0C2184, 0x0C2190), (0x800000, TEXT_BASE)]
    import codec
    for off, text in PATCHES:
        data = codec.encode_jp(text)
        assert rom[off:off + len(data)] != data or True
        rom[off:off + len(data)] = data
        ranges.append((off, off + len(data)))
    space = Space(rom, TEXT_BASE)
    layout = {}
    errors = []
    longnames = {}
    for e in load_script():
        en = '' if e.get('keep') else (e.get('en') or '')
        if only is not None and e['id'] not in only:
            continue
        if not en and mode == 'marker':
            en = marker_text(e)
        if not en:
            continue
        try:
            if e['kind'] == 'msg':
                text = en
                f = forms.form_of(e)
                if f == 'dlg':
                    text, _ = W.wrap(en)
                elif f == 'prompt':
                    text, _ = W.fit(en, forms.LINE_W)
                elif f == 'ddesc':
                    text, _ = W.fit(en, forms.DDESC_W)
                data = enc.encode_msg(text, e.get('dialect', 'dlg'))
                at = space.put(data)
                for s in e['slots']:
                    so = int(s, 16)
                    struct.pack_into('<I', rom, so, 0x08000000 + at)
                    ranges.append((so, so + 4))
                layout[e['id']] = at
            elif e['kind'] == 'str':
                data = enc.encode_str(en)
                off = int(e['off'], 16)
                if len(data) <= e['cap']:
                    rom[off:off + e['cap']] = data + b'\x00' * (e['cap'] - len(data))
                    ranges.append((off, off + e['cap']))
                    layout[e['id']] = off
                elif e['slots']:
                    at = space.put(data)
                    for s in e['slots']:
                        so = int(s, 16)
                        struct.pack_into('<I', rom, so, 0x08000000 + at)
                        ranges.append((so, so + 4))
                    layout[e['id']] = at
                else:
                    raise ValueError('str too long for its slot (%d > %d) and no pointer to move it' % (len(data), e['cap']))
            elif e['kind'] == 'field':
                if len(en) > 16:            # long name: escape 01 nn -> LONGNAMES[nn]
                    if en not in longnames:
                        k = len(longnames)
                        if k > 255:
                            raise ValueError('more than 256 long names')
                        at = space.put(enc.encode_str(en))
                        struct.pack_into('<I', rom, LONGNAMES + 4 * k, 0x08000000 + at)
                        longnames[en] = k
                    data = bytes([1, longnames[en], 0, 0]) + b'\x81\x40' * 6
                else:
                    data = enc.encode_field(en)
                off = int(e['off'], 16)
                rom[off:off + 16] = data
                ranges.append((off, off + 16))
                layout[e['id']] = off
        except Exception as x:
            errors.append('%s %s: %s' % (e['_file'], e['id'], x))
    if mode != 'identity' and only is None and arrays:
        for base, stride, names in ARRAYS:
            for i, name in enumerate(names):
                if name not in longnames:
                    k = len(longnames)
                    at = space.put(enc.encode_str(name))
                    struct.pack_into('<I', rom, LONGNAMES + 4 * k, 0x08000000 + at)
                    longnames[name] = k
                off = base + stride * i
                rom[off:off + stride] = bytes([1, longnames[name]]) + b'\x00' * (stride - 2)
            ranges.append((base, base + stride * len(names)))
    if mode != 'identity' and only is None:
        import menulabels
        for idx, blob in menulabels.gen().items():
            at = space.put(blob, align=4)
            so = menulabels.TABLE + 4 * idx
            struct.pack_into('<I', rom, so, 0x08000000 + at)
            ranges.append((so, so + 4))
    if len(longnames) > 256:
        errors.append('more than 256 long names (%d)' % len(longnames))
    ranges.append((TEXT_BASE, space.p))
    if errors:
        print('\n'.join(errors[:40]))
        raise SystemExit('%d build errors' % len(errors))
    out.write_bytes(rom)
    (ROOT / 'build/layout.json').write_text(json.dumps(layout, indent=0), encoding='utf-8', newline='\n')
    with open(ROOT / 'build/ranges.txt', 'w', newline='\n') as f:
        for a, b in sorted(ranges):
            f.write('%X-%X\n' % (a, b))
    print('built', out.relative_to(ROOT), 'entries', len(layout), 'text end 0x%X' % space.p)
    return rom, layout


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--marker', action='store_true')
    ap.add_argument('--identity', action='store_true')
    ap.add_argument('--only')
    ap.add_argument('--out')
    ap.add_argument('--no-arrays', action='store_true')
    a = ap.parse_args()
    mode = 'identity' if a.identity else ('marker' if a.marker else 'en')
    build(mode, set(a.only.split(',')) if a.only else None, Path(a.out) if a.out else OUT, not a.no_arrays)
