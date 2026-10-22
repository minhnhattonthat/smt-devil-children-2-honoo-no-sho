# Bugs

Tick `- [x] (fixed in <build>)` once re-checked from the cited state. `(not a bug: ...)` = checked and closed.
Savestates go stale when a rebuild moves text (RAM holds ROM text pointers): start playtests from an in-game save
(`work/states/*.sav`, title > Continue) or from states made on the same build.

## 2026-10-22 playtest - honoo_en.gba sha1 096f70a4a861
Evidence: `work/playtest/ev_pC4/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0080 - text - field dialogue, Rand talk - 8-kana hero name: line runs off the right edge, rest of page lost - "ああああああああ, don't let your guar" (hero name budget 48 -> 56 px: any real 8-letter Latin name fits; 8 kana (96 px) still can overflow, known limit)
- [x] step 0008 - text - Vinecom status Spells/Skills help line cut at ~36 chars - "Water spout: small damage to two foe" (fixed: 8 help-line callers draw the whole ROM string, engine.asm HELPSITES)
- [x] step 0042 - text - same help line cut-off - "Light wave: small damage to all foes" (period lost) (fixed, as above)
- [x] step 0043 - text - same help line cut-off - "Light restores a lot of HP to all al" (fixed, as above)
- [x] step 0045 - text - same help line cut-off; "enemies" vs glossary "foes" - "Big damage to all enemies; cures sel" (cut-off fixed; wording open)
- [x] step 0053 - text - Magic > Pick Magic/Skill help line cut off - "Bubbles: medium damage, confuses two" (fixed, as above)
- [x] step 0040-0041 - text - partner name in Japanese - "ランド" (not a bug: name saved in a savestate older than the build; a new game shows Rand)
- [ ] step 0059-0063 - wording - Items tab labels vs footer names: FIGHT=Attack Items, BOOST=Support Items, GEAR=Arcane Items, HEAL=Recovery Items - "GEAR" vs "Arcane" (tab area 19x9 px; flagged choice in tools/itemtabs.py, needs the user's call)
- [x] step 0014 - wording - Vine Center "Dismiss" opens a screen titled "Release" - "Release Allies: 4" (fixed: わかれる = Dismiss everywhere)
- [x] step 0006 - text - screen titles touch/clipped by left edge - "Vine Center", "Pick Ally", "Pick Magic/Skill"; "EXP:" cut at 0011 (fixed: menu text at x 0 starts at x 2)
- [ ] step 0013 - wording - prompts flush to left edge, one or two words per line - "Send / Ally: / Please / choose.", "Use it / on whom?"
- [ ] step 0019-0021 - text - Disk menu stray period after "Name disk" when not selected - "Name disk." (str ends 7F 00 00 correctly; source of the dot not found)
- [x] step 0077 - text - Save confirm Yes/No box covers Play Time - "00: 10: 45" (not a bug: same layout in the original)

## 2026-10-22 playtest - honoo_en.gba sha1 096f70a4a861
Evidence: `work/playtest/ev_pB/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [x] step 0027-0030 - text - battle Status/Magic skill descriptions cut at 36 chars (same as field help lines) - "Big damage to all enemies; cures sel" (fixed with the help lines)
- [x] step 0015 - text - heal message missing verb - "Yurlungur" / " all HP!" (not a bug: demon names in that savestate were written before odd names got their 7F pad, c3a14bf)
- [x] step 0011-0012 - text - talk option list: hand cursor covers the first letter - "[hand]lead" / " Stare" (fixed: options start with the 12 px fullwidth space like the JP)
- [ ] step 0050 - wording - recruit message breaks to 2 lines, line 2 starts with a space - "Mini Frost joined" / " you!" (JP layout: name+particle / rest)
- [x] step 0025 - text - battle Status detail: race label flush to panel left edge; MP Cost/HP Cost too - "God Sol Leon" (fixed with the x 2 margin)
- [x] step 0042 - text - two-digit numbers show a gap between digits - "3 0 Macca gained!" (not a bug: the original shows the same gap)
- [x] step 0056 - wording - Escape says "ran away!" before the result - "'s party ran away!" (fixed: "'s party made a run for it!")
- [x] step 0040 - wording - attack announcement only name + "!!!" - "Yurlungur" / "!!!" (not a bug: JP is ！！！ too)
- [ ] step 0065 - wording - two enemies, singular message - "Mystery demon appeared!" (JP has no plural; one piece serves both)
- [x] (found by the controller) battle talk reaction "!!! (Looks confident!)(Looks confide" - (not a bug: stale savestate on a rebuilt ROM; [n] restored as in the JP anyway)

