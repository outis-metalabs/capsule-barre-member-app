"""Native booking sheet (PO 2026-10-15): every booking entry point opens the sheet (never a chat jump), the steps complete
(service -> date/time -> review -> success) and the booking appears in My bookings. EN/VI/KO, 44px, AA, crisis. Usage: booking_sheet.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/booking-sheet'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
A11Y = r"""()=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};
 const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c}return 'rgb(255,255,255)'};
 const els=[...document.querySelectorAll('.sheet button,.sheet p,.sheet dd,.sheet dt,.sheet .opt')].filter(e=>e.offsetParent&&e.innerText.trim()&&!e.closest('.storebar'));
 const bad=els.map(e=>{const a=lum(getComputedStyle(e).color),b=lum(bg(e));return [e.innerText.slice(0,20),+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)]}).filter(x=>x[1]<4.5);
 const small=[...document.querySelectorAll('.sheet button')].filter(e=>e.offsetParent&&!e.disabled).map(e=>[e.innerText.slice(0,15),e.getBoundingClientRect().height,e.getBoundingClientRect().width]).filter(x=>x[1]<43.5||x[2]<43.5);return {bad,small}}"""
with sync_playwright() as p:
  b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844})
  def page(lang='en', h=''):
    g = ctx.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.E = E
    g.goto(U); g.evaluate('localStorage.clear()'); g.goto(U + h); g.wait_for_timeout(250); g.evaluate(f"()=>{{setLang('{lang}');render()}}"); return g
  J = lambda g, js: g.evaluate(js)
  def shot(g, n):
    if n: J(g, "()=>{document.activeElement&&document.activeElement.blur();const s=document.querySelector('.sheet');if(s)s.scrollTop=0}"); g.wait_for_timeout(450); g.screenshot(path=f'{SH}/{n}.png')
  def finish(g, name, lang='en', shots=None, move=False):
    """from any sheet step: (step1) -> step2 -> (join) -> review -> success -> My bookings"""
    ok(f'[{lang}] {name}: no chat jump, sheet open', J(g, "ST.tab")!='cici' and g.locator('.sheet').count()==1, [J(g, "ST.tab"), g.locator('.sheet').count()])
    if g.locator('#bk-svcs').count():
      ok(f'[{lang}] {name}: step 1 (service/class)', 'Step 1 of 3' in g.inner_text('#bk-step') if lang=='en' else g.locator('#bk-step').count()==1)
      a = J(g, A11Y); ok(f'[{lang}] {name}: step 1 AA + 44px', not a['bad'] and not a['small'], a); shot(g, shots and shots+'-1-service')
      g.click('#bk-svcs .svc >> nth=0'); g.wait_for_timeout(100)
    if g.locator('#jb-go').count(): g.click('#jb-go'); g.wait_for_timeout(150)
    if g.locator('.sheet .slot').count():
      ok(f'[{lang}] {name}: step 2 day chips + real slots', g.locator('.sheet [data-k=d]').count()==7 and g.locator('.sheet .slot:not([disabled])').count()>0 and (move or g.locator('#bk-step').count()==1))
      a = J(g, A11Y); ok(f'[{lang}] {name}: step 2 AA + 44px', not a['bad'] and not a['small'], a); shot(g, shots and shots+'-2-time')
      g.click('.sheet .slot:not([disabled]) >> nth=0'); g.wait_for_timeout(100)
    ok(f'[{lang}] {name}: step 3 review (price, policy{"" if move else ", earn"})', g.locator('.sheet [data-act=dobook]').count()==1 and g.locator('.sheet .tot').count()==1 and (move or (g.locator('#rv-earn').count()==1 and g.locator('.sheet .rv-pol').count()==1)))
    if not move: a = J(g, A11Y); ok(f'[{lang}] {name}: review AA + 44px', not a['bad'] and not a['small'], a)
    shot(g, shots and shots+'-3-review')
    n0 = J(g, "B.filter(b=>b.status==='confirmed').length"); g.click('.sheet [data-act=dobook]'); g.wait_for_timeout(300)
    nb = J(g, "B.at(-1)")
    ok(f'[{lang}] {name}: booked via the shared engine', nb['status']=='confirmed' and (move or J(g, "B.filter(b=>b.status==='confirmed').length")==n0+1))
    if move: return nb
    ok(f'[{lang}] {name}: success: Cici cheer + summary + earn + View in My bookings', g.locator('#bk-confirm .pic').count()==1 and g.locator('#bk-earn').count()==1 and g.locator('#bk-view').count()==1 and g.locator('[data-act=addcal]').count()==1)
    a = J(g, A11Y); ok(f'[{lang}] {name}: success AA + 44px', not a['bad'] and not a['small'], a); shot(g, shots and shots+'-4-success')
    g.click('#bk-view'); g.wait_for_timeout(250)
    ok(f'[{lang}] {name}: appears in My bookings', J(g, "ST.page")=='bookings' and g.locator(f"#bk-{nb['id']}").count()==1 and J(g, "ST.tab")!='cici')
    ok(f'[{lang}] {name}: no page errors', not g.E, g.E[:2])
    return nb
  # 1 store page "Book here" (joined, multi-class) — the reported bug; full step screenshots EN/KO
  for L in ['en', 'ko', 'vi']:
    g = page(L); J(g, "()=>{ST.store='capsule';render()}"); g.click('#st-book'); finish(g, 'store Book here', L, shots=(f'{L}-store' if L!='vi' else None)); g.close()
  # 2 service row + class slot on store page
  g = page(); J(g, "()=>{ST.store='salon';render()}"); g.click('.sv-list [data-act=svc] >> nth=0') if g.locator('.sv-list [data-act=svc]').count() else g.click('[data-act=svc] >> nth=0'); finish(g, 'store service row'); g.close()
  g = page(); J(g, "()=>{ST.store='capsule';render()}"); g.click('[data-act=classpick]:not([disabled]) >> nth=0'); finish(g, 'store class slot'); g.close()
  # 3 unjoined store: Join & book step -> sheet
  g = page(); J(g, "()=>{ST.store='nails';render()}"); g.click('#st-jbook'); finish(g, 'unjoined store Join & book'); g.close()
  # 4 Discover next-slot chip (joined + unjoined) and card -> store -> Book
  for sid in ['capsule', 'yoga']:
    g = page(); J(g, "()=>{setTab('discover');render()}"); g.click(f'[data-act=dslot][data-v={sid}]'); finish(g, f'Discover next-slot chip ({sid})'); g.close()
  g = page(); J(g, "()=>{setTab('discover');render()}"); g.click('[data-act=store][data-v=spa] >> nth=0'); g.wait_for_timeout(150); g.click('#st-book'); finish(g, 'Discover card -> store Book'); g.close()
  # 5 Home: Next class empty -> Book, Book again chip
  g = page(); J(g, "()=>{B.forEach(x=>x.status='cancelled');setTab('home');render()}"); g.click('#home-next #bk-start'); ok('Home empty Next class: place step', g.locator('#bk-places .svc').count()>=3); g.click('#bk-places [data-s=spa]'); finish(g, 'Home Next class (empty) Book'); g.close()
  # 6 My bookings: reschedule (move, one booking id swap) and past Book again
  g = page(); J(g, "openBookings('up')"); bid = J(g, "(()=>{const b=B.find(x=>x.status==='confirmed'&&!bkStarted(x)&&bkFree(x));return b&&b.id})()")
  J(g, f"()=>{{const b=B.find(x=>x.id==={bid});const e=document.createElement('button');e.dataset.act='resched';e.dataset.id={bid};document.body.appendChild(e);e.click();e.remove()}}") if g.locator(f'#bk-{bid} [data-act=resched]').count()==0 else g.click(f'#bk-{bid} [data-act=resched]')
  nb = finish(g, 'My bookings reschedule', move=True); ok('reschedule: old moved, new confirmed in My bookings', J(g, f"B.find(x=>x.id==={bid}).status")=='moved' and nb['id']!=bid); g.close()
  g = page(); J(g, "openBookings('past')")
  if g.locator('[data-act=pastagain]').count(): g.click('[data-act=pastagain] >> nth=0'); finish(g, 'My bookings past Book again')
  else: ok('past Book again button present', False)
  g.close()
  # 7 wallet Book, notifications Book, deep link
  g = page(); J(g, "()=>{setTab('you');ST.page='wallet';render()}"); g.click('[data-act=wallet] >> nth=0'); g.wait_for_timeout(150)
  if g.locator('[data-act=walletbook]').count(): g.click('[data-act=walletbook] >> nth=0'); finish(g, 'Wallet Book')
  else: ok('wallet book present', False)
  g.close()
  g = page(); J(g, "()=>{ST.page='notif';render()}"); ok('notifications: store notices have a Book link', g.locator('.nbook').count()>0); g.click('.nbook >> nth=0'); finish(g, 'Notification Book'); g.close()
  g = page(h='#book?store=salon'); g.wait_for_timeout(300); finish(g, 'Deep link #book?store=salon'); g.close()
  # 8 sheet extras: back from review -> step 2; Ask Cici link opens chat with store context
  g = page(); J(g, "()=>{ST.store='salon';render()}"); g.click('#st-book'); g.click('#bk-svcs .svc >> nth=0'); g.click('.sheet .slot:not([disabled]) >> nth=0'); g.click('.sheet [data-act=bkback]')
  ok('review Back returns to step 2, nothing booked', g.locator('.sheet .slot').count()>0); g.click('#bk-ask'); g.wait_for_timeout(200)
  ok('Ask Cici: opens chat scoped to the store', J(g, "ST.tab")=='cici' and J(g, "CH.cici.scope")=='salon' and g.locator('.sheet').count()==0); g.close()
  # 9 pass reuse on review
  g = page(); sid = J(g, "Object.keys(WALLET).find(k=>S[k].joined&&S[k].kind!=='rental'&&WALLET[k].some(p=>p.left>0&&!p.credit))")
  J(g, f"bookSheet('{sid}',{{svc:(WALLET['{sid}'].find(p=>p.left>0&&!p.credit).svc)||S['{sid}'].svcs[0].id}})"); g.click('.sheet .slot:not([disabled]) >> nth=0')
  ok(f'review reuses passFor ({sid})', g.locator('.sheet .rv-pass').count()==1, g.inner_text('.sheet')[:200]); g.close()
  # 10 typing a booking in chat still works
  g = page(); J(g, "()=>{setTab('cici');render()}"); J(g, "chatSend('cici','book a haircut tomorrow at 3pm')"); g.wait_for_timeout(300)
  ok('typed chat booking still drafts a confirm card', J(g, "CH.cici.msgs.some(m=>m.confirm)")); g.close()
  # 11 crisis: no booking sheet
  g = page(); J(g, "chatSend('cici','I want to kill myself')"); g.wait_for_timeout(200); J(g, "()=>{closeSheet();bookSheet('salon')}")
  ok('crisis turn: no booking sheet opens', J(g, "gated()") and g.locator('.sheet [data-act=bkpick], .sheet .slot').count()==0); g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
