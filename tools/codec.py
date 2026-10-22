"""Text codec for Devil Children 2 Honoo no Sho.

Script text = stream of u16 little-endian units:
  0x00E5..0x00FE  control codes (some take one u16 argument), 0x00FF = end of message;
  >= 0x0100       a character: bytes (lo, hi) in ROM are the glyph code high byte, low byte (SJIS-like, tbl/jp.tbl);
  in the English build, a unit may instead hold two ASCII bytes (see docs/re/engine.md).
Readable form: characters as text, controls as [name] or [name:arg], unknown units as [#XXXX].
"""
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# control code -> (name, number of u16 args)   (dispatcher 0x08032998, jump table 0x080329C8)
CTRL = {
    0xE5: ('e5', 0), 0xE6: ('e6', 0), 0xE7: ('e7', 0), 0xE8: ('e8', 0), 0xE9: ('e9', 0), 0xEA: ('ea', 0),
    0xEB: ('eb', 0), 0xEC: ('ec', 1), 0xED: ('ed', 1), 0xEE: ('name', 1), 0xEF: ('ef', 0), 0xF0: ('f0', 0),
    0xF1: ('f1', 0), 0xF2: ('f2', 0), 0xF3: ('f3', 0), 0xF4: ('f4', 0), 0xF5: ('f5', 1), 0xF6: ('face', 1),
    0xF7: ('f7', 1), 0xF8: ('f8', 0), 0xF9: ('wait', 0), 0xFA: ('pause', 1), 0xFB: ('fb', 1), 0xFC: ('clr', 0),
    0xFD: ('page', 0), 0xFE: ('n', 0), 0xFF: ('end', 0),
}
NAME2CODE = {v[0]: k for k, v in CTRL.items()}


def load_tbl(path=ROOT / 'tbl/jp.tbl'):
    d = {}
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if '=' in line:
            k, v = line.split('=', 1)
            d[int(k, 16)] = v
    return d


TBL = load_tbl()
REV = {}
for k, v in TBL.items():
    REV.setdefault(v, k)


def decode_units(data, off, limit=None):
    """Decode from data[off] until [end]. Returns (text, end_offset_exclusive)."""
    out = []
    i = off
    end = len(data) if limit is None else limit
    while i + 1 < end:
        u = data[i] | data[i + 1] << 8
        i += 2
        if u < 0x100:
            if u in CTRL:
                name, nargs = CTRL[u]
                args = []
                for _ in range(nargs):
                    args.append(data[i] | data[i + 1] << 8)
                    i += 2
                out.append('[%s%s]' % (name, ''.join(':%d' % a for a in args)))
                if u == 0xFF:
                    break
            else:
                out.append('[#%04X]' % u)
        else:
            code = data[i - 2] << 8 | data[i - 1]   # stored hi, lo
            ch = TBL.get(code)
            out.append(ch if ch and ch not in '[]' else '[#%04X]' % code)
    return ''.join(out), i


TOKEN = re.compile(r'\[([a-z0-9]+)((?::\d+)*)\]|\[#([0-9A-F]{4})\]|(.)', re.S)


def encode_jp(text):
    """Inverse of decode_units for Japanese text (roundtrip)."""
    b = bytearray()
    for m in TOKEN.finditer(text):
        if m.group(1):
            code = NAME2CODE[m.group(1)]
            b += struct.pack('<H', code)
            for a in filter(None, m.group(2).split(':')):
                b += struct.pack('<H', int(a))
        elif m.group(3):
            v = int(m.group(3), 16)
            if v < 0x100:
                b += struct.pack('<H', v)
            else:
                b += bytes([v >> 8, v & 0xFF])
        else:
            code = REV[m.group(4)]
            b += bytes([code >> 8, code & 0xFF])
    return bytes(b)
