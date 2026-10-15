-- Log every DrawString call (0x080C20E8): frame, caller (lr), target, string pointer, x, y, first 24 bytes.
-- --var FROM=/TO= limit frames. Used to find which string a screen draws and with which bitmap.
local from, to = FROM or 0, TO or math.huge
L.on_exec(0x080C20E8, 0x080C20E8, function()
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local p = s["cpu.r1"]
  local t = {}
  for i = 0, 23 do t[#t + 1] = string.format("%02X", emu.read(p + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d lr=%08X tgt=%08X str=%08X x=%d y=%d %s", L.frame, s["cpu.r14"], s["cpu.r0"], p, s["cpu.r2"],
    s["cpu.r3"], table.concat(t, " ")))
end)
