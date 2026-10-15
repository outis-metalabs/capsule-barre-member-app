"""platform-app-v2.html full-screen Home (owner-app layout): Cici image fills the screen, face never covered, ONE glass card top-left,
header overlay (date + language + bell), floating bar with centre Book, nothing else on the first screen; the rest in a light sheet.
Face box comes from CICI_HOME (swap config). 360/390/430 x KO/EN/VI. Usage: v2_home.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/home-fixed'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
GEO = r"""(()=>{const rc=e=>{const r=e.getBoundingClientRect();return {l:r.left,t:r.top,r:r.right,b:r.bottom}};const i=document.querySelector('#cici-real video, #cici-real img'),ir=i.getBoundingClientRect(),C=CICI_HOME,cs=getComputedStyle(i),s=Math.max(ir.width/C.w,ir.height/C.h);
 const px=parseFloat(cs.objectPosition.split(' ')[0])/100,py=parseFloat(cs.objectPosition.split(' ')[1])/100,ox=ir.left+(ir.width-C.w*s)*px,oy=ir.top+(ir.height-C.h*s)*py;  /* object-fit: cover mapping */
 const f={l:ox+C.face[0]*s,t:oy+C.face[1]*s,r:ox+C.face[2]*s,b:oy+C.face[3]*s,fit:cs.objectFit,pos:cs.objectPosition};
 const bar=rc(document.querySelector('#tabs')),fab=document.querySelector('#tabs .tfab'),barTop=Math.min(bar.t,fab?rc(fab).t:1e9);
 const card=rc(document.querySelector('#hb-bubble')),hdr=[...document.querySelectorAll('#top button, #top .brand')].map(rc);
 const ov=(a,b)=>a.l<b.r&&b.l<a.r&&a.t<b.b&&b.t<a.b;
 const firstScreen=[...document.querySelectorAll('#view *')].filter(e=>e.offsetParent&&!e.closest('#v2-hero')&&e.children.length===0&&(e.innerText||'').trim()).map(e=>[e,rc(e)]).filter(([e,r])=>r.b>0&&r.t<barTop&&r.r>0&&r.l<innerWidth).map(([e])=>(e.innerText||'').trim().slice(0,20));
 return {f,card,barTop,W:innerWidth,H:innerHeight,coverCard:ov(f,card),coverHdr:hdr.some(h=>ov(f,h)),firstScreen,loaded:i.tagName==='VIDEO'?(i.readyState>=1||!!i.poster):(i.complete&&i.naturalWidth>0),
   cards:document.querySelectorAll('#v2-hero .hbub').length,em:!!document.querySelector('#hb-line em'),chev:!!document.querySelector('#hb-bubble .hbgo'),sec:document.querySelectorAll('#hb-bubble .hbsec').length,
   hdrBg:getComputedStyle(document.querySelector('header.top')).backgroundColor,date:document.querySelector('#top .brand span.t').innerText,heroH:rc(document.querySelector('#v2-hero')).b-rc(document.querySelector('#v2-hero')).t,
   sh:document.documentElement.scrollHeight,ch:document.documentElement.clientHeight,bsh:document.body.scrollHeight,bch:document.body.clientHeight,pull:!!document.querySelector('#v2-pull'),peek:!!document.querySelector('body.v2home > #app #home-sheet, #view > #home-sheet')}})()"""
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang, w, h, q='?phase2=1'):
    g = b.new_context(viewport={'width': w, 'height': h}).new_page(); g.E = []; g.on('pageerror', lambda e: g.E.append(str(e)))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(500); g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render();scrollTo(0,0)}}"); g.wait_for_timeout(300); return g
  for w, h in [(360, 640), (360, 780), (390, 844), (430, 932)]:
    for L in ('ko', 'en', 'vi'):
      g = page(L, w, h); k = f'[{w}/{L}]'; G = g.evaluate(GEO); f = G['f']
      ok(f'{k} official Mochi (petting) loop/poster loads full-bleed (cover, 50% 35%) and the hero fills the screen', G['loaded'] and abs(G['heroH'] - h) < 2 and f['fit'] == 'cover' and f['pos'] == '50% 35%', [G['heroH'], f])
      ok(f'{k} face fully on screen, in the upper-middle, above the bar', f['l'] >= 0 and f['r'] <= w and f['t'] >= 0 and f['b'] <= G['barTop'] and f['t'] < h * .5 and abs((f['l'] + f['r']) / 2 - w / 2) < w * .12, [f, G['barTop']])
      ok(f'{k} face never covered by the glass card or the header', not G['coverCard'] and not G['coverHdr'], [f, G['card']])
      ok(f'{k} ONE glass card top-left: greeting, bold line with berry highlight, chevron, <=1 secondary row', G['cards'] == 1 and G['card']['l'] <= 20 and G['card']['t'] < 120 and G['em'] and G['chev'] and G['sec'] <= 1, G)
      ok(f'{k} header overlays the photo (transparent) with a date title', G['hdrBg'] in ('rgba(0, 0, 0, 0)', 'transparent') and len(G['date']) > 3, [G['hdrBg'], G['date']])
      ok(f'{k} nothing else on the first screen', not G['firstScreen'], G['firstScreen'][:6])
      ok(f'{k} centre Book button present', g.locator('#tabs .tfab[data-act=bk]').count() == 1)
      ok(f'{k} Home is not scrollable (scrollHeight ≈ clientHeight) and no peeking sheet', abs(G['sh'] - G['ch']) <= 2 and abs(G.get('bsh', G['sh']) - G.get('bch', G['ch'])) <= 8 and not G.get('peek') and G.get('pull'), G)
      if w in (390, 430) and L != 'vi': g.screenshot(path=f'{SH}/home-{L}-{w}.png')
      J = g.evaluate
      g.click('#hb-bubble .hbgo'); g.wait_for_timeout(500)
      ok(f'{k} glass card opens Today sheet overlay', J("!!document.querySelector('.sheet #home-sheet')"))
      ok(f'{k} sheet holds stage+stats, missions, next class, level and room', J("['#g-comp','#g-bars','#home-dm','#home-next','#home-lvl','#p2-room'].every(s=>document.querySelector('#home-sheet '+s))"))
      if w in (390, 430) and L != 'vi': g.screenshot(path=f'{SH}/sheet-{L}-{w}.png')
      J("()=>{typeof closeSheet==='function'&&closeSheet()}"); g.wait_for_timeout(200)
      g.click('#v2-pull'); g.wait_for_timeout(400)
      ok(f'{k} pull cue also opens the sheet', J("!!document.querySelector('.sheet #home-sheet')"))
      ok(f'{k} dual-video crossfade stage present', J("document.querySelectorAll('#cici-real .catvid').length>=2 || !!document.querySelector('#cici-real img.catstill, #cici-real img')"))
      J("()=>{typeof closeSheet==='function'&&closeSheet()}")
      ok(f'{k} no page errors', not g.E, g.E); g.close()
  # crisis: no full-screen hero/card; calm Home
  for L in ('ko', 'en'):
    g = page(L, 390, 844); g.evaluate("()=>{CH.cici.gate=true;CH.cici.msgs.push({who:'cici',text:'x',care:true});ST.tab='home';render()}")
    ok(f'[{L}] crisis: no full-screen hero, no glass card, no centre Book', g.evaluate("!document.querySelector('#v2-hero,#hb-bubble,.tfab') && !document.body.classList.contains('v2home')")); g.close()
  g = page('ko', 390, 844, ''); ok('flag off: classic Home (no full-screen hero)', g.evaluate("!document.querySelector('#v2-hero')")); g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
