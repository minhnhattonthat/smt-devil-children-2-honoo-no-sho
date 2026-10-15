"""Apply reviewer fixes: fixes/*.tsv lines `id<TAB>English` (later files win). Each fix must pass the lint.
python -X utf8 tools/apply_fixes.py [files...]     (default: every fixes/*.tsv, in name order)
"""
import glob, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint

ROOT = Path(__file__).resolve().parents[1]


def main(paths):
    fixes = {}
    for p in paths or sorted(glob.glob(str(ROOT / 'fixes/*.tsv'))):
        for k, line in enumerate(open(p, encoding='utf-8-sig'), 1):
            line = line.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            i, en = line.split('\t', 1)
            fixes[i.strip()] = (en, '%s:%d' % (Path(p).name, k))
    bad, n = 0, 0
    for f in sorted(glob.glob(str(ROOT / 'script/**/*.json'), recursive=True)):
        es = json.load(open(f, encoding='utf-8'))
        ch = False
        for e in es:
            if e['id'] in fixes:
                en, where = fixes.pop(e['id'])
                errs = lint.check_entry(e, en)
                if errs:
                    print('%s %s: %s' % (where, e['id'], '; '.join(errs)))
                    bad += 1
                    continue
                if e.get('en') != en:
                    e['en'] = en
                    ch = True
                    n += 1
        if ch:
            with open(f, 'w', encoding='utf-8', newline='\n') as fh:
                json.dump(es, fh, ensure_ascii=False, indent=1)
                fh.write('\n')
    for i, (en, where) in fixes.items():
        print('%s: unknown id %s' % (where, i))
        bad += 1
    print('applied %d fixes, %d problems' % (n, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
