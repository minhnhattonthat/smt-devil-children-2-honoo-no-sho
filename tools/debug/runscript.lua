-- Run a hand-made event script: at the first event-interpreter step (0x08038B5A) after frame AFTER, point the script
-- pointer (0x03002F0C) at bytes SCRIPT (e.g. "3C 03 03" = staff roll) written to EWRAM 0x0203FF00.
-- Event opcodes: table 0x08224088 (opcode 3 = end). Opcode 0x3C sub 3 = ending staff roll (0x0804BAA8).
local done = false
L.on_exec(0x08038B5A, 0x08038B5A, function()
  if done or L.frame < (AFTER or 0) then return end
  done = true
  local a = 0x0203FF00
  for hx in SCRIPT:gmatch("%x%x") do emu.write(a, tonumber(hx, 16), emu.memType.gbaMemory); a = a + 1 end
  emu.write32(0x03002F0C, 0x0203FF00, emu.memType.gbaMemory)
  L.log("script run at f" .. L.frame)
end)
