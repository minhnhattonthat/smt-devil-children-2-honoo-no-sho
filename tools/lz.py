"""GBA BIOS LZ77 (type 0x10) decompress / compress, and a ROM scan for blocks.

python -X utf8 tools/lz.py scan [--min 64]            -> work/lz/<offset>.bin for every plausible LZ77 block
python -X utf8 tools/lz.py find TILES.bin             -> blocks containing these 32-byte tiles
"""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def decompress(data, off=0, limit=1 << 20):
    if data[off] != 0x10:
        raise ValueError('not LZ77')
    size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
    if size == 0 or size > limit:
        raise ValueError('bad size')
    out = bytearray()
    i = off + 4
    while len(out) < size:
        flags = data[i]
        i += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                x = data[i] << 8 | data[i + 1]
                i += 2
                n = (x >> 12) + 3
                d = (x & 0xFFF) + 1
                if d > len(out):
                    raise ValueError('bad back-reference')
                for _ in range(n):
                    out.append(out[-d])
            else:
                out.append(data[i])
                i += 1
    return bytes(out[:size]), i - off


def compress(src):
    """Greedy LZ77 (VRAM-safe: back-references of distance >= 2)."""
    out = bytearray([0x10, len(src) & 0xFF, len(src) >> 8 & 0xFF, len(src) >> 16 & 0xFF])
    i = 0
    n = len(src)
    while i < n:
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for b in range(8):
            if i >= n:
                break
            best_len, best_d = 0, 0
            lo = max(0, i - 4096)
            for j in range(i - 2, lo - 1, -1):
                l = 0
                while l < 18 and i + l < n and src[j + l] == src[i + l]:
                    l += 1
                if l > best_len:
                    best_len, best_d = l, i - j
                    if l == 18:
                        break
            if best_len >= 3:
                x = (best_len - 3) << 12 | (best_d - 1)
                out += bytes([x >> 8, x & 0xFF])
                flags |= 0x80 >> b
                i += best_len
            else:
                out.append(src[i])
                i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def scan(rom, minsize=64):
    found = []
    for off in range(0, len(rom) - 4, 4):
        if rom[off] != 0x10:
            continue
        size = rom[off + 1] | rom[off + 2] << 8 | rom[off + 3] << 16
        if size < minsize or size > 0x40000:
            continue
        try:
            d, used = decompress(rom, off)
        except (ValueError, IndexError):
            continue
        found.append((off, d, used))
    return found


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('scan')
    s.add_argument('--min', type=int, default=64)
    f = sp.add_parser('find')
    f.add_argument('tiles')
    a = ap.parse_args()
    rom = (ROOT / 'rom/honoo.gba').read_bytes()
    outdir = ROOT / 'work/lz'
    if a.cmd == 'scan':
        outdir.mkdir(parents=True, exist_ok=True)
        blocks = scan(rom, a.min)
        for off, d, used in blocks:
            (outdir / ('%06X.bin' % off)).write_bytes(d)
        print(len(blocks), 'blocks ->', outdir)
    else:
        t = Path(a.tiles).read_bytes()
        tiles = [t[i:i + 32] for i in range(0, len(t), 32) if any(t[i:i + 32])]
        for p in sorted(outdir.glob('*.bin')):
            d = p.read_bytes()
            hit = sum(1 for x in tiles if x in d)
            if hit:
                print(p.stem, hit, '/', len(tiles))
