-- Save a state at the first show_message (0x08033C48) call after frame AFTER (default 3000). Var OUTSTATE = path.
local done = false
L.on_exec(0x08033C48, 0x08033C48, function()
  if done or L.frame < (AFTER or 3000) then return end
  done = true
  L.save_state(OUTSTATE, function() L.log("saved at f" .. L.frame); L.finish(0) end)
end)
