# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (v1.1 published on GitHub 2026-10-22: github.com/minhnhattonthat/smt-devil-children-2-honoo-no-sho).
- **Release v1.1:** patch SHA-1 41242f6abe5609bf38ca5c088c08779983e4d6af, patched ROM SHA-1
  b509d2ef369d0c630b1a09418e41fcd8bcdc0f06 (CRC32 31842A45); includes the 2026-10-22 playtest fixes.
- **Done:** Translation 7139/7149 (10 kept: kana grid, arrays, false ptr); all batches reviewed, fixes applied (fixes/*.tsv).
  Graphics: title logo, field menu labels, item tabs, name entry (both button sets, Big/Small), Vinecom, ally-screen
  plates, settings buttons; battle menu x fix; condensed en8 font. Strs end on a 0000 unit (game strcpy is unit-wise:
  recruiting a demon hung); wrap keeps the space before vars.
- **2026-10-22 playtests (5 agents, docs/bugs.md):** fixed full help lines (8 menu callers + battle box drew a
  36-char copy; engine.asm HELPSITES), x-0 menu text margin (clamped to the target), name entry ABC grid/field in
  12 px cells (02 cc escape), talk options indent, title [fw] space, wording. Released in v1.1.
- **Next:** late-game graphics labels not yet seen in QA; playtest past Harajuku Avenue (needs a later in-game save);
  open items in docs/bugs.md (item tab names need the user's call).
- **Open bugs:** settings screen cursor box keeps the JP word width; see docs/bugs.md.
- **Debug:** work/states/sNNNNNN.mss are stale (older build: wrong names, garbled text); start playtests from
  work/states/jin_start.sav (title > Continue). Savestates go stale whenever text moves. tools/debug/btlsrc.lua,
  btladd.lua, btllines.lua: battle box lines; glyphlog.lua: glyph positions.
- **Waiting on the user:** nothing.
