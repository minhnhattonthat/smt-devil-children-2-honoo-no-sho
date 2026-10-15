"""Translation batches.

python -X utf8 tools/batches.py split [--size 3000]   -> work/tl/bNNN.tsv for untranslated entries (+ auto-fills dev placeholders)
python -X utf8 tools/batches.py check bNNN            -> validates work/tl/bNNN.out.tsv (prints OK or errors)
python -X utf8 tools/batches.py merge bNNN [--force]  -> writes `en` into script/*.json (refuses if check fails)
python -X utf8 tools/batches.py status                -> per-batch state
Input TSV: id <TAB> speaker <TAB> form <TAB> limit <TAB> jp <TAB> ref   (ref = Book of Ice proto English, may be empty)
Output TSV: id <TAB> English   (one line per input id; same ids, any order)
"""
import argparse, glob, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import forms
import lint

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / 'work/tl'
AUTO = {'開発中[end]': 'In development.[end]', '開発中[wait][end]': 'In development.[wait][end]',
        'ダミー[end]': 'Dummy[end]', '使用禁止[end]': 'Unused[end]', '開発中': 'In dev.', 'ダミー': 'Dummy'}


def load():
    files = {}
    for f in sorted(glob.glob(str(ROOT / 'script/**/*.json'), recursive=True)):
        files[f] = json.load(open(f, encoding='utf-8'))
    return files


