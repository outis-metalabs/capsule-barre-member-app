"""PR #14 Discover photos: photo-load fallback (image URLs blocked), KO/EN neighbourhood search, sample data. Usage: python3 tests/discover_photos.py [url]"""
import sys, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8851/platform-app.html'
R = {}
def ok(k, c, d=''): R[k] = [bool(c), str(d)[:200]]
with sync_playwright() as p:
  b = p.chromium.launch()
  for lang in ['ko', 'en', 'vi']:
    pg = b.new_page(viewport={'width': 390, 'height': 844}); E = []
    pg.on('pageerror', lambda e: E.append(str(e)))
    pg.route('**/assets/shops/*', lambda r: r.abort())
    pg.goto(U); pg.evaluate(f"()=>{{localStorage.clear();setLang('{lang}');ST.tab='discover';ST.store=null;render()}}")
    for _ in range(3): pg.mouse.wheel(0, 1500); pg.wait_for_timeout(300)
    pg.wait_for_timeout(500)
    r = pg.evaluate("""()=>{const ph=[...document.querySelectorAll('#dres .dphoto')];
      return {n:ph.length, imgs:document.querySelectorAll('#dres img').length, init:ph.filter(e=>e.classList.contains('dinit')&&e.querySelector('span')&&e.querySelector('span').textContent.trim().length>=2).length,
        h:ph.map(e=>e.getBoundingClientRect().height).filter(x=>x<100).length}}""")
    ok(f'blocked: every card falls back to brand tint + initials [{lang}]', r['n'] >= 10 and r['init'] == r['n'] and r['imgs'] == 0, r)
    ok(f'blocked: cards keep their 16:10 size [{lang}]', r['h'] == 0, r)
    j = pg.evaluate("()=>{const j=document.querySelector('#dc-capsule .dov.dj'),p=document.querySelector('#dc-capsule .dphoto');return j&&p?[j.getBoundingClientRect().top>=p.getBoundingClientRect().top, p.innerText.trim()]:null}")
    ok(f'blocked: Joined chip shown over the tint, no alt text in the card [{lang}]', j and j[0] and j[1] == 'CB', j)
    pg.evaluate("()=>{ST.store='capsule';render()}"); pg.wait_for_timeout(600)
    h = pg.evaluate("()=>{const c=document.querySelector('.cover');return c?[!!c.querySelector('img'), getComputedStyle(c).backgroundImage.includes('gradient'), c.getBoundingClientRect().height]:null}")
    ok(f'blocked: store hero swaps to brand gradient [{lang}]', h and not h[0] and h[1] and h[2] > 60, h)
    ok(f'no page errors [{lang}]', not E, E)
    pg.close()
  pg = b.new_page(viewport={'width': 390, 'height': 844}); pg.goto(U)
  pg.evaluate("()=>{localStorage.clear();setLang('ko');ST.tab='discover';render()}")
  pg.wait_for_timeout(800)
  ok('photos load normally (no fallback)', pg.evaluate("()=>[...document.querySelectorAll('#dres .dimg')].length>=1 && !document.querySelector('#dres .pfail')"))
  ok('data: photo path + sample flag on all 10 stores', pg.evaluate("()=>['capsule','salon','skin','spa','pickle','nails','yoga','barber','moc','rally'].every(s=>__plat.S[s].photo==='assets/shops/'+s+'.webp'&&__plat.S[s].sample===true)"))
  exp = {'한남': 'nails', '성수': 'capsule', '연남': 'salon', '망원': 'barber', '뚝섬': 'pickle', '청담': 'spa', '강남': 'skin', '서울숲': 'yoga', 'Hannam': 'nails', 'seongsu dong': 'capsule', 'Yeonnam-dong': 'salon', 'mangwon': 'barber'}
  for q, sid in exp.items():
    pg.fill('#dq', q); pg.wait_for_timeout(250)
    ids = pg.evaluate("()=>[...document.querySelectorAll('#dres .dcard')].map(e=>e.id)")
    ok(f'area search "{q}" finds {sid}', f'dc-{sid}' in ids, ids)
  pg.fill('#dq', '부산'); pg.wait_for_timeout(250)
  ok('area search "부산" finds nothing', pg.evaluate("()=>document.querySelectorAll('#dres .dcard').length") == 0)
for k, (c, d) in R.items(): print('PASS' if c else 'FAIL', k, '' if c else d)
print('TOTAL', sum(1 for c, _ in R.values() if c), '/', len(R))
