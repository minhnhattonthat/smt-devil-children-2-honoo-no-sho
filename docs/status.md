# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (released v1.0, local zip only). Last build: 93565c6 (2026-10-16).
- **Done:** Translation 7139/7149 (10 kept: kana grid, arrays, false ptr); all batches reviewed, fixes applied (fixes/*.tsv).
  Graphics: title logo, field menu labels, item tabs, name entry (both button sets, Big/Small), Vinecom, ally-screen
  plates, settings buttons; battle menu x fix; condensed en8 font. Strs end on a 0000 unit (game strcpy is unit-wise:
  recruiting a demon hung); wrap keeps the space before vars.
- **Release v1.0:** patch SHA-1 b11c5236897e9f6dc88c8e737bef84bc6fa6da28, patched ROM SHA-1 acacd07d...
- **2026-10-22 playtests (5 agents, docs/bugs.md):** fixed full help lines (8 menu callers + battle box drew a
  36-char copy; engine.asm HELPSITES), x-0 menu text margin (clamped to the target), name entry ABC grid/field in
  12 px cells (02 cc escape), talk options indent, title [fw] space, wording. Not released yet (v1.0 zip is older).
- **Next:** late-game graphics labels not yet seen in QA; playtest past Harajuku Avenue (needs a later in-game save);
  open items in docs/bugs.md (item tab names need the user's call).
- **Open bugs:** settings screen cursor box keeps the JP word width; see docs/bugs.md.
- **Debug:** work/states/sNNNNNN.mss are stale (older build: wrong names, garbled text); start playtests from
  work/states/jin_start.sav (title > Continue). Savestates go stale whenever text moves. tools/debug/btlsrc.lua,
  btladd.lua, btllines.lua: battle box lines; glyphlog.lua: glyph positions.
- **Waiting on the user:** nothing.
