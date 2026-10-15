-- Warp by event: replace the event id of the first RunEvent (0x08038B30, r0 = event index into table 0x082D2DDC)
-- called after frame AFTER with EVENT. Use from a field savestate (--state-in) or a cold boot route.
local done = false
L.on_exec(0x08038B30, 0x08038B30, function()
  if done or L.frame < (AFTER or 0) then return end
  local s = emu.getState()
  L.log(string.format("f%d RunEvent %d -> %d", L.frame, s["cpu.r0"], EVENT))
  s["cpu.r0"] = EVENT
  emu.setState(s)
  done = true
end)
