"""platform-app-v2.html family style (owner-app design language adapted for members): floating glass tab bar with a centre Book action,
berry mission hero card, glass bubble, AA + 44px, KO/EN/VI, crisis. Usage: v2_family.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/v2-family'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
A11Y = r"""(sel)=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};
 const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;const m=c.match(/[\d.]+/g);if(m&&(m.length<4||+m[3]>.5))return c}return 'rgb(247,242,239)'};
 return [...document.querySelectorAll(sel)].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect(),a=lum(getComputedStyle(e).color),b=lum(bg(e));return {t:(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,24),h:Math.round(r.height),w:Math.round(r.width),c:+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)}})}"""
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='?phase2=1', lang='ko', w=390):
    g = b.new_context(viewport={'width': w, 'height': 844}).new_page(); g.E = []; g.on('pageerror', lambda e: g.E.append(str(e)))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(400); g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render()}}"); return g
  J = lambda g, js: g.evaluate(js)
  for L, lab in [('ko', '예약하기'), ('en', 'Book a visit'), ('vi', 'Đặt lịch')]:
    g = page(lang=L)
    st = J(g, "(()=>{const n=document.querySelector('#tabs'),c=getComputedStyle(n),r=n.getBoundingClientRect();return {bf:c.backdropFilter||c.webkitBackdropFilter,rad:c.borderRadius,l:r.left,b:innerHeight-r.bottom,order:[...n.children].map(e=>e.dataset.v||e.className)}})()")
    ok(f'[{L}] floating glass tab bar (inset, rounded, blur)', 'blur' in st['bf'] and st['rad'] == '30px' and st['l'] >= 10 and st['b'] >= 12, st)
    ok(f'[{L}] centre action sits between Discover and Cici', st['order'] == ['home', 'discover', 'tfab', 'cici', 'you'], st['order'])
    ok(f'[{L}] centre action = Book (member action), localized name', J(g, "document.querySelector('.tfab').dataset.act") == 'bk' and g.get_attribute('.tfab', 'aria-label') == lab)
    a = g.evaluate(A11Y, '#tabs button, #hb-bubble .hbhi, #hb-bubble .hbt, #hb-bubble .hbgo')
    ok(f'[{L}] tab bar + bubble: 44px and AA', all(x['h'] >= 44 and x['w'] >= 44 for x in g.evaluate(A11Y, '#tabs button, #hb-bubble .hbgo')) and all(x['c'] >= 4.5 for x in a), [x for x in a if x['c'] < 4.5])
    J(g, "()=>{openHomeSheet()}"); g.wait_for_timeout(300)
    m = g.evaluate(A11Y, '#home-dm #dm-head, #home-dm #dm-sub, #home-dm .mt, #home-dm .btn, #home-dm .tag')
    ok(f'[{L}] berry mission hero card: AA on every text + 44px buttons', all(x['c'] >= 4.5 for x in m) and all(x['h'] >= 44 for x in g.evaluate(A11Y, '#home-dm .btn')), m)
    ok(f'[{L}] segmented 3-part progress', J(g, "document.querySelectorAll('#home-dm .dmbar i').length") == 3)
    if L != 'vi':
      g.screenshot(path=f'{SH}/missions-{L}-390.png')
    J(g, "()=>{closeSheet()}"); g.wait_for_timeout(200)
    g.screenshot(path=f'{SH}/home-{L}-390.png') if L != 'vi' else None
    if L != 'vi':
      for tab in ['discover', 'cici', 'you']:
        J(g, f"()=>{{closeSheet();ST.tab='{tab}';ST.page=null;ST.store=null;render();scrollTo(0,0)}}"); g.wait_for_timeout(300); g.screenshot(path=f'{SH}/{tab}-{L}-390.png')
    J(g, "()=>{closeSheet();ST.tab='home';render()}"); g.wait_for_timeout(200)
    J(g, "()=>{const b=document.querySelector('.tfab'); if(b)b.click()}"); g.wait_for_timeout(300)
    ok(f'[{L}] centre action opens the booking sheet', J(g, "!!document.querySelector('.sheet #bk-places, .sheet #bk-svcs')"))
    ok(f'[{L}] no page errors', not g.E, g.E); g.close()
  for L in ('ko', 'en'):
    g = page(lang=L); J(g, "()=>{CH.cici.gate=true;CH.cici.msgs.push({who:'cici',text:'x',care:true});ST.tab='home';render()}")
    ok(f'[{L}] crisis: no centre Book nudge, no bubble, no mission card', J(g, "!document.querySelector('.tfab,#hb-bubble,#home-dm')")); g.close()
  # nothing tappable under the floating bar / centre button at the end of a scroll (all tabs, KO/EN/VI, 390 + 360)
  UNDER = r"""(()=>{const bar=document.querySelector('#tabs').getBoundingClientRect(),f=document.querySelector('#tabs .tfab');const fr=f?f.getBoundingClientRect():null;const top=Math.min(bar.top,fr?fr.top:1e9);
   const hit=r=>r.bottom>top+1&&r.top<bar.bottom&&r.width>0&&r.height>0;
   return [...document.querySelectorAll('#view button,#view a[href],#view input,#view textarea,#view select,#view [data-act],#view [tabindex]:not([tabindex="-1"])')].filter(e=>e.offsetParent&&!e.closest('#tabs,.sheet,.toast,.v2pull,#v2-pull')).map(e=>[e,e.getBoundingClientRect()]).filter(([e,r])=>hit(r)).map(([e,r])=>(e.dataset.act||e.tagName)+':'+(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,20)+'@'+Math.round(r.top))})()"""
  for w in (390, 360):
    for L in ('ko', 'en', 'vi'):
      g = page(lang=L, w=w)
      for tab in ['home', 'discover', 'cici', 'you']:
        J(g, f"()=>{{ST.tab='{tab}';ST.page=null;ST.store=null;render()}}"); g.wait_for_timeout(150)
        J(g, "scrollTo(0,document.documentElement.scrollHeight)"); g.wait_for_timeout(250)
        bad = J(g, UNDER)
        ok(f'[{w}/{L}] {tab}: end of scroll, nothing tappable under the bar/centre button', not bad, bad)
        if w == 390 and L != 'vi' and tab == 'home': g.screenshot(path=f'{SH}/home-end-{L}-390.png')
      ok(f'[{w}/{L}] v2 Home has no duplicate full-width Book CTA (centre button books)', J(g, "(()=>{ST.tab='home';render();return !document.querySelector('#g-book')})()"))
      g.close()
  g = page(''); ok('flag off: tab bar still works (4 tabs + centre Book)', J(g, "document.querySelectorAll('#tabs [data-act=tab]').length") == 4); g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
