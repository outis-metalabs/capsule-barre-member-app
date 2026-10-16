"""(helpers from v3_youngcat) v3 young-cat look (CAT_LOOK_READY.cat): at Bud/Blossom every mood plays a -cat clip, kitten clips never appear in the session,
switches never blend two clips (face crops saved), 2D collar is suppressed because the -cat clips have it baked in. Usage: v3_youngcat.py [base_url] [shots_dir]"""
import sys, os, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/v3-bowls-bed'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:400]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={seenLook:0};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;ST.catMis=null;ST.catGrew=false;CH.cici.gate=false;ME.streak=3;ME.paused=false;closeSheet();render()}"
TRACE = "()=>{window.__s=[];window.__src=new Set();const f=()=>{const vs=[...document.querySelectorAll('.catvid')];vs.forEach(v=>{if(v.currentSrc&&+getComputedStyle(v).opacity>0.01)window.__src.add(v.currentSrc.split('/').pop())});window.__s.push([performance.now(),Date.now(),...vs.map(v=>{const cs=getComputedStyle(v);return [v.dataset.clip,+cs.opacity,+cs.zIndex||0,v.currentTime]})]);requestAnimationFrame(f)};f()}"
TOP = "(()=>{const v=[...document.querySelectorAll('.catvid')].filter(v=>+getComputedStyle(v).opacity>0.5).sort((a,b)=>(+getComputedStyle(b).zIndex||0)-(+getComputedStyle(a).zIndex||0))[0];return v?[v.dataset.clip,v.currentSrc.split('/').pop()]:null})()"
COLOFF = "(()=>{const c=document.querySelector('#cat-layer .catcollar');return !c||!c.classList.contains('on')})()"
def check(S, t):
  top = lambda s: max((v for v in s[2:] if v[1] > 0.01), key=lambda v: v[2], default=None)
  blend = [s for s in S if sum(1 for v in s[2:] if v[1] > 0.01) > 1 and top(s)[1] < 0.99 and len({v[0] for v in s[2:] if v[1] > 0.01}) > 1]
  ok(f'[{t}] never two different clips blended (no doubled face)', not blend, [[round(s[0]), s[2:]] for s in blend[:3]])
  return [(S[i][1], top(S[i - 1])[0], top(S[i])[0]) for i in range(1, len(S)) if top(S[i]) and top(S[i - 1]) and top(S[i])[0] != top(S[i - 1])[0]]
def crops(frames, sw, d):
  os.makedirs(d, exist_ok=True); [os.remove(os.path.join(d, x)) for x in os.listdir(d)]; n = 0
  for ts, dat in frames:
    if any(-0.25 <= ts - w / 1000 <= 0.45 for w, a, b2 in sw):
      Image.open(io.BytesIO(base64.b64decode(dat))).convert('RGB').crop((95, 200, 295, 420)).resize((400, 440)).save(f'{d}/{n:03d}.png'); n += 1
  return n
