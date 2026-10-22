"""Release: build, romdiff against build/ranges.txt, BPS patch (made + re-applied + verified), README, zip.

python -X utf8 tools/release.py   -> release/smt-devil-children-2-honoo-no-sho_en.zip (patch + README only). Local only.
"""
import hashlib, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SCRIPTS as SKILL  # noqa: E402
SLUG = 'smt-devil-children-2-honoo-no-sho'
PY = [sys.executable, '-X', 'utf8']


def run(*a):
    r = subprocess.run([*a], cwd=ROOT)
    if r.returncode:
        raise SystemExit('failed: %s' % ' '.join(map(str, a)))


def main():
    run(*PY, 'tools/build.py')
    rs = sorted(tuple(int(x, 16) for x in l.split('-')) for l in (ROOT / 'build/ranges.txt').read_text().split())
    merged = []
    for a, b in rs:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    run(*PY, str(SKILL / 'romdiff.py'), 'rom/honoo.gba', 'build/honoo_en.gba', *['%X-%X' % (a, b - 1) for a, b in merged])
    rel = ROOT / 'release'
    rel.mkdir(exist_ok=True)
    patch = rel / (SLUG + '_en.bps')
    run(*PY, str(SKILL / 'bps.py'), 'make', 'rom/honoo.gba', 'build/honoo_en.gba', str(patch))
    out_sha1 = hashlib.sha1((ROOT / 'build/honoo_en.gba').read_bytes()).hexdigest()
    readme = (ROOT / 'tools/README.release.txt').read_text(encoding='utf-8').replace('{OUT_SHA1}', out_sha1)
    z = rel / (SLUG + '_en.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as f:
        f.write(patch, patch.name)
        f.writestr('README.txt', readme.replace('\n', '\r\n'))
    print('zip', z)
    print('patch sha1', hashlib.sha1(patch.read_bytes()).hexdigest(), 'rom sha1', out_sha1)


if __name__ == '__main__':
    main()
