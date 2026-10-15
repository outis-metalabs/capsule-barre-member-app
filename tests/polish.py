"""UI polish (PR #13 r2): Nari never covers content, opaque header, chat-app Nari tab, store action row, no wrapped button text. Usage: python3 tests/polish.py [url]"""
import sys, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
R = {}; E = []
def ok(k, c, d=''): R[k] = [bool(c), d]
WRAP = """()=>[...document.querySelectorAll('#view button.btn, #view .chip, .sheet button.btn, #toast button')].filter(e=>e.offsetParent).map(e=>{const r=document.createRange();r.selectNodeContents(e);const ts=[...r.getClientRects()].filter(q=>q.width>2).map(q=>q.top);const sp=ts.length?Math.max(...ts)-Math.min(...ts):0;return {t:e.innerText.trim().slice(0,40),wrap:sp>10&&!e.querySelector('br')&&!e.classList.contains('sact'),over:e.scrollWidth>e.clientWidth+1}}).filter(x=>x.wrap||x.over)"""
with sync_playwright() as p:
  br = p.chromium.launch()
  for L in ('ko', 'en'):
    pg = br.new_page(viewport={'width': 390, 'height': 844}); pg.on('pageerror', lambda e: E.append(str(e)))
    pg.goto(U); pg.evaluate("()=>localStorage.clear()"); pg.goto(U); pg.evaluate(f"()=>{{setLang('{L}');render()}}"); pg.wait_for_timeout(200)
    J = lambda js: pg.evaluate(js)
    hd = J("()=>{const h=document.querySelector('header.top'),cs=getComputedStyle(h);return {bg:cs.backgroundColor,z:+cs.zIndex,bf:cs.backdropFilter}}")
    ok(f'{L} header opaque and above confetti', hd['bg'].startswith('rgb(') and hd['z'] > 12 and hd['bf'] in ('none', ''), hd)
    J("()=>{window.scrollTo(0,600);celebrate();toast('+10')}"); pg.wait_for_function("()=>{const e=document.getElementById('wintoast');return e&&!e.hidden}", timeout=4000); pg.wait_for_timeout(320)
    w = J("()=>{const t=document.getElementById('wintoast').getBoundingClientRect(),tb=document.getElementById('tabs').getBoundingClientRect().top,h=document.querySelector('header.top').getBoundingClientRect(),c=document.querySelector('.confetti');return {top:t.top,bottom:t.bottom,hb:h.bottom,tb,h:t.height,pops:document.querySelectorAll('.cheerpop').length,cz:c?+getComputedStyle(c).zIndex:0,hz:+getComputedStyle(document.querySelector('header.top')).zIndex}}")
    ok(f'{L} win = bottom toast above the tab bar (PO 2026-10-15: no header pill), no floating Cici', w['pops'] == 0 and w['top'] >= w['hb'] and w['bottom'] <= w['tb'] and w['h'] <= 72 and w['cz'] < w['hz'], w)
    # the header hides confetti: topmost element at a header point is the header
    ok(f'{L} confetti never shows through the header', J("()=>{const e=document.elementFromPoint(200,20);return !!(e&&e.closest('header.top'))}"))
    pg.wait_for_timeout(3700); J("()=>window.scrollTo(0,0)")
    # Nari tab empty
    J("()=>{setTab('cici');render()}"); pg.wait_for_timeout(200)
    e = J("()=>{const c=document.querySelector('.nhero .cut-wave'),i=document.getElementById('in-cici').getBoundingClientRect(),n=document.getElementById('tabs').getBoundingClientRect();return {h:c?Math.round(c.getBoundingClientRect().height):0,inBottom:i.bottom,navTop:n.top,q:document.querySelectorAll('#view [data-act=qbook]').length}}")
    ok(f'{L} empty Nari: large wave cut-out + greeting', e['h'] >= 180 and J("()=>!!document.querySelector('.nhero .msg.n')"), e)
    ok(f'{L} input pinned to the bottom, above the tab bar', e['navTop'] - e['inBottom'] < 80 and e['inBottom'] <= e['navTop'], e)
    ok(f'{L} quick chips once on empty', e['q'] == 1, e)
    J("()=>toast('x')"); t2 = J("()=>{const t=document.getElementById('toast').getBoundingClientRect(),i=document.querySelector('#view .dock').getBoundingClientRect();return {tb:t.bottom,dt:i.top}}")
    ok(f'{L} Nari tab: toast sits above the docked input', t2['tb'] <= t2['dt'] + 1, t2); J("()=>{document.getElementById('toast').hidden=true}")
    pg.click('[data-act=qbook]'); pg.wait_for_timeout(200)
    r = J("()=>({q:document.querySelectorAll('#view [data-act=qbook],#view [data-act=qask]').length,sug:[...document.querySelectorAll('#th-cici .mchips .chip.sug')].map(c=>getComputedStyle(c).borderStyle),plain:getComputedStyle(document.querySelector('.chip:not(.sug)')||document.body).borderStyle,ib:document.getElementById('in-cici').getBoundingClientRect().bottom,nt:document.getElementById('tabs').getBoundingClientRect().top})")
    ok(f'{L} after a reply: no repeated Book/Ask/My bookings chips', r['q'] == 0, r)
    ok(f'{L} example chips use the lighter suggestion style', len(r['sug']) >= 3 and all(x == 'dashed' for x in r['sug']), r)
    ok(f'{L} input still pinned after a reply', 0 <= r['nt'] - r['ib'] < 80, r)
    for q in ['주차 돼요?', 'what time do you open?', '내일 바레']: J(f"()=>{{__plat.chatSend('cici',{json.dumps(q)});render()}}")
    pg.wait_for_timeout(100); J("()=>window.scrollTo(0,0)"); pg.wait_for_timeout(50)
    k = J("()=>{const i=document.getElementById('in-cici').getBoundingClientRect(),n=document.getElementById('tabs').getBoundingClientRect();return {ib:i.bottom,nt:n.top,long:document.documentElement.scrollHeight>innerHeight}}")
    ok(f'{L} long thread: input stays docked above the tab bar while scrolled to top', (not k['long']) or (0 <= k['nt'] - k['ib'] < 80), k)
    # store page
    J("()=>{ST.tab='discover';ST.store='capsule';ST.page=null;render();window.scrollTo(0,0)}"); pg.wait_for_timeout(100)
    sp = J("()=>{const b=document.querySelector('.sacts > #st-book'),a=[...document.querySelectorAll('.sact3 .sact')].map(x=>{const r=x.getBoundingClientRect();return [x.innerText.replace(/\\s+/g,' ').trim(),Math.round(r.width),Math.round(r.height),Math.round(r.top)]});return {bw:b?Math.round(b.getBoundingClientRect().width):0,cw:Math.round(document.querySelector('.sacts').getBoundingClientRect().width),a,call:document.querySelector('.sact[data-act=callstore]')?.getAttribute('aria-label')}}")
    labels = {'ko': ['전화', '카카오톡', '지도'], 'en': ['Call', 'KakaoTalk', 'Map']}[L]
    ok(f'{L} store: full-width Book here', sp['bw'] == sp['cw'] and sp['bw'] > 300, sp)
    ok(f'{L} store: 3 equal icon+label buttons Call/KakaoTalk/Map, one row', [x[0] for x in sp['a']] == labels and len({x[1] for x in sp['a']}) == 1 and len({x[3] for x in sp['a']}) == 1 and all(x[2] >= 44 for x in sp['a']), sp)
    ok(f'{L} store: Call keeps the full store name for screen readers', 'Capsule Barre' in (sp['call'] or ''), sp['call'])
    # no wrapped button text across main screens
    bad = {}
    for nm, js in [('home', "setTab('home')"), ('discover', "setTab('discover')"), ('cici', "setTab('cici')"), ('you', "setTab('you')"), ('you-wallet', "setTab('you');ST.page='wallet'"), ('you-vouchers', "setTab('you');ST.page='vouchers';ST.vseg='more'"), ('you-settings', "setTab('you');ST.page='settings'"), ('store', "ST.tab='discover';ST.store='capsule'"), ('store-salon', "ST.tab='discover';ST.store='salon'"), ('bookings', "__plat.openBookings('up')"), ('past', "__plat.openBookings('past')")]:
      for w in (320, 390):
        pg.set_viewport_size({'width': w, 'height': 844}); J(f"()=>{{ST.page=null;ST.store=null;{js};render()}}"); pg.wait_for_timeout(40); x = J(WRAP)
        if x: bad[f'{nm}@{w}'] = x
    ok(f'{L} no text wrapping or overflow inside buttons (8 screens, 320+390)', not bad, bad)
    pg.close()
  br.close()
ok('no page errors', not E, E[:3])
for k, (v, d) in R.items(): print('PASS' if v else 'FAIL', k, '' if v else json.dumps(d, ensure_ascii=False)[:400])
print('TOTAL', sum(v for v, _ in R.values()), '/', len(R))
