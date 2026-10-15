# Shin Megami Tensei: Devil Children 2 Honoo no Sho / Book of Fire (GBA) English translation

Skill: translate-retro-game (H:/translation/batch/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.
Batch brief: H:/translation/batch/projects/BATCH_BRIEF.md (all rulings pre-approved; never push/publish).

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/honoo_en.gba (`--marker` id build, `--identity`, `--only ID,ID`)
- Check:    `python -X utf8 tools/check.py` (pytest + lint; pre-commit runs it)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/honoo_en.gba --out work/qa/smoke --frames 2400 --smoke`
- Intro route: `--route-str "600 -;6 start;120 -;6 a;120 -;6 a;120 -;6 a" --frames 6000 --mash 50 --mash-key a` (dialogue from ~f3700)
- Translation: `tools/batches.py split|check bNNN|merge bNNN|status`; brief docs/translator-brief.md; style docs/style-reference.md.
  Batch files in work/tl (gitignored; merged English lives in script/*.json). Extract: `tools/extract.py` (never --force: clobbers en).
- Release:  (not yet) BPS via skill bps.py; release/<slug>_en.zip local only.

## Paths
- Original ROM: `rom/honoo.gba` (8 MiB, SHA-1 8c29d692..., DEBITIRUFLAMB, SRAM save). Ref only: `rom/ref/ice_ref.gba`
  (Book of Ice + English proto patch; tools/refice.py -> work/ref_en.json hints).
- Emulator `tools/mesen/` (MesenCE 2.2.1 + gba_bios), armips `tools/armips/` (gitignored).
- Table `tbl/jp.tbl` (tools/mktbl.py). Codec `tools/codec.py`, English enc `tools/enc.py`, wrap `tools/wrap.py`, forms `tools/forms.py`.
- Engine `asm/engine.asm` (VWF hook in DrawString 0x080C20E8), fonts `font/en12.txt`, `font/en8.txt` (hand-editable).
- RE notes: `docs/re/README.md`.

## Rulings
- Edit source only with Edit/Write tools. Honorifics dropped, given-name-first, DemiKids official names (glossary.md).
  Credits English. Graphics text in scope. Full names; engine work before abbreviation.
- Freeze tools/{enc,wrap,forms,lint}.py and font/*.txt while translator agents run (widths!).

## Debug tools (tools/debug/)
- `msgtour.py IDS --jobs 4` = any main-table message in the real box (state work/states/show.mss, `--regen` after builds).
- `runscript.lua` (--var AFTER=900 --var "SCRIPT='hex bytes'") runs a hand-made event script from the cold-boot intro
  route ("600 -;6 start;120 -;6 a;120 -;6 a"): `3C 03 03` = staff roll; `32 MM 00 XX YY DD 05 1D 00 35 00 03` = warp to map MM.
  Event opcodes: table 0x08224088 (16 xx xx = show message, 03 = end). evlog.lua logs executed opcodes.
- Review: `tools/batches.py pairs bNNN` -> reviewer brief docs/reviewer-brief.md; fixes in fixes/*.tsv -> tools/apply_fixes.py.
  Cross-batch spellings: tools/normalize.tsv -> tools/normalize.py.

## Status (2026-10-16)
- All 7137 entries translated (b000-b055) and merged. Reviews of batches in progress.
- Done: Step 0, recon (encoding, fonts, all text located), extraction (4910 msgs, 517 strs, 1719 fields), VWF engine, marker build
  boots through intro to field, pilot b000 merged; batches b001-b055 split; b001-b004 dispatched.
- Next: dispatch remaining batches; English name entry screen; debug states (menus, battle, shops); graphics survey; width gate
  for desc/ddesc/choice/menus/fields (provisional limits in tools/forms.py).
