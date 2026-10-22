# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (v1.2 published on GitHub 2026-10-22: github.com/minhnhattonthat/smt-devil-children-2-honoo-no-sho).
- **Release v1.2:** patch SHA-1 810649eaa9a2b770b0213294c2ddcd4bf72f5426, patched ROM SHA-1
  9443bea3d521bd3d28d2613bdda78a78cd152cdd (CRC32 840A7BE0). v1.1 had the playtest fixes; v1.2 adds the QA-gate fixes.
- **QA gate (2026-10-22):** msgtour 0-5330 -> 164 boxsheets, 4 reviewer agents, work/qa/manifest.tsv + verdicts/;
  tools/release.py now runs `qa_gate.py check` first (re-init the manifest after a new tour). Fixed: option lists after
  [page] (m2281-2290) and var+punctuation wrap (m1473) in wrap.py, m1960 wording. Tour artefacts, not bugs: battle-dialect
  msgs (m4382-4413 [f5], m4518-4557 [ec]: field engine reads an arg there), ids 4087-4293 (not text), end shots of
  [end]-only msgs (race: msgtour --end-delay 4 shows them), Yes/No fade-in. JP ROM shows the same in each case.
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
