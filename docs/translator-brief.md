# Translator brief - Shin Megami Tensei: Devil Children Book of Fire (GBA, 2003)

You translate part of the Japanese script of *Devil Children: Honoo no Sho* (Book of Fire) into English for a fan patch.
Monster-collecting kids' RPG (Atlus, DemiKids line): the hero Jin, a DemiKid, and his partner Rand (a Sol Cat demon) go to the
Demon World to rescue Lena and children kidnapped by angels during "Armageddon". Light, punchy kids' adventure tone.
Work only on the batch named in your dispatch. Do all translation yourself; do not dispatch subagents.
Repo root: H:\translation\batch\projects\smt-devil-children-2-honoo-no-sho (run commands from there).

## Read first
1. `docs/style-reference.md` - voices and approved example pairs (the prologue). Match this voice.
2. `glossary.md` - binding names and terms (Avoid column = banned spellings; the check enforces it).
3. `docs/names.md` - binding English for every demon, skill, item and ability name already translated. Search it (Grep)
   for each name you meet in your batch instead of inventing a new spelling.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese<TAB>ref`
- Lines are in game order; use neighbours for context.
- `speaker`: from the `[name:N]` code. `[name:0]` = the hero (Jin, player-named; written `[f3]` in text), `[name:1]` = Rand
  (his partner), `[name:4]` = the demon being talked to (negotiation). No `[name:]` = narration or an unnamed NPC.
- `ref`: an unofficial, loose English proto patch of the sister game (Book of Ice). Often a different scene. Use it at most as
  a hint for terminology; translate from the Japanese.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (Write), never a shell heredoc
`id<TAB>English`, every input id exactly once. Plain ASCII only (straight quotes, `...`); no tabs inside, no Japanese.
Exceptions allowed: `♥` and the Macca sign `〒` (keep `〒` before a money number exactly as in the JP: `〒[ec:0]`).

## Control codes (in square brackets) - copy them all
- Keep every code from the JP, same count, in the matching place: `[name:N] [face:N] [wait] [page] [clr] [pause:N] [e5]`
  `[f7:N]` (text colour on/off, wrap the same words) `[fb:N]` (yes/no prompt) `[end]` and the variables below.
- Variables (inserted text): `[f3]` hero name; `[f4] [ef] [e8] [f2] [f1] [eb] [ed:N] [f5]` item/skill/demon names; `[ec:N]`
  a number. No suffix glued to a variable ("[ec:0]th" is banned), no "a/an" right before one, and keep the sentence
  correct for singular and plural names ("[e8] joined you!" not "[e8] join").
- Line breaks: in `dlg`, the build wraps text itself (2 lines per box). Do NOT place `[n]` for wrapping. Keep `[n]` only where
  the JP has `[wait][n]` (a pause, then the next line). A bare `[n]` you leave in is treated as a space.
  `[page]` starts a new box; `[clr]` scrolls (after `[wait]`). Keep the JP's `[wait][page]` / `[wait][clr]` structure;
  long English simply flows into extra boxes automatically.
- Other forms (see `form`/`limit` columns):
  - `prompt`: yes/no question, max 2 lines of 216 px (about 45 characters per line); the build wraps.
  - `choice`: option list, one option per line, separated by `[n]`: SAME number of `[n]`-lines as the JP; each line must fit the
    pixel limit given. Leading fullwidth spaces in options can be dropped.
  - `desc`: one-line help text, max 216 px (~45 chars), no `[n]`. Use terse help-text style ("Restores HP to one ally.").
  - `ddesc`: demon description, the build wraps into max 6 lines of 120 px (~24 chars each); write normal prose, no `[n]`.
  - `label`: name/place/shout, one line, pixel limit given.
  - `btl`: battle message; `[f5]` = acting demon's name, `[ef]` = item/skill name, `[ec]` = number (no argument in battle text).
  - `str`: menu text, byte limit given (1 byte per English char). If "relocatable", it may be longer, but keep menus tight.
  - `field`: a 16-byte name (demon, skill, item...): max 96 px (any length in characters; names over 16 chars are stored through an escape). In field batches the `speaker` column
    gives the category (demon / skill / item / combo skill / enemy/NPC record / passive ability). Each Japanese name
    appears once; the build copies it to every duplicate. Demons: the official Atlus English spelling of the mainline
    SMT / Persona games (Cerberus, Jack Frost, Pyro Jack, Pixie, Kaiwan...). Spells: SMT names (Agi, Agilao, Bufu,
    Zio, Zan, Dia, Media, Patra, Tarukaja...). Kana-only skill names: short natural English (きずぐすり = Medicine).
    Dev placeholders (ダミー123, ■予備■) -> "Dummy 123", "(reserve)".
- Width: proportional font, about 4.5 px per lowercase char (i 2px, m 8px, W 9px). Check with the tool below.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` and fix every reported id until it prints OK.
Dry-run one line: `python -X utf8 tools/wrap.py "text"` prints the wrapped lines and pixel widths.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add or drop content. Wordplay and jokes
  keep their punch (adapt them; no translator notes). Characters' verbal tics become an English voice, not romanized endings.
- Names/terms exactly as in the glossary. Demon/skill names: official SMT English spellings (Agi, Bufu, Zio, Zan, Dia, Pixie,
  Jack Frost, Cerberus...). Never abbreviate to fit; if impossible, keep meaning and report `LONG: id`.
- Honorifics dropped (さま -> Lord/Lady for Michael/Lucifer and similar masters; otherwise plain names). Given name first.
- Punctuation: 「」『』 -> "..." (no quotes around a simple item name); ・・・ -> `...`; ！！ -> `!!`; ？！ -> `?!`;
  katakana-only speech -> ALL CAPS only for robotic/possessed/eerie voices (e.g. brainwashed children, the Ice Apostle's
  minions); ordinary katakana emphasis or slang shouts stay in normal case. Check the glossary's "Decisions" section. Kana-only words for kids stay simple English.
- Mistakes already caught: making Rand sound formal (he's a cocky, warm big-brother type); dropping `[pause:N]` codes; turning
  `[wait][n]` into `[wait][page]`.

## Consistency
Never edit `glossary.md` or any file other than your output. For a recurring name/term not in the glossary, pick one form,
use it consistently, and report it.

## Report (reply with only this)
File written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
