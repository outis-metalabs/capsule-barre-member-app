"""Feed reacts within ~250ms (tap path skips loop-end wait): squish + fish now, cat area fades ~120ms to the shared first-frame poster,
clip starts at 0 and fades in ~160ms; never two clips visible together. Passive mood changes keep loop-end timing.
Usage: feed_instant.py [base_url] [shots_dir]"""
import sys, os, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/feed-instant'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;CH.cici.gate=false;ME.streak=12;ME.paused=false;P2S.cat.demoHour=18;P2S.cat.treats=1;closeSheet();render()}"
TRACE = "()=>{window.__s=[];const f=()=>{const p=document.querySelector('#cici-real img.catpost');window.__s.push([performance.now(),p&&!p.hidden?1:0,...[...document.querySelectorAll('.catvid')].map(v=>[v.dataset.clip,+getComputedStyle(v).opacity,v.currentTime])]);if(window.__s.length<240)requestAnimationFrame(f)};requestAnimationFrame(f)}"
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    for run in range(4):  # runs 0-2: timing at different points in the hungry loop; run 3: screenshots only (capture stalls rAF)
      c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e)))
      q = '?phase2=1'; g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(500); J = g.evaluate
      J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); g.wait_for_timeout(1800 + (run % 3) * 1100); t = f'{L}-390-r{run}'
      ok(f'[{t}] hungry room clip playing before the tap', J("(document.querySelector('.catvid.on')||{}).dataset.clip===(CAT_ROOM.hungry?'room-hungry':'petting')"))
      J(TRACE); t0 = J("performance.now()"); J("()=>{window.__tap=performance.now();document.querySelector('#cat-feed').click()}")
      ok(f'[{t}] squish + fish arc start at once', J("!!document.querySelector('.catfab.squish')") and J("!!document.querySelector('.catfish,.fisharc,[class*=fish]')"))
      if run == 3:
        for i in range(14): g.screenshot(path=f'/tmp/feedi-{L}-{i:02d}.png', clip={'x': 0, 'y': 150, 'width': 390, 'height': 560}); g.wait_for_timeout(30)
      g.wait_for_timeout(1200); S = J("window.__s"); tap = J("window.__tap")
      if run == 3: c.close(); continue
      react = next((s[0] - tap for s in S if s[0] >= tap and any(v[1] < 0.95 and v[0] != 'petting' for v in s[2:] if v[1] > 0) or (s[0] >= tap and any(v[0] == 'petting' and v[1] > 0.05 for v in s[2:]))), None)
      shown = next((s[0] - tap for s in S if s[0] >= tap and any(v[0] == 'petting' and v[1] > 0.9 for v in s[2:])), None)
      print(f"  [{t}] reaction {react and round(react)}ms, petting full {shown and round(shown)}ms"); ok(f"[{t}] Mochi reacts < 300ms after tap", react is not None and react < 300, react)
      ok(f'[{t}] petting fully in < 450ms', shown is not None and shown < 450, shown)
      two = [s for s in S if sum(1 for v in s[2:] if v[1] > 0.15) > 1]
      ok(f'[{t}] never two clips visible together', not two, two[:2])
      ok(f'[{t}] petting starts at its first frame', all(v[2] < 0.35 for s in S for v in s[2:] if v[0] == 'petting' and 0.05 < v[1] < 0.9))
      out = [s for s in S if s[1] and any(v[0] != 'petting' and 0.15 < v[1] < 0.85 for v in s[2:])]
      ok(f'[{t}] outgoing fade over the poster ≤ 130ms', (out[-1][0] - out[0][0] if out else 0) <= 130, len(out))
      if run == 0: json.dump(S, open(f'{SH}/opacity-trace-{L}.json', 'w'))
      ok(f'[{t}] no page errors', not E, E[:2]); c.close()
  # passive change still waits for the loop end (no tap)
  c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); g.goto(U + '?phase2=1'); g.wait_for_timeout(500); J = g.evaluate
  J("()=>{setLang('en');ST.tab='home';ST.page=null;render()}"); J(FRESH); g.wait_for_timeout(1500)
  J(TRACE); J("()=>{window.__t=performance.now();ST.catEat=false;P2S.cat.demoHour=9;catSyncMood()}"); g.wait_for_timeout(3500); S = J("window.__s")
  ok('passive mood change: no poster dip (loop-end timing kept)', not any(s[1] for s in S))
  c.close()
  # reduced motion
  c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.goto(U + '?phase2=1'); g.wait_for_timeout(500); J = g.evaluate
  J("()=>{setLang('en');ST.tab='home';ST.page=null;render()}"); J(FRESH); g.wait_for_timeout(600); J("()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(500)
  ok('reduced motion: feed still works (treat used, not hungry), no poster dip, no errors', J("catDay().treats===0&&!catHungry()&&!document.querySelector('#cici-real img.catpost:not([hidden])')") and not E, E[:2])
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
