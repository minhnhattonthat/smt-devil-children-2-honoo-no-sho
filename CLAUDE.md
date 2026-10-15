# Shin Megami Tensei: Devil Children 2 Honoo no Sho / Book of Fire (GBA) English translation

Skill: translate-retro-game (H:/translation/batch/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.
Batch brief: H:/translation/batch/projects/BATCH_BRIEF.md (all rulings pre-approved; never push/publish).

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/honoo_en.gba (not yet)
- Check:    `python -X utf8 tools/check.py` (pytest + lint; pre-commit runs it)
- Smoke:    `python -X utf8 H:/translation/batch/.claude/skills/translate-retro-game/scripts/emu.py build/honoo_en.gba --out work/qa/smoke --frames 2400 --smoke`
- Release:  (not yet) BPS via skill bps.py; release/<slug>_en.zip local only.

## Paths
- Original ROM: `rom/honoo.gba` (copy of the No-Intro file in rom/; 8 MiB, SHA-1 8c29d692..., header DEBITIRUFLAMB, SRAM save).
- Reference only: `rom/ref/ice_ref.gba` = Koori no Sho (Book of Ice, BDYJ) with someone's English proto patch, 16 MiB.
- Emulator: `tools/mesen/` (MesenCE 2.2.1 + gba_bios). armips: `tools/armips/`. Both gitignored.
- Table `tbl/jp.tbl` (glyph code -> char; built by tools/mktbl.py from tools/ocr_font.py). Codec `tools/codec.py`. Fonts `tools/font.py`.
- RE notes: `docs/re/README.md`.

## Rulings
- Edit source only with Edit/Write tools. Honorifics dropped (register), given-name-first. Official SMT / DemiKids English names.
  Credits English. Graphics text in scope. Full names, engine work before abbreviation.

## Status
- Step 0 done (emu boots original). Phase 1 recon in progress: encoding, controls, fonts, main table done (docs/re/README.md).
