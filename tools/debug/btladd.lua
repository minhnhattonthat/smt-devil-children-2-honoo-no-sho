-- Battle message box AddLine (0x080B18B4, r1 = line string): log caller and 48 bytes of each line added.
L.on_exec(0x080B18B4, 0x080B18B4, function()
  local s = emu.getState()
  local p = s["cpu.r1"]
  local t = {}
  for i = 0, 47 do t[#t + 1] = string.format("%02X", emu.read(p + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d lr=%08X line=%08X %s", L.frame, s["cpu.r14"], p, table.concat(t, " ")))
end)
