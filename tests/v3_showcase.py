"""platform-app-v3.html?show=1 — investor showcase preset: curated state on every load, clips prefetched, presentation frame + brand panel
only on wide screens, entrance animation, no errors / 404s. The plain app (no ?show) is untouched. Usage: v3_showcase.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/showcase'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:320]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(w, h, q):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(r.url))
    g.goto(U + q); g.evaluate("localStorage.clear()"); g.goto(U + q); g.wait_for_timeout(1200); return g
  J = lambda g, s: g.evaluate(s)
  g = page(1280, 800, '?show=1&lang=ko')
  st = J(g, "({show:document.body.classList.contains('showcase'),streak:ME.streak,treats:catDay().treats,hour:P2S.cat.demoHour,mood:catMood(),dm:Object.keys(dmDay().done).length,tab:ST.tab,page:ST.page})")
  ok('SHOW preset: noon, 7-day streak (Mochi playing), 1 treat, missions 0/3, Home', st['show'] and st['streak'] == 7 and st['treats'] == 1 and st['hour'] == 12 and st['mood'] == 'play' and st['dm'] == 0 and st['tab'] == 'home' and not st['page'], st)
  ok('SHOW clips prefetched (webm + posters)', J(g, "document.querySelectorAll('link.showpre').length") >= 12, J(g, "document.querySelectorAll('link.showpre').length"))
  ok('SHOW wide screen: phone frame ring + brand panel visible', J(g, "getComputedStyle(document.body,'::after').content") == '""' and J(g, "getComputedStyle(document.querySelector('.showbrand')).display") == 'block')
  ok('SHOW wide screen: app column centred, nothing outside the 430px phone is interactive', J(g, "(()=>{const a=document.querySelector('#app').getBoundingClientRect();return Math.abs(a.left+a.width/2-640)<2&&a.width===430})()"))
  g.wait_for_timeout(1600); g.screenshot(path=f'{SH}/desk-ko.png')
  ok('SHOW entrance animation done, circles all visible', J(g, "[...document.querySelectorAll('#v2-acts .v2act')].length===3 && [...document.querySelectorAll('#v2-acts .v2act')].every(e=>+getComputedStyle(e).opacity===1)"))
  ok('SHOW greeting next-class line fits on one line in the wider card', J(g, "(()=>{const e=document.querySelector('#v2-next');if(!e)return true;return e.getBoundingClientRect().height<30})()"), J(g, "document.querySelector('#v2-next')?.getBoundingClientRect().height"))
  J(g, "()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(600)
  ok('SHOW feed from the preset works (room-eat scene)', J(g, "ST.catEat==='feed'"))
  g.wait_for_timeout(1000); g.screenshot(path=f'{SH}/desk-feed.png')
  ok('SHOW no 404s, no page errors (desktop)', not g.NF and not g.E, g.NF[:3] + g.E[:2]); g.close()
  g = page(390, 844, '?show=1&lang=ko')
  ok('SHOW phone: preset on, no frame, no brand panel', J(g, "document.body.classList.contains('showcase') && getComputedStyle(document.body,'::after').content==='none' && getComputedStyle(document.querySelector('.showbrand')).display==='none'"))
  g.screenshot(path=f'{SH}/phone-ko.png'); ok('SHOW no 404s, no page errors (phone)', not g.NF and not g.E, g.NF[:3] + g.E[:2]); g.close()
  g = page(1280, 800, '?lang=ko')
  ok('PLAIN app (no ?show): no showcase class, no brand panel, no prefetch links', not J(g, "document.body.classList.contains('showcase')") and not J(g, "!!document.querySelector('.showbrand')") and J(g, "document.querySelectorAll('link.showpre').length") == 0)
  g.close(); b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