## 2026-10-22 playtest - honoo_en.gba sha1 096f70a4a861
Evidence: `work/playtest/ev_pA/NNNN.png|.sheetK.png|.<state>`, presses in `log.tsv`.

- [ ] step 0030-0033 - wording - Items GEAR tab graphic vs footer "Arcane Items" (glossary 魔装 = Arcane) - "GEAR" (see above)
- [x] step 0029 - text - START status screen: hero name and "Next LV" flush to x=0, J hook clipped - "Jin", "Next LV" (fixed with the x 2 margin)
- [ ] step 0020-0024 - text - name entry: stray white pixel right of the Back button - "Back,"
- [ ] step 0020-0022 - text - name entry field: B after typing over "J" leaves "あ n" (wrong slot erased / bad redraw) - "あ n"
- [x] step 0080 - wording - Arianrhod: "Judgment" capitalisation inconsistent - "will face Judgment" (fixed: lowercase as elsewhere; the [clr] scroll mid-sentence is the JP style)
- [ ] step 0083-0084 - wording - Rand: page ends mid-sentence - "Looks like once again you need the power" / "of us demons."
- [ ] step 0055-0058 - wording - Mom: one sentence split in three waits - "You always go" / "jumping headfirst" / "into trouble."
- [x] step 0016 - wording - space before doubled punctuation - "Whaaa... !!", "The sky... ??" (fixed)
- [x] step 0017 - wording - Harmil redundant - "But then, that airhead wouldn't be Paku otherwise." (fixed)
- [x] step 0027 - wording - silhouette odd comma - "Go, to the world beyond this light..." (fixed)
- [ ] step 0082 - wording - Rand: line 1 wraps early (sized for long name) - "Partner to the DemiKid Jin, the / chosen one," (hero name is budgeted at 56 px; a runtime wrap would be needed)
- [ ] step 0015 - text - portrait boxes: text flush against the portrait edge - "Paku, what are you up to?"
- [x] (found by the controller) title menu "New    Game": [fw] space was the 12 px fullwidth space (fixed: space + 7F pad)

## 2026-10-22 playtest round 2 - build after 366f5db
Evidence: `work/playtest/r1/NNNN.png|.mss` (story from jin_start.sav), `work/playtest/r2/` (new game "Wolfgang").
r1 steps 0100+ ran on a ROM rebuilt mid-session.

- [x] r2 step 0022-0040 - text - name entry ABC grid: 12 px cursor over proportional letters - "ABCDEFGHIJ" (fixed: grid message uses 02 cc fixed-cell escapes)
- [x] r2 step 0024-0050 - text - name entry field: slot cursor over proportional name - "Wolfgan [ ]" (fixed: field drawn in 12 px cells)
- [ ] r2 step 0062 - text - Items footer gap - "Recovery      Items" (JP layout: category right-aligned, "Items" at a fixed x; left as is)
- [ ] r2 step 0073 - wording - Mom: sentence split over two waits - "Once you make up your mind," / "you never listen to a word I say."
- [x] r1 step 0058, 0111 - text - battle Skill help line cut at 36 chars - "Light wave: small damage to all foes" (fixed: battle box draws ROM sources whole)
- [x] r1 step 0050, 0091, 0103 - text - battle command labels clipped by the 2 px margin - "Combc" (fixed: margin limited to the target's free pixels)
- [x] r1 step 0075 - text - Vinecom Status race label clipped - "Monste" (fixed, same)
- [x] r1 step 0058 - text - broken "H" in highlighted skill row - "Light Fowling" (not reproduced on the current build)
- [x] r1 step 0099 - text - JP Macca line after a recruit - "0のマッカを手に入れた" (not a bug: emulator loaded a half-written ROM during a rebuild)
- [ ] r1 step 0095 - text - talk hand cursor still touches the first letter by 1 px - "Soothe"
- [ ] r1 step 0066, 0085 - text - choice bracket touches the first letter - "[Do nothing" (dialogue choices sit at x 0; readable)
- [x] r1 step 0090 - wording - preemptive line 2 starts with a colon - ": surprise attack launched!" (fixed: "Surprise attack launched!")
- [x] r1 step 0069 - wording - wrap splits "R / Button." (fixed; also M2516 "B / Button" reworded)
- [ ] r1 step 0062 - wording - Arianrhod "Ngh... ..." then a wait mid-sentence
- [ ] r1 step 0047/0063 - wording - Rand greets Jin twice in one scene (check JP)
