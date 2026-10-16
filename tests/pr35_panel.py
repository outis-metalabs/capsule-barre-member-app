"""PR #35 panel r1 fixes: glass missions panel (no dim / no X, 44px handle, swipe + tap-outside close), loop-point crossfade (no double face),
stretch chip clear of Mochi + card hidden, toast at top, gentle feed pulse (none under reduced motion), hungry bowl bubble.
Usage: pr35_panel.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/panel-pr35-fix'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;CH.cici.gate=false;ME.streak=12;ME.paused=false;P2S.cat.demoHour=18;P2S.cat.treats=1;closeSheet();render()}"
RECT = "s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom]}"
OVL = lambda a, b: a and b and a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
VIS = "()=>[...document.querySelectorAll('.catvid')].map(v=>[v.dataset.clip,+getComputedStyle(v).opacity,v.currentTime,v.duration])"
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('en', 'ko'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e)))
    q = '?phase2=1'; g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(500); J = g.evaluate
    J(f"()=>{{setLang('{L}');ST.tab='home';ST.page=null;render()}}"); J(FRESH); g.wait_for_timeout(2600); t = f'{L}-390'
    # hungry
    ok(f'[{t}] hungry: empty-bowl bubble near Mochi visible', J("(()=>{const e=document.querySelector('#cici-real .cathbub');return !!e&&+getComputedStyle(e).opacity>0.9})()"))
    ok(f'[{t}] feed button: gentle pulse (not the bounce)', J("getComputedStyle(document.querySelector('#cat-feed')).animationName==='fabpulse'&&parseFloat(getComputedStyle(document.querySelector('#cat-feed')).animationDuration)>=3"))
    g.screenshot(path=f'{SH}/hungry-{t}.png')
    # missions panel
    J("()=>document.querySelector('[data-act=hbmis],#v2-mis,[data-act=hbsheet]').click()"); g.wait_for_timeout(600)
    ok(f'[{t}] missions: glass panel, no dim, no X, 44px handle', J("(()=>{const bg=document.querySelector('.sheet-bg'),sh=document.querySelector('.sheet');if(!bg||!sh)return false;const h=sh.querySelector('.gldrag').getBoundingClientRect();return bg.classList.contains('glass')&&getComputedStyle(bg).backgroundColor.replace(/ /g,'') in {'rgba(0,0,0,0)':1,'transparent':1}&&!sh.querySelector('[data-act=close] svg,.icb')&&h.height>=44&&h.width>=44&&getComputedStyle(sh).backdropFilter.includes('blur')})()"), J("[!!document.querySelector('.sheet'),getComputedStyle(document.querySelector('.sheet-bg')||document.body).backgroundColor]"))
    g.screenshot(path=f'{SH}/missions-panel-{t}.png')
    hb = J(RECT, '.sheet .gldrag'); g.mouse.move(hb[0] + 30, hb[1] + 20); g.mouse.down(); g.mouse.move(hb[0] + 30, hb[1] + 80, steps=5); g.mouse.move(hb[0] + 30, hb[1] + 200, steps=5); g.mouse.up(); g.wait_for_timeout(500)
    ok(f'[{t}] missions: swipe down closes', not J("!!document.querySelector('.sheet')"))
    J("()=>openHomeSheet()"); g.wait_for_timeout(400); g.mouse.click(195, 40); g.wait_for_timeout(300)
    ok(f'[{t}] missions: tap outside closes', not J("!!document.querySelector('.sheet')"))
    # feed: no double face. Sample opacities every frame for 7s; two different, non-aligned poses must never both be visible
    J("()=>{window.__s=[];const f=()=>{window.__s.push([performance.now(),...[...document.querySelectorAll('.catvid')].map(v=>[v.dataset.clip,+getComputedStyle(v).opacity,v.currentTime,v.duration])]);if(window.__s.length<600)requestAnimationFrame(f)};requestAnimationFrame(f)}")
    J("()=>document.querySelector('#cat-feed').click()"); sq = J("document.querySelector('.catfab.squish')!==null")
    ok(f'[{t}] feed: button squishes at once', sq)
    for i in range(36): g.screenshot(path=f'/tmp/feedseq-{L}-{i:02d}.png', clip={'x': 0, 'y': 160, 'width': 390, 'height': 560}); g.wait_for_timeout(110)
    g.wait_for_timeout(3000); S = J("window.__s")
    bad = []
    for s in S:
      vs = [v for v in s[1:] if v[1] > 0.04]
      if len(vs) == 2:
        a, bb = vs
        # overlap allowed only when the incoming clip is at its start and the outgoing is at/near its loop end or start (shared petting first frame)
        if a[0] == bb[0]: continue
        # both on the shared petting first frame: each within 0.25s of its start or its end
        near = lambda v: v[2] < 0.25 or (v[3] and v[3] - v[2] < 0.25)
        AL = lambda n: n == 'petting' or (n or '').startswith('room-')
        if not (AL(a[0]) and AL(bb[0]) and near(a) and near(bb)) and min(a[1], bb[1]) > 0.15 and min(a[1], bb[1]) < 0.99: bad.append(s)  # both opaque = the top one covers the other (swap frame), not a blend
    ok(f'[{t}] feed: no overlap of two different poses (loop-point switch / dip)', not bad, bad[:3])
    g.screenshot(path=f'{SH}/happy-after-feed-{t}.png')
    # stretch
    J("()=>{const x=document.querySelector('[data-act=stretchgo],[data-act=stretch]');stretchChip();catMisPlay('stretch')}"); g.wait_for_timeout(1200)
    chip = J(RECT, '#stretch-chip')
    ok(f"[{t}] stretch chip small and clear of Mochi (lower-middle) and Cici's raised hands (top band)", chip and chip[2] - chip[0] <= 100 and not OVL(chip, [90, 480, 320, 760]) and not OVL(chip, [0, 0, 390, 230]), chip)
    ok(f'[{t}] stretch: glass card hidden off her hands', J("getComputedStyle(document.querySelector('#hb-bubble')).visibility==='hidden'"))
    ok(f'[{t}] stretch chip buttons ≥44px', J("[...document.querySelectorAll('#stretch-chip button')].every(b=>b.getBoundingClientRect().height>=44)"))
    g.screenshot(path=f'{SH}/stretch-{t}.png'); J("()=>stretchStop()"); g.wait_for_timeout(500)
    # toast at top, off Mochi's face
    J("()=>toast('+10 points · test · 🐟 +1 treat')"); g.wait_for_timeout(300); tr = J(RECT, '#toast')
    ok(f'[{t}] toast at the top, off Mochi', tr and tr[3] < 300, tr)
    ok(f'[{t}] no page errors', not E, E[:2]); c.close()
  # reduced motion
  c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); g = c.new_page(); g.goto(U + '?phase2=1'); g.wait_for_timeout(500)
  g.evaluate("()=>{setLang('en');ST.tab='home';ST.page=null;render()}"); g.evaluate(FRESH); g.wait_for_timeout(600)
  ok('reduced motion: feed button has no animation, bubble static', g.evaluate("getComputedStyle(document.querySelector('#cat-feed')).animationName==='none'&&getComputedStyle(document.querySelector('#cici-real .cathbub')).animationName==='none'"))
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
