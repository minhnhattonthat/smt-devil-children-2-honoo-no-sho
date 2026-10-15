-- Log every event opcode the interpreter executes (0x08038B72 reads the opcode at [0x03002F0C]) with 10 bytes.
L.on_exec(0x08038B72, 0x08038B72, function()
  local p = emu.read32(0x03002F0C, emu.memType.gbaMemory)
  local t = {}
  for i = 0, 9 do t[#t + 1] = string.format("%02X", emu.read(p + i, emu.memType.gbaMemory)) end
  L.log(string.format("f%d %08X %s", L.frame, p, table.concat(t, " ")))
end)
