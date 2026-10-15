"""Wallet rows on You are real buttons with a detail sheet; KR voucher titles/terms always show ₩ (never ₫)."""
import sys, os, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
SH = '/workspace/hana-shots/cutouts/fixes'; os.makedirs(SH, exist_ok=True)
R = {}; E = []
def ok(k, c, d=''): R[k] = [bool(c), d]
with sync_playwright() as p:
  br = p.chromium.launch()
  def page(q='', lang=None):
    pg = br.new_page(viewport={'width': 390, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U + q); pg.evaluate("()=>localStorage.clear()"); pg.goto(U + q); pg.wait_for_timeout(100)
    if lang: pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
    pg.evaluate("()=>{if(!B.some(b=>b.dep&&b.status==='confirmed')){const b=B.find(b=>b.status==='confirmed'&&b.d>=0);if(b)b.dep=200000}setTab('you');ST.page='wallet';render()}")
    return pg
  for lang in ['en', 'vi', 'ko']:
    pg = page(lang=lang)
    rows = pg.evaluate("()=>[...document.querySelectorAll('.wrow')].map(b=>{const r=b.getBoundingClientRect();return {tag:b.tagName,h:r.height,lbl:b.getAttribute('aria-label'),chev:!!b.querySelector('svg.ico'),act:b.dataset.act,tab:b.tabIndex}})")
    ok(f'{lang}: 4 wallet rows (pass, package, credit, deposit)', len(rows) >= 4 and {r['act'] for r in rows} == {'wallet', 'walletdep'}, rows)
    ok(f'{lang}: rows are 44px focusable buttons w/ aria-label + chevron', all(r['tag'] == 'BUTTON' and r['h'] >= 44 and r['lbl'] and r['chev'] and r['tab'] >= 0 for r in rows), rows)
    for i, r in enumerate(rows):
      pg.evaluate(f"()=>document.querySelectorAll('.wrow')[{i}].click()"); pg.wait_for_timeout(150)
      s = pg.evaluate("()=>{const s=document.querySelector('.sheet');return s?{t:s.innerText,btn:[...s.querySelectorAll('.btn:not(.ghost)')].map(b=>b.dataset.act+'|'+(b.dataset.v||b.dataset.s||'')+'|'+b.innerText)}:null}")
      ok(f'{lang}: row {i} opens detail sheet with store, value, validity, rules, action', s and len(s['btn']) == 1 and s['t'].count('\n') > 6, s)
      if lang == 'ko' and s:
        ok(f'ko: row {i} sheet is Korean (no English rule words)', not any(w in s['t'] for w in ['How it works', 'Refund rule', 'Book with this', 'Valid']), s['t'][:200])
      if s:
        b = s['btn'][0]
        exp = 'walletbook' if 'Pass' in r['lbl'] or 'pass' in r['lbl'] or 'ackage' in r['lbl'] or '회' in r['lbl'] or 'gói' in r['lbl'].lower() or 'thẻ' in r['lbl'].lower() else None
        ok(f'{lang}: row {i} action type', b.startswith('walletbook|') or b.startswith('go|store:') or b.startswith('go|bookings:up:'), b)
        if lang == 'en': R[f'en: row {i} action'] = [True, b]
        if lang in ('en', 'ko') and i < 4: pg.screenshot(path=f'{SH}/wallet-{lang}-390-{["pass","package","credit","deposit"][i]}.png')
      pg.evaluate("()=>closeSheet()"); pg.wait_for_timeout(100)
    if lang in ('en', 'ko'): pg.screenshot(path=f'{SH}/wallet-{lang}-390-you.png', full_page=True)
    pg.close()
  # actions do what they say (EN)
  pg = page(lang='en')
  acts = pg.evaluate("()=>[...document.querySelectorAll('.wrow')].map(b=>b.getAttribute('aria-label'))")
  def run(i):
    pg.evaluate("()=>{setTab('you');ST.page='wallet';render()}"); pg.evaluate(f"()=>document.querySelectorAll('.wrow')[{i}].click()"); pg.wait_for_timeout(100)
    pg.evaluate("()=>document.querySelector('.sheet .btn:not(.ghost)').click()"); pg.wait_for_timeout(200)
    return pg.evaluate("()=>({tab:ST.tab,store:ST.store,page:ST.page,scope:CH.cici.scope,sheet:!!document.querySelector('.sheet'),bks:(document.querySelector('.sheet .slot,.sheet #bk-svcs')&&BS?BS.store:null)||(document.querySelector('.sheet #bk-svcs [data-s]')||{dataset:{}}).dataset.s||null,last:(document.querySelector('#view').innerText||'').slice(-200)})")
  res = [run(i) for i in range(len(acts))]
  for a, r in zip(acts, res):
    if a.startswith('Store credit'): ok('credit → Use at {store} opens the store page', r['store'] == 'pickle', r)
    elif a.startswith('Deposit'): ok('deposit → View booking opens My bookings', r['page'] == 'bookings', r)
    else: ok(f'{a.split(",")[0]} → Book with this opens the booking sheet at that store (no chat jump)', r['tab'] != 'cici' and r['sheet'] and r['bks'] in ('capsule', 'spa'), r)
  pg.evaluate("()=>{setTab('you');ST.page='wallet';render();document.querySelector('[data-act=walletdep]').click()}"); pg.wait_for_timeout(100)
  ok('deposit sheet shows the refund rule', 'Refund rule' in pg.evaluate("()=>document.querySelector('.sheet').innerText"))
  pg.evaluate("()=>closeSheet()"); pg.keyboard.press('Tab')
  ok('wallet row reachable by keyboard (focus + Enter opens sheet)', pg.evaluate("()=>{const b=document.querySelector('.wrow');b.focus();return document.activeElement===b}"))
  pg.keyboard.press('Enter'); pg.wait_for_timeout(100); ok('Enter opens sheet', pg.evaluate("()=>!!document.querySelector('.sheet')"))
  pg.close()
  # --- KR: every voucher title / term in ₩ ---
  for lang in ['ko', 'en', 'vi']:
    pg = page('?realRewards=1&demo=1', lang)
    bad = pg.evaluate("""()=>{const out=[];const L=['en','vi','ko'];
      for(const v of PV.defs){for(const k of ['title','terms']){const x=v[k];for(const s of (Array.isArray(x)?x:[x]))if(typeof s==='string'&&/₫|\\bVND\\b|\\dđ/.test(s))out.push(v.id+':'+s)}; const tx=[pvTx(v.title),pvTx(v.terms)].join(' '); if(/₫/.test(tx))out.push('pvTx '+v.id+':'+tx)}
      const r=publish({title:['Max 50.000 ₫ off','Giảm tối đa 50.000 ₫','최대 50.000 ₫ 할인'],terms:['Max 50.000 ₫ per visit','Tối đa 50.000₫','최대 50,000 ₫'],type:'pct',value:10,cost:100,store:'pickle'});
      if(r.ok){for(const s of [...r.v.title,...[].concat(r.v.terms)])if(/₫/.test(s))out.push('published:'+s)} else out.push('publish failed '+JSON.stringify(r.errors));
      ['Max 50.000 ₫','50,000₫','50000 đ','50.000 VND','₫50.000'].forEach(s=>{const y=fxMoneyTxt(s);if(/₫|đ|VND/.test(y)||!/₩/.test(y))out.push('fx '+s+'→'+y)});
      if(fxMoneyTxt('đẹp đi')!=='đẹp đi')out.push('fx ate Vietnamese');
      return out}""")
    ok(f'KR {lang}: all voucher titles/terms (incl. newly published) in ₩', not bad, bad)
    txt = ''
    for js in ["()=>{setTab('you');render()}", "()=>{setTab('you');ST.page='wallet';render()}", "()=>{setTab('you');ST.page='vouchers';ST.vseg='mine';render()}", "()=>{setTab('you');ST.page='vouchers';ST.vseg='more';render()}", "()=>{setTab('you');ST.page='settings';render()}", "()=>{setTab('home');render()}", "()=>{setTab('discover');render()}"]:
      if lang == 'ko' and 'vouchers' in js: pg.evaluate("()=>{for(const v of PV.defs){try{claim(ME,v.id)}catch(e){}}}")
      pg.evaluate(js); pg.wait_for_timeout(80); txt += pg.evaluate("()=>document.body.innerText")
    for v in pg.evaluate("()=>PV.defs.map(v=>v.id)"):
      try:
        pg.evaluate(f"()=>{{try{{claimSheet('{v}')}}catch(e){{}}}}"); pg.wait_for_timeout(40); txt += pg.evaluate("()=>(document.querySelector('.sheet')||{}).innerText||''"); pg.evaluate("()=>closeSheet()")
      except Exception: pass
    ok(f'KR {lang}: no ₫ on You/Home/Discover/voucher sheets', '₫' not in txt, [l for l in txt.split('\n') if '₫' in l][:5])
    pg.close()
  # --- You hub structure ---
  for lang in ['en', 'ko', 'vi']:
    pg = br.new_page(viewport={'width': 390, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e)))
    for q in ['', '?demo=1']:
      pg.goto(U + q); pg.evaluate("()=>localStorage.clear()"); pg.goto(U + q); pg.evaluate(f"()=>{{setLang('{lang}');ME.notices.forEach(n=>n.seen=true);setTab('you');render()}}")
      st = pg.evaluate("""()=>{const v=document.getElementById('view');return {kids:[...v.children].map(c=>c.id||c.className),tiles:[...v.querySelectorAll('.ytile')].map(b=>({v:b.dataset.v,h:b.getBoundingClientRect().height,txt:b.innerText})),btns:[...v.querySelectorAll('button')].map(b=>b.dataset.act+':'+(b.dataset.v||'')),bar:!!v.querySelector('#you-next [role=progressbar]'),pts:(v.querySelector('#you-pts')||{}).innerText||''}}""")
      ok(f'You {lang}{q}: MVP-Y1 profile + tiles (Wallet/Bookings/Look[+Vouchers]), Settings', st['kids'][:3] == ['you-prof', 'you-tiles', 'stack'] and 'youpage:look' in st['btns'] and ('youpage:vouchers' in st['btns']) == ('realRewards' in q), st)
      ok(f'You {lang}{q}: tiles >=44px', len(st['tiles']) >= 3 and all(x['h'] >= 44 for x in st['tiles']), st['tiles'])
      ok(f'You {lang}{q}: one points + streak line', st['pts'].count('\n') == 0 and '·' in st['pts'], st['pts'])
      for sp in (['wallet', 'bookings', 'look', 'settings', 'points'] + (['vouchers'] if 'realRewards' in q else [])):
        pg.evaluate("()=>{setTab('you');render()}"); pg.click(f'[data-act=youpage][data-v={sp}]'); pg.wait_for_timeout(80)
        at = pg.evaluate("()=>ST.page"); pg.evaluate("()=>sysBack()"); back = pg.evaluate("()=>[ST.tab,ST.page]")
        pg.evaluate("()=>{setTab('you');render()}"); pg.click(f'[data-act=youpage][data-v={sp}]'); pg.click('[data-act=back]'); back2 = pg.evaluate("()=>[ST.tab,ST.page]")
        ok(f'{lang}{q}: tile {sp} opens its page; system back + header back return to You', at == sp and back == ['you', None] and back2 == ['you', None], [at, back, back2])
      pg.evaluate("()=>{setTab('you');ST.page='settings';render()}"); sh = pg.inner_html('#view')
      ok(f'Settings {lang}{q}: language, notifications, points info' + (', demo tools' if q else ', no demo tools'), all(x in sh for x in ['data-act="setlang"', 'data-act="nset"']) and (('pvstore' in sh) == bool(q)), '')
    pg.close()
  # --- Vouchers: Mine / Get more + Ready card layout ---
  for lang, w in [('en', 390), ('ko', 390), ('vi', 320), ('en', 320)]:
    pg = br.new_page(viewport={'width': w, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U + '?realRewards=1'); pg.evaluate("()=>localStorage.clear()"); pg.goto(U + '?realRewards=1')
    pg.evaluate(f"()=>{{setLang('{lang}');ME.notices.forEach(n=>n.seen=true);ME.ledger.push({{id:'Ltest',member:ME.id,store:null,src:'test',delta:600,life:0,reason:'test_grant',actor:'test',t:PV.now()}});/* old coins are dropped (no ×5): fixture balance */for(const v of PV.defs)claim(ME,v.id);setTab('you');ST.page='vouchers';ST.vseg=null;render()}}")
    segs = pg.evaluate("()=>[...document.querySelectorAll('[data-act=vseg]')].map(b=>b.dataset.v+':'+b.getAttribute('aria-selected'))")
    ok(f'Vouchers {lang} {w}: Mine/Get more segments, Mine first', segs == ['mine:true', 'more:false'], segs)
    L = pg.evaluate("""()=>[...document.querySelectorAll('.pv-c.vready')].map(c=>{const r=c.getBoundingClientRect(),x=c.querySelector('.vtx').getBoundingClientRect(),u=c.querySelector('.vuse').getBoundingClientRect(),k=c.querySelector('.vcan');const q=k&&k.getBoundingClientRect();
      const ov=(a,b)=>!(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom);
      return {tw:x.width/r.width,uw:u.width/r.width,uh:u.height,order:x.bottom<=u.top+1&&(!q||u.bottom<=q.top+1),ov:ov(x,u)||(q&&(ov(x,q)||ov(u,q))),ch:q?q.height:44,ghost:!k||k.classList.contains('ghost'),cw:q?q.width/r.width:0}})""")
    ok(f'Ready card {lang} {w}: text >=60% wide, full-width Use, small ghost Cancel below, no overlap', L and all(c['tw'] >= .6 and c['uw'] >= .9 and c['uh'] >= 44 and c['ch'] >= 44 and c['order'] and not c['ov'] and c['ghost'] and c['cw'] < .95 for c in L), L)
    pg.screenshot(path=f'{SH}/vouchers-ready-{lang}-{w}.png', full_page=True)
    pg.click('[data-act=vseg][data-v=more]'); ok(f'Vouchers {lang} {w}: Get more lists claimable vouchers', pg.locator('#pv-rewards').count() == 1 and pg.locator('[data-act=pvclaim]').count() > 0)
    pg.close()
  br.close()
ok('no page errors', not E, E[:3])
f = [k for k, v in R.items() if not v[0]]
print(json.dumps({k: v for k, v in R.items() if not v[0]}, ensure_ascii=False, indent=1)[:3000]); print(f'{len(R)-len(f)}/{len(R)} pass')
sys.exit(1 if f else 0)
