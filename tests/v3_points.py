"""platform-app-v3.html — points programme (docs/points-brainstorm.md, 2026-10-17): redemption on by default, ONE spendable balance shown as
"{n}P · ₩ 상당" everywhere (lifetime hidden, level is progress only), Points tile replaces Cici's style (look picker inside Cici & Mochi),
Wallet balance row first, points toggle on pass checkout (≤30% / ≤₩20,000, never on deposits) with the discount on the receipt, counter code,
Home points pill, check-in / success / store-page copy, chat balance intent, points notifications, expiry clock reset by spend, investor liability line.
Usage: v3_points.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/points'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:360]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='?lang=ko', w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(700); return g
  g = page(); J = g.evaluate
  ok('P1 redemption is on by default (PV.flag), ?realRewards=0 still turns it off', J("PV.flag===true"))
  bal0 = J("bal(ME)"); life0 = J("life(ME)")
  ok('P1 balance is the spendable number, not the inflated lifetime (migration grant excluded)', bal0 < life0 and bal0 > 0, (bal0, life0))
  # ---- Home pill
  ok('P2 Home card: points pill "{n}P · ₩ 상당" beside the membership pill, opens the Points page', J("(()=>{const e=document.querySelector('#hb-pts');return !!e&&/^\\d[\\d,]*P · ₩/.test(e.innerText)&&/개 매장/.test(document.querySelector('#hb-mem').innerText)})()") and J("(()=>{document.querySelector('#hb-pts').click();return ST.tab==='you'&&ST.page==='points'})()"))
  g.wait_for_timeout(300); g.screenshot(path=f'{SH}/points-ko.png')
  # ---- Points page
  ok('P3 Points page: ONE balance (P + ₩ 상당), no lifetime number, legal line, level as progress with a note', J("!!document.querySelector('#pv-bal') && /P$/.test(document.querySelector('#pv-bal').innerText) && /상당/.test(document.querySelector('#pv-worth').innerText) && !document.querySelector('#pv-earned') && /현금 환급 불가/.test(document.querySelector('#pv-legal').innerText) && /레벨 \\d까지 [\\d,]+P|아이콘/.test(document.querySelector('#pv-level+div').innerText) && !!document.querySelector('#pv-lvlnote')"))
  ok('P3 Points page: how to earn + how to use (pass ≤30%/₩20,000, counter code, never the deposit) + vouchers link', J("!!document.querySelector('#pv-how') && /예약금에는 포인트를 쓸 수 없어요/.test(document.querySelector('#pv-use').innerText) && /30%/.test(document.querySelector('#pv-use').innerText) && /₩20,000/.test(document.querySelector('#pv-use').innerText) && !!document.querySelector('#pv-vouchers')"))
  ok('P3 Points page: two burn actions (이용권에 쓰기 / 카운터에서 쓰기) and the streak card after them', J("(()=>{const a=document.querySelector('#pv-usepass'),c=document.querySelector('#pv-usecounter'),s=document.querySelector('#pv-streak');return !!a&&!!c&&!!s&&a.compareDocumentPosition(s)&Node.DOCUMENT_POSITION_FOLLOWING})()"))
  ok('P3 no "곧 나와요" placeholder anywhere on You / Points / Wallet', not J("(()=>{for(const p of [null,'points','wallet','vouchers']){ST.tab='you';ST.page=p;render();if(/곧 나와요/.test(document.querySelector('#view').innerText))return true}return false})()"))
  # ---- counter code
  J("()=>{ST.tab='you';ST.page='points';render()}"); g.click('#pv-usecounter'); g.wait_for_timeout(200)
  ok('P4 counter: code sheet with P-code, QR, cap in ₩, legal line, demo apply button', J("(()=>{const s=document.querySelector('.sheet');return !!s&&/^P\\d{6}$/.test(document.querySelector('#pts-code').innerText)&&!!s.querySelector('svg.qr')&&/현금 환급 불가/.test(s.innerText)&&!!document.querySelector('#pts-demo')})()"))
  g.screenshot(path=f'{SH}/counter-ko.png'); b1 = J("bal(ME)"); g.click('#pts-demo'); g.wait_for_timeout(300); b2 = J("bal(ME)")
  ok('P4 counter demo: store applies ₩ off, balance drops by off/₩10, ledger row spend_counter (life 0), expiry clock reset', b2 < b1 and J("(()=>{const r=ME.ledger[ME.ledger.length-1];return r.reason==='spend_counter'&&r.life===0&&r.delta<0&&ME.lastSpend>0})()") and J("/할인 적용 · −\\d+P/.test(document.querySelector('#pts-msg').innerText)"), (b1, b2))
  ok('P4 level never drops on spend', J("lvlOf(ME)") == J("(()=>{let n=1;LVL.forEach((x,i)=>{if(life(ME)>=x)n=i+1});return n})()"))
  J("closeSheet()")
  J("()=>{row(ME,{store:'capsule',reason:'visit',delta:500,life:500,actor:'ops:test'});render()}") # the counter demo drained the sample balance; top up so the checkout toggle has something to offer
  # ---- You hub
  J("()=>{ST.tab='you';ST.page=null;render()}"); g.wait_for_timeout(200)
  tiles = J("[...document.querySelectorAll('.ytile')].map(b=>b.dataset.v)")
  ok('P5 You tiles: Wallet · My bookings · Points · Cici & Mochi (no Cici\'s style, no vouchers tile)', tiles == ['wallet', 'bookings', 'points', 'growth'], tiles)
  ok('P5 You: Points tile sub and profile line read "{n}P · ₩ 상당"', J("/^\\d[\\d,]*P · ₩[\\d,]+ 상당$/.test(document.querySelector('.ytile[data-v=points] .sub').innerText) && /P · ₩[\\d,]+ 상당 · \\d+일 연속/.test(document.querySelector('#you-pts').innerText)"), J("document.querySelector('#you-pts').innerText"))
  g.screenshot(path=f'{SH}/you-ko.png')
  J("()=>{ST.page='growth';render()}"); g.wait_for_timeout(200)
  ok('P5 Cici & Mochi page hosts the look picker row (opens Cici 스타일)', J("(()=>{const e=document.querySelector('#g-look');if(!e)return false;e.click();return ST.page==='look'})()"))
  g.screenshot(path=f'{SH}/look-ko.png')
  # ---- Wallet
  J("()=>{ST.page='wallet';render()}"); g.wait_for_timeout(200)
  ok('P6 Wallet: points row is the FIRST row (balance, ₩ 상당, 쓰기) and opens the Points page', J("(()=>{const l=document.querySelector('#wallet-list');const f=l.querySelector('.svc');return !!f&&f.id==='wallet-pts'&&/내 포인트 \\d[\\d,]*P/.test(f.innerText)&&/상당/.test(f.innerText)&&/쓰기/.test(f.innerText)})()") and J("(()=>{document.querySelector('#wallet-pts').click();return ST.page==='points'})()"))
  g.screenshot(path=f'{SH}/wallet-ko.png')
  # ---- pass checkout with the toggle
  J("()=>{ST.page='wallet';render()}"); g.click('#wallet-buy'); g.wait_for_timeout(200); g.click('#pass-shop [data-act=paybuy]'); g.wait_for_timeout(200)
  price = J("PAYX.amount"); bal1 = J("bal(ME)")
  ok('P7 pass checkout: points toggle present with the cap note; deposit note absent', J("!!document.querySelector('#pay-pts') && /P 사용 · ₩/.test(document.querySelector('#pay-pts').innerText) && /최대 30%/.test(document.querySelector('#pay-pts').innerText) && !document.querySelector('#pay-nopts')"))
  due0 = J("document.querySelector('#pay-due').innerText"); g.click('#pay-pts input'); g.wait_for_timeout(200); due1 = J("document.querySelector('#pay-due').innerText")
  off = J("ptsMaxOff(bal(ME), PAYX.amount)")
  ok('P7 toggle on: amount due drops by min(balance×₩10, 30%, ₩20,000); "{p}P 사용 · ₩ 할인" shown', due0 != due1 and J("!!document.querySelector('#pay-off')") and off <= min(bal1 * 100, price * 0.3, 200000) and off > 0, (due0, due1, off))
  g.screenshot(path=f'{SH}/checkout-toggle-ko.png'); g.click('[data-act=paygo][data-v=kakao]'); g.wait_for_timeout(300)
  ok('P7 receipt: list price, 포인트 할인 −₩, amount = price − off; ledger spend_pass; balance reduced; pass added', J("(()=>{const r=document.querySelector('#receipt');return !!r&&!!r.querySelector('#rc-off')&&/포인트 할인/.test(r.innerText)})()") and J("ME.ledger.some(r=>r.reason==='spend_pass'&&r.life===0)") and J("bal(ME)") == bal1 - off // 100 and J("document.querySelector('#rc-amount').innerText") == J(f"vnd({price - off})"), J("document.querySelector('#receipt').innerText"))
  g.screenshot(path=f'{SH}/receipt-ko.png'); J("closeSheet()")
  # ---- deposit checkout: no toggle
  J("()=>{ST.tab='home';ST.page=null;render()}"); J("()=>{PEND={store:'salon',svc:S.salon.svcs[0].id,d:todayIdx()+2,m:900,len:60};}")
  J("()=>{paySheet({ amount: S.salon.policy.dep, dep: true, ptsOk: false, title: '예약금 결제', label: '예약금 · ' + S.salon.name, quietReceipt: true, onDone: () => {} })}"); g.wait_for_timeout(200)
  ok('P8 deposit checkout: no points toggle, says 예약금에는 포인트를 쓸 수 없어요', not J("!!document.querySelector('#pay-pts')") and J("/예약금에는 포인트를 쓸 수 없어요/.test(document.querySelector('#pay-nopts').innerText)"))
  g.screenshot(path=f'{SH}/deposit-ko.png'); J("()=>{PAYX=null;closeSheet()}")
  # ---- check-in + success + store page copy
  J("()=>{ST.tab='home';ST.page=null;render()}")
  J("()=>{let b=upcoming().find(x=>x.d===todayIdx());if(!b){b=upcoming()[0];b.d=todayIdx();render()}checkin(b)}"); g.wait_for_timeout(200)
  ok('P9 check-in sheet says 체크인하면 약 NP 적립', J("/체크인하면 약 \\d+P 적립/.test(document.querySelector('#ci-earn').innerText)"))
  b3 = J("bal(ME)"); g.click('[data-act=attend]'); g.wait_for_timeout(400)
  ok('P9 check-in toast: 방문 확인! +NP 들어왔어요 · 이제 NP예요 (balance grew)', J("/방문 확인! \\+\\d+P 들어왔어요 · 이제 [\\d,]+P예요/.test(document.querySelector('#toast').innerText)") and J("bal(ME)") > b3, J("document.querySelector('#toast').innerText"))
  J("()=>{ST.store='capsule';ST.page=null;render()}"); g.wait_for_timeout(200)
  ok('P9 store page (joined): 방문하면 약 NP 적립 · 포인트 할인 가능 under the open line', J("/방문하면 약 \\d+P 적립 · 포인트 할인 가능/.test(document.querySelector('#st-pts').innerText)"))
  g.screenshot(path=f'{SH}/store-ko.png')
  J("()=>{ST.store=null;ST.tab='home';render()}"); J("()=>success(upcoming()[0], ()=>{})"); g.wait_for_timeout(200)
  ok('P9 success sheet: earn line + "다음 이용권에 ₩ 할인으로 쓸 수 있어요"', J("/방문 확인 시 약 \\d+P/.test(document.querySelector('#bk-earn').innerText) && /다음 이용권 ₩[\\d,]+ 할인/.test(document.querySelector('#bk-earn').innerText)"), J("document.querySelector('#bk-earn').innerText"))
  g.screenshot(path=f'{SH}/success-ko.png'); J("closeSheet()")
  # ---- chat
  J("()=>{ST.tab='cici';ST.page=null;render()}"); g.wait_for_timeout(200)
  for q in ['포인트 얼마 있어?', '포인트로 뭐 할 수 있어?', 'how many points do I have']:
    J(f"()=>chatSend('cici', {q!r})"); g.wait_for_timeout(150)
    last = J("CH.cici.msgs[CH.cici.msgs.length-1]")
    ok(f'P10 chat "{q}": balance answer with ₩ 상당, burn surfaces, next earn; chips 포인트 쓰기 + 이용권 구매', last['who'] == 'n' and re.search(r'\d[\d,]*P', last['text']) and ('상당' in last['text'] or 'worth' in last['text']) and [c['label'] for c in last.get('chips', [])][:2] in (['포인트 쓰기', '이용권 구매'], ['Use points', 'Buy a pass']), last['text'])
  ok('P10 chat: 포인트 쓰기 chip opens the Points page', J("(()=>{const m=CH.cici.msgs[CH.cici.msgs.length-1];chatChip('cici', CH.cici.msgs.length-1, 0);return ST.tab==='you'&&ST.page==='points'})()"))
  J("()=>{ST.tab='cici';ST.page=null;render()}"); J("()=>chatSend('cici', '가격 얼마야?')"); g.wait_for_timeout(150)
  ok('P10 chat: a plain price question still goes to prices (which place?)', J("/어느 매장 가격|Which place's prices/.test(CH.cici.msgs[CH.cici.msgs.length-1].text)"))
  g.screenshot(path=f'{SH}/chat-ko.png')
  # ---- notifications
  J("()=>{ST.tab='you';ST.page='notif';render()}"); g.wait_for_timeout(200)
  tx = J("document.querySelector('#view').innerText")
  ok('P11 notifications: earn receipt (방문 확인! +50P 들어왔어요 · 이제 NP예요) and expiry nudge (안 쓰면 … 사라져요) with a 포인트 link; type toggle exists', re.search(r'방문 확인! \+50P 들어왔어요 · 이제 [\d,]+P예요', tx) and re.search(r'안 쓰면 .+에 ₩[\d,]+이 사라져요', tx) and J("[...document.querySelectorAll('.nbook,.link')].some(e=>e.dataset.act==='youpage'&&e.dataset.v==='points')") and J("NTYPES.some(t=>t[0]==='points') && NSET.types.points===true"), tx[:300])
  g.screenshot(path=f'{SH}/notif-ko.png')
  # ---- expiry clock
  ok('P12 expiry: warning window keyed on max(lastVisit, lastSpend, enabledAt); spend resets it', J("(()=>{const m=ME;const t0=Math.max(m.lastVisit||0,m.lastSpend||0,m.enabledAt||0);return !pointsWarn(m, t0 + 300*DAY) && !!pointsWarn(m, t0 + 350*DAY) && !pointsWarn(m, t0 + 400*DAY)})()"))
  # ---- room items: one currency, no sub-ledger warning, never below zero
  ok('P13 room items: buying never takes the balance below zero; no "can\'t be used for vouchers" warning', J("(()=>{const it=P2_ITEMS.find(x=>x.pts&&x.pts>bal(ME)+1);if(!it)return true;const r=p2BuyRoom(it.id);return !r.ok&&r.need>0})()") and not J("(()=>{ST.tab='you';ST.page='growth';render();p2DecoSheet();const it=P2_ITEMS.find(x=>x.pts);if(it){const bt=document.querySelector('[data-act=p2buypts]');if(bt){bt.disabled=false;bt.click()}}const t=(document.querySelector('.sheet')||{innerText:''}).innerText+document.querySelector('#view').innerText;closeSheet();return /바우처에 쓸 수 없어요/.test(t)})()"))
  ok('no page errors / 4xx', not g.E and not g.NF, (g.E, g.NF)); g.context.close()
  # ---- EN + VI copy
  for L, pat in [('en', r'^\d[\d,]*P · worth ₩'), ('vi', r'^\d[\d,]*P · tương đương ₩')]:
    g = page(f'?lang={L}'); J = g.evaluate; J("()=>{ST.tab='you';ST.page=null;render()}")
    ok(f'P14 [{L}] Points tile reads the one-balance line', re.search(pat, J("document.querySelector('.ytile[data-v=points] .sub').innerText")), J("document.querySelector('.ytile[data-v=points] .sub').innerText"))
    g.screenshot(path=f'{SH}/you-{L}.png'); ok(f'[{L}] no page errors', not g.E, g.E); g.context.close()
  # ---- investor mode
  g = page('?lang=ko&show=1', 1280, 900); J = g.evaluate
  ok('P15 investor frame: 1P = ₩10 bullet and a points-liability line', J("/1P = ₩10/.test(document.querySelector('.showbrand').innerText) && /포인트 부채 회원당 ₩[\\d,]+/.test(document.querySelector('#sb-pts').innerText)"), J("document.querySelector('.showbrand').innerText"))
  g.screenshot(path=f'{SH}/investor.png'); ok('[show] no page errors', not g.E, g.E); g.context.close()
  # ---- flag off still works
  g = page('?lang=ko&realRewards=0'); J = g.evaluate
  ok('P16 ?realRewards=0: flag off, no Home pill, Points tile still shows the balance, no burn buttons', J("PV.flag===false && !document.querySelector('#hb-pts')") and J("(()=>{ST.tab='you';ST.page='points';render();return !document.querySelector('#pv-usepass')&&!!document.querySelector('#pv-bal')})()"))
  ok('[off] no page errors', not g.E, g.E); g.context.close()
  b.close()
print(f'\n{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