def save(files, which):
    for f in which:
        with open(f, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(files[f], fh, ensure_ascii=False, indent=1)
            fh.write('\n')


def speakers(files):
    names = {}
    for es in files.values():
        for e in es:
            for i in e.get('idx') or []:
                if 2320 <= i < 2420:
                    names[i - 2320] = (e['jp'].replace('[end]', ''), e.get('en', '').replace('[end]', ''))
    return names


def order_key(e, f):
    group = Path(f).relative_to(ROOT / 'script').as_posix()
    fm = forms.form_of(e)
    rank = {'dlg': 0, 'prompt': 0, 'choice': 0, 'label': 1, 'btl': 2, 'desc': 3, 'ddesc': 4, 'str': 5, 'field': 6}[fm]
    i = (e.get('idx') or [10 ** 6])[0]
    if fm in ('dlg', 'prompt', 'choice') and not group.startswith('main'):
        rank = 2
    return (rank, i, group, e['id'])


def cmd_split(a):
    files = load()
    refs = {}
    rp = ROOT / 'work/ref_en.json'
    if rp.exists():
        refs = json.load(open(rp, encoding='utf-8'))
    names = speakers(files)
    todo, auto_files = [], set()
    for f, es in files.items():
        for e in es:
            if e.get('en') or e.get('keep'):
                continue
            if e['jp'] in AUTO and e['kind'] != 'field':
                e['en'] = AUTO[e['jp']]
                auto_files.add(f)
                continue
            todo.append((order_key(e, f), e))
    save(files, auto_files)
    todo.sort(key=lambda x: x[0])
    TL.mkdir(parents=True, exist_ok=True)
    existing = sorted(TL.glob('b*.tsv'))
    taken = set()
    for p in existing:
        if not p.name.endswith('.out.tsv'):
            for line in open(p, encoding='utf-8'):
                taken.add(line.split('\t', 1)[0])
    n = len([p for p in existing if not p.name.endswith('.out.tsv')])
    batch, chars, made = [], 0, 0

    def flush():
        nonlocal batch, chars, n, made
        if not batch:
            return
        p = TL / ('b%03d.tsv' % n)
        with open(p, 'w', encoding='utf-8', newline='\n') as fh:
            for e in batch:
                sp = ''
                m = re.match(r'\[name:(\d+)\]', e['jp'])
                if m and int(m.group(1)) in names:
                    jpn, enn = names[int(m.group(1))]
                    sp = enn or jpn
                ref = refs.get(e['id'], '').replace('\t', ' ')
                fh.write('\t'.join([e['id'], sp, forms.form_of(e), forms.limit_text(e), e['jp'], ref]) + '\n')
        n += 1
        made += 1
        batch, chars = [], 0
    prev_rank = None
    for key, e in todo:
        if e['id'] in taken:
            continue
        if prev_rank is not None and key[0] != prev_rank and chars > a.size // 3:
            flush()
        prev_rank = key[0]
        batch.append(e)
        chars += len(re.sub(r'\[[^\]]*\]', '', e['jp']))
        if chars >= a.size or len(batch) >= 160:
            flush()
    flush()
    print('auto-filled placeholders in %d files; made %d batches (next b%03d)' % (len(auto_files), made, n))


def read_out(b):
    p = TL / (b + '.out.tsv')
    if not p.exists():
        return None, ['no output file %s' % p.name]
    out, errs = {}, []
    for k, line in enumerate(open(p, encoding='utf-8-sig'), 1):
        line = line.rstrip('\n').rstrip('\r')
        if not line.strip():
            continue
        if '\t' not in line:
            errs.append('line %d: no TAB' % k)
            continue
        i, en = line.split('\t', 1)
        if i in out:
            errs.append('duplicate id %s' % i)
        out[i.strip()] = en
    return out, errs


def cmd_check(a, quiet=False):
    files = load()
    byid = {e['id']: e for es in files.values() for e in es}
    ids = [line.split('\t', 1)[0] for line in open(TL / (a.batch + '.tsv'), encoding='utf-8')]
    out, errs = read_out(a.batch)
    if out is None:
        print('\n'.join(errs))
        return 1
    missing = [i for i in ids if i not in out]
    extra = [i for i in out if i not in ids]
    if missing:
        errs.append('missing ids: %s' % ' '.join(missing[:20]))
    if extra:
        errs.append('extra ids: %s' % ' '.join(extra[:20]))
    for i in ids:
        if i in out:
            for x in lint.check_entry(byid[i], out[i]):
                errs.append('%s: %s' % (i, x))
    if errs:
        print('\n'.join(errs[:80]))
        print('%d problems' % len(errs))
        return 1
    if not quiet:
        print('OK %s (%d entries)' % (a.batch, len(ids)))
    return 0


def cmd_merge(a):
    if cmd_check(a, quiet=True) and not a.force:
        print('merge refused: check fails')
        return 1
    files = load()
    out, _ = read_out(a.batch)
    changed = set()
    for f, es in files.items():
        for e in es:
            if e['id'] in out and (a.force or not lint.check_entry(e, out[e['id']])):
                e['en'] = out[e['id']]
                changed.add(f)
    # name fields are batched once per unique JP: copy the English to every other field with the same JP
    byjp = {}
    for es in files.values():
        for e in es:
            if e['kind'] == 'field' and e['id'] in out:
                byjp[e['jp']] = e['en']
    for f, es in files.items():
        for e in es:
            if e['kind'] == 'field' and not e.get('en') and e['jp'] in byjp:
                e['en'] = byjp[e['jp']]
                changed.add(f)
    save(files, changed)
    print('merged %s into %d files' % (a.batch, len(changed)))
    return 0


def cmd_status(a):
    files = load()
    byid = {e['id']: e for es in files.values() for e in es}
    for p in sorted(TL.glob('b*.tsv')):
        if p.name.endswith('.out.tsv'):
            continue
        ids = [l.split('\t', 1)[0] for l in open(p, encoding='utf-8')]
        done = sum(1 for i in ids if byid.get(i, {}).get('en'))
        has_out = (TL / (p.stem + '.out.tsv')).exists()
        print('%s %4d entries  merged %4d  out=%s' % (p.stem, len(ids), done, 'yes' if has_out else 'no'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('split')
    s.add_argument('--size', type=int, default=3000)
    for c in ('check', 'merge'):
        s = sp.add_parser(c)
        s.add_argument('batch')
        s.add_argument('--force', action='store_true')
    sp.add_parser('status')
    a = ap.parse_args()
    sys.exit({'split': cmd_split, 'check': cmd_check, 'merge': cmd_merge, 'status': cmd_status}[a.cmd](a) or 0)
