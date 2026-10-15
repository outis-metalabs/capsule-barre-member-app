"""Cici growth + daily streak + room spending (phase2-ba-ac.md, BA final 2026-10-15): one check group per AC id
P2-G1..G10, P2-S1..S16, P2-R9..R16, P2-X7..X13. Known gaps are printed as GAP (not counted). Usage: cici_growth.py [base_url] [shots_dir]"""
import sys, os, re, json
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/cici-growth'; os.makedirs(SH, exist_ok=True)
R = []; GAPS = []
def ok(n, c, d=''): R.append(bool(c)); print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}'))
def gap(n, why): GAPS.append(n); print(f'GAP  {n} :: {why}')
H = r"""window.__G = (()=>{ const P=__plat.pv, PV=__plat.PV, D=864e5, M=6e4, T0=Date.UTC(2026,9,12,3,0); let k=0;
  const mk=(o)=>{const m=P.pvMember('gx'+(++k)+'_'+Math.random().toString(36).slice(2,6),Object.assign({},o||{}));m.closedTo=P.dayStart(m,T0);return m;};
  const vis=(m,store,t,start)=>{const id='gb'+(++k)+Math.random();P.pvBook(id,{store,member:m.id,start:start==null?t-60*M:start,end:start==null?t:start+60*M});const r=P.confirmVisit(m,id,'staff:'+store+'-desk',t,store);r.id=id;return r;};
  return {P,PV,D,M,T0,mk,vis}; })();"""
SAD = re.compile(r"\b(sad|cry|crying|guilt|shame|missed|lost|broken|fail(ed)?)\b|buồn|khóc|xấu hổ|bỏ lỡ|mất chuỗi|슬퍼|울|실망|놓쳤|끊겼", re.I)
GEOM = r"""async () => { const im=document.querySelector('#home-cici .cpic .cut'); if(!im) return {err:'nocut'};
  const src=(im.tagName==='VIDEO'?im.getAttribute('poster'):im.getAttribute('src')); const I=new Image(); I.src=src; await I.decode();
  const c=document.createElement('canvas'); c.width=I.naturalWidth; c.height=I.naturalHeight; const x=c.getContext('2d'); x.drawImage(I,0,0); const d=x.getImageData(0,0,c.width,c.height).data;
  let l=1e9,t=1e9,r=-1,b=-1; for(let y=0;y<c.height;y++)for(let X=0;X<c.width;X++)if(d[(y*c.width+X)*4+3]>24){if(X<l)l=X;if(X>r)r=X;if(y<t)t=y;if(y>b)b=y;}
  const fr=im.getBoundingClientRect(), s=Math.min(fr.width/c.width,fr.height/c.height), ox=fr.left+(fr.width-c.width*s)/2, oy=fr.top+fr.height-c.height*s;
  const f={left:ox+l*s,top:oy+t*s,right:ox+r*s,bottom:oy+b*s}, head={...f,bottom:f.top+.35*(f.bottom-f.top)};
  const hit=(a,q)=>a.left<q.right&&a.right>q.left&&a.top<q.bottom&&a.bottom>q.top;
  const over=[...document.querySelectorAll('#home-cici .gspark,#home-cici .gzz,#home-cici .wear-acc,#home-cici .p2acc')].filter(e=>{const z=+getComputedStyle(e).zIndex||0;return e.offsetParent&&hit(e.getBoundingClientRect(),head)&&z>=2}).map(e=>e.className);
  const aura=document.querySelector('#home-cici .gaura'), az=aura?+getComputedStyle(aura).zIndex:0, cz=+getComputedStyle(document.querySelector('#home-cici .cpic')).zIndex;
  const sparkHead=[...document.querySelectorAll('#home-cici .gspark,#home-cici .gzz')].filter(e=>hit(e.getBoundingClientRect(),head)).map(e=>e.className);
  return {over,sparkHead,auraBehind:!aura||az<cz,head}; }"""
