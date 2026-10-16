"""Optional eat slot (assets/cici-real/cici-room-eat_tall.*): missing -> feed keeps petting step; present -> fish arc, eat clip (once, via tap blur dip), then happy.
Uses the real 3D Designer eat clip; the 'missing' case is simulated by forcing the slot off. Usage: feed_eat.py [base_url]"""
import sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;CH.cici.gate=false;ME.streak=12;ME.paused=false;P2S.cat.demoHour=18;P2S.cat.treats=1;closeSheet();render()}"
TOP = "(()=>{const v=[...document.querySelectorAll('.catvid')].filter(v=>+getComputedStyle(v).opacity>0.01).sort((a,b)=>(+getComputedStyle(b).zIndex||0)-(+getComputedStyle(a).zIndex||0))[0];return v?v.dataset.clip:null})()"
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    for present in (False, True):
      c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e)))
      g.goto(U + '?phase2=1'); g.evaluate('localStorage.clear()'); g.goto(U + '?phase2=1'); g.wait_for_timeout(800); J = g.evaluate; t = f'{L}-{"eat" if present else "no-eat"}'
      J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); g.wait_for_timeout(1200)
      ok(f'[{t}] slot listed and probed via the existing check', J("'eat' in CAT_ROOM && CAT_CLIPS['room-eat']==='assets/cici-real/cici-room-eat_tall'"))
      if present: ok(f'[{t}] real eat file present -> slot on (HEAD probe)', J("CAT_ROOM.eat"))
      else: J("()=>{CAT_ROOM.eat=false}")  # simulate the file missing
      J("()=>{window.__tap=performance.now();document.querySelector('#cat-feed').click()}")
      ok(f'[{t}] fish arc starts at once', J("!!document.querySelector('.catfish')"))
      g.wait_for_timeout(400); first = J(TOP)
      ok(f'[{t}] first step: {"eat clip" if present else "petting"} within 400ms', first == ('room-eat' if present else 'petting'), first)
      if present:
        ok(f'[{t}] eat clip plays once (not looping), from its start', J("(()=>{const v=document.querySelector('.catvid[data-clip=\"room-eat\"]');return !!v&&!v.loop&&v.currentTime<1})()"))
        g.wait_for_timeout(2600); ok(f'[{t}] still eating before the clip ends', J(TOP) == 'room-eat', J(TOP))
        g.wait_for_timeout(1700)
      else: g.wait_for_timeout(2700)
      ok(f'[{t}] then happy', J(TOP) == 'room-happy' and J("ST.catEat==='play'"), [J(TOP), J("ST.catEat")])
      ok(f'[{t}] no page errors', not E, E[:2]); c.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
