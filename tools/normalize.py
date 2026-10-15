"""Apply cross-batch spelling fixes (tools/normalize.tsv: wrong<TAB>right, whole words) to every `en` in script/.
python -X utf8 tools/normalize.py      (run after merges; prints the number of entries changed)
"""
import glob, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    pairs = []
    for line in open(ROOT / 'tools/normalize.tsv', encoding='utf-8'):
        line = line.rstrip('\n')
        if line and not line.startswith('#'):
            a, b = line.split('\t')
            pairs.append((re.compile(r'(?<![A-Za-z])%s(?![a-z])' % re.escape(a)), b))
    n = 0
    for f in glob.glob(str(ROOT / 'script/**/*.json'), recursive=True):
        es = json.load(open(f, encoding='utf-8'))
        ch = False
        for e in es:
            en = e.get('en')
            if not en:
                continue
            new = en
            for rx, b in pairs:
                new = rx.sub(b, new)
            if new != en:
                e['en'] = new
                ch = True
                n += 1
        if ch:
            with open(f, 'w', encoding='utf-8', newline='\n') as fh:
                json.dump(es, fh, ensure_ascii=False, indent=1)
                fh.write('\n')
    print('normalized %d entries' % n)


if __name__ == '__main__':
    main()
