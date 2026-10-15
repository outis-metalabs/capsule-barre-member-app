"""PR cutout-fixes: videos really play in every placement (headless Chrome), win message in free space, asset fixes, PO conditions for NT-14 / NT-25."""
import sys, os, glob, json, subprocess, tempfile
import numpy as np
from PIL import Image
from scipy import ndimage
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
R = {}; E = []
def ok(k, c, d=''): R[k] = [bool(c), d]
CT = "sel=>new Promise(r=>{const t0=performance.now();(function f(){const v=document.querySelector(sel);if(v&&v.currentTime>0&&!v.paused)return r({t:v.currentTime,src:v.currentSrc.split('/').pop()});if(performance.now()-t0>2500)return r(v?{t:v.currentTime,paused:v.paused,rs:v.readyState,on:v.dataset.on||null}:null);requestAnimationFrame(f)})()})"
OVL = """()=>{const p=document.getElementById('wintoast');if(!p||p.hidden)return {err:'no toast',wait:!!p};const a=p.getBoundingClientRect(),h=document.querySelector('header.top').getBoundingClientRect(),tb=document.getElementById('tabs').getBoundingClientRect();
 const hit=[...document.querySelectorAll('button, .chip, input, textarea, a, select')].filter(e=>e.offsetParent&&!p.contains(e)).map(e=>[e,e.getBoundingClientRect()]).filter(([e,r])=>r.width&&!(r.top<h.bottom&&!e.closest('header.top'))&&!(r.right<=a.left||r.left>=a.right||r.bottom<=a.top||r.top>=a.bottom)).map(([e])=>(e.dataset.act||e.tagName)+':'+e.innerText.trim().slice(0,20));
 return {hit,belowHeader:a.top>=h.bottom,aboveTabs:a.bottom<=tb.top,w:Math.round(a.width),txt:p.innerText.trim(),full:p.querySelector('.vh').textContent,fun:p.classList.contains('fun'),live:p.getAttribute('aria-live')}}"""
