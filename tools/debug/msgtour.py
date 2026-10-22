"""Message tour: screenshots of main-table messages shown in the real dialogue box (no playthrough needed).

python -X utf8 tools/debug/msgtour.py IDS [--jobs 4] [--out work/qa/msgs] [--rom build/honoo_en.gba] [--regen]
IDS: comma list / ranges of main-table indexes or entry ids, e.g. "4-75,2611" or "M0004,M0010".
Makes (or reuses, --regen to rebuild) work/states/show.mss = state at the first show_message after the intro,
then runs N emulator jobs; shots land in OUT/m<idx>_<page>.png, contact sheets OUT/sheet_<job>.png.
"""
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SCRIPTS  # noqa: E402
EMU = [sys.executable, '-X', 'utf8', str(SCRIPTS / 'emu.py')]
ROUTE = '600 -;6 start;120 -;6 a;120 -;6 a;120 -;6 a'


def parse_ids(s):
    out = []
    for part in s.split(','):
        part = part.strip().lstrip('M')
        if '-' in part:
            a, b = part.split('-')
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--out', default='work/qa/msgs')
    ap.add_argument('--rom', default='build/honoo_en.gba')
    ap.add_argument('--regen', action='store_true')
    ap.add_argument('--frames-per', type=int, default=700)
    a = ap.parse_args()
    rom = str(ROOT / a.rom)
    state = ROOT / 'work/states/show.mss'
    if a.regen or not state.exists():
        state.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(EMU + [rom, '--out', str(ROOT / 'work/qa/mkstate'), '--route-str', ROUTE, '--frames', '6000',
                              '--mash', '50', '--mash-key', 'a', '--script', str(ROOT / 'tools/debug/mkstate_show.lua'),
                              '--var', "OUTSTATE='%s'" % state.as_posix()], check=True)
    ids = parse_ids(a.ids)
    chunks = [ids[i::a.jobs] for i in range(a.jobs)]
    procs = []
    for j, ch in enumerate(chunks):
        if not ch:
            continue
        out = ROOT / a.out / ('j%d' % j)
        out.mkdir(parents=True, exist_ok=True)
        cmd = EMU + [rom, '--out', str(out), '--frames', str(a.frames_per * len(ch) + 600), 
                     '--timeout', '3600', '--script', str(ROOT / 'tools/debug/msgtour.lua'),
                     '--var', 'IDS="{%s}"' % ','.join(map(str, ch)), '--var', "STATE='%s'" % state.as_posix()]
        procs.append(subprocess.Popen(cmd, stdout=subprocess.DEVNULL))
    for p in procs:
        p.wait()
    print('done; shots in', a.out)


if __name__ == '__main__':
    main()
