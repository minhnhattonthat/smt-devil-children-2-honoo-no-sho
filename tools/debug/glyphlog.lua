-- Log every DrawGlyph call (0x080C208C): frame, caller (lr), target, code, x, y. --var FROM=/TO= limit frames.
-- Shows where DrawStringVWF actually puts each glyph (drawlog.lua shows only the DrawString arguments).
local from, to = FROM or 0, TO or math.huge
L.on_exec(0x080C208C, 0x080C208C, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  L.log(string.format("f%d lr=%08X tgt=%08X code=%04X x=%d y=%d", L.frame, s["cpu.r14"], s["cpu.r0"], s["cpu.r1"],
    s["cpu.r2"], s["cpu.r3"]))
end)
