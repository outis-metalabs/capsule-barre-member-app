"""PR #11 round 2 checks: BA decisions (PR11-P/N/H/D), Korea-first defaults, screenshots. Usage: python pr11_r2.py [base_url] [shots_dir]"""
import sys, os, re, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/pr11-r2'; os.makedirs(SH, exist_ok=True)
R = {}; E = []
def ok(k, c, d=''): R[k] = [bool(c), d]
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='', lang=None, w=390):
    pg = b.new_page(viewport={'width': w, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e))); pg.on('console', lambda m: E.append(m.text) if m.type == 'error' else None)
    pg.goto(U + q); pg.evaluate("()=>localStorage.clear()"); pg.goto(U + q); pg.wait_for_timeout(150)
    if lang: pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
    return pg
  def send(pg, cid, q):
    pg.evaluate(f"()=>{{CH['{cid}'].msgs=[];CH['{cid}'].care=false;ST.tab='{cid}';render()}}"); pg.evaluate("([c,q])=>__plat.chatSend(c,q)", [cid, q])
    return pg.evaluate(f"CH['{cid}'].msgs.filter(x=>x.who!=='me')")
  pg = page()
  ok('KR-default-locale', pg.evaluate("L") == 'ko')
  home = pg.inner_text('#view'); ok('KR-currency', '₫' not in pg.inner_text('body') and '₩' in pg.evaluate("(()=>{ST.tab='you';ST.page='settings';render();return document.body.innerText})()"))
  ok('KR-stores', 'Seongsu' in pg.evaluate("__plat.S.capsule.area") and not re.search(r'Quận|Thảo Điền|Mây Hair|Sen Spa', pg.evaluate("(()=>{ST.tab='discover';ST.page=null;render();return document.body.innerText})()")))
  pg.close()
  for lang in ['en', 'vi', 'ko']:
    pg = page('', lang); PAGES = [(None, None), ('wallet', None), ('vouchers', 'mine'), ('vouchers', 'more'), ('points', None), ('settings', None)]  # You hub + its subpages (ends on Settings)
    you = html = ''
    for sp, sg in PAGES: pg.evaluate("([p,s])=>{ST.tab='you';ST.page=p;ST.vseg=s;render()}", [sp, sg]); you += pg.inner_text('#view'); html += pg.inner_html('#view')
    life = pg.evaluate("__plat.pv.life(__plat.pv.ME())")
    pg.evaluate("()=>{ST.tab='you';ST.page='points';render()}")
    ok(f'PR11-P1 {lang}', 'pv-earned' in html and 'pv-how' in html and pg.inner_text('#pv-how').count('+') >= 3)
    ok(f'PR11-P2 {lang}', pg.locator('#pv-legacy').count() == 0 and not re.search(r'pending|đang chờ|대기 중', pg.inner_text('#view')))
    nocash = {'en': 'no cash value', 'vi': 'giá trị quy đổi', 'ko': '현금 가치'}[lang]
    ok(f'PR11-P3 {lang}', nocash not in you and 'pv-bal' not in html and 'pvclaim' not in html)
    ok(f'PR11-P5 {lang}', 'pv-flag' not in html and 'pvstore' not in html)
    pg.evaluate("()=>{ST.tab='home';ST.page=null;render()}"); order = pg.evaluate("(()=>{const v=document.getElementById('view');const n=v.querySelector('#pv-notes'),h=v.querySelector('.hero,[class*=hero]');return n&&h?!!(h.compareDocumentPosition(n)&Node.DOCUMENT_POSITION_FOLLOWING):null})()")
    bt = pg.inner_text('#pv-notes p'); ok(f'PR11-P4 {lang}', order is not False and bt.count('\n') <= 1 and not re.search(r'pending|đang chờ|대기 중', bt) and re.sub(r'\D', '', bt).find(str(life)) >= 0, bt)
    for cid in ['book', 'ask']:
      pg.evaluate(f"()=>{{ST.tab='{cid}';render()}}"); h = pg.inner_html('#view')
      ok(f'PR11-H1 {lang} {cid}', 'sosbar' not in h and 'helplink' in h and pg.evaluate("(()=>{const l=document.querySelector('.helplink'),f=document.querySelector('.chatbox');return !!(f.compareDocumentPosition(l)&Node.DOCUMENT_POSITION_FOLLOWING)})()"))
    pg.click('.helplink'); hs = pg.inner_text('.sheet'); ok(f'PR11-H2 {lang}', not re.search(r'(?<![\d.,])(1\d\d|911|999|112)(?![\d.,])', hs) and len(hs) > 80); pg.evaluate("closeSheet()")
    ok(f'PR11-D3 {lang}', not re.search(r'No ads|Không quảng cáo|광고 없음|광고', pg.evaluate("(()=>{let t='';for(const x of ['ask','discover','home']){ST.tab=x;render();t+=document.body.innerText}ST.store='capsule';render();t+=document.body.innerText;ST.store=null;return t})()")))
    pg.close()
  pg = page('', 'ko')
  for lang, q, exp in [('ko', '처음인데 바레 혼자 가도 괜찮아요?', '괜찮아요'), ('en', "first time at barre, can I come alone?", 'Yes'), ('vi', 'lần đầu đi barre một mình được không?', 'Được'), ('en', 'what should I wear to barre?', 'Grip socks'), ('en', 'how early should I arrive for barre?', '10 minutes'), ('ko', '바레 처음인데 뭐 입고 가요?', ''), ('en', 'first time at pickleball, what should I wear?', 'court shoes')]:
    pg.evaluate(f"()=>setLang('{lang}')"); m = send(pg, 'ask', q); t = m[0]['text'] if m else ''
    ok(f'PR11-N1/N2 {lang} {q}', len(m) == 1 and exp in t and not m[0].get('confirm') and len(m[0].get('chips') or []) <= 1, [x['text'][:80] for x in m])
  pg.evaluate("()=>setLang('en')"); m = send(pg, 'ask', 'first time getting a facial, can I come alone?'); ok('PR11-N5', "don't have that" in m[0]['text'], m[0]['text'][:80])
  pg.evaluate("()=>setLang('ko')"); m = send(pg, 'book', '바레 내일 오전'); ok('PR11-N3', any(len(x.get('chips') or []) for x in m), [x['text'] for x in m])
  for lang, q in [('en', 'first time at barre and now I have chest pain'), ('ko', '처음인데 가슴 통증'), ('en', 'first class alone, I want to kill myself')]:
    pg.evaluate(f"()=>setLang('{lang}')"); m = send(pg, 'ask', q); ok(f'PR11-N4/H3/H4 {lang} {q}', all(x.get('care') for x in m) and not any(c.get('val', {}).get('say') for x in m for c in (x.get('chips') or [])), [x['text'][:60] for x in m])
  for lang, q in [('ko', '커트 예약'), ('en', 'haircut Saturday 2pm'), ('vi', 'cắt tóc thứ bảy')]:
    pg.evaluate(f"()=>setLang('{lang}')"); send(pg, 'book', q); ok(f'PR11-H5 {lang}', not re.search(r'danger|nguy hiểm|위험|hurt|bị thương|다쳤', pg.inner_text('#view')))
  st = pg.evaluate("__plat.selfTest()"); ok('PR11-H6 selfTest', st['passed'] == st['total'], [st['total'], st['fail'][:3]])
  pg.close()
  pg = page('?demo=1', 'en'); pg.evaluate("()=>{ST.tab='you';ST.page='settings';render()}"); ok('PR11-P5 demo mode shows tools', pg.locator('#pv-flag').count() == 1 and pg.locator('[data-act=pvstore]').count() == 1); pg.close()
  # round 3: Korean staff/store names everywhere in KR, decimal-point km, staff store check, Ask title
  OLD = re.compile(r'(?<![\w])(Linh|Khôi|Ngân|Hoa|Phương|Ngọc|Trâm|Tuấn|Lành|Vy|Sen Spa|센 ?스파|마이 ?헤어|District|Quận|1군|3군|호아|응언|코이)(?![\w])')
  for lang in ['en', 'vi', 'ko']:
    pg = page('', lang); hits = set()
    for q in ['pregnancy massage', '임산부 마사지', 'massage bầu', 'beard trim saturday', '수염 정리', 'tỉa râu']:
      for m_ in OLD.finditer(' '.join(x['text'] for x in send(pg, 'ask', q))): hits.add(m_.group(0))
    for js in ["ST.page='notif'", "ST.tab='home'", "ST.tab='book'", "ST.tab='ask'", "ST.store='salon'", "ST.store='skin'", "ST.store='spa'"]:
      pg.evaluate(f"()=>{{ST.page=null;ST.store=null;{js};render()}}"); [hits.add(m_.group(0)) for m_ in OLD.finditer(pg.inner_text('body'))]
    ok(f'R3-names {lang}', not hits, sorted(hits))
    pg.evaluate("()=>{ST.page=null;ST.store=null;ST.tab='discover';ST.page=null;render()}"); ok(f'R3-km {lang}', not re.search(r'\d,\d km', pg.inner_text('body')) and re.search(r'0\.6 km', pg.inner_text('body')))
    pg.close()
  pg = page('', 'ko'); m = send(pg, 'book', '토요일 오후 소라 커트'); ok('R3-book-by-KO-name', pg.evaluate("(CH.book.draft||{}).staff") == 'linh', [x['text'] for x in m])
  pg.evaluate("()=>setLang('en')"); send(pg, 'book', 'haircut with Sora Saturday afternoon'); ok('R3-book-by-name', pg.evaluate("(CH.book.draft||{}).staff") == 'linh')
  # R4: service + staff + store together from one message (KO/VI were missing the service before, also on dba9c09)
  for lang, q in [('ko', '하늘이랑 수분 페이셜 일요일'), ('ko', '일요일 하늘 수분 페이셜'), ('en', 'hydrating facial with Haneul on Sunday'), ('vi', 'facial cấp ẩm với Haneul chủ nhật'), ('vi', 'chăm sóc da dưỡng ẩm với Haneul chủ nhật')]:
    pg.evaluate(f"()=>{{setLang('{lang}');CH.book.draft=null}}"); send(pg, 'book', q); dr = pg.evaluate("CH.book.draft||{}")
    ok(f'R4-svc+staff {lang} {q}', dr.get('store') == 'skin' and dr.get('svc') == 'hydra' and dr.get('staff') == 'ngan', dr)
  pg.evaluate("()=>{setLang('ko');CH.book.draft=null}"); send(pg, 'book', '수분 크림 뭐 써요?'); ok('R4-no-false-service', (pg.evaluate("CH.book.draft||{}")).get('svc') != 'hydra')
  r = pg.evaluate("(()=>{const P=__plat.pv,m=P.ME(),n=__plat.PV.now();P.pvBook('x1',{store:'capsule',member:m.id,start:n-60*6e4,end:n-10*6e4});return [P.confirmVisit(m,'x1','staff:salon-desk'),P.confirmVisit(m,'x1','staff:a',n,'salon'),P.confirmVisit(m,'x1','staff:capsule-desk').ok]})()")
  ok('R3-staff-store', r[0]['err'] == 'wrong_store' and r[1]['err'] == 'wrong_store' and r[2] is True, r)
  h = pg.evaluate("(()=>{setLang('ko');ST.tab='ask';ST.page=null;render();const e=document.querySelector('#view h1');return Math.round(e.getBoundingClientRect().height/parseFloat(getComputedStyle(e).lineHeight))})()"); ok('R3-ask-title-one-line-ko', h == 1, h)
  pg.close()
  # R5
  pg = page('', 'en')
  pg.evaluate("()=>{setLang('vi');CH.book.draft=null}"); send(pg, 'book', 'massage chân 45 phút ngày mai'); ok('R5-vi-foot45', (pg.evaluate("CH.book.draft||{}")).get('svc') == 'foot', pg.evaluate("CH.book.draft"))
  r = pg.evaluate("(()=>{const sid=Object.keys(WALLET).find(k=>(WALLET[k]||[]).length),ps=WALLET[sid][0],v=__plat.S[sid].svcs[0];const h=String(draftRows({store:sid,svc:v.id,rids:[],usePass:ps.id,len:60,party:1,d:1,m:600}));return h})()")
  ok('R5-pass-total-krw', '₩' in r and '₫' not in r, r[:300])
  pg.evaluate("()=>{__plat.S.nails.joined=true}")
  for lang, q, sid, svc in [('ko','순한 페이셜','skin','gentle'),('ko','얼굴·어깨 마사지','skin','fsm'),('ko','젤 네일','nails','gel'),('ko','기본 매니큐어','nails','mani'),('vi','Gội & sấy','salon','blow'),('vi','Chăm sóc da dịu nhẹ','skin','gentle'),('vi','Massage mặt & vai','skin','fsm'),('vi','Sơn gel','nails','gel'),('vi','Làm móng cơ bản','nails','mani'),('en','Gel nails','nails','gel'),('en','Classic manicure','nails','mani')]:
    pg.evaluate(f"()=>{{setLang('{lang}');CH.book.draft=null}}"); send(pg, 'book', q + {'ko':' 토요일','vi':' thứ bảy','en':' Saturday'}[lang]); dr = pg.evaluate("CH.book.draft||{}")
    ok(f'R5-name {lang} {q}', dr.get('store') == sid and dr.get('svc') == svc, dr)
  r = pg.evaluate("(()=>{const P=__plat.pv,m=P.ME(),n=__plat.PV.now();P.pvBook('x5',{store:'capsule',member:m.id,start:n-60*6e4,end:n-10*6e4});return [P.confirmVisit(m,'x5','staff:a'),P.confirmVisit(m,'x5','ops:hq').ok]})()")
  ok('R5-storeless-staff-refused', r[0].get('err') == 'wrong_store' and r[1] is True, r)
  pg.evaluate("()=>{setLang('en');CH.book.draft=null}"); m = send(pg, 'book', 'haircut with Linh'); txt = ' '.join(x['text'] for x in m); chips = [c['label'] for x in m for c in (x.get('chips') or [])]
  ok('R5-kr-unknown-linh', "don't know Linh" in txt and 'Sora' in ' '.join(chips) and 'Minho' in ' '.join(chips), [txt[:200], chips])
  pg.close()
  pg = page('?market=vn', 'en'); ok('R3-vn-keeps-names', pg.evaluate("__plat.S.salon.staff[0].n") == 'Linh'); pg.close()
  # screenshots 390 EN + KO
  for lang in ['en', 'ko']:
    for tab in ['home', 'discover', 'book', 'ask', 'you']:
      pg = page('', lang); pg.evaluate(f"()=>{{ST.tab='{tab}';render();scrollTo(0,0)}}"); pg.wait_for_timeout(200)
      if tab == 'ask': pg.evaluate("([q])=>__plat.chatSend('ask',q)", [{'en': 'first time at barre, can I come alone?', 'ko': '처음인데 바레 혼자 가도 괜찮아요?'}[lang]]); pg.wait_for_timeout(150)
      pg.screenshot(path=f'{SH}/{tab}-390-{lang}.png', full_page=True); pg.close()
    pg = page('', lang); pg.evaluate("()=>{ST.tab='book';ST.page=null;render()}"); pg.click('.helplink'); pg.wait_for_timeout(300); pg.screenshot(path=f'{SH}/help-sheet-390-{lang}.png'); pg.close()
  b.close()
for k, v in R.items(): print('PASS' if v[0] else 'FAIL', k, '' if v[0] else json.dumps(v[1], ensure_ascii=False)[:300])
print('errors', E); print('TOTAL', sum(v[0] for v in R.values()), '/', len(R))
