import json
from playwright.sync_api import sync_playwright
U='http://localhost:8851/platform-app.html';O={}
def sheet(pg): return pg.evaluate("(()=>{const s=document.querySelector('.sheet');return s?s.innerText.replace(/\\n+/g,' | ').slice(0,400):null})()")
with sync_playwright() as p:
  b=p.chromium.launch()
  for vw in [(390,844),(320,568)]:
   for lang in ['en','vi','ko']:
    for i in range(5):
      pg=b.new_page(viewport={'width':vw[0],'height':vw[1]});E=[]
      pg.on('console',lambda m:E.append(m.text) if m.type in('error','warning') else None);pg.on('pageerror',lambda e:E.append(str(e)))
      pg.goto(U);pg.evaluate(f"()=>{{localStorage.clear();setLang('{lang}');ST.tab='cici';render()}}");n0=pg.evaluate("__plat.B.length")
      taps=[];pg.locator(f'[data-act=nagain][data-i="{i}"]').click();taps.append('nagain');pg.wait_for_timeout(150)
      s1=pg.evaluate("(document.querySelector('#th-cici .mcard')||{}).innerText||''").replace('\n',' | ')  # Nari tab: inline confirm card, next slot pre-picked
      if pg.locator('[data-act=chatbook]').count(): s2=s1;pg.locator('[data-act=chatbook]').last.click();taps.append('chatbook')
      for step in range(0 if 'chatbook' in taps else 4):
        if pg.locator('.sheet [data-act=dobook]').count(): 
          s2=sheet(pg);pg.locator('.sheet [data-act=dobook]').first.click();taps.append('dobook');break
        el=pg.locator('.sheet [data-act=slot], .sheet [data-act=classpick]').first
        if el.count(): el.click();taps.append('slot');pg.wait_for_timeout(150);continue
        break
      pg.wait_for_timeout(200)
      O[f'{vw[0]}|{lang}|{i}']={'taps':len(taps),'path':taps,'booked':pg.evaluate("__plat.B.length")-n0,'slotSheet':s1,'confirm':s2 if ('dobook' in taps or 'chatbook' in taps) else None,'after':sheet(pg),'err':E}
      if vw[0]==390 and lang=='en': pg.screenshot(path=f'tap-{i}-done.png')
      pg.close()
json.dump(O,open('taps.json','w'),ensure_ascii=False,indent=1)
for k,v in O.items(): print(k,v['taps'],v['path'],'booked',v['booked'],v['err'][:1])
for k in ['390|en|0','390|en|1','390|en|2','390|en|3','390|en|4']: print(k,'CONFIRM:',O[k]['confirm']);print('  AFTER:',O[k]['after'])
