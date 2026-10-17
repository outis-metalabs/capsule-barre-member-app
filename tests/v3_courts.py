"""platform-app-v3.html — court-number choice for rental stores (docs/specialists-and-ratings.md §4f, 2026-10-17): time first, then court rows
under the chosen time (Any court first, attributes, surcharge, taken rows stay visible), court-first entry from the store page, "assigned on arrival"
for a no-selector club, the court on confirm / success / My bookings / check-in, the club-moved-your-game notification.
Usage: v3_courts.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/courts'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:360]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='?lang=ko', w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(700); return g
  for L in ('en', 'ko'):
    g = page(f'?lang={L}'); J = g.evaluate
    J("()=>{NOWX=600;ST.tab='discover';ST.page=null;ST.store='pickle';render()}"); g.wait_for_timeout(300) # 10:00 so today has open courts
    # ---- store page: courts as cards
    ok(f'[{L}] store page: a Courts section with one row per court (attributes, next free time, surcharge on the indoor ones)', J("(()=>{const rows=[...document.querySelectorAll('#st-courts .svc')];return rows.length===4&&rows.every(r=>/(outdoor|indoor|야외|실내)/.test(r.innerText))&&rows.filter(r=>/\\+₩4,000/.test(r.innerText)).length===2&&rows.every(r=>/(next free|가능|full this week|마감)/.test(r.innerText))})()"), J("[...document.querySelectorAll('#st-courts .svc')].map(r=>r.innerText)"))
    g.screenshot(path=f'{SH}/store-courts-{L}.png', full_page=True)
    # ---- Book sheet: time rows → court rows
    J("()=>bookSheet('pickle')"); g.wait_for_timeout(400)
    ok(f'[{L}] step 2: options line has no court (block · players · paddles only); time rows say "N of 4 courts free"', not J("/코트|Court/.test(document.querySelector('#bk-opts summary').innerText)") and J("[...document.querySelectorAll('#bk-slots .slot')].slice(0,3).every(r=>/(\\d of 4 courts free|코트 4면 중 \\d면 가능)/.test(r.innerText))"), J("document.querySelector('#bk-slots .slot')?.innerText"))
    g.click('#bk-slots .slot >> nth=0'); g.wait_for_timeout(300)
    rows = J("[...document.querySelectorAll('#bk-courts .slot')].map(r=>[r.className, r.innerText.replace(/\\n/g,' | ')])")
    ok(f'[{L}] tap a time: court rows open under it; Any court first (club assigns, cheapest), four courts with attributes, the indoor ones +₩4,000, taken ones visible but disabled', len(rows) == 5 and 'any' in J("document.querySelector('#bk-courts .slot').dataset.v") and all(re.search(r'(outdoor|indoor|야외|실내)', r[1]) for r in rows[1:]) and sum(1 for r in rows if '₩24,000' in r[1]) >= 1 and J("document.querySelector('#bk-slots .slot.open')?.getAttribute('aria-expanded')") == 'true', rows)
    ok(f'[{L}] a taken court row says taken and is not a button; a free one is', J("(()=>{const t=document.querySelector('#bk-courts .slot.taken'),f=document.querySelector('#bk-courts button.slot.court[data-v]:not([data-v=any])');return (!t||t.tagName==='DIV')&&!!f})()"))
    g.screenshot(path=f'{SH}/pick-{L}.png')
    ok(f'[{L}] tapping the time again closes the court rows', J("(()=>{document.querySelector('#bk-slots .slot.open').click();return !document.querySelector('#bk-courts')&&BS.m===null})()"))
    g.click('#bk-slots .slot >> nth=0'); g.wait_for_timeout(200); g.click('#bk-courts [data-v=c3]'); g.wait_for_timeout(300)
    ok(f'[{L}] pick Court 3 (indoor): confirm names the court with attributes, price includes the surcharge, not "assigned"', J("(()=>{const d=document.querySelector('.sheet dl.conf').innerText;return /Court 3|3번 코트/.test(d)&&/(indoor|실내)/.test(d)&&PEND.rids[0]==='c3'&&PEND.anyCourt===false&&PEND.price===240000})()"), J("document.querySelector('.sheet dl.conf')?.innerText"))
    J("()=>document.querySelector('.sheet [data-act=dobook]').click()"); g.wait_for_timeout(400)
    ok(f'[{L}] success sheet and the booking carry the court', J("/Court 3|3번 코트/.test(document.querySelector('#bk-confirm').innerText) && B[B.length-1].rids[0]==='c3' && B[B.length-1].anyCourt===false"))
    g.screenshot(path=f'{SH}/success-{L}.png'); J("closeSheet()")
    # ---- Any court path + check-in reveal
    J("()=>bookSheet('pickle')"); g.wait_for_timeout(300); g.click('#bk-slots .slot >> nth=1'); g.wait_for_timeout(200); g.click('#bk-courts [data-v=any]'); g.wait_for_timeout(300)
    ok(f'[{L}] Any court: confirm and success say "Court assigned on arrival"', J("PEND.anyCourt===true && /(Court assigned on arrival|코트는 도착 시 배정)/.test(document.querySelector('.sheet dl.conf').innerText)") and (J("()=>document.querySelector('.sheet [data-act=dobook]').click()") or True) and (g.wait_for_timeout(300) or True) and J("/(assigned on arrival|도착 시 배정)/.test(document.querySelector('#bk-confirm').innerText)"))
    J("closeSheet()"); J("()=>{ST.tab='you';ST.page='bookings';ST.bkSeg='up';render()}"); g.wait_for_timeout(300)
    ok(f'[{L}] My bookings: the Court 3 booking shows its court; the Any booking says assigned on arrival', J("(()=>{const t=[...document.querySelectorAll('#view .bkrow')].map(r=>r.innerText);return t.some(x=>/Court 3|3번 코트/.test(x))&&t.some(x=>/(Court assigned on arrival|코트는 도착 시 배정)/.test(x))})()"))
    J("()=>{const b=B[B.length-1];b.d=todayIdx();b.m=(nowMin()%1440)+60;checkin(b)}"); g.wait_for_timeout(200)
    ok(f'[{L}] check-in reveals the court the club allocated', J("/(assigned by the club|클럽 배정)/.test(document.querySelector('#ci-court').innerText) && /Court \\d|\\d번 코트/.test(document.querySelector('#ci-court').innerText)"), J("document.querySelector('#ci-court')?.innerText")); J("closeSheet()")
    # ---- court-first entry from the store page
    J("()=>{ST.tab='discover';ST.page=null;ST.store='pickle';render()}"); g.wait_for_timeout(200); g.click('#st-courts [data-v=c1]'); g.wait_for_timeout(300)
    ok(f'[{L}] court-first: the Book sheet opens with Court 1 fixed (line + Any court link) and every time row names it; a time goes straight to confirm', J("BS.court==='c1' && !!document.querySelector('#bk-court-fixed') && /Court 1|1번 코트/.test(document.querySelector('#bk-slots .slot').innerText)") and (g.click('#bk-slots .slot >> nth=0') or True) and (g.wait_for_timeout(300) or True) and J("!!document.querySelector('.sheet [data-act=dobook]') && PEND.rids[0]==='c1' && PEND.anyCourt===false"))
    J("closeSheet()")
    # ---- no-selector club
    J("()=>{S.rally.joined=true;ST.store='rally';render()}"); g.wait_for_timeout(300)
    ok(f'[{L}] Rally (identical courts): no Courts section, one "assigned on arrival" line; time rows say so; a time goes straight to confirm as assigned', J("!document.querySelector('#st-courts') && /(assigned on arrival|도착 시 배정)/.test(document.querySelector('#st-courts-note').innerText)") and (J("()=>bookSheet('rally')") or True) and (g.wait_for_timeout(300) or True) and J("/(assigned on arrival|도착 시 배정)/.test(document.querySelector('#bk-slots .slot').innerText)") and (g.click('#bk-slots .slot >> nth=0') or True) and (g.wait_for_timeout(300) or True) and J("!document.querySelector('#bk-courts') && !!document.querySelector('.sheet [data-act=dobook]') && PEND.anyCourt===true"))
    J("closeSheet()")
    # ---- notification
    J("()=>{ST.tab='you';ST.page='notif';render()}"); g.wait_for_timeout(200)
    ok(f'[{L}] notifications: the club moved the game to Court 2, same price', J("/(moved to Court 2|2번 코트.*바뀌었어요)/.test(document.querySelector('#view').innerText)"))
    ok(f'[{L}] price: Court 3 for 90 min after 17:00 adds ₩6,000', J("priceFor(S.pickle, svcOf('pickle','court'), 1080, 90, {court:'c3'})") == 420000 + 60000)
    ok(f'[{L}] no page errors / 4xx', not g.E and not g.NF, (g.E, g.NF)); g.context.close()
  b.close()
print(f'\n{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
