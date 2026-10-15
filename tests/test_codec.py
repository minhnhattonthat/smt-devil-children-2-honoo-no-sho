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
