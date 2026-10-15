"""Book on an unjoined store: every entry point opens 'Join {store} & book' and reaches booked in <= 3 taps.
Entry points: Discover next-slot chip, store page Join & book, store service row, store class slot, Cici chat (typed). Usage: join_book.py [base_url]"""
import sys, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/acc-fix'
R = []; ok = lambda n, c, d='': (R.append(c), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {d}')))
CHAT = {'en': 'book a gel manicure tomorrow', 'vi': 'đặt lịch làm móng gel ngày mai', 'ko': '내일 젤 네일 예약해 줘'}
A11Y = r"""()=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};
 const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c}return 'rgb(255,255,255)'};
 const els=[...document.querySelectorAll('.sheet button,.sheet p,.sheet dd,.sheet dt')].filter(e=>e.offsetParent&&e.innerText.trim());
 const bad=els.map(e=>{const a=lum(getComputedStyle(e).color),b=lum(bg(e));return [e.innerText.slice(0,20),(Math.max(a,b)+.05)/(Math.min(a,b)+.05)]}).filter(x=>x[1]<4.5);
 const small=[...document.querySelectorAll('.sheet button')].filter(e=>e.offsetParent).map(e=>[e.innerText.slice(0,15),e.getBoundingClientRect().height]).filter(x=>x[1]<43.5);return {bad,small}}"""
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang):
    g = b.new_page(viewport={'width': 390, 'height': 844}); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.E = E
    g.goto(U); g.evaluate('localStorage.clear()'); g.goto(U); g.wait_for_timeout(200); g.evaluate(f"()=>{{setLang('{lang}');render()}}"); return g
  def finish(g, name, sid, taps, lang, shot=None):
    sh = g.locator('#jb-go').count() == 1
    ok(f'[{lang}] {name}: Join & book sheet with store + slot', sh and g.locator('.sheet .storebar').count() == 1 and (g.locator('#jb-slot').count() == 1 or g.locator('#jb-noslot').count() == 1), g.locator('.sheet').count() and g.inner_text('.sheet')[:120])
    if not sh: return
    a = g.evaluate(A11Y); ok(f'[{lang}] {name}: sheet AA contrast + 44px', not a['bad'] and not a['small'], a)
    if shot: g.wait_for_timeout(500); g.screenshot(path=f'{SH}/joinbook-{shot}-{lang}-390.png')
    g.click('#jb-go'); taps += 1; g.wait_for_timeout(150)
    ok(f'[{lang}] {name}: joined, normal review opens', g.evaluate(f"S['{sid}'].joined") and g.locator('.sheet [data-act=dobook]').count() == 1)
    if shot: g.wait_for_timeout(500); g.screenshot(path=f'{SH}/joinbook-{shot}-review-{lang}-390.png')
    n0 = g.evaluate('B.length'); g.click('.sheet [data-act=dobook]'); taps += 1; g.wait_for_timeout(200)
    ok(f'[{lang}] {name}: booked in {taps} taps (<= 3)', g.evaluate('B.length') == n0 + 1 and g.evaluate(f"B[B.length-1].store") == sid and taps <= 3, [taps, g.evaluate('B.length'), n0])
    ok(f'[{lang}] {name}: no page errors', not g.E, g.E[:2])
  for lang in ['en', 'vi', 'ko']:
    for sid in ['nails', 'yoga', 'barber', 'moc', 'rally']:
      g = page(lang); g.evaluate("()=>{ST.tab='discover';render()}"); g.click(f'.dslot[data-v={sid}]'); finish(g, f'Discover next-slot {sid}', sid, 1, lang, 'discover' if sid == 'nails' else None); g.close()
    g = page(lang); g.evaluate("go('store:nails')"); ok(f'[{lang}] store page: service rows enabled', g.locator('#view [data-act=svc]:disabled').count() == 0); g.click('#st-jbook'); finish(g, 'store page Join & book', 'nails', 1, lang, 'store'); g.close()
    g = page(lang); g.evaluate("go('store:nails')"); g.click('#view [data-act=svc] >> nth=1'); finish(g, 'store service row', 'nails', 1, lang); g.close()
    g = page(lang); g.evaluate("go('store:yoga')"); c = g.locator('#view [data-act=classpick]:not([disabled])')
    ok(f'[{lang}] store class slots tappable', c.count() > 0)
    if c.count(): c.first.click(); finish(g, 'store class slot', 'yoga', 1, lang)
    g.close()
    g = page(lang); g.evaluate(f"()=>{{go('tab:cici');__plat.chatSend('cici',{CHAT[lang]!r})}}"); g.wait_for_timeout(150)
    ch = g.locator('#th-cici .chip').filter(has_text=re.compile('Ipsae'))
    ok(f'[{lang}] Cici chat offers Join & book chip', ch.count() >= 1, g.evaluate("[...document.querySelectorAll('#th-cici .msg.n')].pop().innerText"))
    if ch.count(): ch.first.click(); g.wait_for_timeout(150); ok(f'[{lang}] Cici chat: slot keeps the requested day (tomorrow)', g.evaluate('JBX && JBX.x && JBX.x.d')==1, g.evaluate('JSON.stringify(JBX)')); finish(g, 'Cici chat', 'nails', 1, lang, 'chat')
    g.close()
    # no silent dead ends
    g = page(lang); g.evaluate("()=>{const d=new Date();__plat; window.__nf=nextFree; nextFree=()=>null; ST.tab='discover';render()}")
    g.evaluate("joinBookSheet('nails', null, null)"); ok(f'[{lang}] no free slot: sheet explains, Join and book opens the timetable', g.locator('#jb-noslot').count() == 1)
    g.click('#jb-go'); g.wait_for_timeout(150); ok(f'[{lang}] no free slot: lands in the booking timetable', g.evaluate("S.nails.joined") and g.locator('.sheet').count() == 1 and g.locator('.sheet [data-act=jbgo]').count() == 0); g.close()
    g = page(lang); g.evaluate("()=>{go('tab:cici');__plat.chatSend('cici','i want to end my life')}"); g.evaluate("()=>{closeSheet();ST.tab='discover';render()}")
    if g.locator('.dslot[data-v=nails]').count(): g.click('.dslot[data-v=nails]')
    else: g.evaluate("joinBookSheet('nails', nextFree('nails'), null)")
    g.wait_for_timeout(100); ok(f'[{lang}] crisis turn: no booking sheet, but a visible message', g.locator('#jb-go').count() == 0 and g.locator('.toast').count() >= 1 and not g.evaluate('S.nails.joined')); g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
