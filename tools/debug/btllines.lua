-- Battle message box: log each line buffer the box copies from (0x080B1C00: r0 = line pointer, 18 units max),
-- with 48 bytes of it. Shows how a main-table message was split into battle lines.
local seen = {}
L.on_exec(0x080B1C00, 0x080B1C00, function()
  local p = emu.getState()["cpu.r0"]
  local t = {}
  for i = 0, 47 do t[#t + 1] = string.format("%02X", emu.read(p + i, emu.memType.gbaMemory)) end
  local s = table.concat(t, " ")
  if seen[p] == s then return end
  seen[p] = s
  L.log(string.format("f%d line=%08X %s", L.frame, p, s))
end)