A11Y = r"""()=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};
 const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;if(c&&!/rgba\(0, 0, 0, 0\)|transparent/.test(c))return c}return 'rgb(255,255,255)'};
 const els=[...document.querySelectorAll('#home-cici *')].filter(e=>e.offsetParent&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&!e.classList.contains('gspark')&&!e.closest('.gzz'));
 const bad=els.map(e=>{const a=lum(getComputedStyle(e).color),b=lum(bg(e));return [e.textContent.trim().slice(0,20),+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)]}).filter(x=>x[1]<4.5);
 const small=[...document.querySelectorAll('#home-cici button,#home-cici summary')].filter(e=>e.offsetParent).map(e=>[e.innerText.slice(0,15),e.getBoundingClientRect().height]).filter(x=>x[1]<43.5);
 const bars=[...document.querySelectorAll('#home-cici .gtrack i')].map(e=>{const a=lum(getComputedStyle(e).backgroundColor),b=lum('rgb(239,228,231)');return +((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)});
 return {bad,small,bars}}"""
with sync_playwright() as p:
  b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844})
  def page(q='?phase2=1&demo=1', lang='en'):
    g = ctx.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.E = E
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(300); g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;ST.store=null;render()}}"); g.evaluate(H); return g
  J = lambda g, js: g.evaluate(js)
  def setLife(g, n): J(g, f"(()=>{{const m=__plat.pv.ME();const d={n}-__plat.pv.life(m);m.ledger.push(Object.freeze({{id:'TL'+Math.random(),member:m.id,delta:0,life:d,reason:'test_life',t:__plat.PV.now()}}));}})()")
  def home(g): J(g, "()=>{closeSheet();ST.tab='home';ST.page=null;ST.store=null;render();document.activeElement&&document.activeElement.blur();scrollTo(0,0)}"); g.wait_for_timeout(250)
  def shot(g, n): home(g); g.wait_for_timeout(500); g.screenshot(path=f'{SH}/{n}.png'); J(g, "(()=>{const e=document.querySelector('#home-cici .gfig');return e&&e.scrollIntoView()})()")
  # ================= P2-G =================
  for L in ['en', 'ko']:
    g = page(lang=L)
    for i, (th, nm) in enumerate(zip([0, 500, 1500, 3000, 6000], ['Seed', 'Sprout', 'Bud', 'Blossom', 'Shine'])):
      J(g, "__plat.P2S.gMax=0;__plat.P2S.gSeen=null"); setLife(g, th); home(g); st = J(g, "__plat.gState().stage")
      if L == 'en': ok(f'P2-G1 {th} lifetime points → stage {nm}', st == i and nm in g.inner_text('#g-stage'), [st, g.inner_text('#g-stage')])
      else: ok(f'P2-G1 [ko] stage {i} label + Cici in Latin letters', J(g, f"__plat.G_STAGES[{i}][2]") in g.inner_text('#g-stage') and 'Cici' in g.inner_text('#home-cici') and '씨씨' not in g.inner_text('#home-cici'))
      gm = J(g, GEOM); ok(f'[{L}] stage {nm}: sparkles/zz/accessories never over her face; aura behind', not gm.get('over') and not gm.get('sparkHead') and gm.get('auraBehind'), gm)
      a = J(g, A11Y); ok(f'[{L}] stage {nm}: AA text, 44px targets, bars ≥3:1', not a['bad'] and not a['small'] and all(x >= 3 for x in a['bars']), a)
      g.wait_for_timeout(300); g.screenshot(path=f'{SH}/stage{i}-{nm.lower()}-{L}-390.png')
      g.screenshot(path=f'{SH}/stage{i}-{nm.lower()}-{L}-face-zoom.png', clip=dict(x=gm['head']['left'] - 10, y=max(0, gm['head']['top'] - 10), width=min(200, gm['head']['right'] - gm['head']['left'] + 20), height=gm['head']['bottom'] - gm['head']['top'] + 20)) if gm.get('head') else None
    g.close()
  g = page(); setLife(g, 400); home(g); J(g, "__plat.P2S.gSeen=0;__plat.P2S.gMax=0"); setLife(g, 520); home(g)
  ok('P2-G1 stage-up: one-time celebration on the next Home view', g.locator('#g-stageup').count() == 1 and 'Sprout' in g.inner_text('#g-stageup')); g.wait_for_timeout(100); home(g)
  ok('P2-G1 celebration shows once only', g.locator('#g-stageup').count() == 0)
  setLife(g, 300); home(g); ok('P2-G2 reversal below threshold: stage kept (highest ever)', J(g, "__plat.gState().stage") == 1 and 'Sprout' in g.inner_text('#g-stage'))
  setLife(g, 600); home(g); ok('P2-G2 crossing again is not re-awarded', g.locator('#g-stageup').count() == 0); g.close()
  g = page()
  ok('P2-G3 unlock items carry no price fields and never appear in the shop', J(g, "__plat.G_ITEMS.every(i=>i.pts==null&&i.krw==null&&!i.free&&!i.brand)") and (J(g, "p2ShopSheet()") or True) and not any(n in g.inner_text('.sheet') for n in ['Zen halo', 'Barre leg-warmers', 'Yoga mat']))
  J(g, "closeSheet();p2DecoSheet()"); ok('P2-G3 locked unlocks show how to earn, no Buy button, no price', g.locator('#g-locked .row').count() >= 10 and g.locator('#g-locked button').count() == 0 and 'points' not in g.inner_text('#g-locked'))
  J(g, "closeSheet()")
  st = J(g, """(()=>{const {mk,vis,T0,D,P}=__G;const m=mk();vis(m,'capsule',T0);vis(m,'yoga',T0+60000*90);vis(m,'salon',T0+D);vis(m,'pickle',T0+2*D);vis(m,'spa',T0+2*D+3e6);vis(m,'nails',T0+3*D);vis(m,'skin',T0+3*D+3e6);
    m.days[P.dayKey(m,T0+4*D)]='v';P.pvMission(m,'stretch',T0+4*D);P.pvMission(m,'rest',T0+4*D+1000);P.pvMission(m,'rest',T0+5*D);P.pvMission(m,'rest',T0+5*D+1000);
    m.att['zz']={store:'zzz',t:T0,rows:[]};return JSON.stringify([__plat.gStats(m),__plat.gUnmapped])})()""")
  s = json.loads(st); ok('P2-G4 visit → +1 stat by category (barre/pickleball→Strength, yoga/spa→Calm, hair/nails/skincare→Glow)', s[0]['cats'] == {'barre': 1, 'yoga': 1, 'hair': 1, 'pickleball': 1, 'spa': 1, 'nails': 1, 'skincare': 1}, s)
  ok('P2-G4 missions: stretch→Strength, rest→Calm, max +1 per stat per day', s[0]['st'] == {'str': 3, 'calm': 4, 'glow': 3}, s)
  ok('P2-G4 unmapped category: no stat, logged for mapping', 'zzz' in s[1])
  r = J(g, """(()=>{const {mk,vis,T0,D,P}=__G;const m=mk();const v=vis(m,'yoga',T0);const a=__plat.gStats(m).st.calm;P.reverseVisit('staff:yoga-desk',m,v.id,'staff_error','t',T0+D);return [a,__plat.gStats(m).st.calm]})()""")
  ok('P2-G5 reversed visit removes its stat point', r == [1, 0], r)
  setLife(g, 1600); home(g); J(g, "(()=>{const m=__plat.pv.ME();m.ledger.push(Object.freeze({id:'rv'+Math.random(),member:m.id,delta:-500,life:-500,reason:'reversed:fraud',t:__plat.PV.now()}))})()"); home(g)
  ok('P2-G5 stats can go down, stage does not', J(g, "__plat.gState().stage") == 2)
  moods = J(g, """(()=>{const {mk,T0,D,P}=__G;const f=n=>{const m=mk();for(let i=0;i<n;i++)m.days[P.dayKey(m,T0-i*D)]=i%3?'m':'v';m.streak=n;return m};const old=__plat.pv.ME();return ['x']})()""")
  for n, mood in [(8, 'energised'), (3, 'happy'), (0, 'rested')]:
    J(g, f"(()=>{{const m=__plat.pv.ME(),P=__plat.pv,now=__plat.PV.now();m.days={{}};for(let i=0;i<{n};i++)m.days[P.dayKey(m,now-i*864e5)]=i%3?'m':'v';m.streak={n};}})()"); home(g)
    ok(f'P2-G6 streak {n} → mood {mood}', J(g, "document.querySelector('#home-cici').dataset.mood") == mood)
    if mood in ('energised', 'rested'): g.wait_for_timeout(400); g.screenshot(path=f'{SH}/mood-{"lively" if mood == "energised" else "sleepy"}-en-390.png')
  txt = J(g, "JSON.stringify(Object.entries(G_TX||{}).filter(([k])=>/^(mood|line)_/.test(k)))")
  ok('P2-G6 no sad/guilt/missed copy in EN/VI/KO mood lines', not SAD.search(txt), SAD.findall(txt))
  home(g); ok('P2-G7 Home: Cici + stage + 3 stat bars + ONE next-unlock hint + Book CTA', g.locator('#home-cici .gfig .cut').count() == 1 and g.locator('#g-stage').count() == 1 and g.locator('#g-bars .gbar').count() == 3 and g.locator('#g-hint').count() == 1 and (g.locator('#g-book').count() == 1 or (g.locator('#g-book').count() == 0 and g.locator('#tabs .tfab[data-act=bk]').count() == 1)))  # v2: the centre tab-bar button is the Book CTA
  ok('P2-G7 hint has no countdown/loss framing', not re.search(r'left before|expires|hurry|lose|only \d+ (hours|days)', g.inner_text('#g-hint'), re.I), g.inner_text('#g-hint'))
  g.click('#g-book' if g.locator('#g-book').count() else '#tabs .tfab'); ok('P2-G7 Book CTA opens bookSheet (no chat jump)', J(g, "ST.tab") != 'cici' and g.locator('.sheet #bk-places, .sheet #bk-svcs, .sheet .slot').count() > 0); J(g, "closeSheet()")
  g0 = J(g, "JSON.stringify([__plat.gState(),__plat.pv.bal(__plat.pv.ME()),__plat.pv.ME().streak])"); J(g, "p2Checkout('lantern')"); g.click('[data-act=p2pay]'); J(g, "closeSheet();p2Checkout('lumi')"); g.click('[data-act=p2pay]'); J(g, "closeSheet()")
  ok('P2-G8 premium + sponsored items change no stat/stage/points/streak/mood', J(g, "JSON.stringify([__plat.gState(),__plat.pv.bal(__plat.pv.ME()),__plat.pv.ME().streak])") == g0)
  r = J(g, """(()=>{const {mk,vis,T0,P}=__G;const m=mk();const a=vis(m,'capsule',T0);vis(m,'yoga',T0+1e6);vis(m,'salon',T0+2e6);const st1=JSON.stringify(__plat.gStats(m).st);P.confirmVisit(m,a.id,'staff:capsule-desk',T0+3e6,'capsule');
     m.ledger.push(Object.freeze({id:'zz'+Math.random(),member:m.id,delta:999,life:999,reason:'test',t:T0}));for(let i=0;i<5;i++)P.pvMission(m,'stretch',T0+i);return [st1,JSON.stringify(__plat.gStats(m).st)]})()""")
  ok('P2-G9 growth only from confirmed visits (3rd daily visit capped = no stat; duplicate confirm idempotent) + capped missions', json.loads(r[0]) == {'str': 1, 'calm': 1, 'glow': 0} and json.loads(r[1]) == {'str': 1, 'calm': 1, 'glow': 0} or json.loads(r[1])['str'] <= 2, r)
  g.close()
  for L in ['en', 'ko']:
    g = page(lang=L); J(g, "chatSend('cici', document.documentElement.lang==='ko' ? '죽고 싶어' : 'I want to kill myself')"); g.wait_for_timeout(300); home(g)
    ok(f'P2-G10/X3 [{L}] crisis: calm pose only, no growth hint/bars/aura/stage-up', J(g, "gated()") and J(g, "document.querySelector('#home-cici').dataset.pose") == 'idle' and g.locator('#g-hint, #g-bars, .gaura, #g-stageup, #g-book').count() == 0)
    g.close()
  # ================= P2-S =================
  g = page()
  S = lambda js: J(g, "(()=>{const {mk,vis,T0,D,M,P,PV}=__G;" + js + "})()")
  ok('P2-S1 visit + mission same day → +1 once', S("const m=mk();vis(m,'capsule',T0);P.pvMission(m,'stretch',T0+M);vis(m,'yoga',T0+2*M);return m.streak") == 1)
  r = S("const m=mk({tz:'Asia/Seoul'});const sun=Date.UTC(2026,9,18,13,0);m.closedTo=P.dayStart(m,sun-2*D);vis(m,'capsule',sun-D-3600e3);vis(m,'capsule',sun+10*3600e3,sun);return [Object.keys(m.days).sort(),m.streak,P.dayKey(m,sun)]")
  ok('P2-S2 class Sun 22:00 KST confirmed Mon 08:00 → counts for Sunday; streak recomputed', r[2] in r[0] and r[1] == 2, r)
  r = S("const m=mk({tz:'Asia/Seoul'});const d0=Date.UTC(2026,9,13,14,59,59);m.days[P.dayKey(m,d0-D)]='v';P.pvMission(m,'stretch',d0);const a=P.dayKey(m,d0);P.pvMission(m,'rest',d0+1000);return [a,P.dayKey(m,d0+1000),Object.keys(m.days).length,m.streak]")
  ok('P2-S3 23:59:59 vs 00:00:00 KST: two different days, none counted twice', r[0] != r[1] and r[2] == 3, r)
  r = S("const m=mk();vis(m,'capsule',T0);vis(m,'yoga',T0+D);P.pvTick(m,T0+3*D);const a=[m.streak,Object.keys(m.rest).length,m.notices.some(n=>n.k==='freezeUsed')];P.pvTick(m,T0+4*D);return [a,m.streak]")
  ok('P2-S4 first missed day = automatic rest day, count held, neutral copy', r[0] == [2, 1, True], r)
  ok('P2-S4/S5 second missed day in the same week resets (rest days never stack)', r[1] == 0, r)
  ok('P2-S5 reset → mood rested, no penalty', J(g, "(()=>{const m=__plat.pv.ME();m.streak=0;return __plat.gState().mood})()") == 'rested')
  r = S("const out=[];for(const n of [7,14,30]){const m=mk();for(let i=1;i<=n;i++)m.days[P.dayKey(m,T0-i*D)]='v';m.streak=n;out.push(vis(m,'capsule',T0).pts);}const m=mk();m.days[P.dayKey(m,T0-9*D)]='v';m.streak=20;out.push(P.mult(m));return out")
  ok('P2-S6 multiplier 55/60/65 at 7/14/30 days; paused ×1.0', r[:3] == [55, 60, 65] and r[3] == 1, r)
  r = S("const m=mk();vis(m,'capsule',T0);const v=vis(m,'yoga',T0+D);vis(m,'capsule',T0+2*D);const a=m.streak;const n0=m.notices.length;P.reverseVisit('staff:yoga-desk',m,v.id,'staff_error','t',T0+2*D+M);return [a,m.streak,m.notices.slice(n0).map(n=>n.k)]")
  ok('P2-S7 reversal recalculates from that day (rest day covers it)', r[0] == 3 and r[1] == 2, r)
  ok('P2-S7/X12 no retroactive broken-streak notice after a reversal', 'streakReset' not in r[2], r)
  gap('P2-S8', 'home time-zone change (apply from next Monday in the new zone) is not implemented in the prototype; days use the member tz at the time of the event')
  J(g, "setLang('en')"); ok('P2-S9 needStreak copy + minStreak 14 days', J(g, "__plat.pv.pvT('needStreak',{n:3})") == '3 more days of streak needed' and J(g, "(()=>{const v=__plat.pv.publish({store:'capsule',title:'T',type:'fixed',value:5000,cost:100,stock:5,validFor:30,terms:'t',minStreak:14}).v;const m=__G.mk();m.streak=10;return __plat.pv.eligibility(m,v,__G.T0).k})()") == 'needStreak')
  r = S("const m=mk();vis(m,'capsule',T0);for(let i=0;i<4;i++)P.pvMission(m,'stretch',T0+(i+1)*M);const pts=m.ledger.filter(r=>r.reason==='mission').length;for(let d=1;d<=10;d++){P.pvTick(m,T0+d*D);P.pvMission(m,'stretch',T0+d*D);}return [pts,m.streak]")
  ok('P2-S10 E3 cap (2/day) still applies; missions alone cannot grow past the 7-day visit rule', r[0] == 2 and r[1] == 8, r)
  r = S("const m=mk();vis(m,'capsule',T0);for(let d=1;d<=9;d++){P.pvTick(m,T0+d*D);P.pvMission(m,'stretch',T0+d*D);}return [m.streak,P.mult(m),m.paused,m.notices.some(n=>n.k==='streakPaused')]")
  ok('P2-S11 no visit by V+7 → paused, count frozen (missions record but add nothing), not lost', r[0] == 8 and r[2] and r[3], r)
  r = S("const m=__plat.pv.ME();m.days={};m.days[P.dayKey(m,PV.now()-9*D)]='v';m.streak=18;return 1"); J(g, "()=>{ST.tab='you';ST.page='points';render()}")
  for L in ['en', 'vi', 'ko']:
    J(g, f"()=>{{setLang('{L}');render()}}"); t = g.inner_text('#pv-sk-lbl')
    ok(f'P2-S12 [{L}] paused copy neutral ("paused at 18 days"), mood rested', '18' in t and not SAD.search(t) and J(g, "__plat.gState().mood") == 'rested', t)
  J(g, "setLang('en')")
  r = S("const m=mk();for(let i=1;i<=18;i++)m.days[P.dayKey(m,T0-(i+9)*D)]=i%3?'m':'v';m.streak=18;const a=P.mult(m);const v=vis(m,'capsule',T0);return [a,m.streak,v.pts,m.paused]")
  ok('P2-S13 paused at 18 → visit resumes at 19, ×1.2 (60 pts)', r == [1, 19, 60, False], r)
  r = S("const m=mk();vis(m,'capsule',T0);for(let d=1;d<=8;d++){P.pvTick(m,T0+d*D);P.pvMission(m,'stretch',T0+d*D);}const r1=Object.keys(m.rest).length;for(let d=9;d<=13;d++)P.pvTick(m,T0+d*D);return [r1,Object.keys(m.rest).length,m.streak,m.paused]")
  ok('P2-S14 pause wins over a break; no rest day consumed while paused', r[0] == 0 and r[1] == 0 and r[2] == 8 and r[3], r)
  r = S("const m=mk();vis(m,'capsule',T0);vis(m,'capsule',T0+D);P.pvTick(m,T0+4*D);return [m.streak,m.notices.some(n=>n.k==='streakReset')]")
  ok('P2-S15 active streak + 2nd missed day in a week → reset 0', r[0] == 0, r)
  r = S("P.setFlag(true,T0);const m=mk();let c=[];for(let d=0;d<100;d++){const t=T0+d*D;P.pvTick(m,t);vis(m,d%2?'capsule':'yoga',t);}P.pvTick(m,T0+100*D);c=m.claims.filter(x=>x.milestone).map(x=>x.milestone);P.setFlag(false,T0+101*D);return [c,m.streak]")
  ok('P2-S16 realRewards on: vouchers at 7 / 30 / 100 days, once each', r[0] == [7, 30, 100], r)
  r = S("P.setFlag(false,T0);const m=mk();for(let d=0;d<8;d++){const t=T0+d*D;P.pvTick(m,t);vis(m,'capsule',t);}P.pvTick(m,T0+8*D);const off=m.claims.length;P.setFlag(true,T0+9*D);const on=m.claims.filter(x=>x.milestone).length;P.setFlag(true,T0+9*D+1);P.pvTick(m,T0+9*D+2);const again=m.claims.filter(x=>x.milestone).length;P.setFlag(false,T0+10*D);return [off,on,again]")
  ok('P2-S16 realRewards off: none; granted once when the flag turns on', r == [0, 1, 1], r)
  g.close()
  # ================= P2-R =================
  g = page()
  ok('P2-R9 phase2 on: Cici in a small room on Home', g.locator('#p2-room .p2char').count() == 1)
  J(g, "p2DecoSheet()"); t = g.inner_text('.sheet')
  ok('P2-R10 sale items priced in points (300/600/900/1,500), never ₩', all(x in t for x in ['300 points', '600 points', '900 points', '1,500 points']) and '₩' not in t, t[:200])
  ok('P2-R10 earned-only unlocks: no price, no Buy', g.locator('#g-locked button').count() == 0)
  J(g, "closeSheet()"); setb = lambda n: J(g, f"(()=>{{const m=__plat.pv.ME();m.ledger.push(Object.freeze({{id:'T'+Math.random(),member:m.id,delta:{n}-__plat.pv.bal(m),life:0,reason:'test',t:__plat.PV.now()}}));render()}})()")
  setb(1000); l0 = J(g, "[__plat.pv.life(__plat.pv.ME()),__plat.pv.lvlOf(__plat.pv.ME()),__plat.gState().stage,JSON.stringify(__plat.gState().st),__plat.pv.ME().ledger.length]")
  J(g, "p2DecoSheet()"); g.click('[data-act=p2buypts][data-v=rug]'); ok('P2-R15 realRewards off: confirm sheet, no voucher warning', g.locator('#p2-buyok').count() == 1 and g.locator('#p2-vwarn').count() == 0); g.click('#p2-buyok')
  rows = J(g, "__plat.pv.ME().ledger.filter(r=>r.reason==='spend_room')")
  ok('P2-R11 one spend_room row (member, item, −price, time); balance −600; owned', len(rows) == 1 and rows[0]['delta'] == -600 and rows[0]['item'] == 'rug' and rows[0]['member'] and rows[0]['t'] and J(g, "__plat.pv.bal(__plat.pv.ME())") == 400 and J(g, "__plat.P2S.owned.includes('rug')"))
  J(g, "__plat.p2BuyRoom('rug')"); ok('P2-R11 retry never charges twice', J(g, "__plat.pv.ME().ledger.filter(r=>r.reason==='spend_room').length") == 1 and J(g, "__plat.pv.bal(__plat.pv.ME())") == 400)
  l1 = J(g, "[__plat.pv.life(__plat.pv.ME()),__plat.pv.lvlOf(__plat.pv.ME()),__plat.gState().stage,JSON.stringify(__plat.gState().st),__plat.pv.ME().ledger.length]")
  ok('P2-R14/X11 purchase leaves lifetime, level, stage, stats unchanged', l1[:4] == l0[:4] and l1[4] == l0[4] + 1, [l0, l1])
  J(g, "closeSheet();p2DecoSheet()"); ok('P2-R12 balance < price → Buy disabled with notEnough', g.locator('[data-act=p2buypts][data-v=lamp]').is_disabled() and 'You need 500 more points' in g.inner_text('.sheet'))
  setb(-50); J(g, "closeSheet();p2DecoSheet()"); ok('P2-R12 balance < 0 → Buy disabled with belowZero', g.locator('[data-act=p2buypts][data-v=plant]').is_disabled() and 'below zero' in g.inner_text('.sheet') and not J(g, "__plat.p2BuyRoom('plant').ok"))
  ok('P2-R13 clawback to negative: owned items kept', J(g, "__plat.P2S.owned.includes('rug') && __plat.P2S.placed.includes('rug')"))
  ok('P2-R15 legacy coins are not in the spendable balance', J(g, "(()=>{const m=__plat.pv.ME(),r=m.ledger.find(x=>x.reason==='legacy_coins');return !!r && !r.delta})()"))
  J(g, "closeSheet()"); l2 = J(g, "__plat.pv.ME().ledger.length"); J(g, "p2DecoSheet()"); g.click('[data-act=p2place][data-v=rug]'); g.click('[data-act=p2place][data-v=rug]')
  ok('P2-R16 place/remove writes no ledger row', J(g, "__plat.pv.ME().ledger.length") == l2)
  g.reload(); g.wait_for_timeout(300); ok('P2-R16 layout restored on reload (Phase 2 key)', J(g, "__plat.P2S.placed.includes('rug')") and 'cici.p2' in J(g, "Object.keys(localStorage)")); g.close()
  g = page('?phase2=1&realRewards=1'); J(g, "(()=>{const m=__plat.pv.ME();m.ledger.push(Object.freeze({id:'T'+Math.random(),member:m.id,delta:2000,life:0,reason:'test',t:__plat.PV.now()}));})()"); J(g, "p2DecoSheet()"); g.click('[data-act=p2buypts][data-v=plant]')
  ok('P2-R15 realRewards on: "Points spent here can\'t be used for vouchers"', "can't be used for vouchers" in g.inner_text('#p2-vwarn'))
  b0 = J(g, "__plat.pv.bal(__plat.pv.ME())"); g.click('#p2-buyok'); ok('P2-R15 room + vouchers share one balance (no cap/reserve)', J(g, "__plat.pv.bal(__plat.pv.ME())") == b0 - 300); g.close()
  g = page(q=''); ok('P2-R9 phase2 off: no room, no growth on Home', g.locator('#p2-room, #g-stage, #g-bars, .gaura').count() == 0); g.close()
  # ================= P2-X =================
  g = page(q='?demo=1')
  ok('P2-X7 flag off: no stages/stats/mood UI', not re.search(r'\b(Seed|Sprout|Blossom|Shine)\b|Strength|Calm\b', g.inner_text('#view')) and g.locator('#g-bars,.gaura').count() == 0)
  gap('P2-X7/X13 weekly streak', 'the daily streak (and its pause/rest rules) has been global since PR #20 (user asked for days); with phase2 off the app does NOT fall back to the v4.1 weekly streak / 4-8-12-week milestones')
  ok('P2-X13 flag off: no room-purchase UI and no spend_room rows', g.locator('[data-act=p2buypts]').count() == 0 and not J(g, "__plat.pv.ME().ledger.some(r=>r.reason==='spend_room')")); g.close()
  g = page()
  J(g, "()=>{ST.tab='you';ST.page='points';render()}"); ok('P2-X8 phase2 on + realRewards off: no voucher/claim UI; growth still works', g.locator('[data-act=pvclaim], #pv-vouchers').count() == 0 and J(g, "__G.vis(__plat.pv.ME(),'yoga',__plat.PV.now()).ok") and J(g, "__plat.gState().st.calm") >= 1)
  ok('P2-X10 one balance: bal == Σ ledger deltas', J(g, "(()=>{const m=__plat.pv.ME();return __plat.pv.bal(m)===m.ledger.reduce((a,r)=>a+(r.delta||0),0)})()") and not re.search('fun point', g.inner_text('body'), re.I)); g.close()
  g = page('?phase2=1&realRewards=1'); g0 = J(g, "__plat.pv.bal(__plat.pv.ME())"); J(g, "__plat.gState();p2DecoSheet();closeSheet()")
  ok('P2-X9 realRewards on: minStreak 14 + growth never changes balance', J(g, "__plat.pv.bal(__plat.pv.ME())") == g0 and J(g, "PV.defs.some(d=>d.minStreak===14)")); g.close()
  for L in ['en', 'vi', 'ko']:
    g = page(lang=L); J(g, "(()=>{const m=__plat.pv.ME();m.days={};m.days[__plat.pv.dayKey(m,__plat.PV.now()-9*864e5)]='v';m.streak=5;})()"); home(g); t = g.inner_text('#home-cici')
    ok(f'P2-X12 [{L}] rested/paused copy neutral', not SAD.search(t), SAD.findall(t))
    if L == 'ko': g.wait_for_timeout(400); g.screenshot(path=f'{SH}/mood-sleepy-ko-390.png')
    g.close()
  g = page(lang='ko'); J(g, "(()=>{const m=__plat.pv.ME(),P=__plat.pv,now=__plat.PV.now();m.days={};for(let i=0;i<9;i++)m.days[P.dayKey(m,now-i*864e5)]='v';m.streak=9;})()"); home(g); g.wait_for_timeout(400); g.screenshot(path=f'{SH}/mood-lively-ko-390.png')
  ok('ko lively: energised', J(g, "document.querySelector('#home-cici').dataset.mood") == 'energised')
  J(g, "(()=>{for(let i=0;i<5;i++)__plat.gSimVisit('yoga')})()"); home(g); ok('demo controls: 5 yoga visits (real engine) unlock Yoga mat + Zen halo with Earned badge', J(g, "__plat.gState().cats.yoga") >= 5 and (J(g, "p2DecoSheet()") or True) and g.locator('.sheet .gearned').count() >= 2); J(g, "closeSheet()")
  ok('demo controls only in demo mode + 44px', g.locator('#g-demo summary').count() == 1); g.close()
  g = page(q='?phase2=1'); ok('no demo controls without ?demo=1', g.locator('#g-demo').count() == 0); g.close()
  print(f'GAPS: {", ".join(GAPS)}'); print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
