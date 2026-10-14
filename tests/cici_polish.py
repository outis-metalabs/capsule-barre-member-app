"""PR17 review P3s: KO SR prefix, KO instructor names, Cici mark, voice demo removed."""
import sys
from playwright.sync_api import sync_playwright
U=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8894/platform-app.html'; R=[]
def ok(n,c,x=''): R.append(bool(c)); print(('PASS ' if c else 'FAIL ')+n+('' if c else ' :: '+str(x)))
with sync_playwright() as p:
  b=p.chromium.launch();g=b.new_page();g.goto(U);g.evaluate('localStorage.clear()');g.goto(U)
  ok('P3-3 header mark is C',g.inner_text('.brand .nm')=='C')
  g.evaluate("()=>{go('tab:cici');__plat.chatSend('cici','바레 내일 오전')}")
  sr=g.evaluate("[...document.querySelectorAll('#th-cici .msg.n .vh')].map(e=>e.textContent)"); ok('P3-1 KO SR prefix uses 씨씨',sr and all(x=='씨씨: ' for x in sr),sr)
  g.locator('#th-cici .mchips .chip').first.click(); c=g.inner_text('#th-cici .mcard'); ok('P3-2 KO review card says 유나',('유나' in c) and 'Yuna' not in c,c[:200])
  g.evaluate("()=>{setLang('en');render()}"); ok('P3-1 EN SR prefix Cici',g.evaluate("[...document.querySelectorAll('#th-cici .msg.n .vh')].every(e=>e.textContent==='Cici: ')"))
  ok('P3-5 voice demo code removed',g.evaluate("typeof openCall==='undefined'&&typeof endCall==='undefined'&&!document.getElementById('call')"))
  g.evaluate("()=>{__plat.pv.setFlag?__plat.pv.setFlag(true):PV.flag=true;ST.tab='you';ST.page='wallet';render()}")
  ok('P3-3 wallet points badge not N',g.evaluate("![...document.querySelectorAll('#view .slogo')].some(e=>e.textContent.trim()==='N')"))
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
