"""PR #12 review round 1 regressions (P2-1, P3-1..7). Usage: python3 tests/nari_r1.py [url] [shots]"""
import sys, os, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/nari-tab'
os.makedirs(SH, exist_ok=True); R = {}; E = []
def ok(k, c, d=''): R[k] = [bool(c), d]
with sync_playwright() as p:
  br = p.chromium.launch()
  def page(lang=None, w=390, ctx=None):
    pg = ctx.new_page() if ctx else br.new_page(viewport={'width': w, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U); pg.evaluate("()=>localStorage.clear()"); pg.goto(U); pg.wait_for_timeout(100)
    if lang: pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
    return pg
  J = lambda pg, js, a=None: pg.evaluate(js, a)
  # P2-1 crisis check-in -> I'm fine -> fallback chips visible again
  for lang, q in [('en', 'my sister left a note on the bridge'), ('ko', 'my sister left a note on the bridge')]:
    pg = page(lang); J(pg, "()=>{setTab('nari');render()}")
    J(pg, "q=>__plat.chatSend('nari',q)", q); pg.wait_for_timeout(80)
    chk = J(pg, "()=>!!CH.nari.msgs[CH.nari.msgs.length-1].checkin")
    pg.locator('#th-nari .chip').last.click(); pg.wait_for_timeout(120)
    chips = pg.locator('#th-nari .mchips .chip').all_inner_texts()
    ok(f'P2-1 {lang} fine -> Book/Ask/Someone is hurt chips', chk and len(chips) == 3 and any('Book' in c or '예약' in c for c in chips) and any('hurt' in c or '다쳤' in c for c in chips), chips)
    pg.locator('#th-nari .mchips .chip').last.click(); pg.wait_for_timeout(80)
    ok(f'P2-1 {lang} hurt chip still opens SOS', J(pg, "()=>CH.nari.gate===true && /Which is closest|어느 쪽/.test(CH.nari.msgs.at(-1).text)"))
    pg.close()
  pg = page('en')
  # helpers
  J(pg, """()=>{ window.mk=(o)=>{ const b=Object.assign({id:BID++,status:'confirmed',source:'app',party:0,paddles:0,dep:0,rids:['yuna'],len:50},o); b.pol=Object.assign({},S[b.store].policy); B.push(b); return b.id; }; window.bkx=id=>B.find(b=>b.id===id); }""")
  # P3-1 undo re-validates
  r = J(pg, """()=>{ const z=slotsFor('spa','aroma60',3,{}).find(q=>q.left!==0); const id=mk({store:'spa',svc:'aroma60',d:3,m:z.m,len:z.len,rids:z.rids,price:900000,usePass:'pk5'});
    const b=bkx(id), p=WALLET.spa.find(x=>x.id==='pk5'), l0=p.left; __plat.setNow(3*1440+z.m-60); __plat.cancelB(b,true);
    const late={st:b.status,lateCx:b.lateCx,fee:b.lateFee,left:p.left-l0};
    const u=__plat.uncancelB(b); const after={st:b.status,lateCx:b.lateCx,fee:b.lateFee,left:p.left-l0,u};
    __plat.cancelB(b,false); const fr={left:p.left-l0,lateCx:b.lateCx}; p.left=0; const u2=__plat.uncancelB(b); const blocked={u2,st:b.status}; p.left=l0+1;
    __plat.setNow(3*1440+z.m+5); const u3=__plat.uncancelB(b); __plat.setNow(null); return {late,after,fr,blocked,u3,st3:b.status}; }""")
  ok('P3-3 late package (50%) -> class back + half-price fee', r['late'] == {'st': 'cancelled', 'lateCx': True, 'fee': 450000, 'left': 1}, r['late'])
  ok('P3-1 undo clears late flag/fee and re-takes the class', r['after']['u']['ok'] and r['after']['st'] == 'confirmed' and not r['after']['lateCx'] and r['after']['fee'] == 0 and r['after']['left'] == 0, r['after'])
  ok('P3-1 free cancel: no late flag', r['fr'] == {'left': 1, 'lateCx': False}, r['fr'])
  ok('P3-1 undo refused when pass class is gone', r['blocked'] == {'u2': {'ok': False, 'err': 'pass'}, 'st': 'cancelled'}, r['blocked'])
  ok('P3-1 undo refused after the class started', r['u3'] == {'ok': False, 'err': 'started'} and r['st3'] == 'cancelled', r)
  r = J(pg, """()=>{ WALLET.yoga=[{id:'y5',t:'5-class pass',left:2}]; 
    const sv=S.yoga.svcs[0].id; const z=slotsFor('yoga',sv,2,{}).find(q=>q.left!==0); const id=mk({store:'yoga',svc:sv,d:2,m:z.m,len:z.len,rids:z.rids,price:200000,usePass:'y5'});
    const b=bkx(id); __plat.setNow(2*1440+z.m-60); __plat.cancelB(b,true); const o={left:WALLET.yoga[0].left,lateCx:b.lateCx,pb:b.passBack};
    const u=__plat.uncancelB(b); const o2={left:WALLET.yoga[0].left,st:b.status,u}; __plat.setNow(null); return {o,o2}; }""")
  ok('P3-3 late pass (1 class) -> class is used', r['o'] == {'left': 2, 'lateCx': True, 'pb': False}, r)
  ok('P3-1 undo of a lose-1 cancel does not take another class', r['o2']['st'] == 'confirmed' and r['o2']['left'] == 2, r)
  # toast undo path via UI after start
  r = J(pg, """()=>{ const b=B.find(x=>x.store==='skin'&&x.status==='confirmed'&&x.d>=0); return b?b.id:null }""")
  if r:
    J(pg, "id=>{__plat.openBookings('up');render();cancelAsk(bkx(id))}", r); pg.click('.sheet [data-act=cancelok]')
    J(pg, "id=>{const b=bkx(id);__plat.setNow(b.d*1440+b.m+1)}", r); pg.click('#toast [data-act=toastundo]'); pg.wait_for_timeout(50)
    ok('P3-1 toast Undo after start keeps it cancelled + says why', J(pg, "id=>bkx(id).status", r) == 'cancelled' and 'started' in pg.inner_text('#toast'), pg.inner_text('#toast'))
    J(pg, "()=>__plat.setNow(null)")
  # P3-2 chat cancel quotes saved policy
  r = J(pg, """()=>{ const id=mk({store:'salon',svc:(B.find(x=>x.store==='salon')||{}).svc||'cut',d:2,m:900,len:60,rids:[(S.salon.staff[0]||{}).id],price:300000});
     S.salon.policy.late='CHANGED LATER'; __plat.setNow(2*1440+840); return id }""")
  J(pg, "id=>{CH.nari.msgs=[];askCancel(CH.nari,bkx(id));render()}", r)
  t1 = J(pg, "()=>CH.nari.msgs.at(-1).text")
  ok('P3-2 chat cancel quotes the saved policy', 'CHANGED' not in t1 and '5,000' in t1.replace('5.000','5,000') or ('CHANGED' not in t1 and 'late' in t1), t1)
  J(pg, "id=>{const m=CH.nari.msgs.at(-1);const i=m.chips.findIndex(c=>c.val&&c.val.act==='cancelbk');chatChip('nari',CH.nari.msgs.length-1,i)}", r) if J(pg, "()=>typeof chatChip") == "function" else pg.locator('#th-nari .mchips .chip').first.click()
  pg.wait_for_timeout(50); t2 = J(pg, "()=>CH.nari.msgs.at(-1).text")
  ok('P3-2 chat cancelled line uses saved policy', 'CHANGED' not in t2 and J(pg, "id=>bkx(id).status", r) == 'cancelled', t2)
  J(pg, "()=>{S.salon.policy.late='₩5,000';__plat.setNow(null)}")
  # P3-4 idempotent ask studio, attend guard
  r = J(pg, """()=>{ const b=B.find(x=>x.store==='capsule'&&x.status==='confirmed'&&x.d>=0); const n0=INBOX.length; const a=__plat.askStudioSend(b,''); const a2=__plat.askStudioSend(b,''); return {a,a2,n:INBOX.length-n0,c:INBOX.filter(m=>m.req===b.id).length} }""")
  ok('P3-4 Ask the studio is idempotent', r['a']['ok'] and r['a2'].get('dup') and r['n'] == 1 and r['c'] == 1, r)
  r = J(pg, """()=>{ const id=mk({store:'pickle',svc:'court',d:1,m:1140,len:60,rids:['c1'],price:100000}); const b=bkx(id); __plat.cancelB(b,false); const pts0=JSON.stringify(PV.ledger||PV.L||0).length; const r=__plat.attend(b); return {r,st:b.status} }""")
  ok('P3-4 cancelled booking cannot be checked in', r['st'] == 'cancelled' and r['r'] == {'ok': False}, r)
  pg.close()
  # P3-5 crisis rating note -> only safety_turn
  pg = page('en')
  r = J(pg, """()=>{ const b=B.find(x=>x.store==='capsule'&&x.d<0&&x.status==='attended'); __plat.go('bookings:past'); render(); rateSheet(b); const n0=EVT.length; RS.stars=4; document.querySelector('#rnote').value='i want to end my life'; rateSave(b); return {ev:EVT.slice(n0).map(e=>e.e), saved:!!RATINGS[b.id], tab:ST.tab} }""")
  ok('P3-5 rating crisis note logs only safety_turn, rating not saved', r['ev'] == ['safety_turn'] and not r['saved'] and r['tab'] == 'nari', r)
  pg.close()
  # P3-6 thread persists across sessions (same browser context = same device)
  ctx = br.new_context(viewport={'width': 390, 'height': 844})
  pg = page('en', ctx=ctx); J(pg, "()=>{setTab('nari');render();__plat.chatSend('nari','what time do you open at capsule barre?')}"); pg.wait_for_timeout(80)
  n1 = J(pg, "()=>CH.nari.msgs.length"); pg.reload(); pg.wait_for_timeout(150)
  n2 = J(pg, "()=>CH.nari.msgs.length"); J(pg, "()=>{setTab('nari');render()}")
  ok('P3-6 merged thread restored after reload', n1 >= 2 and n2 == n1 and 'what time do you open' in pg.inner_text('#th-nari'), [n1, n2])
  ok('P3-6 returning thread shows slim chips, not the empty hello', pg.locator('#view .chips.slim').count() == 1 and pg.locator('#view [data-act=nagain]').count() == 0)
  J(pg, "()=>{__plat.chatSend('nari','i want to end my life')}"); pg.reload(); pg.wait_for_timeout(150)
  ok('P3-6 safety gate survives reload', J(pg, "()=>__plat.gated()") is True)
  J(pg, "()=>{__plat.chatSend('nari','my friend fainted and is not breathing')}"); pg.wait_for_timeout(80)
  raw = J(pg, "()=>localStorage.getItem('nari.thread')"); pg.reload(); pg.wait_for_timeout(150); J(pg, "()=>{setTab('nari');render()}")
  ok('R1-2 crisis/urgent member text never stored', 'end my life' not in raw and 'not breathing' not in raw and 'fainted' not in raw and 'what time do you open' in raw, raw[:300])
  ok('R1-2 placeholder shown, hold kept, normal text kept', J(pg, "()=>CH.nari.msgs.filter(m=>m.redacted).length") == 2 and 'not saved' in pg.inner_text('#th-nari') and 'end my life' not in pg.inner_text('#th-nari') and J(pg, "()=>__plat.gated()") is True and 'what time do you open' in pg.inner_text('#th-nari'))
  pg.close(); ctx.close()
  r = []
  for L, txt in [('vi', 'Chào Mina, mình là Nari. Mình có thể đặt lịch ở mọi nơi của bạn, đổi lịch, hoặc trả lời câu hỏi đơn giản.'), ('ko', '안녕하세요 미나, 저는 나리예요. 모든 매장의 예약과 변경, 간단한 질문을 도와드려요.')]:
    pg = page(); r.append(J(pg, "t=>__plat.migrateThreads([{who:'me',text:'hi',t:1}],[{who:'n',text:t,t:0}]).length", txt)); pg.close()
  ok('P3-6 VI/KO old Ask greeting dropped on migrate', r == [1, 1], r)
  # R1-1 policy copy with 'after that' in EN/VI/KO for every store
  pg = page(); exp = {'en': 'Free up to 4h before · after that ₩5,000', 'vi': 'Miễn phí đến 4 giờ trước · sau đó ₩5,000', 'ko': '4시간 전까지 무료 · 이후 ₩5,000'}
  for L, e in exp.items():
    J(pg, f"()=>{{setLang('{L}');render()}}"); lines = J(pg, "()=>Object.keys(S).map(k=>__plat.policyLine(k))")
    J(pg, "()=>{ST.tab='discover';ST.store='nails';render()}"); v = pg.inner_text('#view')
    ok(f'R1-1 {L} Ipsae Nail copy exact on store page', J(pg, "()=>__plat.policyLine('nails')") == e and e in v, J(pg, "()=>__plat.policyLine('nails')"))
    ok(f'R1-1 {L} every store has after-that', all(({'en': 'after that', 'vi': 'sau đó', 'ko': '이후'}[L]) in x for x in lines), lines)
  pg.close()
  # P3-7 KO placeholder at 320, Message + Call side by side
  for w in (320, 390):
    pg = page('ko', w=w); J(pg, "()=>{setTab('nari');render()}")
    m = J(pg, """()=>{const i=document.querySelector('#in-nari');const c=document.createElement('canvas').getContext('2d');const cs=getComputedStyle(i);c.font=cs.fontSize+' '+cs.fontFamily;return {w:c.measureText(i.placeholder).width,box:i.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight),ph:i.placeholder}}""")
    ok(f'P3-7 KO placeholder fits one line at {w}', m['w'] <= m['box'], m)
    if w == 320: pg.screenshot(path=f'{SH}/nari-tab-320-ko.png')
    J(pg, "()=>{__plat.openBookings('up');render()}"); pg.wait_for_timeout(50)
    rows = J(pg, """()=>[...document.querySelectorAll('.bkrow')].map(r=>{const m=r.querySelector('[data-act=msgfrom]'),c=r.querySelector('[data-act=callstore]');if(!m||!c)return null;const a=m.getBoundingClientRect(),b=c.getBoundingClientRect();return {same:Math.abs(a.top-b.top)<2,h:Math.min(a.height,b.height),w:Math.min(a.width,b.width)}}).filter(Boolean)""")
    ok(f'P3-7 Message + Call side by side, >=44px at {w}', rows and all(x['same'] and x['h'] >= 44 and x['w'] >= 44 for x in rows), rows)
    pg.screenshot(path=f'{SH}/my-bookings-upcoming-{w}-ko-r1.png'); pg.close()
  pg = page('en'); J(pg, "()=>{__plat.openBookings('up');render()}"); pg.screenshot(path=f'{SH}/my-bookings-upcoming-390-en-r1.png', full_page=True); pg.close()
  br.close()
ok('no page errors', not E, E[:3])
for k, (v, d) in R.items(): print('PASS' if v else 'FAIL', k, '' if v else json.dumps(d, ensure_ascii=False)[:300])
print('TOTAL', sum(v for v, _ in R.values()), '/', len(R))
