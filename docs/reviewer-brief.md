# Translation reviewer brief - Shin Megami Tensei: Devil Children Book of Fire

You review batches of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, widths) is already enforced by the check tool - judge
translation quality. Return the report as your final message.

## Inputs (paths in your dispatch; repo root H:\translation\batch\projects\smt-devil-children-2-honoo-no-sho)
- Pairs files `work/tl/<batch>.pairs.txt`: every entry as `>> id | speaker | form` / `JP:` / `EN:`, in game order.
  Read ALL of each file, in passes if large.
- `glossary.md` (rulings at the top + decisions), `docs/style-reference.md`, `docs/names.md` (binding demon/skill/item names).
- Control codes in [brackets]: [f3] hero name, [name:N] speaker tag, [wait]/[page]/[clr] box flow, [n] line break
  (the build re-wraps dialogue; bare [n] are hints only), [ec:N] a number, [f4]/[ef]/[e8]... inserted names.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say what
  it means.
- Consistency: glossary/names.md spellings exactly (one-letter slips are what players notice); same NPC voice within a
  scene; the pilot's voices (Jin blunt, Rand cocky big brother, Paku slangy, Harmil sharp).
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable;
  abbreviated names or terms; stock phrases that read awkwardly ("... GET!"); singular/plural wrong around [ec]/[e8].
- Naturalness for a kids' adventure.

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - deferred)
Each: `id - JP gist - problem - suggested EN` (give the full corrected EN for Critical/Important, keeping every control code).
### Assessment
Approved | Needs fixes - one sentence why.

## Fix file (do this after the report)
Write your Critical + Important fixes (not Minor) with the Write tool to `fixes/r_<first batch>.tsv`, one line per entry:
`id<TAB>full corrected English` (all control codes kept). Validate with
`python -X utf8 tools/apply_fixes.py fixes/r_<first batch>.tsv --dry` until it prints `0 problems`. Do not edit any
other file. The controller applies the fixes.
