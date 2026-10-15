"""Text form of each script entry and its English limits (shared by batches.py, lint.py, build.py).

Forms (msg entries are classified from their JP and main-table index):
  dlg     dialogue with [wait]: free text, the build auto-wraps (216 px/line, 192 with a portrait, 2 lines/box).
  prompt  yes/no question ending [fb:N]: at most 2 lines of 216 px (auto-wrapped, no extra boxes).
  choice  option list (lines split by [n], one option per line): same number of lines; each line <= max(JP px, 120).
  desc    one-line help text (skills/items/maps, idx 2611-3439): 1 line <= 216 px.
  ddesc   demon description (idx 3440-3989): 6 lines (12 if the JP has 12) <= 120 px each; the build wraps.
  label   short single text (names, places, battle shouts): <= max(JP px, 96) px, 1 line.
  btl     battle-preprocessed message: lines <= 216 px (provisional).
  str     menu byte string: <= cap bytes (in place) unless it has pointer slots; px <= max(JP px, 48).
  field   16-byte name field: <= 16 chars, <= 96 px (12 px font) and <= 72 px (8 px font) (provisional).
"""
import re

LINE_W = 216
DDESC_W = 120


def jp_lines(jp):
    t = re.sub(r'\[(?!n\])[^\]]*\]', '', jp)
    return t.split('[n]')


def form_of(e):
    jp = e['jp']
    if e['kind'] == 'field':
        return 'field'
    if e['kind'] == 'str':
        return 'str'
    if e.get('dialect') == 'btl':
        return 'btl'
    i = (e.get('idx') or [None])[0]
    if '[wait]' in jp:
        return 'dlg'
    if '[fb:' in jp:
        return 'prompt'
    if i is not None and 3440 <= i < 3990:
        return 'ddesc'
    if i is not None and 2611 <= i < 3440:
        return 'desc'
    if '[n]' in jp:
        return 'choice'
    return 'label'


def jp_px(line):
    return 12 * len(line)


def limit_text(e):
    f = form_of(e)
    if f == 'dlg':
        return 'auto-wrap (216px lines, 192 with portrait, 2 lines/box)'
    if f == 'prompt':
        return '<=2 lines x 216px'
    if f == 'choice':
        w = max(max(jp_px(l) for l in jp_lines(e['jp'])), 120)
        return '%d options, each <=%dpx' % (len(jp_lines(e['jp'])), w)
    if f == 'desc':
        return '1 line <=216px'
    if f == 'ddesc':
        return '<=%d lines x %dpx (auto-wrap)' % (12 if len(jp_lines(e['jp'])) > 6 else 6, DDESC_W)
    if f == 'label':
        return '<=%dpx' % max(max(jp_px(l) for l in jp_lines(e['jp'])), 96)
    if f == 'btl':
        return 'lines <=216px'
    if f == 'str':
        return '<=%d bytes%s' % (e['cap'] - 1, ' (or longer: relocatable)' if e['slots'] else '')
    if f == 'field':
        return '<=96px'
    return ''
