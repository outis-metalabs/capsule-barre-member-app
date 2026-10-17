"""platform-app-v3.html — stranger-PO review fixes (2026-10-17, /tmp/trial/po/PO-REVIEW.md): membership on Home + first run, undo holds the slot,
mission honesty (card sync, undo revokes credit, timer gate, no silent sheet reopen), one currency (no stat bars, no won shop, hidden audit rows),
pass purchase + deposit payment with a receipt, join & book through the picker, Korean wellbeing, question exits slot-filling, Discover reasons to choose,
success sheet with a real .ics, one Manage per booking card, policy once above slot lists, notification deep link + collapsed held list + one store table,
tap-to-call in the urgent reply, chat move keeps the pass, You hub rows, paddles ≤ players.
Usage: v3_po_fixes.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/po'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:360]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='?lang=ko', w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(700); return g
  # ---- first run + Home membership line
  g = page('?lang=ko&intro=1'); J = g.evaluate
  ok('intro: two-screen first run names the product (Cici · one membership · N places)', J("!!document.querySelector('#intro') && /하나의 멤버십/.test(document.querySelector('#intro').innerText) && /개 매장/.test(document.querySelector('#intro').innerText)"))
  g.screenshot(path=f'{SH}/intro-1.png'); g.click('#intro-next'); g.wait_for_timeout(200)
  ok('intro: second screen introduces Mochi, button becomes 시작하기', J("/모찌/.test(document.querySelector('.ipanel.on').innerText) && document.querySelector('#intro-next').innerText==='시작하기'"))
  g.screenshot(path=f'{SH}/intro-2.png'); g.click('#intro-next'); g.wait_for_timeout(200)
  ok('intro: dismissed and remembered', not J("!!document.querySelector('#intro')") and J("localStorage.getItem('cici.intro')") == '1')
  ok('Home card: membership line (N개 매장 · 하나의 멤버십 · pass left) opens the wallet', J("/^\\d+개 매장 · .+ \\d+회 남음$/.test(document.querySelector('#hb-mem').innerText)") and J("(()=>{document.querySelector('#hb-mem').click();return ST.page==='wallet'})()"))
  J("()=>{ST.page=null;ST.tab='home';render()}"); g.wait_for_timeout(300)
  ok('header carries the brand on Home', J("/^Cici · /.test(document.querySelector('#top .brand .t').innerText)"), J("document.querySelector('#top .brand .t').innerText"))
  ok('streak line is tappable (opens points)', J("(()=>{const e=document.querySelector('#cat-line');return !!e&&e.tagName==='BUTTON'})()"))
  ok('missions head reads 오늘의 미션 N/3 (no trailing 완료)', not J("/미션 \\d\\/3 완료/.test(dmCard())"))
  g.screenshot(path=f'{SH}/home-ko.png')
  # ---- undo holds the slot
  r = J("(()=>{const out={};for(const k of ['salon','pickle','capsule']){const b=B.find(b=>b.store===k&&b.status==='confirmed'&&!b.pv);cancelB(b,false);out[k]=uncancelB(b).ok}return out})()")
  ok('undo after cancel restores hair, court and class bookings', r == {'salon': True, 'pickle': True, 'capsule': True}, r)
  # ---- mission honesty
  J("()=>{P2S.dm=null;render()}"); g.wait_for_timeout(300)
  J("()=>{const z=nextFree('salon');openConfirm(Object.assign({},z,{rids:z.rids,len:z.len}))}"); g.wait_for_timeout(300); J("()=>document.querySelector('.sheet [data-act=dobook]')?.click()"); g.wait_for_timeout(500)
  ok('booking from the mission updates the Home card at once (1/3, badge)', J("/1\\/3/.test(document.querySelector('#hb-bubble').innerText)") and J("dmDay().done.book===true"), J("document.querySelector('#hb-bubble').innerText"))
  ok('success sheet: one primary 완료, a real .ics calendar link, maps + view as links', J("!!document.querySelector('#bk-confirm') && !!document.querySelector('#bk-done') && /^data:text\\/calendar/.test(document.querySelector('#bk-cal').getAttribute('href')) && document.querySelector('#bk-cal').hasAttribute('download') && document.querySelectorAll('#bk-done-acts .btn.full').length===1 && !!document.querySelector('#bk-links .bkmap')"))
  g.screenshot(path=f'{SH}/success-ko.png')
  J("()=>document.querySelector('[data-act=succundo]').click()"); g.wait_for_timeout(400)
  ok('undoing the booking takes the mission credit back (0/3)', J("!dmDay().done.book") and J("/0\\/3/.test(document.querySelector('#hb-bubble').innerText)"), J("[dmDay().done, document.querySelector('#hb-bubble').innerText]"))
  J("()=>{ST.stretchMin=60;stretchSheet()}"); g.wait_for_timeout(1500)
  ok('stretch: Finish is hidden for the first minute (no one-tap reward)', J("(()=>{const f=document.querySelector('#stretch-chip [data-act=stretchdone], .sheet [data-act=stretchdone]');return !!f&&f.hidden})()"))
  J("()=>{ST.stretchMin=0}"); J("()=>stretchStop()"); g.wait_for_timeout(300)
  ok('showcase/demo keeps Finish available at once', J("(()=>{ST.stretchMin=0;return stretchMin()===0})()"))
  J("()=>{P2S.dm=null;ST.sheetReturn=true;ST.catMis=null;catSheetReturn()}"); g.wait_for_timeout(200)
  ok('after a mission the sheet does not reopen by itself; a next-mission chip appears instead', not J("!!document.querySelector('.sheet')") and J("!!document.querySelector('#dm-next')"))
  ok('streak card says what counts', J("()=>{ST.tab='you';ST.page='points';render();return /방문 확인이나 미션 완료/.test(document.querySelector('#pv-sk-how').innerText)}"))
  # ---- one currency
  J("()=>{ST.page='growth';render()}"); g.wait_for_timeout(300)
  ok('growth page: no stat bars, photoreal Cici in the room, no points line in the room', not J("!!document.querySelector('#g-bars')") and J("!!document.querySelector('#p2-room img.p2real')") and not J("!!document.querySelector('#p2-pts')"))
  g.click('#p2-room [data-act=p2shop]'); g.wait_for_timeout(300)
  ok('item shop: partner items only, nothing priced in won', J("[...document.querySelectorAll('.sheet .p2sk')].every(e=>!/₩|\\d\\s*₫/.test(e.innerText))") and J("document.querySelectorAll('.sheet .p2sk').length") >= 1, J("[...document.querySelectorAll('.sheet .p2sk')].map(e=>e.innerText.replace(/\\n/g,' '))"))
  J("closeSheet()"); g.click('#p2-room [data-act=p2deco]'); g.wait_for_timeout(300)
  ok('decorate: no buy-with-points list', not J("!!document.querySelector('.sheet [data-act=p2buypts]')")); J("closeSheet()")
  J("()=>{ST.page='points';render();histSheet()}"); g.wait_for_timeout(300)
  ok('points history: no "not carried over" audit row; pre-app points labelled plainly', not J("/이월되지 않음/.test(document.querySelector('#pv-hist').innerText)") and J("/앱 이전 활동 포인트/.test(document.querySelector('#pv-hist').innerText)")); J("closeSheet()")
  J("()=>{__plat.pv.setFlag(true,PV.now());ST.page='vouchers';ST.vseg=null;render()}"); g.wait_for_timeout(300)
  ok('vouchers open on "get more" when nothing is claimed; copy says points become vouchers', J("document.querySelector('.seg [aria-selected=true]').innerText") == '더 받기' and J("/이용권 구매와 카운터 할인에 쓸 수 있어요/.test(pvT('noCash'))"))
  J("()=>{__plat.pv.setFlag(false,PV.now())}")
  # ---- money
  J("()=>{ST.page='wallet';render()}"); g.wait_for_timeout(200); g.click('#wallet-buy'); g.wait_for_timeout(300)
  ok('wallet: Buy a pass lists products with per-visit price', J("document.querySelectorAll('#pass-shop .svc').length") >= 3 and J("/회당/.test(document.querySelector('#pass-shop').innerText)"))
  left0 = J("WALLET.capsule.find(p=>p.id==='p10').left"); g.click('#pass-shop [data-v=p5]'); g.wait_for_timeout(300)
  ok('checkout: amount + KakaoPay / Toss / card', J("!!document.querySelector('#pay-methods') && document.querySelectorAll('#pay-methods .svc').length===3"))
  g.screenshot(path=f'{SH}/pay-ko.png'); g.click('#pay-methods [data-v=kakao]'); g.wait_for_timeout(400)
  ok('receipt sheet, pass added to the wallet', J("!!document.querySelector('#receipt') && /카카오페이/.test(document.querySelector('#receipt').innerText)") and J("!!WALLET.capsule.find(p=>p.id==='p5'&&p.left===5)"))
  g.screenshot(path=f'{SH}/receipt-ko.png'); J("closeSheet()")
  J("()=>{const z=nextFree('skin');openConfirm(Object.assign({},z,{rids:z.rids,len:z.len}))}"); g.wait_for_timeout(300); J("()=>document.querySelector('.sheet [data-act=dobook]')?.click()"); g.wait_for_timeout(400)
  ok('deposit store: the book button opens the payment step first', J("!!document.querySelector('#pay-methods')"))
  n0 = J("B.length"); g.click('#pay-methods [data-v=toss]'); g.wait_for_timeout(500)
  ok('… paying books it and the success sheet names the method', J("B.length") == n0 + 1 and J("/Toss/.test(document.querySelector('#bk-confirm').innerText)"), J("document.querySelector('#bk-confirm')?.innerText.slice(0,200)")); J("closeSheet()")
  # ---- join & book through the picker
  J("()=>{S.moc.joined=false;ST.page=null;ST.tab='discover';ST.store='moc';render()}"); g.wait_for_timeout(300); g.click('#st-jbook'); g.wait_for_timeout(300)
  ok('join & book opens the time picker (member picks the slot)', J("!!document.querySelector('.sheet #bk-slots')"))
  J("()=>{const s=[...document.querySelectorAll('.sheet .slot')].find(s=>!s.disabled);s.click()}"); g.wait_for_timeout(300)
  ok('… the confirm says booking also joins the place', J("/내 매장에 추가/.test(document.querySelector('.sheet').innerText)"))
  J("()=>document.querySelector('.sheet [data-act=dobook]').click()"); g.wait_for_timeout(400)
  ok('… booking joins the place', J("S.moc.joined===true")); J("closeSheet()")
  # ---- bookings list + slot list
  J("()=>{ST.store=null;ST.tab='you';ST.page='bookings';ST.bkSeg='up';render()}"); g.wait_for_timeout(200)
  ok('My bookings: exactly one 관리 button per card, no KST', J("[...document.querySelectorAll('#view .bkrow .acts')].every(a=>a.querySelectorAll('button').length===1&&/관리/.test(a.innerText))") and not J("/KST/.test(document.querySelector('#view').innerText)"))
  g.screenshot(path=f'{SH}/bookings-ko.png')
  J("()=>openBook('salon','cut')"); g.wait_for_timeout(300)
  ok('slot list: policy once above the list; rows carry no deadline text unless the free window passed', J("!!document.querySelector('.sheet #bk-pol')") and not J("[...document.querySelectorAll('.sheet .slot')].some(s=>/무료 취소 기한 (오늘|내일|\\d)/.test(s.innerText))"))
  J("closeSheet()"); J("()=>openBook('pickle','court',{party:2,paddles:4})"); g.wait_for_timeout(300)
  ok('paddles never exceed players (2 players → no 4-paddle chip, selection clamped)', not J("!!document.querySelector('.sheet [data-k=paddles][data-v=\"4\"]')") and J("BS.paddles") <= 2)
  J("closeSheet()")
  # ---- notifications
  J("()=>{ST.page='notif';ST.seenN=true;render()}"); g.wait_for_timeout(200)
  ok('nudge CTA deep-links to the promised 18:00 slot', J("(()=>{const b=document.querySelector('#view [data-act=classpick][data-m=\"1080\"]');return !!b&&/18:00/.test(b.innerText)})()"))
  ok('held-by-rules list is collapsed behind "why"', J("(()=>{const d=document.querySelector('#n-held');return !!d&&!d.open})()"))
  J("()=>{ST.page='nset';render()}"); g.wait_for_timeout(200)
  ok('notification settings: one store table with alerts + offers switches', J("!!document.querySelector('#n-places')") and J("document.querySelectorAll('#n-places [data-act=nstore]').length") == J("document.querySelectorAll('#n-places [data-act=noptin]').length") and J("document.querySelectorAll('#view h2').length") <= 3)
  g.screenshot(path=f'{SH}/nset-ko.png')
  # ---- You hub
  J("()=>{ST.page=null;render()}"); g.wait_for_timeout(200)
  ok('You hub: next booking + pass rows, 2-column tiles, gear icon', J("!!document.querySelector('#you-next .up, #you-next .svc') && !!document.querySelector('#you-next .wrow')") and J("getComputedStyle(document.querySelector('.ytiles')).gridTemplateColumns.split(' ').length") == 2)
  g.screenshot(path=f'{SH}/you-ko.png')
  # ---- Discover
  J("()=>{ST.tab='discover';render()}"); g.wait_for_timeout(300)
  ok('Discover cards show rating (count) and a from-price; the paid card is not first', J("[...document.querySelectorAll('#dres > .dcard .dmeta')].every(m=>/★ \\d\\.\\d \\(\\d+\\)/.test(m.innerText)&&/₩/.test(m.innerText))") and not J("!!document.querySelector('#dres > .dcard:first-child .splabel')"), J("[...document.querySelectorAll('#dres > .dcard .dmeta')].map(m=>m.innerText)"))
  g.screenshot(path=f'{SH}/discover-ko.png')
  # ---- Cici
  J("()=>{ST.tab='cici';render()}"); g.wait_for_timeout(200)
  ok('chat title row sticks under the app header with the Need-help icon; no help link in the composer', J("(()=>{const h=document.querySelector('#cici-hd');return !!h&&getComputedStyle(h).position==='sticky'&&!!h.querySelector('.helplink')&&!document.querySelector('.dock .helplink')})()"))
  ok('chat composer is fixed at the bottom, flush with the tab bar', J("(()=>{const d=document.querySelector('#view.cici-v .dock'),r=d.getBoundingClientRect(),t=document.querySelector('nav.tabs').getBoundingClientRect();return getComputedStyle(d).position==='fixed'&&Math.abs(t.top-r.bottom)<2})()"), J("(()=>{const d=document.querySelector('#view.cici-v .dock').getBoundingClientRect(),t=document.querySelector('nav.tabs').getBoundingClientRect();return [d.bottom,t.top]})()"))
  g.fill('#in-cici', '오늘 너무 피곤해'); g.press('#in-cici', 'Enter'); g.wait_for_timeout(800)
  ok('KO "오늘 너무 피곤해" gets the warm rest reply with stretch / spa / listen chips, not a medical deflection', J("/쉬는 것도/.test(document.querySelector('#th-cici').innerText) && [...document.querySelectorAll('.mchips .chip')].some(c=>/그냥 들어줘/.test(c.innerText))") and not J("/상의해 주세요/.test(document.querySelector('#th-cici').innerText)"), J("document.querySelector('#th-cici').innerText.slice(-200)"))
  J("()=>{CH.cici.msgs=[];CH.cici.care=false;CH.cici.gate=false;render()}"); g.fill('#in-cici', '바레 갈 때 뭐 준비해야 해?'); g.press('#in-cici', 'Enter'); g.wait_for_timeout(800)
  ok('"바레 갈 때 뭐 준비해야 해?" is answered from the store info', J("(()=>{const m=CH.cici.msgs[CH.cici.msgs.length-1];return !!m.faq})()"), J("document.querySelector('#th-cici').innerText.slice(-200)"))
  J("()=>{CH.cici.msgs=[];render()}"); g.fill('#in-cici', '바레 예약'); g.press('#in-cici', 'Enter'); g.wait_for_timeout(700); g.fill('#in-cici', '내 예약 확인'); g.press('#in-cici', 'Enter'); g.wait_for_timeout(800)
  ok('a new intent exits a half-filled booking ("내 예약 확인" answers with the next booking, not "which place?")', J("(()=>{const m=CH.cici.msgs[CH.cici.msgs.length-1];return !!m.bk})()") and not J("!!CH.cici.ask"), J("[CH.cici.ask, CH.cici.msgs[CH.cici.msgs.length-1].text]"))
  J("()=>{NOWX=600;CH.cici.msgs=[];CH.cici.ask=null;CH.cici.draft=null;render()}"); g.fill('#in-cici', '바레 예약 옮겨줘'); g.press('#in-cici', 'Enter'); g.wait_for_timeout(800)
  J("()=>{const c=[...document.querySelectorAll('.mchips .chip')].find(x=>/내일/.test(x.innerText));if(c)c.click()}"); g.wait_for_timeout(700) # the tomorrow 07:00 pass booking
  J("()=>{const c=[...document.querySelectorAll('.mchips .chip')].find(x=>!/오늘/.test(x.innerText));if(c)c.click()}"); g.wait_for_timeout(700) # a later day, never 오늘 (its slot list depends on the clock)
  J("()=>{const c=document.querySelector('.mchips .chip');if(c)c.click()}"); g.wait_for_timeout(700) # first open time -> move review
  J("()=>{NOWX=null}")
  ok('a move by chat keeps the pass (₩0 · 이용권), never a surprise cash total', J("(()=>{const m=CH.cici.msgs.find(x=>x.confirm&&x.confirm.move);return !!m&&!!m.confirm.usePass})()") and J("/₩0/.test(document.querySelector('#th-cici .mcard .tot')?.innerText||'')"), J("CH.cici.msgs.map(m=>m.text.slice(0,60)).slice(-3)"))
  g.close()
  g = page(); J = g.evaluate; J("()=>{ST.tab='cici';render()}"); g.fill('#in-cici', '누가 다쳤어요'); g.press('#in-cici', 'Enter'); g.wait_for_timeout(800)
  ok('urgent reply has tap-to-call 119 and the store', J("!!document.querySelector('#tel-em') && document.querySelector('#tel-em').getAttribute('href')==='tel:119' && !!document.querySelector('#tel-store')"))
  g.screenshot(path=f'{SH}/urgent-ko.png')
  ok('no page errors / 404s', not g.E and not g.NF, g.E[:2] + g.NF[:2]); g.close()
  g = page('?lang=ko&show=1', 1280, 800); J = g.evaluate
  ok('investor panel states the platform, not one store', J("/하나의 멤버십 · \\d+개 매장/.test(document.querySelector('.showbrand .sb-sub').innerText)") and not J("!!document.querySelector('#intro')"))
  g.close(); b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
