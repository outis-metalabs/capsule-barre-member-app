import json
from playwright.sync_api import sync_playwright
U='http://localhost:8851/platform-app.html';O={}
with sync_playwright() as p:
  b=p.chromium.launch();E=[]
  def new(lang='en',vw=(390,844)):
    pg=b.new_page(viewport={'width':vw[0],'height':vw[1]});pg.on('console',lambda m:E.append(m.text) if m.type in('error','warning') else None);pg.on('pageerror',lambda e:E.append(str(e)))
    pg.goto(U);pg.evaluate(f"()=>{{localStorage.clear();setLang('{lang}');render()}}");return pg
  for lang in ['en','vi','ko']:
    for ans in ['callyes','callno']:
      pg=new(lang);pg.evaluate("()=>{ST.tab='nari';render()}");n0=pg.evaluate("__plat.B.length");pg.locator('[data-act=nmore]').first.click();pg.locator('[data-act=calldemo]').first.click()
      pg.wait_for_selector('[data-act=callpick]',timeout=30000);pg.locator('[data-act=callpick][data-v=court]').click();pg.wait_for_selector('[data-act=callyes]',timeout=30000);cap1=pg.inner_text('#caps');foc=pg.evaluate("document.activeElement.dataset.act")
      pg.screenshot(path=f'call-{lang}-readback.png');pg.locator(f'[data-act={ans}]').click();pg.wait_for_timeout(6000)
      O[f'call|{lang}|{ans}']={'caps':cap1,'focusOnAsk':foc,'booked':pg.evaluate("__plat.B.length")-n0,'callOpen':pg.evaluate("!document.getElementById('call').hidden"),'toast':pg.evaluate("document.getElementById('toast').innerText"),'src':pg.evaluate("__plat.B.slice(-1)[0].source")}
      pg.close()
  pg=new();pg.evaluate("()=>{ST.tab='nari';render()}");pg.locator('[data-act=nmore]').first.click();pg.locator('[data-act=calldemo]').first.click();pg.wait_for_timeout(800);pg.keyboard.press('Escape');pg.wait_for_timeout(300);O['call-esc']=[pg.evaluate("document.getElementById('call').hidden"),pg.evaluate("document.activeElement.dataset.act||document.activeElement.id")]
  # notifications
  pg=new();O['nset-defaults']=pg.evaluate("JSON.stringify(NSET)");pg.evaluate("()=>{ST.page='notif';render()}");O['notif']=pg.inner_text('#view')[:3000]
  # joins
  pg=new();pg.evaluate("()=>{ST.tab='discover';render()}");pg.locator('[data-act=joinsheet]').first.click();pg.locator('.sheet [data-act=qr]').first.click();pg.wait_for_timeout(200);O['qr-sheet']=pg.inner_text('.sheet')[:300];pg.locator('[data-act=qrscan]').click();pg.wait_for_timeout(200);O['join-consent']=pg.inner_text('.sheet')[:600]
  O['consent-boxes']=pg.evaluate("[...document.querySelectorAll('.sheet input[type=checkbox]')].map(i=>[i.checked,i.disabled,i.closest('label')?.innerText.slice(0,60)])")
  pg.locator('.sheet [data-act=joinok]').click();pg.wait_for_timeout(300);O['joined']=[pg.evaluate("__plat.S.nails.joined"),pg.inner_text('#view')[:400],pg.evaluate("document.getElementById('toast').innerText")]
  pg=new();pg.evaluate("()=>{ST.tab='discover';render()}");pg.locator('[data-act=joinsheet]').first.click();pg.locator('.sheet [data-act=linkjoin]').first.click();pg.wait_for_timeout(200);O['link-sheet']=pg.inner_text('.sheet')[:300]
  pg=new();pg.evaluate("()=>{ST.tab='discover';render()}");pg.fill('#dq','cat toc');pg.wait_for_timeout(300);O['search-cattoc']=pg.inner_text('#dres')[:300];pg.fill('#dq','nail');pg.wait_for_timeout(300);O['search-nail']=pg.inner_text('#dres')[:200]
  # store space policies and ads
  pg=new();pg.evaluate("()=>{ST.store='salon';render()}");O['store-salon']=pg.inner_text('#view')[:1500]
  # game: attend flow
  pg=new();x0=pg.evaluate("[ST.xp,ST.coins,ST.steps,JSON.stringify(ST.miss)]");pg.locator('[data-act=checkin]').first.click();pg.wait_for_timeout(300);s1=pg.inner_text('.sheet') if pg.locator('.sheet').count() else pg.evaluate("document.getElementById('toast').innerText");x1=pg.evaluate("[ST.xp,ST.coins,ST.steps]")
  att=pg.locator('[data-act=attend]');a2=None
  if att.count(): att.first.click();pg.wait_for_timeout(300);a2=pg.evaluate("[ST.xp,ST.coins,ST.steps,JSON.stringify(ST.miss)]")
  O['game']={'start':x0,'checkinSheet':s1[:400],'afterCheckin':x1,'afterAttend':a2,'toast':pg.evaluate("document.getElementById('toast').innerText")}
  pg=new();pg.evaluate("()=>{ST.tab='nari';render()}");n0=pg.evaluate("__plat.B.length");pg.locator('[data-act=nagain][data-i="0"]').click();pg.locator('[data-act=chatbook]').last.click();O['xpOnBook']=pg.evaluate("ST.xp")
  # shop
  pg=new();pg.evaluate("()=>{ST.tab='you';render()}");O['you']=pg.inner_text('#view')[:2500];btn=pg.locator('[data-act=buy]')
  O['shop']=[btn.count(),pg.evaluate("[...document.querySelectorAll('[data-act=buy]')].map(b=>b.dataset.c+':'+b.getAttribute('aria-label'))")]
  if btn.count(): btn.first.click();pg.wait_for_timeout(200);O['buy']=[pg.evaluate("[ST.coins,JSON.stringify(ST.owned)]"),pg.evaluate("document.getElementById('toast').innerText")]
  pg=new('vi');pg.evaluate("()=>{ST.tab='you';render()}");btn=pg.locator('[data-act=buy]');O['buy-vi']=None if not btn.count() else [pg.evaluate("document.getElementById('toast').innerText"),pg.evaluate("[...document.querySelectorAll('.tag.ok')].map(e=>e.innerText)")]
  # coin shop removed (spec §10): explicit check that no buy control exists in any language
  O['shop-gone']={l:new(l).evaluate("(()=>{ST.tab='you';render();return document.querySelectorAll('[data-act=buy]').length})()") for l in ['en','vi','ko']}
  assert all(v==0 for v in O['shop-gone'].values()), O['shop-gone']
  pg=new('ko');pg.evaluate("()=>{ST.tab='home';render()}");pg.locator('[data-act=rest]').click();pg.wait_for_timeout(200);O['rest-ko-toast']=pg.evaluate("document.getElementById('toast').innerText")
  O['err']=E
json.dump(O,open('flows.json','w'),ensure_ascii=False,indent=1)
for k,v in O.items(): print('##',k,str(v)[:900])
