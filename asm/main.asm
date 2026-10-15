; Entry point; tools/build.py runs: armips asm/main.asm -root <repo>
; build/ holds the generated font sheets (tools/build.py writes them before assembling).
.gba
.open "build/honoo_en.gba", 0x08000000

ENGINE_BASE     equ 0x08800000
LONGNAMES       equ 0x0880F000      ; 256 u32 pointers, filled by tools/build.py (long names of 16-byte fields)

.include "asm/engine.asm"

; ---------------------------------------------------------------- English fonts
; font object = {header ptr, bitmap struct (20 bytes), width table ptr}, read-only (all game code only reads it)
.align 4
EN12_OBJ:
    .word   EN12_HDR
    .halfword 0, 1, 24, 12          ; flags, bpp, width tiles (16 glyphs * 12 px), height tiles (8 rows * 12 px)
    .word   0, EN12_DATA, 8*24      ; palette map, data, bytes per tile row
    .word   EN12_W
EN12_HDR:
    .word   24*12*8 + 16
    .halfword 24, 12, 16
    .byte   12, 12, 1, 0
EN8_OBJ:
    .word   EN8_HDR
    .halfword 0, 1, 16, 8           ; 16 glyphs * 8 px wide, 8 rows * 8 px
    .word   0, EN8_DATA, 8*16
    .word   EN8_W
EN8_HDR:
    .word   16*8*8 + 16
    .halfword 16, 8, 16
    .byte   8, 8, 1, 0
.align 4
EN12_W:     .incbin "build/en12_w.bin"
EN8_W:      .incbin "build/en8_w.bin"
.align 4
EN12_DATA:  .incbin "build/en12.bin"
EN8_DATA:   .incbin "build/en8.bin"

.close
