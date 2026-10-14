import json
from playwright.sync_api import sync_playwright
U='http://localhost:8851/platform-app.html';O={}
A="(()=>{const e=document.activeElement;const cs=getComputedStyle(e);return (e.dataset.act||e.id||e.tagName)+'|'+(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,25)+'|'+(cs.outlineStyle!='none'&&cs.outlineWidth!='0px'||cs.boxShadow!='none')})()"
with sync_playwright() as p:
  b=p.chromium.launch()
  for vw in [(390,844),(320,568)]:
    pg=b.new_page(viewport={'width':vw[0],'height':vw[1]});pg.goto(U);pg.evaluate("localStorage.clear()");pg.reload();pg.wait_for_timeout(400)
    sk=pg.evaluate("(()=>{const a=document.querySelector('a[href^=\"#\"]');const r=a.getBoundingClientRect();return [a.innerText,r.x,r.y,r.width,r.height,getComputedStyle(a).clipPath,getComputedStyle(a).position,getComputedStyle(a).transform]})()")
    seq=[]
    for i in range(14): pg.keyboard.press('Tab');seq.append(pg.evaluate(A))
    pg.screenshot(path=f'kb-skip-{vw[0]}.png',clip={'x':0,'y':0,'width':vw[0],'height':200}) 
    # open book again via keyboard
    pg.evaluate("()=>{ST.tab='book';render()}");pg.locator('[data-act=again][data-i="1"]').focus();pg.keyboard.press('Enter');pg.wait_for_timeout(200);inSheet=pg.evaluate("!!document.activeElement.closest('.sheet')")
    trap=[]
    for i in range(40): pg.keyboard.press('Tab');trap.append(pg.evaluate("!!document.activeElement.closest('.sheet')"))
    pg.keyboard.press('Escape');pg.wait_for_timeout(200);esc=[pg.evaluate("!!document.querySelector('.sheet')"),pg.evaluate(A)]
    # chat by keyboard
    pg.evaluate("()=>{ST.tab='book';render()}");pg.locator('#in-book').focus();pg.keyboard.type('haircut with Linh Saturday afternoon');pg.keyboard.press('Enter');pg.wait_for_timeout(200);chat=pg.evaluate(A)
    # discover chips arrow / enter
    pg.evaluate("()=>{ST.tab='discover';render()}");pg.locator('[data-act=dview][data-v=map]').focus();pg.keyboard.press('Enter');pg.wait_for_timeout(200);pg.locator('[data-act=pin]').first.focus();pg.keyboard.press('Enter');pg.wait_for_timeout(200);pin=[pg.evaluate("DF.pin"),pg.evaluate(A)]
    O[vw[0]]={'skip':sk,'tabseq':seq,'sheetFocus':inSheet,'trap':all(trap),'esc':esc,'chatFocus':chat,'pin':pin}
json.dump(O,open('kb.json','w'),ensure_ascii=False,indent=1);print(json.dumps(O,ensure_ascii=False)[:3000])
