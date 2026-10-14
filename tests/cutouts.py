"""Nari alpha cut-outs (WebM VP9 alpha + WebP still) + chat-card saved policy. Usage: python3 tests/cutouts.py [url] [shots]"""
import sys, os, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/cutouts'
os.makedirs(SH, exist_ok=True); R = {}; E = []
def ok(k, c, d=''): R[k] = [bool(c), d]
SAFARI = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
MACSAF = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15'
with sync_playwright() as p:
  br = p.chromium.launch()
  def page(q='', ua=None, rm=None, w=390):
    ctx = br.new_context(viewport={'width': w, 'height': 844}, user_agent=ua, reduced_motion=rm or 'no-preference')
    pg = ctx.new_page(); pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U + q); pg.evaluate("()=>localStorage.clear()"); pg.goto(U + q); pg.wait_for_timeout(150); return pg
  J = lambda pg, js, a=None: pg.evaluate(js, a)
  CUTS = "()=>[...document.querySelectorAll('.cut')].map(e=>({tag:e.tagName,name:[...e.classList].find(c=>c.startsWith('cut-')),src:e.currentSrc||e.getAttribute('src')||'',poster:e.getAttribute('poster')||'',pre:e.getAttribute('preload'),lazy:e.getAttribute('loading'),blend:getComputedStyle(e).mixBlendMode,mask:getComputedStyle(e).maskImage||getComputedStyle(e).webkitMaskImage,inVideo:!!e.closest('video')&&e.tagName==='IMG'}))"
  pg = page()
  ok('KO default', J(pg, "()=>L") == 'ko')
  c = [x for x in J(pg, CUTS) if not x['inVideo']]
  hero = [x for x in c if x['name'] == 'cut-wave']
  ok('Home hero = 01 wave, WebM video with WebP poster', hero and hero[0]['tag'] == 'VIDEO' and hero[0]['poster'].endswith('nari-cut/wave.webp'), hero)
  pg.wait_for_timeout(600)
  st = J(pg, "()=>{const v=document.querySelector('video.cut-wave');return v?{on:v.dataset.on,src:v.currentSrc,paused:v.paused,rs:v.readyState}:null}")
  ok('hero video lazy-hydrates and plays the alpha WebM', st and st['on'] == '1' and st['src'].endswith('wave.webm') and st['rs'] >= 2, st)
  ok('no multiply/mask stopgap on any cut-out', all(x['blend'] == 'normal' and x['mask'] in ('none', None, '') for x in c), c)
  ok('fallback still inside every video', J(pg, "()=>[...document.querySelectorAll('video.cut')].every(v=>v.querySelector('img.cut[src$=\".webp\"]'))"))
  ok('hero has KO alt label', '나리' in (J(pg, "()=>document.querySelector('video.cut-wave').getAttribute('aria-label')") or ''))
  # transparency: the cut-out has no box (corner pixel shows the scene gradient)
  bx = J(pg, "()=>{const r=document.querySelector('.scene .pic').getBoundingClientRect();return [r.x+4,r.y+4]}")
  pg.screenshot(path=f'{SH}/home-390-ko.png')
  from PIL import Image
  im = Image.open(f'{SH}/home-390-ko.png').convert('RGB'); px = im.getpixel((int(bx[0]), int(bx[1])))
  ok('hero corner is the pink scene gradient, not a box', px[0] > 240 and px[1] > 200 and px[2] > 200 and not (px[0] > 250 and px[1] > 250 and px[2] > 250), px)
  # booking confirm sheet: 02 cheer
  J(pg, "()=>{success(B.find(b=>b.status==='confirmed'&&b.d>=0),()=>{})}"); pg.wait_for_timeout(700)
  ok('booking confirmed = 02 cheer video', J(pg, "()=>!!document.querySelector('.sheet video.cut-cheer[poster$=\"cheer.webp\"]')"))
  pg.screenshot(path=f'{SH}/booking-confirm-390-ko.png'); J(pg, "()=>closeSheet()"); pg.wait_for_timeout(2100)
  # typing: 04 thinking at 120 (empty thread) and 40 (thread)
  J(pg, "()=>{setTab('nari');render()}"); pg.fill('#in-nari', '내일 바레'); pg.wait_for_timeout(500)
  big = J(pg, "()=>{const e=document.querySelector('#nthink-nari.on .cut');return e?[e.tagName,Math.round(e.getBoundingClientRect().width)]:null}")
  ok('typing on empty thread: thinking at 120px', big == ['VIDEO', 120], big)
  pg.screenshot(path=f'{SH}/chat-typing-120-390-ko.png')
  J(pg, "()=>{__plat.chatSend('nari','주차 돼요?');render()}"); pg.fill('#in-nari', '내일'); pg.wait_for_timeout(400)
  sm = J(pg, "()=>{const e=document.querySelector('#nthink-nari.on .cut');return e?[e.tagName,Math.round(e.getBoundingClientRect().width),Math.round(e.getBoundingClientRect().height)]:null}")
  ok('typing in a thread: thinking at 40px', sm == ['VIDEO', 40, 40], sm)
  pg.screenshot(path=f'{SH}/chat-typing-40-390-ko.png')
  # empty state: 05 still
  J(pg, "()=>{B.forEach(b=>{if(b.status==='confirmed')b.status='cancelled'});__plat.openBookings('up');render()}"); pg.wait_for_timeout(200)
  es = J(pg, "()=>{const e=document.querySelector('.nempty .cut');return e?[e.tagName,e.getAttribute('src'),e.getAttribute('loading'),Math.round(e.getBoundingClientRect().height)]:null}")
  ok('empty state = 05 still (img, lazy, 96px)', es and es[0] == 'IMG' and es[1].endswith('nari-cut/idle.webp') and es[2] == 'lazy' and es[3] == 96, es)
  pg.screenshot(path=f'{SH}/empty-bookings-390-ko.png')
  J(pg, "()=>{ST.page=null;setTab('home');render()}"); es2 = J(pg, "()=>document.querySelector('.nempty .cut')?.getAttribute('src')")
  ok('Home empty next class uses 05 idle', (es2 or '').endswith('idle.webp'), es2)
  # points win pop: 03 jump; voucher claimed: 06
  J(pg, "()=>celebrate()"); pg.wait_for_timeout(100)
  ok('points/streak win pop = 03 jump (padded)', J(pg, "()=>!!document.querySelector('.cheerpop.pop-jump video.cut-jump')"))
  J(pg, """()=>{window.claim=()=>({ok:true,c:{terms:{title:['Voucher','Voucher','바우처']}}}); document.body.insertAdjacentHTML('beforeend','<button id=tclaim data-act=pvclaimok data-v=x>c</button>'); document.getElementById('tclaim').click()}"""); pg.wait_for_timeout(100)
  ok('voucher claimed pop = 06 voucher', J(pg, "()=>!!document.querySelector('.cheerpop.pop-voucher .cut-voucher')"))
  pg.close()
  # ribbon: realRewards only
  for q, want in [('', False), ('?realRewards=1', True)]:
    pg = page(q); J(pg, "()=>{ME.notices.push({k:'milestone',v:{n:4},t:PV.now()});setTab('home');render()}")
    got = J(pg, "()=>!!document.querySelector('#pv-notes .cut-ribbon')")
    ok(f'07 ribbon milestone {"shown with" if want else "hidden without"} realRewards', got == want, got)
    if want: pg.screenshot(path=f'{SH}/streak-ribbon-390-ko.png')
    pg.close()
  # Safari / iOS -> stills; reduced motion -> stills
  for nm, ua, rm in [('iOS Safari', SAFARI, None), ('macOS Safari', MACSAF, None), ('reduced motion', None, 'reduce')]:
    pg = page(ua=ua, rm=rm); J(pg, "()=>{success(B.find(b=>b.status==='confirmed'&&b.d>=0),()=>{})}"); J(pg, "()=>{celebrate()}")
    v = J(pg, "()=>document.querySelectorAll('video').length"); imgs = J(pg, "()=>[...document.querySelectorAll('img.cut')].map(e=>e.getAttribute('src'))")
    ok(f'{nm}: no video, WebP stills only', v == 0 and any(s.endswith('wave.webp') for s in imgs) and any(s.endswith('cheer.webp') for s in imgs), [v, imgs])
    pg.close()
  # lazy: off-screen videos don't download
  pg = page(); n = J(pg, "()=>performance.getEntriesByType('resource').filter(r=>r.name.endsWith('.webm')).map(r=>r.name.split('/').pop())")
  ok('only on-screen WebMs are fetched (lazy)', set(n) <= {'wave.webm'}, n)
  pg.close()
  # file sizes
  d = 'assets/nari-cut'; sz = {f: os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)}
  ok('every WebM <= 200 KB, every WebP <= 25 KB, total < 1 MB', all(v <= 200_000 for k, v in sz.items() if k.endswith('.webm')) and all(v <= 25_000 for k, v in sz.items() if k.endswith('.webp')) and sum(sz.values()) < 1_000_000, sz)
  from PIL import Image as I
  a = I.open(f'{d}/jump.webp').getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()
  ok('03 jump still has transparent top padding (>=40px of 480)', a[1] >= 40, a)
  # P3: in-chat booking card shows the saved policy
  pg = page('', w=390)
  r = J(pg, """()=>{ const b=B.find(x=>x.store==='salon'&&x.status==='confirmed'); const saved=b.pol.late; S.salon.policy.late='CHANGED RULE'; S.salon.policy.noshow='CHANGED NOSHOW'; S.salon.policy.free=99;
     setTab('nari'); CH.nari.msgs=[]; askCancel(CH.nari,b); render(); const card=[...document.querySelectorAll('#th-nari .mcard')].pop(); return {saved, txt:card?card.innerText:''} }""")
  ok('P3 in-chat cancel card shows the saved policy, not the current rule', r['txt'] and 'CHANGED' not in r['txt'] and ('5,000' in r['txt'] or '5.000' in r['txt']), r)
  pg.close()
  # AA + 44 px on the new screens
  pg = page()
  for nm, js in [('home', "()=>{setTab('home');render()}"), ('confirm', "()=>{success(B.find(b=>b.status==='confirmed'&&b.d>=0),()=>{})}")]:
    J(pg, js); pg.wait_for_timeout(300)
    sm = J(pg, "()=>[...document.querySelectorAll('#view button, .sheet button')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect()).filter(r=>r.height<44||r.width<44).length")
    ok(f'44px targets on {nm}', sm == 0, sm)
  pg.close(); br.close()
ok('no page errors', not E, E[:3])
for k, (v, d) in R.items(): print('PASS' if v else 'FAIL', k, '' if v else json.dumps(d, ensure_ascii=False)[:400])
print('TOTAL', sum(v for v, _ in R.values()), '/', len(R))
