"""Feed reacts within ~250ms with a soft blur dip (PR36 r2): ~100ms blur 0→14px on the video layer, instant swap to the clip at 0 at peak blur,
~160ms blur back. Only one video visible at any frame — never an opacity blend of two sharp clips. Passive mood changes keep loop-end timing.
Also captures every painted frame 0–400ms after the tap (CDP screencast). Usage: feed_instant.py [base_url] [shots_dir]"""
import sys, os, json, base64
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/feed-instant'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;CH.cici.gate=false;ME.streak=12;ME.paused=false;P2S.cat.demoHour=18;P2S.cat.treats=1;closeSheet();render()}"
TRACE = "()=>{window.__s=[];const f=()=>{window.__s.push([performance.now(),...[...document.querySelectorAll('.catvid')].map(v=>{const cs=getComputedStyle(v);const m=/blur\\(([\\d.]+)px/.exec(cs.filter);return [v.dataset.clip,+cs.opacity,v.currentTime,m?+m[1]:0,+cs.zIndex||0]})]);if(window.__s.length<200)requestAnimationFrame(f)};requestAnimationFrame(f)}"
def analyse(S, tap, t):
  S = [s for s in S if s[0] >= tap - 1]
  # a lower video fully covered by an opaque one above it is not visible; a blend = two showing with the top one not opaque
  top = lambda s: max((v for v in s[1:] if v[1] > 0.01), key=lambda v: v[4], default=None)
  two = [s for s in S if sum(1 for v in s[1:] if v[1] > 0.01) > 1 and top(s)[1] < 0.99]
  ok(f'[{t}] only one video visible on every frame (no opacity blend)', not two, two[:2])
  vis = top
  react = next((s[0] - tap for s in S if vis(s) and vis(s)[3] > 0.5), None)
  sw = next((i for i, s in enumerate(S) if vis(s) and vis(s)[0] == 'petting'), None)
  ok(f'[{t}] Mochi reacts (blur starts) < 300ms', react is not None and react < 300, react)
  bas = max(vis(S[sw - 1])[3], vis(S[sw])[3]) if sw else 0
  ok(f'[{t}] swap at peak blur (≥10px), petting from its first frame', sw is not None and bas >= 10 and vis(S[sw])[2] < 0.25, [sw, bas, sw and vis(S[sw])])
  sharp = next((s[0] - tap for s in S[sw:] if vis(s) and vis(s)[0] == 'petting' and vis(s)[3] < 0.3), None) if sw else None
  ok(f'[{t}] petting sharp again < 450ms', sharp is not None and sharp < 450, sharp)
  print(f'  [{t}] reaction {react and round(react)}ms, swap at {sw and round(S[sw][0]-tap)}ms (blur {bas:.1f}px), sharp at {sharp and round(sharp)}ms')
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    for run in range(6):  # runs 0-4: tap at 5 points of the 4.04s hungry loop; run 5: every-frame capture
      c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e)))
      q = '?phase2=1'; g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(500); J = g.evaluate
      J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); g.wait_for_timeout(1500 + (run % 5) * 790); t = f'{L}-390-r{run}'
      ok(f'[{t}] hungry room clip playing before the tap', J("(document.querySelector('.catvid.on')||{}).dataset.clip===(CAT_ROOM.hungry?'room-hungry':'petting')"))
      ht = J("(document.querySelector('.catvid.on')||{}).currentTime")
      frames = []
      if run == 5:
        cdp = c.new_cdp_session(g)
        cdp.on('Page.screencastFrame', lambda e: (frames.append((e['metadata']['timestamp'], e['data'])), cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})))
        cdp.send('Page.startScreencast', {'format': 'png', 'everyNthFrame': 1}); g.wait_for_timeout(400)
      J(TRACE); J("()=>{window.__tap=performance.now();window.__tapW=Date.now();document.querySelector('#cat-feed').click()}")
      ok(f'[{t}] squish + fish arc start at once', J("!!document.querySelector('.catfab.squish')") and J("!!document.querySelector('.catfish')"))
      g.wait_for_timeout(1200); S = J("window.__s"); tap = J("window.__tap"); print(f'  [{t}] tapped at hungry t={ht:.2f}s')
      analyse(S, tap, t)
      if run == 0: json.dump(S, open(f'{SH}/opacity-blur-trace-{L}.json', 'w'))
      if run == 5:
        cdp.send('Page.stopScreencast'); tw = J("window.__tapW") / 1000
        d = f'{SH}/frames-{L}'; os.makedirs(d, exist_ok=True); [os.remove(os.path.join(d, x)) for x in os.listdir(d)]
        sel = [(ts, dat) for ts, dat in frames if -0.02 <= ts - tw <= 0.42]
        for i, (ts, dat) in enumerate(sel): open(f'{d}/{i:03d}_{max(0,int((ts - tw) * 1000)):03d}ms.png', 'wb').write(base64.b64decode(dat))
        ok(f'[{t}] captured ≥10 painted frames in 0–400ms', len(sel) >= 10, len(sel)); print(f'  [{t}] {len(sel)} frames captured')
        try:
          from PIL import Image, ImageStat; import io
          sd = [ImageStat.Stat(Image.open(io.BytesIO(base64.b64decode(dat))).convert('L').crop((95, 220, 295, 420))).stddev[0] for _, dat in sel]
          ok(f'[{t}] no empty/cream frame on the face during the dip (contrast ≥30)', min(sd) >= 30, [round(x) for x in sd])
        except ImportError: pass
      ok(f'[{t}] no page errors', not E, E[:2]); c.close()
  c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); g.goto(U + '?phase2=1'); g.wait_for_timeout(500); J = g.evaluate
  J("()=>{setLang('en');ST.tab='home';ST.page=null;render()}"); J(FRESH); g.wait_for_timeout(1500)
  J(TRACE); J("()=>{ST.catEat=false;P2S.cat.demoHour=9;catSyncMood()}"); g.wait_for_timeout(3500); S = J("window.__s")
  ok('passive mood change: no blur dip (loop-end timing kept)', not any(v[3] > 0.5 for s in S for v in s[1:]))
  c.close()
  c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.goto(U + '?phase2=1'); g.wait_for_timeout(500); J = g.evaluate
  J("()=>{setLang('en');ST.tab='home';ST.page=null;render()}"); J(FRESH); g.wait_for_timeout(600); J("()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(500)
  ok('reduced motion: feed works, no blur dip, no errors', J("catDay().treats===0&&!catHungry()&&!document.querySelector('#cici-real.blurdip,#cici-real.blurout')") and not E, E[:2])
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
