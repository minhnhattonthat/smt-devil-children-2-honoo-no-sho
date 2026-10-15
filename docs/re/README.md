# RE notes: Shin Megami Tensei Devil Children 2 Honoo no Sho (GBA, J)

Base: `Shin Megami Tensei - Devil Children 2 - Honoo no Sho (Japan).gba`, 8 MiB, CRC32 9A0903BC,
SHA-1 8c29d6921e7db8b0e71094d32e32066ac13c500d, header `DEBITIRUFLAMB` / `BDHJ`. Save: SRAM (`SRAM_F_V103` @0x12262C),
so expanding to 16 MiB is safe.

## Fonts (tools/font.py)
Three 1bpp fonts, header u32 size, u16 sheet w/h in 8x8 tiles, u16 glyphs/row (40), u8 glyph w, u8 glyph h, u8 bpp; bitmap at +0x10,
tiles row-major, pixel x = bit (x&7) (LSB first).
- 0x2DA2E0 12x12 (dialogue/menus), 1240 glyphs. 0x2DFB10 8x8, 1240 glyphs. 0x2E21E0 6x8, 320 glyphs.
- Font objects set up at 0x080C1EE0 (RAM 0x03003A20 = 12px, 0x03003A00 = 8px, 0x03003A40 = 6px; current font ptr 0x030039F0,
  select by 0x080C2034(0/1/2)).
- Glyph index (0x080C1DA0): code <= 0x80 -> index = code; else SJIS-like linear: (hi-0x81)*0xBC + lo-0x40 (-1 if lo>0x7F).
  Glyph set = subset of JIS in code order (symbols, ０-９, Ａ-ｚ, kana, Greek, ~900 kanji) + 44 kanji appended out of order.
- Advance = fixed font width byte (+0x0A) via 0x080C2184; line height +0x0B via 0x080C21A0. No VWF.

## Text encoding (tools/codec.py)
- Script: u16 LE units. 0x00E5-0x00FE controls, 0x00FF end. Chars: stored bytes (hi, lo) of the glyph code (e.g. 81 40 = space).
- Controls with one u16 arg: EC ED EE(speaker name) F5 F6(portrait) F7 FA(pause frames) FB. F3 = hero name. FE newline, FD next page,
  F9 wait for key, FC clear box. Dispatcher 0x08032998 (jump table 0x080329C8).
- Byte strings (menus): 2-byte glyph codes, 0x0A newline, 0x00 terminator; drawn by 0x080C20E8 (reads bytes; <=0x7F = one byte).
- Dialogue char path 0x080337CA: copies the unit into obj+0x20 (+0 terminator), draws via 0x080C20E8 at (obj+0x24, obj+0x26),
  then x += 0x080C2184() (fixed 12).

## Text locations
- Main table 0x24EC68: 5331 u32 ptrs -> messages 0x22D4B0-0x24EC67 and 0x253F94-0x27A9xx.
- Byte-string menus 0x2757xx-0x2769FF, referenced straight from code literal pools (and tables 0x0FA..., 0x1003C4...).
- Bank menu strings: table 0x22D324 (96) -> 0x276CAC.
- Battle messages: tables 0x276A74 (55 msgs) / 0x276B78 (77 msgs/strs) -> 0x106B40-0x107380; more strs to 0x1074xx.
- Fixed 16-byte name fields in records: demons ~0x2BB0A2 (stride 0x6A4), skills 0x2C33E0 (stride 0x2BC), items 0x2C5D08 (stride 0x320).
- Default hero name ジン at 0xFA3B4.
- `tools/scan_ptrs.py` lists every pointer to decodable text (work/ptrscan.tsv).

## Reference ROM (rom/ref/ice_ref.gba)
Book of Ice (BDYJ) + English proto patch (16 MiB). Main table 0x250344 (5331 entries, same count/index layout as Fire for
system text; story parts differ). English stored as ASCII byte pairs in u16 units, 0x7F = pad; its VWF hooks live at 0x0822E740+.
