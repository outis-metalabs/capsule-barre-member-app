"""Open map on My bookings (upcoming + past) and the booking confirmation; KR = Naver Map + KakaoMap, other markets = Google Maps;
hidden without an address; EN/KO/VI, 44px, AA. Plus: Home migration card no longer says legacy coins are pending. Usage: bookings_map.py [base_url] [shots_dir]"""
import sys, os, re
from urllib.parse import urlparse, unquote
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/bookings-map'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
A11Y = r"""(sel)=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};
 const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c}return 'rgb(255,255,255)'};
 return [...document.querySelectorAll(sel)].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect(),a=lum(getComputedStyle(e).color),b=lum(bg(e));return {t:e.innerText.trim(),h:Math.round(r.height),w:Math.round(r.width),c:+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2),target:e.target,rel:e.rel,href:e.href,map:e.dataset.map}})}"""
with sync_playwright() as p:
  b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844})
  def page(q='', lang='en'):
    g = ctx.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.E = E
    NET = []; g.on('request', lambda r: NET.append(r.url) if not r.url.startswith(('http://localhost', 'data:', 'blob:')) else None); g.NET = NET
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(250); g.evaluate(f"()=>{{setLang('{lang}');render()}}"); return g
  J = lambda g, js: g.evaluate(js)
  def check(g, where, sel, mk, lang):
    a = J(g, f"(s)=>({A11Y})(s)".replace('(s)=>(', '(s)=>(') if False else A11Y, sel) if False else g.evaluate(A11Y, sel)
    ok(f'[{mk}/{lang}] {where}: Open map present', len(a) >= 1, a)
    if not a: return a
    ok(f'[{mk}/{lang}] {where}: 44px targets + AA contrast', all(x['h'] >= 44 and x['w'] >= 44 and x['c'] >= 4.5 for x in a), a)
    ok(f'[{mk}/{lang}] {where}: opens in a new tab/app link (target=_blank, noopener)', all(x['target'] == '_blank' and 'noopener' in x['rel'] for x in a), a)
    hosts = [urlparse(x['href']).netloc for x in a]
    if mk == 'kr': ok(f'[kr/{lang}] {where}: Naver Map main + KakaoMap option', 'map.naver.com' in hosts and 'map.kakao.com' in hosts and a[0]['map'] == 'naver', hosts)
    else: ok(f'[vn/{lang}] {where}: Google Maps only', set(hosts) == {'www.google.com'} and '/maps/' in a[0]['href'], hosts)
    return a
  for mk, q in [('kr', ''), ('vn', '?market=vn')]:
    for L in ['en', 'ko', 'vi']:
      g = page(q, L)
      # confirmation screen: book via the sheet
      J(g, "()=>{ST.store='salon';render()}"); g.click('#st-book'); g.click('#bk-svcs .svc >> nth=0'); g.click('.sheet .slot:not([disabled]) >> nth=0'); g.click('.sheet [data-act=dobook]'); g.wait_for_timeout(300)
      a = check(g, 'confirmation', '#bk-map .bkmap', mk, L)
      if a: ok(f'[{mk}/{L}] confirmation: uses the store address/coordinates', ('37.' in a[-1]['href'] or '10.' in a[-1]['href']) or unquote(a[0]['href']).endswith(J(g, "S.salon.addr")), [x['href'] for x in a])
      ov = J(g, "(()=>{const t=document.querySelector('#toast');if(!t||t.hidden)return [];const r=t.getBoundingClientRect();return [...document.querySelectorAll('#bk-done-acts a,#bk-done-acts button')].filter(e=>{const q=e.getBoundingClientRect();return r.left<q.right&&q.left<r.right&&r.top<q.bottom&&q.top<r.bottom}).map(e=>e.innerText)})()")
      ok(f'[{mk}/{L}] confirmation: toast covers no button', not ov, ov)
      if L in ('en', 'ko') and mk == 'kr': J(g, "(()=>{const s=document.querySelector('.sheet');s.scrollTop=s.scrollHeight})()"); g.wait_for_timeout(500); g.screenshot(path=f'{SH}/confirm-{L}-390.png')
      J(g, "closeSheet();openBookings('up')"); g.wait_for_timeout(200)
      check(g, 'My bookings upcoming', '.bkrow .bkmap', mk, L)
      if L in ('en', 'ko') and mk == 'kr': J(g, "scrollTo(0,0)"); g.wait_for_timeout(300); g.screenshot(path=f'{SH}/upcoming-{L}-390.png')
      J(g, "openBookings('past')"); g.wait_for_timeout(200)
      check(g, 'My bookings past', '.bkrow .bkmap', mk, L)
      if L in ('en', 'ko') and mk == 'kr': J(g, "scrollTo(0,0)"); g.wait_for_timeout(300); g.screenshot(path=f'{SH}/past-{L}-390.png')
      ok(f'[{mk}/{L}] no map request is made until tapped (links only)', not [u for u in g.NET if 'map' in u], g.NET[:3])
      ok(f'[{mk}/{L}] no page errors', not g.E, g.E[:2]); g.close()
  # no address -> no button
  g = page(); n = J(g, "(()=>{delete S.capsule.addr;delete S.capsule.geo;openBookings('up');return [...document.querySelectorAll('.bkrow')].filter(r=>/Capsule Barre/.test(r.innerText)).map(r=>r.querySelectorAll('.bkmap').length)})()")
  ok('store without an address: Open map hidden', n and all(x == 0 for x in n), n)
  ok('a store without address yields no map links (mapLinks empty)', J(g, "mapLinks('capsule')==='' && mapLinks('moc')===''"))
  g.close()
  # click opens a new tab with the map URL (popup), app stays
  g = page(); J(g, "openBookings('up')"); g.wait_for_timeout(200)
  ctx.route(re.compile(r'https://(map\.naver\.com|map\.kakao\.com|www\.google\.com)/.*'), lambda r: r.fulfill(status=200, body='map'))
  with g.expect_popup() as pi: g.click('.bkrow .bkmap[data-map=naver] >> nth=0')
  pop = pi.value; ok('tap opens Naver Map in a new tab; app page unchanged', 'map.naver.com' in pop.url and J(g, "ST.page") == 'bookings', pop.url); pop.close(); g.close()
  # Home migration card: truthful, no "coins pending"
  for L in ['en', 'ko', 'vi']:
    g = page(lang=L); J(g, "()=>{ST.tab='home';ST.page=null;render()}"); v = g.inner_text('#view')
    ok(f'[{L}] Home migration card no longer says coins are pending', not re.search(r'coins? (are|is) pending|xu của bạn đang chờ|코인 \d+개는 대기', v, re.I) and ('XP' in v), re.findall(r'.{0,40}(?:coin|xu |코인).{0,40}', v)[:3])
    if L in ('en', 'ko'): g.wait_for_timeout(400); g.screenshot(path=f'{SH}/home-migration-{L}-390.png')
    g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
