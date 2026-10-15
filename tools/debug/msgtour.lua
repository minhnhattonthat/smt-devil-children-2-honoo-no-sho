-- Message tour: show any main-table message in the real dialogue box, one after another, from one savestate.
-- Globals (emu.py --var): IDS = "{12,13,...}" (main-table indexes), STATE = savestate taken at a show_message call
-- (0x08033C48, r0 = message index; tools/debug/mkstate_show.lua). After each load the code is exactly at that call,
-- so r0 is replaced with the next id. At every [wait] (handler 0x08032C5A) the script waits DELAY frames (text fully
-- drawn), shoots m<id>_<n>.png and presses A. At [end] (0x080338E0) it shoots and loads the state for the next id.
-- Run without --mash.
local ids = load("return " .. IDS)()
local DELAY = DELAY or 12
local k, cur, page, busy, due, endpending = 0, nil, 0, true, nil, false
local WAIT, ENDMSG = 0x08032C5A, 0x080338E0

local function nextmsg()
  k = k + 1
  if k > #ids then L.finish(0) return end
  cur, page, due, endpending = ids[k], 0, nil, false
  local s = emu.getState()
  s["cpu.r0"] = cur
  emu.setState(s)
  L.log(string.format("f%d show %d", L.frame, cur))
  busy = false
end

L.on_exec(WAIT, WAIT, function()
  if not busy and cur and not due then due = L.frame + DELAY end
end)

L.on_exec(ENDMSG, ENDMSG, function()
  if busy or not cur then return end
  busy, endpending, due = true, true, L.frame + 2
end)

L.on_frame(function(f)
  if due and f >= due then
    due = nil
    L.shot(string.format("m%04d_%02d%s.png", cur, page, endpending and "e" or ""))
    page = page + 1
    if endpending then
      L.load_state(STATE, nextmsg)
    else
      L.press("a", 6)
    end
  elseif cur and not busy and not due and f % 600 == 0 then
    L.press("a", 6)              -- unstick: a prompt or choice waiting for input
  end
end)

L.load_state(STATE, nextmsg)
