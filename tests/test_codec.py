import struct, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import codec as C  # noqa: E402

ROM = ROOT / 'rom/honoo.gba'
pytestmark = pytest.mark.skipif(not ROM.exists(), reason='needs rom/honoo.gba')


def test_main_table_roundtrip():
    a = ROM.read_bytes()
    T, N = 0x24EC68, 5331
    bad = []
    for i in range(N):
        p = struct.unpack_from('<I', a, T + 4 * i)[0] - 0x08000000
        txt, e = C.decode_units(a, p)
        if C.encode_jp(txt) != a[p:e]:
            bad.append(i)
    assert not bad, bad[:10]


def test_glyph_index_code_inverse():
    import font as F
    for i in range(1240):
        assert F.code_to_index(F.index_to_code(i)) == i


def test_wrap_keeps_space_before_variable():
    import wrap as W
    assert W.wrap('So you are called [f3].[wait][end]')[0] == 'So you are called [f3].[wait][end]'
    assert W.fit('Use it on [f5]?[end]', 216)[0] == 'Use it on [f5]?[end]'
    assert '[n]〒[ec:0]' in W.wrap('The attack [f4] will be 〒[ec:0].[end]')[0]
    assert W.wrap('[face:255]What the heck is going on? [f3], let\'s go!![wait][end]')[0] == \
        '[face:255]What the heck is going on?[n][f3], let\'s go!![wait][end]'
    assert W.wrap('OK.[wait][page]To the Demon World[n]To Valhalla[end]')[0].endswith('World[n]To Valhalla[end]')


def test_str_ends_on_zero_unit():
    import enc
    for t in ('Pixie', ' joined', 'ab'):
        b = enc.encode_str(t)
        assert len(b) % 2 == 0 and b[-2:] == b'\0\0' and b'\0' not in b[:-2]
    assert enc.encode_field('Pixie') == b'Pixie\x7f' + b'\x81\x40' * 5
