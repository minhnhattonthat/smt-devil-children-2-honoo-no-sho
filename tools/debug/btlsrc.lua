-- Battle box scroller (bl DrawString at 0x080B1D40): log the line source pointer [r7+0x4C] and 64 bytes of it,
-- once per distinct pointer+content. The scroller copies at most 18 units of it into a stack buffer.
local seen = {}
L.on_exec(0x080B1D40, 0x080B1D40, function()
  local r7 = emu.getState()["cpu.r7"]
  local p = emu.read32(r7 + 0x4C, emu.memType.gbaMemory)
  local t = {}
  for i = 0, 63 do t[#t + 1] = string.format("%02X", emu.read(p + i, emu.memType.gbaMemory)) end
  local s = table.concat(t, " ")
  if seen[p] == s then return end
  seen[p] = s
  L.log(string.format("f%d src=%08X %s", L.frame, p, s))
end)
