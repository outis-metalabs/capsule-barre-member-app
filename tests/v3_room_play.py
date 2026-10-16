"""v3 room-play clip (CAT_OPT["room-play"]): plays on a 7+ day streak and as the last beat of feeding; transitions never blend two clips
(no doubled face). Captures every painted frame around each switch and writes 2x face crops. Usage: v3_room_play.py [base_url] [shots_dir]"""
import sys, os, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/v3-room-play'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={seenLook:0};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;ST.catMis=null;ST.catGrew=false;CH.cici.gate=false;ME.streak=12;ME.paused=false;closeSheet();render()}"
TRACE = "()=>{window.__s=[];const f=()=>{window.__s.push([performance.now(),Date.now(),...[...document.querySelectorAll('.catvid')].map(v=>{const cs=getComputedStyle(v);return [v.dataset.clip,+cs.opacity,+cs.zIndex||0,v.currentTime]})]);requestAnimationFrame(f)};requestAnimationFrame(f)}"
TOP = "(()=>{const v=[...document.querySelectorAll('.catvid')].filter(v=>+getComputedStyle(v).opacity>0.5).sort((a,b)=>(+getComputedStyle(b).zIndex||0)-(+getComputedStyle(a).zIndex||0))[0];return v?v.dataset.clip:null})()"
def check(S, t):
  top = lambda s: max((v for v in s[2:] if v[1] > 0.01), key=lambda v: v[2], default=None)
  blend = [s for s in S if sum(1 for v in s[2:] if v[1] > 0.01) > 1 and top(s)[1] < 0.99 and len({v[0] for v in s[2:] if v[1] > 0.01}) > 1]
  ok(f'[{t}] never two different clips blended (no doubled face)', not blend, [[round(s[0]), s[2:]] for s in blend[:3]])
  sw = [(S[i][1], top(S[i - 1])[0], top(S[i])[0]) for i in range(1, len(S)) if top(S[i]) and top(S[i - 1]) and top(S[i])[0] != top(S[i - 1])[0]]
  return sw
def crops(frames, sw, name, L):
  d = f'{SH}/frames-{name}-{L}'; os.makedirs(d, exist_ok=True); [os.remove(os.path.join(d, x)) for x in os.listdir(d)]
  n = 0
  for ts, dat in frames:
    if any(-0.25 <= ts - w / 1000 <= 0.45 for w, a, b2 in sw):
      Image.open(io.BytesIO(base64.b64decode(dat))).convert('RGB').crop((95, 200, 295, 420)).resize((400, 440)).save(f'{d}/{n:03d}.png'); n += 1
  return n
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); J = g.evaluate
    g.goto(U); J('localStorage.clear()'); g.goto(U); g.wait_for_timeout(900)
    J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); J("()=>{P2S.cat.demoHour=12;ME.streak=3;render()}"); g.wait_for_timeout(1500); t = f'{L}-390'
    ok(f'[{t}] flag on and slot points at the file', J("CAT_OPT['room-play']===true && CAT_CLIPS['room-play']==='assets/cici-real/cici-room-play_tall'"))
    ok(f'[{t}] streak 3: lively (not play)', J(TOP) == 'lively', J(TOP))
    frames = []; cdp = c.new_cdp_session(g)
    cdp.on('Page.screencastFrame', lambda e: (frames.append((e['metadata']['timestamp'], e['data'])), cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})))
    cdp.send('Page.startScreencast', {'format': 'png', 'everyNthFrame': 1}); J(TRACE)
    J("()=>{ME.streak=7;catSyncMood();catRefreshUi()}"); g.wait_for_timeout(5600)
    ok(f'[{t}] streak 7: plays room-play', J("catMood()==='play'") and J(TOP) == 'room-play', [J("catMood()"), J(TOP)])
    S = J("window.__s"); sw = check(S, t + ' streak'); ok(f'[{t}] streak: one switch lively -> room-play', [x[1:] for x in sw] == [('lively', 'room-play')], sw)
    g.screenshot(path=f'{SH}/streak7-play-{L}-390.png'); n = crops(frames, sw, 'streak', L); print(f'  [{t}] streak switch frames: {n}')
    J("()=>{window.__s=[]}"); frames.clear()
    J("()=>{P2S.cat.treats=1;P2S.cat.earned=1;catRefreshUi()}"); J("()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(1500)
    g.screenshot(path=f'{SH}/feed-eat-{L}-390.png'); g.wait_for_timeout(4500)
    ok(f'[{t}] feed ends on room-play (last beat)', J("ST.catEat==='play'") and J(TOP) == 'room-play', [J("ST.catEat"), J(TOP)])
    g.screenshot(path=f'{SH}/feed-last-beat-play-{L}-390.png')
    S = J("window.__s"); sw = check(S, t + ' feed'); print(f'  [{t}] feed switches: {[x[1:] for x in sw]}')
    ok(f'[{t}] feed sequence ends room-eat -> room-play', sw and sw[-1][1:] == ('room-eat', 'room-play'), sw)
    n = crops(frames, sw, 'feed', L); print(f'  [{t}] feed switch frames: {n}')
    cdp.send('Page.stopScreencast')
    ok(f'[{t}] collar shown on Mochi in room-play', J("(()=>{const c=document.querySelector('#cat-layer .catcollar');return !c||c.classList.contains('on')})()"))
    ok(f'[{t}] no page errors', not E, E[:2]); c.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
