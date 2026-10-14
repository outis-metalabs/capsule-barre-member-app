"""PO: Quest · Journey out of MVP. Code kept behind FLAGS.quest=false; no route reaches it."""
import sys, re
from playwright.sync_api import sync_playwright
U=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8894/platform-app.html'; R=[]
def ok(n,c,x=''): R.append(bool(c)); print(('PASS ' if c else 'FAIL ')+n+('' if c else ' :: '+str(x)))
QTXT=re.compile(r'Cross-store quest|Self-care week|Journey|Nhiệm vụ nhiều nơi|Hành trình|여러 매장 퀘스트|여정')
with sync_playwright() as p:
  b=p.chromium.launch(); E=[]
  def pg_(q='',pre=None):
    g=b.new_page(viewport={'width':390,'height':844}); g.on('pageerror',lambda e:E.append(str(e)))
    g.goto(U); g.evaluate('localStorage.clear()')
    if pre: g.evaluate(pre)
    g.goto(U+q); g.wait_for_timeout(250); return g
  g=pg_()
  ok('flag exists and is off',g.evaluate("FLAGS.quest===false && __plat.FLAGS.quest===false"))
  ok('code kept (questSheet, journeySVG)',g.evaluate("typeof questSheet==='function' && typeof journeySVG==='function'"))
  for r in ['quest','journey','tab:quest','tab:journey','page:quest']:
    g.evaluate(f"go('{r}')"); ok(f'go({r}) → Home, no sheet',g.evaluate("ST.tab==='home'&&!ST.page&&!document.querySelector('.sheet')"))
  g.evaluate("()=>{ST.tab='cici';render();questSheet()}"); ok('questSheet() direct → Home, no sheet',g.evaluate("ST.tab==='home'&&!document.querySelector('.sheet')"))
  g.evaluate("()=>{ST.tab='you';render();document.body.insertAdjacentHTML('beforeend','<button id=q data-act=pvquest></button>');document.getElementById('q').click();document.getElementById('q').remove()}")
  ok('stale pvquest button → Home',g.evaluate("ST.tab==='home'&&!document.querySelector('.sheet')"))
  g.evaluate("()=>{ST.page='quest';render()}"); ok('ST.page=quest → cleared',g.evaluate("ST.page===null"))
  g.evaluate("()=>{ST.page='journey';sysBack()}"); ok('system back from journey page safe',g.evaluate("ST.page===null"))
  # links: no visible entry anywhere
  txt=''
  for L in ['en','vi','ko']:
    for js in ["ST.tab='home'","ST.tab='discover'","ST.tab='cici'","ST.tab='you'","ST.tab='you';ST.page='settings'","ST.tab='you';ST.page='points'","ST.tab='you';ST.page='wallet'","ST.tab='you';ST.page='look'"]:
      g.evaluate(f"()=>{{setLang('{L}');ST.page=null;ST.store=null;{js};render()}}"); txt+=g.inner_text('body')
      ok(f'no quest/journey links [{L}] {js}',not g.locator('[data-act=pvquest],[data-act=quest],[data-act=journey],[data-v=quest],[data-v=journey]').count())
  ok('no quest/journey copy visible',not QTXT.search(txt),QTXT.findall(txt)[:5])
  g.evaluate("()=>{setLang('en');joinSheet()}"); ok('join sheet copy no longer mentions journey','journey' not in g.inner_text('.sheet').lower())
  # visits don't advance hidden state
  st0=g.evaluate("JSON.stringify([ST.steps,ST.quest])")
  g.evaluate("()=>{closeSheet();const b=__plat.B.find(x=>x.store==='capsule'&&x.d>=0);if(b)attend(b)}")
  ok('attend does not touch steps/quest state',g.evaluate("JSON.stringify([ST.steps,ST.quest])")==st0)
  ok('no quest analytics',not g.evaluate("__plat.EVT.some(e=>/quest|journey/i.test(e.e+JSON.stringify(e)))"))
  g.close()
  # deep links
  for h in ['#/quest','#/journey','#/quest?x=1']:
    g=pg_(h); ok(f'deep link {h} → Home',g.evaluate("ST.tab==='home'&&!ST.page&&!document.querySelector('.sheet')&&!location.hash")); g.close()
  g=pg_(); g.evaluate("location.hash='#/journey'"); g.wait_for_timeout(250); ok('same-doc hash #/journey → Home',g.evaluate("ST.tab==='home'&&!location.hash")); g.close()
  # saved state
  g=pg_('',"()=>{localStorage.setItem('cici.tab','quest');localStorage.setItem('nari.tab','journey')}"); ok('saved tab quest → Home',g.evaluate("ST.tab==='home'")); g.close()
  # voice-demo strings gone
  g=pg_(); ok('voice-demo strings removed',g.evaluate("['callCici','ciciDemo','mute','unmute','hang','more'].every(k=>['en','vi','ko'].every(l=>!(k in STR[l])))")); g.close()
  ok('no page errors',not E,E[:3])
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
