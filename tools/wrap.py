"""Auto line-wrap for dialogue messages (author paragraphs, the build makes the lines).

Box model (dialogue engine, measured from the JP script and the handlers):
  2 lines per box, 216 px per line; 192 px while a portrait is shown ([face:N], N != 65535).
  [n] = next line; [page] = new box; [clr] = scroll one line (continue on the bottom line) after [wait].
Overflow on line 1 -> [n]; overflow on line 2 -> [wait][clr] (scroll, like the Japanese script does).
Variables are budgeted at their widest plausible English width (VAR_W).

python -X utf8 tools/wrap.py "text"   -> prints the wrapped text and the width of every line
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enc

W_PLAIN, W_FACE = 216, 192
VAR_W = {'f3': 48, 'f4': 84, 'ef': 84, 'e8': 84, 'f2': 84, 'f1': 84, 'eb': 84, 'ed': 84, 'ec': 48, 'f5': 84,
         'f8': 84, 'e6': 84, 'e7': 84, 'e9': 84, 'ea': 84, 'f0': 84}
NEWBOX = {'page', 'e5'}
TOKS = re.compile(r'(\[[^\]]*\])')


def tokens(text):
    for part in TOKS.split(text):
        if not part:
            continue
        if part.startswith('['):
            yield ('c', part)
        else:
            for w in re.split(r'( )', part):
                if w:
                    yield ('t', w)


def wrap(text, dialect='dlg'):
    """Return (wrapped_text, warnings). Existing [n] are kept; breaks are added where a line overflows."""
    out = []
    warn = []
    line, x = 0, 0
    face = False
    limit = W_PLAIN
    pending_space = False

    def brk():
        nonlocal line, x
        if line == 0:
            out.append('[n]')
            line = 1
        else:
            out.append('[wait][clr]')
            line = 1
        x = 0

    for kind, tok in tokens(text):
        if kind == 'c':
            name = tok[1:-1].split(':')[0]
            if name == 'face':
                face = tok != '[face:65535]'
                limit = W_FACE if face else W_PLAIN
            if name == 'n':
                if line == 0:
                    out.append(tok)
                    line = 1
                else:
                    if out and out[-1] == '[wait]':
                        out.append('[clr]')
                    else:
                        out.append('[wait][clr]')
                x = 0
                pending_space = False
                continue
            if name in NEWBOX:
                line, x = 0, 0
                pending_space = False
            elif name == 'clr':
                line, x = 1, 0
                pending_space = False
            if name in VAR_W:
                w = enc.text_width(tok, var_w=VAR_W)
                if x and x + w > limit:
                    brk()
                x += w
            out.append(tok)
            continue
        if tok == ' ':
            pending_space = True
            continue
        w = enc.text_width(tok)
        sp = enc.text_width(' ') if (pending_space and x) else 0
        if x and x + sp + w > limit:
            brk()
            sp = 0
        if sp:
            out.append(' ')
        if w > limit:
            warn.append('word wider than a line: %r' % tok)
        out.append(tok)
        x += sp + w
        pending_space = False
    return ''.join(out), warn


def lines(wrapped):
    """Split wrapped text into displayed lines (for width reports)."""
    return [l for l in re.split(r'\[(?:n|page|clr|e5)\]', wrapped)]


if __name__ == '__main__':
    t, w = wrap(sys.argv[1])
    print(t)
    for l in lines(t):
        print(enc.text_width(l, var_w=VAR_W), repr(l))
    for x in w:
        print('WARN', x)