with sync_playwright() as p:
  br = p.chromium.launch()
  def page(q='', lang=None, w=390):
    pg = br.new_page(viewport={'width': w, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U + q); pg.evaluate("()=>localStorage.clear()"); pg.goto(U + q); pg.wait_for_timeout(100)
    if lang: pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
    return pg
  J = lambda pg, js, a=None: pg.evaluate(js, a)
  # --- every placement plays (currentTime > 0) ---
  pg = page()
  ok('Home hero wave plays', (J(pg, CT, 'video.cut-wave') or {}).get('t', 0) > 0, J(pg, CT, 'video.cut-wave'))
  J(pg, "()=>{const b=B.find(b=>b.status==='confirmed'&&b.d>=0);success(b,()=>{})}")
  r = J(pg, CT, '.sheet video.cut-cheer'); ok('booking-confirmed sheet: 02 cheer video plays (not the still)', r and r.get('t', 0) > 0, r)
  J(pg, "()=>closeSheet()"); pg.wait_for_timeout(2100)
  J(pg, "()=>{celebrate();toast('+10 points for Stretch for 2 minutes')}"); r = J(pg, CT, '#wintoast video.cut-jump'); ok('win: 03 jump plays', r and r.get('t', 0) > 0, r)
  pg.wait_for_timeout(3400)
  J(pg, "()=>{window.claim=()=>({ok:true,c:{terms:{title:['Voucher','Voucher','바우처']}}});document.body.insertAdjacentHTML('beforeend','<button id=tclaim data-act=pvclaimok data-v=x>c</button>');document.getElementById('tclaim').click()}")
  r = J(pg, CT, '#wintoast video.cut-voucher'); ok('voucher claimed: 06 voucher plays', r and r.get('t', 0) > 0, r)
  J(pg, "()=>{setTab('cici');render()}"); r = J(pg, CT, '.nhero video.cut-wave'); ok('Nari tab empty: wave plays', r and r.get('t', 0) > 0, r)
  pg.fill('#in-cici', '내일'); r = J(pg, CT, '#nthink-cici.on video.cut-thinking'); ok('Nari tab typing: 04 thinking plays', r and r.get('t', 0) > 0, r)
  ok('videos stay muted + playsinline', J(pg, "()=>[...document.querySelectorAll('video.cut')].every(v=>v.muted&&v.playsInline)"))
  pg.close()
  pg = page('?realRewards=1'); J(pg, "()=>{ME.notices.push({k:'milestone',v:{n:4},t:PV.now()});setTab('home');render()}")
  r = J(pg, CT, '#pv-notes video.cut-ribbon'); ok('milestone: 07 ribbon plays (realRewards)', r and r.get('t', 0) > 0, r); pg.close()
  for nm, ua, rm in [('iOS', 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1', 'no-preference'), ('reduced motion', None, 'reduce')]:
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, user_agent=ua, reduced_motion=rm); q = ctx.new_page(); q.goto(U); q.evaluate("()=>{success(B.find(b=>b.status==='confirmed'&&b.d>=0),()=>{})}"); q.wait_for_timeout(300)
    ok(f'{nm}: still only (no video) in the sheet', q.evaluate("()=>!document.querySelector('video') && !!document.querySelector('.sheet img.cut-cheer')")); ctx.close()
  # --- win message never covers controls (Home / Nari, 320 + 390, KO + EN) ---
  for w in (320, 390):
    for L in ('ko', 'en'):
      for scr in ('home', 'cici', 'nari-reply'):
        pg = page('', L, w)
        if scr != 'home': J(pg, "()=>{setTab('cici');render()}")
        if scr == 'nari-reply': pg.click('[data-act=qbook]')
        last = {}
        for y in (0, 400, 900):
          J(pg, f"()=>{{window.scrollTo(0,{y});celebrate();toast('+60 points for showing up')}}"); pg.wait_for_timeout(420)
          o = J(pg, OVL)
          if o.get('err'): pg.wait_for_timeout(3600); o = J(pg, OVL)
          ok(f'win toast {scr} {w} {L} y{y}: bottom toast above the tab bar, never in the header, covers no control (or waits)', (o.get('err') and o.get('wait')) or (not o['hit'] and o['belowHeader'] and o['aboveTabs']), o)
          if not o.get('err'): last = o
          pg.wait_for_timeout(2900)
        ok(f'win toast {scr} {w} {L}: "+N points" + reason, aria-live polite, full text for screen readers', '+60' in last.get('txt', '') and 'showing up' in last.get('full', '').lower() and last.get('live') == 'polite', last)
        ok(f'win toast {scr} {w} {L}: auto-dismisses (~2.5s)', J(pg, "()=>!document.getElementById('wintoast')||document.getElementById('wintoast').hidden"))
        pg.close()
  pg = page('', 'ko'); J(pg, "()=>{setTab('home');render();toast('Saved',()=>{})}"); ok('undo toasts stay plain (no win toast)', J(pg, "()=>!document.getElementById('toast').hidden && !(document.getElementById('wintoast')&&!document.getElementById('wintoast').hidden)")); pg.close()
  pg = page('', 'en'); J(pg, "()=>{setTab('home');render();showWin('+10 points for Visit confirmed','jump')}"); pg.wait_for_timeout(400)
  ok('win toast: no header pill exists', J(pg, "()=>!document.getElementById('winpill')"))
  pg.click('#wintoast'); pg.wait_for_timeout(100); ok('win toast: tap dismisses', J(pg, "()=>document.getElementById('wintoast').hidden"))
  J(pg, "()=>showWin('+50 points','cheer',{reason:'7-day streak bonus'})"); pg.wait_for_timeout(450)
  ok('win toast: one points style only (#B04A5E), no fun variant', J(pg, "()=>{const e=document.querySelector('#wintoast .wamt');return !!e&&getComputedStyle(e).color==='rgb(176, 74, 94)'&&e.textContent==='+50 points'&&!document.querySelector('#wintoast.fun')&&![...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>/wintoast\.fun/.test(r.selectorText||''))}catch(e){return false}})}"))
  J(pg, "()=>{setLang('ko');showWin('+5 points','cheer',{reason:'미션 완료'})}"); pg.wait_for_timeout(3200); ok('win toast KO: "+5포인트"', '+5포인트' in J(pg, "()=>document.getElementById('wintoast').innerText")); pg.close()
  ctx = br.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce'); q = ctx.new_page(); q.goto(U); q.evaluate("()=>showWin('+10 points for X','jump')"); q.wait_for_timeout(150)
  ok('win toast: no motion with reduced motion', q.evaluate("()=>getComputedStyle(document.getElementById('wintoast')).transitionDuration.split(',').every(x=>parseFloat(x)===0)")); ctx.close()
  # --- PO conditions: NT-14 ---
  pg = page('', 'en'); J(pg, "()=>{setTab('cici');render();__plat.chatSend('cici','what time do you open at capsule barre?');render()}")
  ok('NT-14 PO: returning thread has the calendar icon → My bookings', J(pg, "()=>!!document.querySelector('#view > .row [data-act=mybk]')"))
  pg.click('#view > .row [data-act=mybk]'); ok('NT-14 PO: calendar icon opens My bookings', J(pg, "()=>ST.page==='bookings'"))
  J(pg, "()=>{ST.page=null;setTab('home');render()}")
  ok('NT-14 PO: Home Next class card links to bookings', J(pg, "()=>!!document.querySelector('#view [data-act=mybk], #view [data-act=go][data-v^=\"bookings\"], #view [data-act=allbk]')"))
  J(pg, "()=>{setTab('you');render()}"); ok('NT-14 PO: You has My bookings', 'My bookings' in pg.inner_text('#view') and pg.locator('[data-act=youpage][data-v=bookings]').count() == 1)
  J(pg, "()=>{setTab('cici');render();__plat.chatSend('cici','book');render()}")
  ok("NT-14 PO: typing 'book' starts booking", J(pg, "()=>{const m=CH.cici.msgs.at(-1);return m.kind==='bookPrompt'||/book/i.test(m.text)&&(m.chips||[]).length>0}"), J(pg, "()=>CH.cici.msgs.at(-1).text"))
  pg.close()
  # --- PO conditions: NT-25 ---
  for L, full, short in [('en', 'Call Capsule Barre', 'Call'), ('ko', 'Capsule Barre에 전화', '전화')]:
    pg = page('', L); bad = []
    for js in ["ST.tab='discover';ST.store='capsule'", "__plat.openBookings('up')", "setTab('home')", "setTab('cici')", "setTab('discover')", "setTab('you')"]:
      J(pg, f"()=>{{ST.page=null;ST.store=null;{js};render()}}")
      bad += J(pg, "()=>[...document.querySelectorAll('[data-act=callstore]')].filter(b=>b.offsetParent&&!b.closest('.sacts, .bkrow, .mcard, .card')).map(b=>b.innerText)")
    ok(f'NT-25 PO {L}: short Call only inside a store or booking card', not bad, bad)
    J(pg, "()=>{ST.store=null;ST.page=null;ST.tab='discover';ST.store='capsule';render()}")
    c = J(pg, "()=>{const b=document.querySelector('[data-act=callstore]');return [b.innerText.trim(),b.getAttribute('aria-label')]}")
    ok(f'NT-25 PO {L}: label "{short}", accessible name keeps "{full}"', c[0] == short and c[1].startswith(full), c)
    J(pg, "()=>{setTab('cici');render();__plat.chatSend('cici','i want to end my life');render()}")
    n = 0
    for js in ["setTab('cici')", "ST.tab='discover';ST.store='capsule'", "__plat.openBookings('up')"]:
      J(pg, f"()=>{{ST.page=null;ST.store=null;{js};render()}}"); n += J(pg, "()=>document.querySelectorAll('[data-act=callstore]').length")
    ok(f'NT-25 PO {L}: no Call button during a crisis turn', n == 0, n); pg.close()
  br.close()
# --- assets ---
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'nari-cut')
ok('shy.webp removed (unused)', not os.path.exists(f'{D}/shy.webp'))
def frames(v):
  t = tempfile.mkdtemp(); subprocess.run(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-i', f'{D}/{v}.webm', f'{t}/%03d.png'], check=True)
  return [np.asarray(Image.open(f).convert('RGBA')).astype(float) for f in sorted(glob.glob(t + '/*.png'))]
def specks(al):
  lab, nc = ndimage.label(al > 8)
  if not nc: return 0
  s = ndimage.sum(np.ones_like(al), lab, range(1, nc + 1)); return int((s < 0.002 * s.max()).sum())
W = frames('wave'); sp = [specks(x[..., 3]) for x in W]
ok('wave video: alpha specks cleaned (≤10 per frame, was up to 34)', max(sp) <= 10, [max(sp), round(sum(sp) / len(sp), 1)])
V = frames('voucher'); st = [np.abs(V[i + 1] - V[i])[..., 3].mean() for i in range(len(V) - 1)] + [np.abs(V[0] - V[-1])[..., 3].mean()]
ok('voucher video: no zoom pop (max frame step ≤ 16, was 48 at 11→12), loop seam smooth', max(st) <= 16 and st[-1] <= 6, [round(max(st), 1), int(np.argmax(st)), round(st[-1], 1)])
ok('no page errors', not E, E[:3])
for k, (v, d) in R.items(): print('PASS' if v else 'FAIL', k, '' if v else json.dumps(d, ensure_ascii=False)[:400])
print('TOTAL', sum(v for v, _ in R.values()), '/', len(R))
