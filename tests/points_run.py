"""Points & vouchers: AC tests + UI sweep (320/390 x EN/VI/KO x realRewards off/on). Usage: python points_run.py [base_url] [shots_dir]"""
import sys, json, re, os
from playwright.sync_api import sync_playwright
# You is now a hub: points info + tools live on Settings, vouchers on Vouchers (Mine / Get more)
YP = lambda pg, p, seg=None: pg.evaluate("()=>{ST.tab='you';ST.store=null;ST.page=%s;%srender()}" % (json.dumps(p), "ST.vseg=%s;" % json.dumps(seg) if seg else ''))
YALL = lambda pg, f: ''.join((YP(pg, p, sg), f())[1] for p, sg in [(None, None), ('wallet', None), ('vouchers', 'mine'), ('vouchers', 'more'), ('settings', None)])
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
SHOTS = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/points'
os.makedirs(SHOTS, exist_ok=True)
ACJS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'points_ac.js')).read()
R = {}; E = []
FORBID = re.compile(r"\bXP\b|\bcoins?\b|cosmetic only|separate from store money|can.t pay for services|\bxu\b|코인|Chỉ trang trí|꾸미기 전용", re.I)
CONTRAST = """() => { const lum = c => { const m = c.match(/[\\d.]+/g).map(Number); const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return [.2126 * f(m[0]) + .7152 * f(m[1]) + .0722 * f(m[2]), m[3] == null ? 1 : m[3]]; };
  const bgOf = el => { while (el) { const b = getComputedStyle(el).backgroundColor; const a = b.match(/[\\d.]+/g).map(Number); if (a.length < 4 || a[3] > .9) return b; el = el.parentElement; } return 'rgb(247,241,234)'; };
  const bad = []; const root = document.querySelector('#view').parentElement;
  const els = [...document.querySelectorAll('#view *, .sheet *')].filter(e => e.offsetParent && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
  for (const e of els) { const cs = getComputedStyle(e); if (+cs.opacity < 1 && e.closest('[disabled]')) continue; const [l1] = lum(cs.color), [l2] = lum(bgOf(e)); const r = (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05); const big = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.66 && +cs.fontWeight >= 700);
    if (r < (big ? 3 : 4.5)) bad.push([e.textContent.trim().slice(0, 40), r.toFixed(2)]); }
  const small = [...document.querySelectorAll('[data-act^=pv], [data-pvd], #pv-dtype, select[id^=pv]')].filter(e => e.offsetParent).map(e => [e, (e.type === 'checkbox' && e.closest('label') ? e.closest('label') : e).getBoundingClientRect()]).filter(([e, r]) => r.height < 43.5 || r.width < 43.5) /* 0.5px tolerance: sheets slide up for ~280ms and 44px reads 43.99997px mid-animation */.map(([e, r]) => [e.dataset.act || e.id, Math.round(r.width), Math.round(r.height)]);
  return { bad, small, hscroll: document.documentElement.scrollWidth > innerWidth }; }"""
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='', w=390):
    pg = b.new_page(viewport={'width': w, 'height': 844})
    pg.on('pageerror', lambda e: E.append(str(e))); pg.on('console', lambda m: E.append(m.text) if m.type == 'error' else None)
    q = q + ('&' if q else '?') + 'demo=1&lang=en'  # PR11-P5: staff tools need demo mode; KO is the default locale, these checks read EN copy
    pg.goto(BASE + q); pg.evaluate("()=>localStorage.clear()"); pg.goto(BASE + q); pg.wait_for_timeout(150); return pg
  def ok(k, c, d=''): R[k] = [bool(c), d]
  # --- engine-level ACs
  pg = page(); pg.add_script_tag(content=ACJS); res = pg.evaluate("__pointsAC()"); pg.close()
  for k, v in res.items(): R[k] = v
  # --- AC-P34 / AC-P54a migration on first load, flag off and on
  pg = page()
  st = pg.evaluate("(()=>{const m=__plat.pv.ME();return {life:__plat.pv.life(m),lvl:__plat.pv.lvlOf(m),streak:m.streak,bal:__plat.pv.bal(m),legacy:(m.ledger.find(r=>r.reason==='legacy_coins')||{}).legacy,mig:m.ledger.filter(r=>r.reason==='migration').length,note:m.notices.filter(n=>n.k==='migrated').length}})()")
  home = pg.inner_text('#view'); banner1 = 'Your XP is now' in home
  pg.click('[data-act=pvseen]'); pg.evaluate("()=>{ST.tab='you';render()}"); banner2 = 'Your XP is now' in pg.inner_text('#view')
  pg.evaluate("()=>{__plat.pv.pvMigrate(__plat.pv.ME(),{xp:640,coins:120,weeks:3})}"); again = pg.evaluate("__plat.pv.ME().ledger.length")
  # wardrobe: owned lantern (above level) selectable
  YP(pg, 'settings'); pg.click('[data-act=pvwardrobe]'); pg.click('[data-act=pvwear][data-v=lan]'); wear = pg.evaluate("ST.wear"); pg.evaluate("closeSheet()")
  pg.click('#pv-flag'); on = pg.evaluate("(()=>{const m=__plat.pv.ME();return {bal:__plat.pv.bal(m),rows:m.ledger.filter(r=>r.reason==='migration'&&r.delta>0).length}})()")
  pg.click('#pv-flag'); pg.click('#pv-flag'); on2 = pg.evaluate("(()=>{const m=__plat.pv.ME();return {bal:__plat.pv.bal(m),rows:m.ledger.filter(r=>r.reason==='migration'&&r.delta>0).length}})()")
  ok('AC-P34', st['life'] == 640 and st['lvl'] == 2 and st['streak'] == 3 and st['bal'] == 0 and st['legacy'] == 120 and st['note'] == 1 and banner1 and not banner2 and again == 2 and on['bal'] == 600 and on['rows'] == 1 and on2 == on, [st, on, on2])
  ok('AC-P54a', st['mig'] == 1 and st['legacy'] == 120 and st['bal'] == 0 and wear == 'lan', [st, wear])
  ok('AC-P54b', on['rows'] == 1 and on2['rows'] == 1 and on2['bal'] == 600, [on, on2])
  pg.close()
  # --- AC-P44 UI with flag off; AC-P2 booking via UI
  pg = page(); pg.click('[data-act=pvseen]'); you = YALL(pg, lambda: pg.inner_html('#view')); YP(pg, 'settings')
  pg.click('[data-act=pvstore]'); st_off = pg.inner_text('.sheet'); pg.evaluate("closeSheet()")
  hidden = not any(x in you for x in ['pv-rewards', 'data-act="pvclaim"', 'pv-mine']) and 'Validate' not in st_off and 'Points earned' in pg.inner_text('#view')
  b0 = pg.evaluate("__plat.pv.bal(__plat.pv.ME())"); pg.evaluate("()=>{ST.tab='home';ST.page=null;render()}")
  pg.locator('[data-act=checkin]').first.click(); pg.locator('[data-act=attend]').first.click(); b1 = pg.evaluate("__plat.pv.bal(__plat.pv.ME())")
  ok('AC-P44', hidden and b1 - b0 == 60 and R.get('AC-P44e', [False])[0], [hidden, b0, b1])
  n0 = pg.evaluate("__plat.pv.ME().ledger.length"); pg.evaluate("()=>{ST.tab='nari';ST.page=null;render()}"); pg.locator('[data-act=nagain][data-i="1"]').click(); pg.locator('[data-act=chatbook]').last.click(); pg.wait_for_timeout(100); pg.evaluate("closeSheet()")  # Nari tab: Book again = chip + Book (the Book tab and its sheet-only row are gone)
  n1 = pg.evaluate("__plat.pv.ME().ledger.length"); nb = pg.evaluate("__plat.B.length")
  ok('AC-P2', R['AC-P2'][0] and n1 == n0, R['AC-P2'][1] + [n0, n1, nb])
  # AC-P3 UI: pending card shown on Home, gone after store scan
  pg.evaluate("()=>{ST.tab='home';ST.page=null;render()}"); pend1 = pg.locator('#pv-pending').count()
  YP(pg, 'settings'); pg.click('[data-act=pvstore]'); pg.click('[data-act=pvscan][data-v=demo-past]'); msg = pg.inner_text('#pv-smsg'); pg.evaluate("closeSheet()")
  pg.evaluate("()=>{ST.tab='home';ST.page=null;render()}"); pend2 = pg.locator('#pv-pending').count()
  ok('AC-P3', R['AC-P3'][0] and pend1 == 1 and pend2 == 0, [R['AC-P3'][1], pend1, pend2, msg])
  # AC-P12 UI: streakReset shows on next open
  pg.evaluate("()=>{const m=__plat.pv.ME();m.notices.forEach(n=>n.seen=true);m.closedTo-=21*864e5;m.weekVisits={};render()}"); ok('AC-P12', R['AC-P12'][0] and 'New week, fresh start' in pg.inner_text('#view'), R['AC-P12'][1])
  pg.close()
  # --- flag ON: claim, use, validate, redeem through the UI
  pg = page('?realRewards=1'); pg.click('[data-act=pvseen]'); YP(pg, 'vouchers', 'more')
  claimBtns = pg.locator('[data-act=pvclaim]').count()
  pg.click('[data-act=pvclaim]:not([disabled])'); sheet = pg.inner_text('.sheet'); pg.click('[data-act=pvclaimok]'); you = YALL(pg, lambda: pg.inner_text('#view'))
  ok('AC-P17', R['AC-P17'][0] and 'Valid until' in sheet and 'Terms' in sheet and 'Ready' in you and '100 points' in you, [R['AC-P17'][1], sheet[:120]])
  ok('AC-P16', R['AC-P16'][0] and 'Unlocks at Level 3' in you and 'more weeks of streak needed' in you, R['AC-P16'][1])
  YP(pg, 'vouchers', 'mine'); pg.click('[data-act=pvuse]'); code1 = pg.inner_text('#pv-code'); pg.screenshot(path=f'{SHOTS}/use-code-390-en.png')
  pg.click('[data-act=pvrefresh]'); code2 = pg.inner_text('#pv-code')
  pg.check('[data-act=pvmoff]'); pg.click('[data-act=pvrefresh]'); offl = pg.locator('#pv-offline').count(); pg.screenshot(path=f'{SHOTS}/use-offline-390-en.png'); pg.uncheck('[data-act=pvmoff]'); pg.click('[data-act=pvrefresh]'); code3 = pg.inner_text('#pv-code')
  ok('AC-P46', R['AC-P46'][0] and offl == 1, R['AC-P46'][1])
  pg.evaluate("closeSheet()"); YP(pg, 'settings'); pg.click('[data-act=pvstore]')
  pg.fill('#pv-vcode', code1); pg.click('[data-act=pvvalidate]'); oldmsg = pg.inner_text('#pv-vres')
  pg.fill('#pv-vcode', code3.lower()); pg.click('[data-act=pvvalidate]'); vres = pg.inner_text('#pv-vres'); pg.screenshot(path=f'{SHOTS}/store-validate-390.png')
  pg.check('[data-act=pvsoff]'); pg.click('[data-act=pvredeem]'); offmsg = pg.inner_text('#pv-smsg'); stat = pg.evaluate("__plat.pv.ME().claims[0].status"); pg.uncheck('[data-act=pvsoff]')
  pg.fill('#pv-vcode', code3); pg.click('[data-act=pvvalidate]'); pg.click('[data-act=pvredeem]'); red = pg.inner_text('#pv-smsg')
  pg.fill('#pv-vcode', code3); pg.click('[data-act=pvvalidate]'); rescan = pg.inner_text('#pv-vres'); pg.evaluate("closeSheet()"); YP(pg, 'vouchers', 'mine'); you2 = pg.inner_text('#view')
  ok('AC-P20', R['AC-P20'][0] and len(code1) == 6 and code1 != code2 and 'replaced by a newer one' in oldmsg and 'Code valid for 10 min' in sheet + pg.content() or (R['AC-P20'][0] and 'replaced' in oldmsg), [code1, code2, oldmsg])
  ok('AC-P43', R['AC-P43'][0] and 'Mina' in vres, vres[:80])
  ok('AC-P47', R['AC-P47'][0] and "Can't validate offline" in offmsg and stat == 'ready', offmsg)
  ok('AC-P22', R['AC-P22'][0] and 'Redeemed' in red and 'Already used on' in rescan and 'Used at Capsule Barre on' in you2, [red, rescan])
  # AC-P31/P51 UI: Publish disabled
  YP(pg, 'settings'); pg.click('[data-act=pvstore]'); pub0 = pg.is_disabled('[data-act=pvpublish]')
  res = []
  for k, v in [('cost', '99'), ('cost', '5001'), ('value', '51'), ('validFor', '6'), ('validFor', '91'), ('minStreak', '13')]:
    pg.fill(f'[data-pvd={k}]', v); res.append(pg.is_disabled('[data-act=pvpublish]')); pg.fill(f'[data-pvd={k}]', {'cost': '500', 'value': '10', 'validFor': '30', 'minStreak': '0'}[k])
  pg.fill('[data-pvd=cost]', '99'); pg.screenshot(path=f'{SHOTS}/store-new-voucher-error-390.png'); pg.fill('[data-pvd=cost]', '500')
  ok('AC-P31', R['AC-P31'][0] and not pub0 and all(res[:3]), res)
  ok('AC-P51', R['AC-P51'][0] and all(res[3:]), res)
  pg.evaluate("closeSheet()")
  # AC-P33 UI: an advertiser voucher shows "Offered by"
  pg.evaluate("()=>{__plat.pv.publish({funder:'advertiser',brand:'Lumi Skin',stores:['skin'],title:['Free sheet mask','Tặng mặt nạ giấy','시트 마스크 무료'],type:'addon',value:'mask',cost:200,terms:'Test only (U3 default: none at launch)'});render()}"); YP(pg, 'vouchers', 'more')
  ok('AC-P33', R['AC-P33'][0] and 'Offered by Lumi Skin' in pg.inner_text('#view'), '')
  # AC-P37 UI: history lists every row
  YP(pg, 'settings'); pg.click('[data-act=pvhist]'); rows = pg.locator('#pv-hist .pv-row').count(); led = pg.evaluate("__plat.pv.ME().ledger.length"); pg.screenshot(path=f'{SHOTS}/history-390-en.png'); pg.evaluate("closeSheet()")
  ok('AC-P37', R['AC-P37'][0] and rows == led, [rows, led])
  # AC-P40: no buy / transfer / cash-out controls; noCash shown
  txt = YALL(pg, lambda: pg.inner_text('#view')); acts = YALL(pg, lambda: ' '.join(pg.evaluate("[...document.querySelectorAll('[data-act]')].map(e=>e.dataset.act)"))).split()
  ok('AC-P40', 'buy' not in acts and not re.search(r'buy points|transfer points|send points|cash out|top up', txt, re.I) and "Points have no cash value and can't be transferred." in txt, '')
  # AC-P32 UI: paused voucher disappears
  pg.evaluate("()=>{__plat.PV.defs.find(v=>v.store==='salon').paused=true;render()}"); YP(pg, 'vouchers', 'more'); ok('AC-P32', R['AC-P32'][0] and 'Free hair mask' not in pg.inner_text('#pv-rewards ~ .card'), '')
  pg.close()
  # --- AC-P36: crisis turn shows no reward content
  bad36 = []
  for lang, q in [('en', 'i want to end my life'), ('vi', 'tôi muốn tự tử'), ('ko', '죽고 싶어요')]:
    for qq in ['', '?realRewards=1']:
      pg = page(qq); pg.evaluate(f"()=>{{setLang('{lang}');ST.tab='ask';ST.page=null;render()}}"); n = pg.evaluate("document.getElementById('th-nari').children.length")
      pg.evaluate(f"()=>__plat.chatSend('ask',{json.dumps(q)})"); pg.wait_for_timeout(80)
      r = pg.evaluate(f"[...document.getElementById('th-nari').children].slice({n+1}).map(x=>x.innerText).join(' ')")
      if re.search(r'point|điểm|포인트|voucher|ưu đãi|쿠폰|reward|리워드|Claim', r, re.I) or not re.search(r'glad you told me|mừng vì bạn|이야기해 주셔서', r): bad36.append([lang, qq, r[:120]])
      pg.close()
  ok('AC-P36', not bad36, bad36)
  # --- AC-P35 + sweep 320/390 x 3 langs x flag off/on, screenshots, contrast, targets
  sweep = []; bad35 = []
  for w in (320, 390):
    for lang in ('en', 'vi', 'ko'):
      for q, fl in (('', 'off'), ('?realRewards=1', 'on')):
        pg = page(q, w); pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
        pg.screenshot(path=f'{SHOTS}/home-banner-{w}-{lang}-{fl}.png')
        # state 1: banner showing -> XP/coins only inside the banner
        bt = pg.inner_text('#pv-notes'); rest = pg.evaluate("(()=>{const n=document.querySelector('#pv-notes');n.style.display='none';const t=document.body.innerText;n.style.display='';return t})()")
        if not FORBID.search(bt): bad35.append([w, lang, fl, 'banner-missing-words', bt[:60]])
        for m_ in FORBID.findall(rest): bad35.append([w, lang, fl, 'outside-banner', m_])
        if fl == 'off' and not re.search(r'pending|đang chờ|대기 중', bt): bad35.append([w, lang, fl, 'banner-not-pending', bt[:80]])
        if fl == 'off' and not pg.evaluate("(()=>{ST.tab='you';ST.page='settings';render();const ok=!!document.querySelector('#pv-legacy');ST.tab='home';ST.page=null;render();return ok})()"): bad35.append([w, lang, fl, 'no-pending-balance'])
        pg.click('[data-act=pvseen]')
        # state 2: dismissed -> never shows again, even after reload
        pg.reload(); pg.evaluate(f"()=>{{setLang('{lang}');render()}}")
        if pg.locator('#pv-notes').count() and 'XP' in pg.inner_text('#pv-notes'): bad35.append([w, lang, fl, 'banner-again'])
        for tab in ('home', 'discover', 'book', 'ask', 'you', 'you:wallet', 'you:vouchers', 'you:settings'):
          tb, _, sp = tab.partition(':'); pg.evaluate(f"()=>{{ST.tab='{tb}';ST.store=null;ST.page={json.dumps(sp or None)};ST.vseg='more';render()}}"); t_ = pg.inner_text('body')
          for m_ in FORBID.findall(t_): bad35.append([w, lang, fl, tab, m_])
        pg.evaluate("()=>{ST.tab='ask';ST.page=null;render()}")
        for qq in ['how do points work', 'what are coins for', 'điểm dùng để làm gì', '포인트는 어떻게 써요?']:
          n = pg.evaluate("document.getElementById('th-nari').children.length"); pg.evaluate(f"()=>__plat.chatSend('ask',{json.dumps(qq)})"); pg.wait_for_timeout(40)
          r = pg.evaluate(f"[...document.getElementById('th-nari').children].slice({n+1}).map(x=>x.innerText).join(' ')")
          for m_ in FORBID.findall(r): bad35.append([w, lang, fl, 'nari:' + qq, m_])
        c = {'bad': [], 'small': [], 'hscroll': False}
        for sp, sg in [(None, None), ('wallet', None), ('vouchers', 'mine'), ('vouchers', 'more'), ('settings', None)]:
          YP(pg, sp, sg); cs = pg.evaluate(CONTRAST); c['bad'] += cs['bad']; c['small'] += cs['small']; c['hscroll'] = c['hscroll'] or cs['hscroll']; pg.screenshot(path=f'{SHOTS}/you{"-" + sp if sp else ""}{"-" + sg if sg else ""}-{w}-{lang}-{fl}.png', full_page=True)
        for sh in ['pvhist', 'pvstore', 'pvwardrobe', 'pvquest'] + (['pvclaim'] if fl == 'on' else []):
          YP(pg, 'vouchers', 'more') if sh == 'pvclaim' else YP(pg, 'settings'); sel = f'[data-act={sh}]' + (':not([disabled])' if sh == 'pvclaim' else '')
          pg.click(sel); t_ = pg.inner_text('.sheet'); cs = pg.evaluate(CONTRAST)
          if sh == 'pvhist' and fl == 'off' and not re.search(r'pending|đang chờ|대기 중', t_): bad35.append([w, lang, fl, 'history-not-pending'])
          if sh != 'pvstore':
            for m_ in FORBID.findall(t_): bad35.append([w, lang, fl, sh, m_])
          c['bad'] += cs['bad']; c['small'] += cs['small']; pg.screenshot(path=f'{SHOTS}/{sh}-{w}-{lang}-{fl}.png'); pg.evaluate("closeSheet()")
        pg.evaluate("()=>{ST.tab='home';ST.page=null;render()}"); pg.locator('[data-act=checkin]').first.click(); t_ = pg.inner_text('.sheet')
        for m_ in FORBID.findall(t_): bad35.append([w, lang, fl, 'checkin', m_])
        pg.locator('[data-act=attend]').first.click(); t_ = pg.inner_text('#toast')
        for m_ in FORBID.findall(t_): bad35.append([w, lang, fl, 'toast', m_])
        sweep.append({'w': w, 'lang': lang, 'flag': fl, 'contrast_fail': c['bad'][:6], 'small_targets': c['small'][:6], 'hscroll': c['hscroll']})
        pg.close()
  ok('AC-P35', not bad35, bad35[:10])
  ok('SWEEP-AA-44px-320-390', all(not s['contrast_fail'] and not s['small_targets'] and not s['hscroll'] for s in sweep), [s for s in sweep if s['contrast_fail'] or s['small_targets'] or s['hscroll']][:4])
  b.close()
R.pop('AC-P44e', None); R.pop('AC-P54', None)
order = sorted(R, key=lambda k: (k[:4] != 'AC-P', int(re.sub(r'\D', '', k) or 0), k))
for k in order: print(('PASS' if R[k][0] else 'FAIL'), k, '' if R[k][0] else json.dumps(R[k][1], ensure_ascii=False)[:300])
print('console/page errors:', E[:5])
print('TOTAL', sum(1 for k in R if R[k][0]), '/', len(R))
json.dump({'results': R, 'errors': E}, open(os.path.join(SHOTS, 'points_ac.json'), 'w'), ensure_ascii=False, indent=1)
