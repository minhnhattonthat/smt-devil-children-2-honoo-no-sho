; English engine: variable-width ASCII in the game's byte-string drawer.
; Assembled by tools/build.py with armips:  armips asm/main.asm  (ROM = build/honoo_en.gba, opened by main.asm)
;
; Bytes 0x20-0x7E in any string are drawn from an English font (index = byte) with per-glyph advance;
; bytes >= 0x81 start a 2-byte Japanese glyph code exactly as before (fixed advance).
; LAST_ADV = total advance of the last DrawString call; the dialogue engine's width getter (0x080C2184)
; now returns it, so the typewriter advances by the real width of each u16 unit (two ASCII chars).

LAST_ADV        equ 0x03003A18      ; unused IWRAM word (spare tail of the 8px font object)
CUR_FONT        equ 0x030039F0      ; current font object pointer
FONT8_OBJ       equ 0x03003A00
FONT12_OBJ      equ 0x03003A20
DrawGlyph       equ 0x080C208D      ; (target, code, x, y)   (+1: Thumb, called via bx)
LineHeight      equ 0x080C21A1      ; () -> current font glyph height

; ---------------------------------------------------------------- hooks
.org 0x080C20E8                     ; DrawString(target, str, x, y) -> jump to ours (args untouched)
.thumb
    bx      pc
    nop
.arm
    ldr     r12, [pc]
    bx      r12
    .word   DrawStringVWF + 1

.org 0x080C2184                     ; GlyphAdvance() -> LAST_ADV
.thumb
    ldr     r0, [pc, #4]
    ldr     r0, [r0]
    bx      lr
    nop
    .word   LAST_ADV

; ---------------------------------------------------------------- new code
.org ENGINE_BASE
.thumb
.align 4
DrawStringVWF:                      ; r0 target, r1 str, r2 x, r3 y
    push    {r4-r7, lr}
    sub     sp, #8
    mov     r4, r0
    mov     r5, r1
    mov     r6, r2
    mov     r7, r3
    str     r2, [sp]                ; x at start (advance)
    str     r2, [sp, #4]            ; x at line start
@@loop:
    ldrb    r0, [r5]
    add     r5, #1
    cmp     r0, #0
    beq     @@done
    cmp     r0, #0x0A
    bne     @@notlf
    ldr     r6, [sp, #4]
    bl      @@callLineHeight
    add     r7, r7, r0
    ldrh    r1, [r4, #6]            ; target height in tiles
    lsl     r1, r1, #3
    cmp     r1, r7
    blt     @@done
    b       @@loop
@@notlf:
    cmp     r0, #0x80
    bhs     @@jp
    cmp     r0, #0x20
    blo     @@loop
    ; ---- English glyph: swap in the matching English font object, draw index = byte
    mov     r1, r0                  ; code
    ldr     r2, =CUR_FONT
    ldr     r3, [r2]
    push    {r1, r3}                ; code, saved font
    ldr     r0, =FONT12_OBJ
    cmp     r3, r0
    beq     @@use12
    ldr     r0, =EN8_OBJ
    b       @@set
@@use12:
    ldr     r0, =EN12_OBJ
@@set:
    str     r0, [r2]
    mov     r0, r4
    mov     r2, r6
    mov     r3, r7
    bl      @@callDrawGlyph
    pop     {r1, r3}
    ldr     r2, =CUR_FONT
    ldr     r0, [r2]                ; English obj in use -> its width table at obj+0x18
    str     r3, [r2]                ; restore game font
    ldr     r0, [r0, #0x18]
    ldrb    r0, [r0, r1]
    add     r6, r6, r0
    b       @@loop
@@jp:
    lsl     r1, r0, #8
    ldrb    r0, [r5]
    add     r5, #1
    orr     r1, r0
    mov     r0, r4
    mov     r2, r6
    mov     r3, r7
    bl      @@callDrawGlyph
    ldr     r0, =CUR_FONT
    ldr     r0, [r0]
    ldr     r0, [r0]
    ldrb    r0, [r0, #0x0A]         ; fixed advance of the game font
    add     r6, r6, r0
    b       @@loop
@@done:
    ldr     r0, [sp]
    sub     r0, r6, r0
    ldr     r1, =LAST_ADV
    str     r0, [r1]
    add     sp, #8
    pop     {r4-r7}
    pop     {r0}
    bx      r0
@@callDrawGlyph:                    ; veneer: keep r0-r3 (args), jump via r12
    push    {r0}
    ldr     r0, =DrawGlyph
    mov     r12, r0
    pop     {r0}
    bx      r12
@@callLineHeight:
    ldr     r0, =LineHeight
    bx      r0
.pool
