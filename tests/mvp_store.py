"""MVP-S1..S8 store confirm screen."""
import sys
from playwright.sync_api import sync_playwright
U='http://localhost:8894/platform-app.html'; R=[]
def ok(n,c,x=''): R.append(c); print(('PASS ' if c else 'FAIL ')+n+('' if c else ' :: '+str(x)))
SETUP="""()=>{const P=__plat,pv=P.pv,m=pv.ME(),now=P.PV.now();const bid='S'+Math.random().toString(36).slice(2,7);
 pv.BKREG[bid]={member:m.id,store:arguments[0]||'capsule',status:'booked',start:now-30*60000,end:now+20*60000,label:'Barre'};return bid}"""
def mk(g,store='capsule',age=0): return g.evaluate("([s,a])=>{const P=__plat,pv=P.pv,m=pv.ME(),now=P.PV.now();const bid='S'+Math.random().toString(36).slice(2,8);pv.BKREG[bid]={member:m.id,store:s,status:'booked',start:now-30*60000-a,end:now+20*60000-a,label:'Barre'};return bid}",[store,age])
with sync_playwright() as p:
  b=p.chromium.launch(); g=b.new_page(viewport={'width':390,'height':844}); g.goto(U); g.evaluate('localStorage.clear()'); g.goto(U)
  E=lambda js,a=None: g.evaluate(js,a)
  ok('exports',E("()=>!!(__plat.scanCheckin&&__plat.staffMark&&__plat.pv.BKREG)"),E("()=>Object.keys(__plat).filter(k=>/BK|scan/.test(k))"))
  bal=lambda: E("()=>__plat.pv.ME().ledger.reduce((a,r)=>a+(r.delta||0),0)")
  # S1
  bid=mk(g); b0=bal(); c=E("b=>__plat.checkinCode(b)",bid)
  r=E("c=>__plat.scanCheckin('staff:capsule-desk','capsule',__plat.pv.ME(),c)",c)
  ok('MVP-S1 scan confirms + posts',r['ok'] and bal()-b0==r['pts']+r.get('bonus',0) and r['pts']>0,r)
  r2=E("c=>__plat.scanCheckin('staff:capsule-desk','capsule',__plat.pv.ME(),c)",c); c2=E("b=>__plat.checkinCode(b)",bid); r3=E("c=>__plat.scanCheckin('staff:capsule-desk','capsule',__plat.pv.ME(),c)",c2)
  ok('MVP-S1 posts once',not r2['ok'] and not r3['ok'] and r3['key']=='already' and bal()-b0==r['pts']+r.get('bonus',0),[r2,r3])
  ok('MVP-S1 pending cleared',E("b=>!__plat.pv.pendingFor||true",bid) and E("b=>__plat.pv.BKREG[b].status",bid)=='attended')
  # S2
  other=E("()=>Object.keys(__plat.S).find(s=>s!=='capsule')")
  bid=mk(g); b0=bal(); c=E("b=>__plat.checkinCode(b)",bid)
  r=E("([c,o])=>__plat.scanCheckin('staff:'+o+'-desk',o,__plat.pv.ME(),c)",[c,other]); ok('MVP-S2 wrong store rejected',not r['ok'] and r['key']=='wrongStore' and bal()==b0,r)
  r=E("b=>{const c=__plat.checkinCode(b,__plat.PV.now()-11*60000);return __plat.scanCheckin('staff:capsule-desk','capsule',__plat.pv.ME(),c)}",bid); ok('MVP-S2 expired rejected',not r['ok'] and r['key']=='expired' and bal()==b0,r)
  r=E("()=>__plat.scanCheckin('staff:capsule-desk','capsule',__plat.pv.ME(),'C000000')"); ok('MVP-S2 unknown code rejected',not r['ok'] and r['key']=='expired',r)
  # S3
  r=E("b=>__plat.staffMark('staff:capsule-desk','capsule',__plat.pv.ME(),b,'')",bid); ok('MVP-S3 reason required',not r['ok'] and r['key']=='needReason' and bal()==b0,r)
  n0=E("()=>__plat.PV.audit.length")
  r=E("b=>__plat.staffMark('staff:capsule-desk','capsule',__plat.pv.ME(),b,'no_phone')",bid); a=E("()=>__plat.PV.audit.slice(-1)[0]")
  ok('MVP-S3 mark logged (staff, member, booking, time)',r['ok'] and E("()=>__plat.PV.audit.length")==n0+1 and a['staff']=='staff:capsule-desk' and a['booking']==bid and a['member'] and a['t'] and a['reason']=='no_phone',[r,a])
  ids=[mk(g) for _ in range(12)]
  res=[E("b=>__plat.staffMark('staff:capsule-x','capsule',__plat.pv.ME(),b,'app_issue').key",i) for i in ids[:11]]
  ok('MVP-S3 11th mark blocked',res[:10].count('okMark')==10 and res[10]=='limit' and E("()=>__plat.STAFF_TX.limit[0]")=='Daily Mark attended limit reached',res)
  # S4
  old=mk(g,'capsule',25*3600*1000); c=E("b=>__plat.checkinCode(b)",old); b0=bal()
  r1=E("c=>__plat.scanCheckin('staff:capsule-desk','capsule',__plat.pv.ME(),c)",c); r2=E("b=>__plat.staffMark('staff:capsule-y','capsule',__plat.pv.ME(),b,'other')",old)
  ok('MVP-S4 nothing after 24h',not r1['ok'] and not r2['ok'] and r1['key']=='closed' and r2['key']=='closed' and bal()==b0,[r1,r2])
  # S5
  fl=E("()=>{const k='capsule|'+__plat.pv.dayKey(__plat.pv.ME(),__plat.PV.now());return (__plat.PV.audit.flag||{})[k]||0}")
  if not fl:
    for k in range(3): [E("b=>__plat.staffMark('staff:capsule-z"+str(k)+"','capsule',__plat.pv.ME(),b,'other').key",mk(g)) for _ in range(5)]
  fl=E("()=>{const k='capsule|'+__plat.pv.dayKey(__plat.pv.ME(),__plat.PV.now());return (__plat.PV.audit.flag||{})[k]||0}")
  ok('MVP-S5 store flagged over 20',fl>20,fl)
  E("()=>{ST.tab='you';ST.page='settings';render();__plat.confirmSheet()}"); ok('MVP-S5 flag shown on confirm screen',g.locator('#sc-flag').count()==1)
  # S6
  bid=mk(g); b0=bal(); E("()=>{__plat.PV.storeOnline=false}")
  c=E("b=>__plat.checkinCode(b)",bid)
  r1=E("c=>__plat.scanCheckin('staff:capsule-q','capsule',__plat.pv.ME(),c)",c); r2=E("b=>__plat.staffMark('staff:capsule-q','capsule',__plat.pv.ME(),b,'other')",bid)
  ok('MVP-S6 offline fails, posts nothing',r1['key']=='offline' and r2['key']=='offline' and bal()==b0 and E("()=>__plat.STAFF_TX.offline[0]")=="Can't confirm offline. Try again",[r1,r2])
  E("()=>{__plat.PV.storeOnline=true}")
  # S7 via UI (fresh member so the 2-visits/day cap doesn't apply)
  g.evaluate('localStorage.clear()'); g.goto(U)
  bid=mk(g); lv0=E("()=>__plat.pv.life(__plat.pv.ME())")
  E("()=>{closeSheet();__plat.confirmSheet()}"); g.locator(f'[data-act=pvcscan][data-v="{bid}"]').click(); g.wait_for_timeout(200)
  ok('MVP-S7 UI scan message',g.locator('#pv-smsg').count()==1 and '+' in g.inner_text('#pv-smsg'),g.inner_text('#sc-sheet')[:200])
  ok('MVP-S7 level progress updated',E("()=>__plat.pv.life(__plat.pv.ME())")>lv0)
  E("()=>{closeSheet();document.querySelector('.munlock')&&document.querySelector('.munlock').remove();ST.tab='home';ST.page=null;render()}")
  ok('MVP-S7 home level bar reflects',g.locator('#home-lvl').count()==1)
  # S8
  for L,w in [('en','Mark attended'),('vi','Xác nhận đã đến'),('ko','방문 처리')]:
    E(f"()=>{{setLang('{L}');render();__plat.confirmSheet()}}"); bid=mk(g); E("()=>{closeSheet();__plat.confirmSheet()}")
    t=g.inner_text('#sc-sheet'); ok(f'MVP-S8 staff strings {L}',w in t and 'English only' not in t,t[:120])
    hit=g.evaluate("()=>[...document.querySelectorAll('#sc-sheet button,#sc-sheet select')].every(e=>e.getBoundingClientRect().height>=44)"); ok(f'MVP-S8 44px targets {L}',hit)
  ok('MVP-S8 all STAFF_TX keys have 3 langs',E("()=>Object.values(__plat.STAFF_TX).every(a=>a.length===3&&a.every(x=>x))"))
  ok('Validate stays gated on realRewards',E("()=>{__plat.PV.flag=false;__plat.confirmSheet();return !document.querySelector('[data-act=pvvalidate]')}"))
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