TO = lambda J, n: J(f"()=>{{let i=0;while(gState().stage<{n}&&i++<200)ME.ledger.push({{id:'TS'+i+'_'+Math.random(),delta:0,life:100,reason:'t',t:PV.now()}});render()}}")
BED = "[...document.querySelectorAll('#cat-layer .catbed.on')].length"
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; NF = []
    g.on('pageerror', lambda e: E.append(str(e))); g.on('response', lambda r: (r.status >= 400 and NF.append((r.status, r.url)))); J = g.evaluate
    g.goto(U); J('localStorage.clear()'); g.goto(U); g.wait_for_timeout(900)
    J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); J("()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(1500); t = f'{L}-390'
    ok(f'[{t}] kitten stage', J("catLook()==='kitten'"))
    frames = []; cdp = c.new_cdp_session(g)
    cdp.on('Page.screencastFrame', lambda e: (frames.append((e['metadata']['timestamp'], e['data'])), cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})))
    cdp.send('Page.startScreencast', {'format': 'png', 'everyNthFrame': 1}); J(TRACE)
    J("()=>{P2S.cat.demoHour=19;render()}"); g.wait_for_timeout(3500); top = J(TOP); ln = J("document.querySelector('#cat-line').innerText")
    ok(f'[{t}] kitten hungry -> room-hungrybowl clip {top}', top and top[0] == 'hungry-room' and 'hungrybowl_tall.' in top[1], top); g.screenshot(path=f'{SH}/hungrybowl-kitten-{L}-390.png')
    J("()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(2500)
    J("()=>catMisPlay('water')"); g.wait_for_timeout(3000); top = J(TOP); ln = J("document.querySelector('#cat-line').innerText")
    ok(f'[{t}] kitten water -> room-waterbowl, caption holds (no sip): {ln!r}', top and top[0] == 'room-waterbowl' and ({'en': 'holds her water', 'ko': '물컵을 들고'}[L] in ln) and 'sip' not in ln.lower() and '모금' not in ln, [top, ln])
    g.screenshot(path=f'{SH}/waterbowl-kitten-{L}-390.png'); J("()=>catMisEnd()"); g.wait_for_timeout(2500)
    S = J("window.__s"); sw = check(S, t + ' kitten bowls'); print(f'  [{t}] kitten switches: {[x[1:] for x in sw]}; crops {crops(frames, sw, f"{SH}/frames-kitten-{L}")}')
    # Blossom: bed earned, young-cat look -> napping-bed aliased to napping-cat, ONE 2D bed
    J("()=>{window.__s=[]}"); frames.clear(); TO(J, 3); g.wait_for_timeout(2500); J("()=>{ME.streak=0;catSyncMood();catRefreshUi()}"); g.wait_for_timeout(3500); top = J(TOP)
    ok(f'[{t}] Blossom: bed owned, napping on napping-cat with exactly one (2D) bed {top}', J("catStage()===3&&catItemOwned('m_bed')") and top and top[1].startswith('cici-cat-napping-cat.') and J(BED) == 1, [top, J(BED)])
    g.screenshot(path=f'{SH}/napping-blossom-{L}-390.png')
    # Shine: napping-bed clip (bed baked in) -> 2D bed hidden
    J("()=>{ME.streak=3;catSyncMood();catRefreshUi()}"); g.wait_for_timeout(2500); TO(J, 4); g.wait_for_timeout(2500)
    J("()=>{ME.streak=0;catSyncMood();catRefreshUi()}"); g.wait_for_timeout(4000); top = J(TOP)
    ok(f'[{t}] Shine napping -> napping-bed clip, 2D bed hidden (no double bed), no 2D collar {top}', top and top[0] == 'napping-bed' and J(BED) == 0 and J(COLOFF), [top, J(BED)])
    ok(f'[{t}] napping-bed caption mentions her bed', 'bed' in J("document.querySelector('#cat-line').innerText") or '침대' in J("document.querySelector('#cat-line').innerText"))
    g.screenshot(path=f'{SH}/napping-bed-shine-{L}-390.png')
    S = J("window.__s"); sw = check(S, t + ' bed'); print(f'  [{t}] bed switches: {[x[1:] for x in sw]}; crops {crops(frames, sw, f"{SH}/frames-bed-{L}")}')
    cdp.send('Page.stopScreencast'); ok(f'[{t}] no 404s / page errors', not NF and not E, (NF[:3], E[:2])); c.close()
  c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); g = c.new_page(); J = g.evaluate
  g.goto(U); J('localStorage.clear()'); g.goto(U); g.wait_for_timeout(900); J(FRESH); TO(J, 4); J("()=>{ME.streak=0;render()}"); g.wait_for_timeout(1200)
  ok('[reduced motion] Shine napping: no video, one bed at most', not J("!!document.querySelector('#cici-real video:not([hidden])')&&[...document.querySelectorAll('#cici-real video')].some(v=>!v.paused)") and J(BED) <= 1, J(BED))
  g.screenshot(path=f'{SH}/napping-bed-reduced-390.png'); c.close(); b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
