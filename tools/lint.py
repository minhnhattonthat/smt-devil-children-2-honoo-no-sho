"""Text lint over script/*.json (run by tools/check.py; batches.py check uses check_entry).

python -X utf8 tools/lint.py [--all]    exit 1 on errors; prints errors and one summary line
Checks per translated entry: encodable, control codes match the JP (except [n], free in wrapped forms),
width/lines per form (tools/forms.py), no Japanese left, no ordinal suffix glued to a variable, glossary Avoid list.
"""
import collections, glob, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enc
import forms
import wrap as W

ROOT = Path(__file__).resolve().parents[1]
JP_RE = re.compile(r'[぀-ヿ一-鿿！-～]')
ALLOWED_GLYPHS = set('♥〒♪●▼■◆◇○◎△▽□→←↑↓')   # JP-font symbol glyphs kept on purpose (icons, Macca sign)
CTRL_RE = re.compile(r'\[([a-z0-9]+)((?::\d+)*)\]')
FREE = {'n'}


def ctrls(t, free=FREE):
    return collections.Counter(m.group(0) for m in CTRL_RE.finditer(t) if m.group(1) not in free)


def glossary_avoid():
    p = ROOT / 'glossary.md'
    out = []
    if not p.exists():
        return out
    for line in p.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 5 and cells[0] not in ('JP', '---') and cells[4]:
            for bad in cells[4].split(','):
                bad = bad.strip()
                if bad:
                    out.append((cells[1], bad))
    return out


AVOID = glossary_avoid()


def check_entry(e, en):
    errs = []
    f = forms.form_of(e)
    if not en:
        return ['empty']
    jpleft = [c for c in en if JP_RE.match(c) and c not in ALLOWED_GLYPHS]
    if jpleft:
        errs.append('Japanese left: %s' % ''.join(jpleft[:8]))
    bad = [c for c in en if ord(c) >= 0x7F and c not in ALLOWED_GLYPHS]
    if bad:
        errs.append('non-ASCII: %r' % ''.join(bad[:8]))
    if '\t' in en or '\\u' in en:
        errs.append('tab or \\u escape')
    if re.search(r'\[(?:ec|f3|f4|ef|e8)[^\]]*\](?:st|nd|rd|th)\b', en):
        errs.append('ordinal suffix glued to a variable')
    for good, badw in AVOID:
        if re.search(r'\b%s\b' % re.escape(badw), en):
            errs.append('glossary: %r -> use %r' % (badw, good))
    if e['kind'] == 'msg':
        free = FREE if f in ('dlg', 'prompt', 'ddesc', 'desc', 'label', 'btl') else set()
        if ctrls(e['jp'], free) != ctrls(en, free):
            a, b = ctrls(e['jp'], free), ctrls(en, free)
            errs.append('controls differ: missing %s extra %s' % (dict(a - b), dict(b - a)))
        if not en.endswith('[end]'):
            errs.append('must end with [end]')
        try:
            enc.encode_msg(en, e.get('dialect', 'dlg'))
        except ValueError as x:
            errs.append(str(x))
        if f == 'dlg':
            _, warn = W.wrap(en)
            errs += warn
        elif f == 'prompt':
            t, ws = W.fit(en, forms.LINE_W)
            if len(ws) > 2 or max(ws) > forms.LINE_W:
                errs.append('prompt needs %d lines (max 2 x 216px)' % len(ws))
        elif f == 'ddesc':
            nmax = 12 if len(forms.jp_lines(e['jp'])) > 6 else 6
            t, ws = W.fit(en, forms.DDESC_W)
            if len(ws) > nmax or max(ws) > forms.DDESC_W:
                errs.append('demon description needs %d lines of %dpx (max %d)' % (len(ws), forms.DDESC_W, nmax))
        elif f == 'desc':
            w = enc.text_width(en.replace('[end]', ''), var_w=W.VAR_W)
            if '[n]' in en or w > forms.LINE_W:
                errs.append('description must be 1 line <= 216px (is %dpx)' % w)
        elif f in ('choice', 'label', 'btl'):
            jl = forms.jp_lines(e['jp'])
            el = forms.jp_lines(en)
            if f == 'choice' and len(jl) != len(el):
                errs.append('choice: %d options in JP, %d in EN' % (len(jl), len(el)))
            lim = max(max(forms.jp_px(l) for l in jl), 120 if f == 'choice' else 96)
            if f == 'btl':
                lim = forms.LINE_W
            for l in el:
                w = enc.text_width(l, var_w=W.VAR_W)
                if w > lim:
                    errs.append('line %dpx > %dpx: %r' % (w, lim, l[:40]))
    elif e['kind'] == 'str':
        try:
            b = enc.encode_str(en)
            if len(b) > e['cap'] and not e['slots']:
                errs.append('str too long: %d bytes > %d (no pointer to relocate)' % (len(b), e['cap']))
        except ValueError as x:
            errs.append(str(x))
    elif e['kind'] == 'field':
        try:
            if len(en) <= 16:
                enc.encode_field(en)
            else:
                enc.encode_str(en)          # long names go through the 01 nn escape (build.py)
        except ValueError as x:
            errs.append(str(x))
        w = enc.text_width(en)
        if w > 96:
            errs.append('name %dpx > 96px' % w)
    return errs


def main():
    nerr, ntr, ntot = 0, 0, 0
    for f in sorted(glob.glob(str(ROOT / 'script/**/*.json'), recursive=True)):
        for e in json.load(open(f, encoding='utf-8')):
            ntot += 1
            if not e.get('en') or e.get('keep'):
                continue
            ntr += 1
            for x in check_entry(e, e['en']):
                if nerr < 60:
                    print('%s %s: %s' % (Path(f).name, e['id'], x))
                nerr += 1
    print('lint: %d errors, %d/%d entries translated' % (nerr, ntr, ntot))
    return 1 if nerr else 0


if __name__ == '__main__':
    sys.exit(main())
