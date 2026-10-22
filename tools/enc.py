"""English encoders + width model (shared by build, wrap, lint, batch checks).

msg (u16 units): ASCII chars packed two per unit (lo byte first); an odd char before a control/JP glyph is padded
with 0x7F (blank, zero width). Controls as in tools/codec.py. A non-ASCII char present in tbl/jp.tbl is emitted as
its 2-byte glyph (e.g. ♥ or the Macca sign 〒).
str: bytes; ASCII, [lf] = 0x0A, JP glyphs 2 bytes; 0-terminated.
field: 16 bytes: ASCII + 0x00, zero-pad to even, rest 81 40 units (trimmed by the game's name-length routine).
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec as C
import mkfont

ROOT = Path(__file__).resolve().parents[1]
PAD = 0x7F
TOK = re.compile(r'\[([a-z0-9]+)((?::\d+)*)\]|\[#([0-9A-F]{4})\]|(.)', re.S)

_W = {}


def widths(name='en12'):
    if name not in _W:
        h = 12 if name == 'en12' else 8
        g = mkfont.load(ROOT / 'font' / (name + '.txt'), h)
        _W[name] = {c: w for c, (w, rows) in g.items()}
    return _W[name]


def text_width(s, font='en12', var_w=None):
    """Pixel width of plain text (no line breaks). JP glyphs count 12 (en12) / 8 (en8). Variables via var_w."""
    W = widths(font)
    jpw = 12 if font == 'en12' else 8
    total = 0
    for m in TOK.finditer(s):
        if m.group(1):
            if var_w and m.group(1) in var_w:
                total += var_w[m.group(1)]
            continue
        if m.group(3):
            continue
        ch = m.group(4)
        o = ord(ch)
        total += W.get(o, 0) if o < 0x80 else jpw
    return total


def ctrl_table(dialect):
    t = dict(C.CTRL)
    if dialect == 'btl':
        for k in (0xEC, 0xF5):
            t[k] = (t[k][0], 0)
    return t


def encode_msg(text, dialect='dlg'):
    ct = ctrl_table(dialect)
    name2code = {v[0]: k for k, v in ct.items()}
    out = bytearray()
    pend = []

    def flush():
        if pend:
            if len(pend) % 2:
                pend.append(PAD)
            out.extend(pend)
            pend.clear()
    for m in TOK.finditer(text):
        if m.group(1):
            name = m.group(1)
            if name not in name2code:
                raise ValueError('unknown control [%s]' % name)
            code = name2code[name]
            args = [int(a) for a in filter(None, m.group(2).split(':'))]
            if len(args) != ct[code][1]:
                raise ValueError('[%s] needs %d args' % (name, ct[code][1]))
            flush()
            out += struct.pack('<H', code)
            for a in args:
                out += struct.pack('<H', a)
        elif m.group(3):
            flush()
            v = int(m.group(3), 16)
            out += struct.pack('<H', v) if v < 0x100 else bytes([v >> 8, v & 0xFF])
        else:
            ch = m.group(4)
            o = ord(ch)
            if 0x20 <= o < 0x7F:
                pend.append(o)
            elif ch in C.REV:
                flush()
                code = C.REV[ch]
                out += bytes([code >> 8, code & 0xFF])
            else:
                raise ValueError('unencodable char %r' % ch)
    flush()
    if not out.endswith(b'\xff\x00'):
        raise ValueError('message must end with [end]')
    return bytes(out)


FW_SRC = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
FW_DST = '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
FW_MAP = dict(zip(FW_SRC, FW_DST))
# space: ASCII space + 0x7F zero-width pad = one unit like the other cells, but 3 px instead of the 12 px '　'
FW_MAP.update({' ': ' \x7f', '!': '！', '?': '？', '.': '。', '-': '－', '/': '／', ':': '：', '(': '（', ')': '）', '+': '＋'})


def encode_str(text):
    """[fw] prefix = store as fullwidth glyph codes (for screens that use 2-byte glyph cells, e.g. the title);
    DrawString still shows fullwidth letters as proportional English."""
    if text.startswith('[fw]'):
        text = ''.join(FW_MAP.get(c, c) for c in text[4:])
    out = bytearray()
    for m in TOK.finditer(text):
        if m.group(1):
            if m.group(1) == 'lf':
                out.append(0x0A)
                continue
            raise ValueError('control [%s] not allowed in str' % m.group(1))
        if m.group(3):
            v = int(m.group(3), 16)
            out += bytes([v >> 8, v & 0xFF])
            continue
        ch = m.group(4)
        o = ord(ch)
        if 0x20 <= o <= 0x7F:
            out.append(o)
        elif ch in C.REV:
            code = C.REV[ch]
            out += bytes([code >> 8, code & 0xFF])
        else:
            raise ValueError('unencodable char %r' % ch)
    # The game copies/joins strings by u16 units up to a 0000 unit (strcpy 0x080C0C6C, strcat 0x080C0CDC): end on a
    # whole zero unit, 0x7F (zero-width) pads odd lengths. A lone 0 byte inside a unit made strcpy run on (hang).
    if len(out) % 2:
        out.append(0x7F)
    return bytes(out) + b'\x00\x00'


def encode_str_inplace(text, cap):
    """Bytes for a str written over its JP original (cap bytes), or None. Falls back to a single 0 byte end when the
    0000 unit does not fit: only for strs with no pointer (fixed-offset headers drawn directly, never strcpy'd)."""
    b = encode_str(text)
    if len(b) <= cap:
        return b
    b = b[:-2].rstrip(b'\x7f') + b'\x00'
    return b if len(b) <= cap else None


def encode_field(text, size=16):
    # No 0 terminator: like the JP names, pad with fullwidth spaces (81 40). The game trims those when it joins a
    # name with a particle ("Pixie" + " joined"); a 0 byte inside the copied units would end the joined line.
    # Odd length: 0x7F (zero-width pad) keeps the 81 40 pads unit-aligned.
    b = encode_str(text)[:-2]       # drop the 0000 unit (encode_str already 0x7F-pads odd lengths)
    if len(b) > size:
        raise ValueError('field too long (%d > %d bytes): %r' % (len(b), size, text))
    while len(b) < size:
        b += b'\x81\x40'
    return b
