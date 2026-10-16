"""v3 young-cat look (CAT_LOOK_READY.cat): at Bud/Blossom every mood plays a -cat clip, kitten clips never appear in the session,
switches never blend two clips (face crops saved), 2D collar is suppressed because the -cat clips have it baked in. Usage: v3_youngcat.py [base_url] [shots_dir]"""
import sys, os, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/v3-youngcat'; os.makedirs(SH, exist_ok=True)
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
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko', 'vi'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; NF = []; REQ = []
    g.on('pageerror', lambda e: E.append(str(e))); g.on('response', lambda r: (r.status >= 400 and NF.append((r.status, r.url))))
    g.on('request', lambda r: 'cici-real/' in r.url and REQ.append(r.url.split('/')[-1])); J = g.evaluate
    g.goto(U); J('localStorage.clear()'); g.goto(U); g.wait_for_timeout(900)
    J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); J("()=>{P2S.cat.demoHour=12;render()}")
    J("()=>{ME.ledger.push({id:'T9',delta:0,life:2500,reason:'t',t:PV.now()});render()}"); g.wait_for_timeout(2500); t = f'{L}-390'
    REQ.clear(); J(TRACE)
    ok(f'[{t}] Bud/Blossom -> catLook cat', J("catLook()==='cat'"), J("[catStage(),catLook()]"))
    frames = []; cdp = c.new_cdp_session(g)
    cdp.on('Page.screencastFrame', lambda e: (frames.append((e['metadata']['timestamp'], e['data'])), cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})))
    cdp.send('Page.startScreencast', {'format': 'png', 'everyNthFrame': 1})
    seen = {}
    steps = [('lively', "()=>{ME.streak=3;catSyncMood();catRefreshUi()}", 5000),
             ('play (streak 7)', "()=>{ME.streak=7;catSyncMood();catRefreshUi()}", 5500),
             ('napping', "()=>{ME.streak=0;catSyncMood();catRefreshUi()}", 6500),
             ('hungry', "()=>{ME.streak=3;P2S.cat.demoHour=19;render()}", 4500),
             ('feed (eat->pet->play)', "()=>{P2S.cat.demoHour=12;P2S.cat.treats=1;P2S.cat.earned=1;render();setTimeout(()=>document.querySelector('#cat-feed').click(),600)}", 9000),
             ('mission water', "()=>{catMisPlay('water')}", 4000)]
    for nm, js, ms in steps:
      J(js); g.wait_for_timeout(ms); top = J(TOP); seen[nm] = top
      g.screenshot(path=f'{SH}/yc-{nm.split()[0]}-{L}-390.png')
      ok(f'[{t}] {nm}: -cat clip on top {top}', top and top[1].rsplit('.', 1)[0].endswith('-cat'), [top, J("catMood()")])
      ln = J("document.querySelector('#cat-line').innerText")
      if nm.startswith('mission'): ok(f'[{t}] water mission on petting-cat reads the cuddle line, not the bowl line: {ln!r}', ('Cici' in ln and ({'en':'lap','ko':'무릎','vi':'lòng'}[L] in ln)) and not any(w in ln for w in ('bowl','그릇','bát')), ln)
      if nm.startswith('play'): ok(f'[{t}] play at streak 7 on lively-cat shows lively text, not "playing": {ln!r}', 'playing' not in ln and '놀아요' not in ln and J("ST.catEat===false&&catMood()==='play'"), ln)
      ok(f'[{t}] {nm}: 2D collar not doubled on baked-in collar', J(COLOFF))
    S = J("window.__s"); sw = check(S, t); print(f'  [{t}] switches: {[x[1:] for x in sw]}')
    print(f'  [{t}] face-crop frames: {crops(frames, sw, f"{SH}/frames-{L}")}')
    cdp.send('Page.stopScreencast')
    src = sorted(J("[...window.__src]")); print(f'  [{t}] painted sources: {src}')
    ok(f'[{t}] no kitten clip painted in the session', src and all(s.rsplit('.', 1)[0].endswith('-cat') for s in src), src)
    vids = [r for r in REQ if r.endswith(('.mp4', '.webm'))]
    ok(f'[{t}] no kitten video requested after reaching Bud', all(r.rsplit('.', 1)[0].endswith('-cat') for r in vids), vids)
    ok(f'[{t}] no 404s', not NF, NF[:3]); ok(f'[{t}] no page errors', not E, E[:2])
    print(f'  [{t}] line: {J("document.querySelector(\'#cat-line\').innerText")!r}'); c.close()
  c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); g = c.new_page(); J = g.evaluate
  g.goto(U); J('localStorage.clear()'); g.goto(U); g.wait_for_timeout(900); J(FRESH)
  J("()=>{ME.ledger.push({id:'T9',delta:0,life:2500,reason:'t',t:PV.now()});render()}"); g.wait_for_timeout(1500)
  ok('[reduced motion] still -cat poster/look, no playing video', J("catLook()==='cat'") and J("[...document.querySelectorAll('.catvid')].every(v=>v.paused)"), J("[...document.querySelectorAll('.catvid')].map(v=>[v.paused,v.poster.split('/').pop()])"))
  g.screenshot(path=f'{SH}/yc-reduced-motion-390.png'); c.close(); b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
