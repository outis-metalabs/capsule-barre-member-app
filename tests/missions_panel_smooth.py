"""Missions glass panel on Home (device report 2026-10-16 flicker.webm): slide up ~280ms / down ~220ms, real frosted glass (room visible),
no black frames, the room video never resized/restarted/re-laid-out, card + nav stay put, page never scrolls, done rows crisp.
Captures every painted frame (CDP screencast) of open, hold and close. Usage: missions_panel_smooth.py [base_url] [shots_dir]"""
import sys, os, base64, io
from playwright.sync_api import sync_playwright
from PIL import Image, ImageStat
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/missions-panel-smooth'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
LOG = """()=>{window.__r=0;const o=window.render;window.render=function(){window.__r++;return o.apply(this,arguments)};const v0=document.querySelector('.catvid.on');window.__v0=v0;window.__src=v0.currentSrc;window.__log=[];
const f=()=>{const v=document.querySelector('.catvid.on'),r=v&&v.getBoundingClientRect(),n=document.querySelector('nav.tabs'),cd=document.querySelector('#hb-bubble'),sh=document.querySelector('.sheet')||((document.querySelector('.sheetghost-host')||{}).shadowRoot||{querySelector:()=>null}).querySelector('.sheetghost');
const ty=sh?new DOMMatrix(getComputedStyle(sh).transform==='none'?undefined:getComputedStyle(sh).transform).m42:null;
window.__log.push([performance.now(),v===window.__v0,v&&v.currentSrc===window.__src,v&&v.currentTime,r&&[r.x,r.y,r.width,r.height],getComputedStyle(v).objectFit,n&&getComputedStyle(n).visibility==='visible'&&+getComputedStyle(n).opacity,cd&&getComputedStyle(cd).visibility==='visible'&&+getComputedStyle(cd).opacity,ty,sh&&sh.className,document.scrollingElement.scrollTop,window.scrollY]);requestAnimationFrame(f)};requestAnimationFrame(f)}"""
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); J = g.evaluate
    g.goto(U + '?phase2=1'); J('localStorage.clear()'); g.goto(U + '?phase2=1'); g.wait_for_timeout(900)
    J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={{}};P2S.cat.demoHour=10;ME.streak=12;render();dmMark('water');dmMark('stretch');render()}}"); g.wait_for_timeout(1500); t = f'{L}-390'
    J(LOG); frames = []; cdp = c.new_cdp_session(g)
    cdp.on('Page.screencastFrame', lambda e: (frames.append((e['metadata']['timestamp'], e['data'])), cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})))
    cdp.send('Page.startScreencast', {'format': 'png', 'everyNthFrame': 1}); g.wait_for_timeout(300)
    to = J("(()=>{window.__o=performance.now();window.__ow=Date.now();document.querySelector('#v2-pull').click();return window.__o})()"); g.wait_for_timeout(1200)
    ok(f'[{t}] panel is frosted glass: translucent bg, backdrop blur, room visible above it', J("(()=>{const s=document.querySelector('.sheet');const c=getComputedStyle(s);const a=+(c.backgroundColor.match(/[\\d.]+(?=\\))/)||[1])[0];return a<=0.6&&c.backdropFilter.includes('blur')&&s.getBoundingClientRect().top>=0.25*innerHeight&&getComputedStyle(s.parentElement).backgroundColor==='rgba(0, 0, 0, 0)'})()"))
    ok(f'[{t}] done rows crisp: no transform/filter on any ancestor, title not grey-on-pink', J("(()=>{const m=document.querySelector('.sheet .mis.done .mt');if(!m)return false;let e=m;while(e&&e!==document.body){const c=getComputedStyle(e);if((c.transform!=='none'&&!/matrix\\(1, 0, 0, 1, 0, 0\\)/.test(c.transform))||c.filter!=='none')return [e.className,c.transform,c.filter];e=e.parentElement}return /255, 255, 255/.test(getComputedStyle(m).color)})()") is True, J("(()=>{const m=document.querySelector('.sheet .mis.done .mt');let e=m,o=[];while(e&&e!==document.body){const c=getComputedStyle(e);o.push([e.className,c.transform,c.filter]);e=e.parentElement}return [getComputedStyle(m).color,o]})()"))
    g.screenshot(path=f'{SH}/open-hold-{t}.png')
    tc = J("(()=>{window.__c=performance.now();window.__cw=Date.now();return window.__c})()"); g.mouse.click(195, 40); g.wait_for_timeout(1000)
    cdp.send('Page.stopScreencast'); Lg = J("window.__log"); ow, cw = J("window.__ow") / 1000, J("window.__cw") / 1000
    ok(f'[{t}] no re-render of Home while opening/closing', J("window.__r") == 0, J("window.__r"))
    ok(f'[{t}] same video element + source the whole time (never restarted)', all(l[1] and l[2] for l in Lg))
    ct = [l[3] for l in Lg]; back = [(a, b2) for a, b2 in zip(ct, ct[1:]) if b2 < a - 0.05 and not (a > 3.5 and b2 < 0.6)]
    ok(f'[{t}] video time only moves forward (loop wrap allowed)', not back, back[:3])
    rects = {tuple(round(x, 1) for x in l[4]) for l in Lg}; ok(f'[{t}] video box never changes (no scale/position jump)', len(rects) == 1, list(rects)[:4])
    ok(f'[{t}] object-fit fixed', {l[5] for l in Lg} == {'cover'}, {l[5] for l in Lg})
    ok(f'[{t}] nav + top card visible on every frame', all(l[6] == 1 and l[7] == 1 for l in Lg), [l for l in Lg if not (l[6] == 1 and l[7] == 1)][:2])
    ok(f'[{t}] page never scrolls', all(l[10] == 0 and l[11] == 0 for l in Lg))
    op = [(l[0] - to, l[8]) for l in Lg if to <= l[0] <= to + 450 and l[8] is not None]
    mid = [y for dt, y in op if 80 <= dt <= 200]; end = [y for dt, y in op if dt >= 330]
    ok(f'[{t}] slides up (~280ms ease, moving mid-way, settled by ~330ms)', mid and max(mid) > 20 and end and abs(end[0]) < 1, [(round(a), round(y)) for a, y in op[:24]])
    cl = [(l[0] - tc, l[8], l[9]) for l in Lg if tc <= l[0] <= tc + 450]
    cm = [y for dt, y, k in cl if 60 <= dt <= 180 and k and 'sheetghost' in k]; gone = [k for dt, y, k in cl if dt >= 300]
    ok(f'[{t}] slides down (~220ms) and is gone after', cm and max(cm) > 20 and all(k is None for k in gone), [(round(a), y and round(y), k) for a, y, k in cl[:20]])
    d = f'{SH}/frames-{L}'; os.makedirs(d, exist_ok=True); [os.remove(os.path.join(d, x)) for x in os.listdir(d)]
    dark = []
    for i, (ts, dat) in enumerate(frames):
      im = Image.open(io.BytesIO(base64.b64decode(dat))).convert('RGB'); ph = 'open' if ts < cw else 'close'
      rel = int(((ts - ow) if ts < cw else (ts - cw)) * 1000); im.save(f'{d}/{i:03d}_{ph}_{rel:+05d}ms.png')
      gy = im.convert('L'); w, h = gy.size
      rows = [ImageStat.Stat(gy.crop((0, y, w, y + 4))).mean[0] for y in range(0, h - 4, 4)]
      if min(rows) < 60: dark.append((i, ph, rel, round(min(rows))))
    ok(f'[{t}] no black/dark strip in any captured frame ({len(frames)} frames)', not dark and len(frames) >= 30, dark[:5])
    ok(f'[{t}] no page errors', not E, E[:2]); c.close()
  c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); g = c.new_page(); J = g.evaluate; g.goto(U + '?phase2=1'); g.wait_for_timeout(800)
  J("()=>{setLang('en');ST.tab='home';ST.page=null;render()}"); J("()=>document.querySelector('#v2-pull').click()"); g.wait_for_timeout(60)
  ok('reduced motion: panel appears without sliding, closes without a ghost', J("getComputedStyle(document.querySelector('.sheet')).animationName==='none'") and (J("closeSheet()") or True) and not J("!!document.querySelector('.sheetghost-host')"))
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
