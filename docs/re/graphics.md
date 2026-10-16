# Graphics text survey

All UI graphics found so far are BIOS LZ77 blocks (tools/lz.py; `lz.py scan` dumps every block to work/lz/ for
`vramfind.py`). The build writes edited blocks to free space and repoints every slot (tools/build.py `gfx` list).

| Screen | Element | Source | Status |
|---|---|---|---|
| Field menu (START) | option labels ヴィネコン まほう アイテム せってい セーブ (OBJ 64x16, 2 blocks each) | table 0x223BCC idx 0-9 | English (tools/menulabels.py, Tahoma Bold italic) |
| Item menu | selected tab 回復 こうげき ほじょ そのた マソウ 化石 (OBJ 24x16) | 0x132C28 (slots 0x02391C, 0x0FAE50) | English, 3x5 caps (tools/itemtabs.py): HEAL FIGHT BOOST OTHER GEAR FOSSIL (flagged short words) |
| Item menu | unselected tabs (BG, in the menu frame tileset) | 0x12E8F8 (slot 0x223C58) | English (itemtabs.gen_bg) |
| Name entry | buttons かな カナ ABC もどる すすむ 決定 (OBJ 32x16) | 0x127B80 (0x035424, 0x100938) | Hira Kata ABC Back Next OK (tools/namebuttons.py; Hira/Kata flagged) |
| Name entry | prompt 名前を入力して下さい (BG 96x16, tiles 12-35) | 0x126A3C (4 slots) | "Enter a name." (tools/nameprompt.py) |
| Name entry | page tabs ひらがな カタカナ 英数・記号 | text: fixed 10-byte strs 0x277A06/10/1A | Hiragana / Katakana / ABC/123!? |
| Name entry | kana grid | text msgs T2777A0... | kept Japanese on purpose (input charset); ABC page is English |
| Title | logo 真・女神転生 デビルチルドレン 炎の書 | (not located yet) | TODO |
| Title | PUSH START, New Game, Continue | text (strs, fullwidth via [fw]) | English |
| Yes/No prompt | はい/いいえ | text | English |
| Staff roll | names/roles | text (main table 5131-5271) | English; "PRESENTED BY ATLUS" already English |
