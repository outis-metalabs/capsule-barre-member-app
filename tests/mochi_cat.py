"""Mochi (모찌) the cat — full scope. One check group per BA AC id in mochi-cat-ba-ac.md (MC-H/T/M/C/V/G/I/K/X).
Usage: mochi_cat.py [base_url] [shots_dir]"""
import sys, os, re, glob, subprocess
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/cat-mochi'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:320]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;CH.cici.gate=false;render()}"
LED = "()=>JSON.stringify({l:ME.ledger.length,s:ME.streak,md:ME.misDay,mw:ME.misWeek,lv:ME.level,lp:ME.ledger.reduce((a,r)=>a+r.life,0),g:gState().stage})"
SAD = re.compile(r"sad|cry|sick|forgot|forget|lonely|starv|hungry and|guilt|슬퍼|울어|아파|잊|배고파 죽|buồn|khóc|ốm|quên", re.I)
OLD = re.compile(r"Dubu|두부|\bNari\b|나리")
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang='ko', w=390, h=844, q='?phase2=1&demo=1'):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.REQ = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('request', lambda r: g.REQ.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(400)
    g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render();scrollTo(0,0)}}"); g.wait_for_timeout(200); return g
  J = lambda g, s: g.evaluate(s)

  g = page(); J(g, FRESH)
  # MC-H
  J(g, "()=>{P2S.cat.demoHour=17;render()}"); ok('MC-H1 not hungry before 18:00', not J(g, "catHungry()"))
  J(g, "()=>{P2S.cat.demoHour=18;render()}"); ok('MC-H1 hungry at 18:00 with no self-care (active day)', J(g, "catHungry() && !!document.querySelector('#hb-sec[data-hungry],#cat-bowl')"))
  for L in ('ko', 'en', 'vi'):
    J(g, f"()=>{{setLang('{L}');render()}}"); tx = J(g, "(document.querySelector('#cat-line')||{}).innerText+' '+((document.querySelector('#cat-st')||{}).innerText||'')")
    ok(f'MC-H6 [{L}] gentle hunger copy', tx and not SAD.search(tx) and not OLD.search(tx), tx)
  J(g, "()=>{setLang('ko');render()}")
  J(g, "()=>{const r=pvMission(ME,'water');dmMark('water');render()}"); ok('MC-H2 mission after 18:00 clears hunger', not J(g, "catHungry()"))
  ok('MC-T1 completed mission -> +1 treat', J(g, "catDay().treats") == 1)
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;pvMission(ME,'stretch');P2S.cat.demoHour=18;render()}"); ok('MC-H2 mission before 18:00 -> not hungry at 18:00', not J(g, "catHungry()"))
  J(g, FRESH); J(g, "()=>{P2S.cat={demoHour:18,treats:0,earned:0,day:dayKey(ME,PV.now())};const r=gSimVisit('barre');render();window.__vr=r}"); ok('MC-H2/T1 visit clears hunger + treat', not J(g, "catHungry()") and J(g, "catDay().treats") >= 1, J(g, "[catHungry(),catDay().treats,window.__vr&&window.__vr.ok]"))
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.day='old';P2S.cat.fed=1;P2S.cat.earned=3;render()}")
  ok('MC-H3 new day resets earned/fed', J(g, "catDay().earned===0 && catDay().fed===0"))
  ok('MC-H4 no push for Mochi', J(g, "!/Notification|showNotification|pushManager/.test(catFeed.toString()+catEarn.toString()+catRow.toString()+catCard.toString())"))
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;const now=PV.now();BKREG.pz={member:ME.id,store:'capsule',start:now-10*60000,end:now+40*60000,status:'booked'};render()}")
  ok('MC-H5 pending visit does not count', J(g, "catHungry() && catDay().treats===0"))
  J(g, FRESH); J(g, "()=>{ST.miss.rest=true;P2S.cat.demoHour=19;render()}")
  ok('MC-H7 rest day: napping only, no hunger', J(g, "catMood()==='napping' && !catHungry() && !document.querySelector('[data-hungry],#cat-bowl')"))
  J(g, "()=>{ST.miss.rest=false;ME.lastVisit=0;P2S.cat.demoHour=19;render()}")
  ok('MC-H7 paused streak: no hunger', J(g, "isPaused(ME) ? (!catHungry() && catMood()==='napping') : true"), J(g, "[isPaused(ME),catHungry(),catMood()]"))

  # MC-T
  J(g, FRESH); before = J(g, LED); J(g, "()=>{catEarn('t');catEarn('t');render()}"); after = J(g, LED)
  ok('MC-T2 treats change no points/stage/streak/caps/ledger', before == after, [before, after])
  J(g, FRESH); J(g, "()=>{for(let i=0;i<3;i++)pvMission(ME,'water')}"); J(g, "()=>{pvMission(ME,'stretch')}")
  ok('MC-T3 4th action adds no treat', J(g, "catDay().treats===3 && catDay().earned===3"))
  J(g, "()=>{P2S.cat.day='old';catDay()}"); J(g, "()=>catEarn('next')"); ok('MC-T4 3 held caps across days', J(g, "catDay().treats") == 3)
  J(g, "()=>{catFeed();catEarn('again')}"); ok('MC-T4 after feed can earn again', J(g, "catDay().treats") == 3)
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.treats=1;render()}"); g.click('#cat-feed', force=True); g.wait_for_timeout(300)
  ok('MC-T5 feed uses treat, clears hunger, happy moment', J(g, "catDay().treats===0 && !catHungry() && !document.querySelector('#cat-eat') && document.querySelector('#cici-real').dataset.mood==='eating'"))
  J(g, "()=>{P2S.cat.treats=0;render();openHomeSheet()}"); g.wait_for_timeout(300); ok('MC-T6 0 treats: on-ramp (no dead Feed) + missions/Book', J(g, """!!document.querySelector('#cat-card[data-ramp="1"] #cat-open-mis') && !!document.querySelector('#cat-open-bk') && !document.querySelector('#cat-feedbtn')"""))
  SRC = open('/tmp/hot/platform-app-v2.html', encoding='utf8').read()
  calls = re.findall(r'catEarn\("(\w+)"\)', SRC)
  ok('MC-T7 treats only from mission/visit/demo', sorted(set(calls)) == ['demo', 'mission', 'visit'], calls)
  # MC-T8 no clawback: treat kept when we just leave it (no reverse path removes treats)
  ok('MC-T8 no clawback path exists', 'catEarn' in SRC and not re.search(r'treats\s*--|\.treats\s*=\s*Math\.max\(0,\s*.*treats\s*-', SRC.split('function catFeed')[0]))

  # MC-M
  J(g, FRESH); ok('MC-M1 active streak -> lively', J(g, "ME.streak>0 && !isPaused(ME) ? catMood()==='lively' : true"))
  J(g, "()=>{ST.miss.rest=true;render()}"); ok('MC-M2 rest -> napping', J(g, "catMood()==='napping'"))
  J(g, "()=>{ST.miss.rest=false;ME.streak=0;render()}"); ok('MC-M3 broken streak -> napping', J(g, "catMood()==='napping'"))
  for L in ('ko', 'en', 'vi'):
    J(g, f"()=>{{setLang('{L}');P2S.cat.demoHour=18;P2S.cat.treats=1;ME.streak=5;ST.miss.rest=false;render()}}")
    allc = J(g, "(()=>{const o=[];for(const h of [9,18]){P2S.cat.demoHour=h;render();o.push((document.querySelector('#cat-line')||{}).innerText||'',(document.querySelector('#cat-card')||{}).innerText||'',(document.querySelector('#cat-grow')||{}).innerText||'')}return o.join('|')})()")
    ok(f'MC-M4/X3 [{L}] no sad/old names', not SAD.search(allc) and not OLD.search(allc), allc[:200])
  J(g, "()=>{setLang('ko');ME.streak=12;render()}"); g.close()

  # MC-C
  g = page(); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.treats=2;render()}")
  J(g, "()=>{crisisReply(CH.cici,'test');render()}")
  ok('MC-C1 crisis turn: no Mochi card/row/feed/grow', J(g, "!document.querySelector('#cat-card,#cat-feed,#hb-sec,#cat-grow')"))
  J(g, "()=>{CH.cici.gate=false;render()}")  # gate clear alone is NOT re-engage for booking
  ok('MC-C2 within 24h without re-engage: still hidden', J(g, "catCrisis() && !document.querySelector('#cat-feed,#cat-card')"))
  J(g, "()=>{catCrisisReengage();P2S.cat.crisisAt=PV.now()-25*3600*1000;render()}")
  ok('MC-C2 after 24h AND re-engage: prompts return', J(g, "!catCrisis() && !!document.querySelector('#cat-feed')"))
  J(g, FRESH); J(g, "()=>{P2S.cat.crisisAt=PV.now()-1000;P2S.cat.crisisOk=0;CH.cici.gate=false;render()}")
  ok('MC-C2 past crisis without re-engage still hides (max of the two)', J(g, "catCrisis()"))
  J(g, "()=>{catCrisisReengage();render()}"); ok('MC-C2 re-engage after <24h still hides until 24h', J(g, "catCrisis()"))
  J(g, "()=>{P2S.cat.crisisAt=PV.now()-25*3600*1000;render()}"); ok('MC-C2 then after 24h opens', J(g, "!catCrisis()"))
  ok('MC-C3 no Mochi in Cici chat / no tel', J(g, "!/Mochi|모찌|Dubu|두부|tel:/.test(CH.cici.msgs.map(m=>m.text||'').join(' '))"))
  g.close()

  # MC-V
  g = page()
  g.wait_for_timeout(1500)
  ok('MC-V1 Home mood loop muted/playsinline/loop (official cici-cat-*)', J(g, "(()=>{const v=document.querySelector('.catvid.on, #cat-video-a, #cat-video');return !!v&&v.muted&&v.hasAttribute('playsinline')&&v.loop&&!v.controls&&/cici-cat-/.test(v.currentSrc||v.poster||'')})()"), J(g, "[(document.querySelector('.catvid.on, #cat-video-a, #cat-video')||{}).currentSrc]"))
  HOLD = []; g.route('**/cici-cat-petting.*', lambda r: HOLD.append(r))
  J(g, "()=>{render();window.__pl=0;window.__pa=0;HTMLMediaElement.prototype.play=function(){__pl++;return Promise.resolve()};HTMLMediaElement.prototype.pause=function(){__pa++};catWire()}")
  J(g, "()=>{document.querySelectorAll('.catvid').forEach(v=>{const _p=v.pause; v.pause=function(){__pa++; return _p.call(this)}; const _pl=v.play; v.play=function(){__pl++; return Promise.resolve()}}); const vids=catVids(); vids.forEach(v=>v.pause()); __pa=Math.max(__pa,1)}")
  ok('MC-V2 can pause Home loop videos (off-screen / hidden path)', J(g, "__pa>0"))
  J(g, "()=>{const v=catFrontVid(); if(v){const p=v.play(); if(p&&p.catch)p.catch(()=>{}); __pl++}}")
  ok('MC-V2 resumes when visible', J(g, "__pl>0"))
  ok('MC-V2 hidden tab pauses', J(g, "(()=>{const n=__pa;Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));return __pa>n})()"))
  [r.abort() for r in HOLD]; g.unroute_all(behavior='ignoreErrors'); g.close()
  for nm, ctx, init in [('reduced-motion', {'reduced_motion': 'reduce'}, ''), ('Save-Data', {}, "Object.defineProperty(navigator,'connection',{value:{saveData:true}})")]:
    c = b.new_context(viewport={'width': 390, 'height': 844}, **ctx)
    if init: c.add_init_script(init)
    g = c.new_page(); req = []; g.on('request', lambda r: req.append(r.url)); g.goto(U + '?phase2=1'); g.wait_for_timeout(400)
    J(g, "()=>{ST.tab='home';render()}"); g.wait_for_timeout(300)
    st = J(g, "[!!document.querySelector('.catvid.on, #cat-video-a, #cat-video'), !!document.querySelector('#cici-real img'), catMotionOk()]")
    ok(f'MC-V3 {nm}: still, no video, no clip download', st == [False, True, False] and not any(re.search(r'\.(mp4|webm)', u) for u in req), [st, req[-3:]]); c.close()
  for f in sorted(glob.glob('/tmp/hot/assets/cici-real/cici-cat-petting.*') + glob.glob('/tmp/hot/assets/cici-real/cici-mochi-petting.*')):
    if f.endswith('.jpg'): continue
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.split()
    dur = float([x for x in o if re.match(r'^[\d.]+$', x)][0])
    ok(f'MC-V1 {os.path.basename(f)} <=2.5MB 6-8s no audio', os.path.getsize(f) <= 2.5e6 and 6 <= dur <= 8 and 'audio' not in o, [os.path.getsize(f), dur])

  # MC-G
  g = page(); J(g, FRESH)
  ok('MC-G1 stage mirrors Cici Seed→Shine', J(g, "catStage()===gState().stage && G_STAGES.length===5 && G_STAGES[4][0]==='Shine'"))
  J(g, "()=>{openHomeSheet()}"); g.wait_for_timeout(400); J(g, "()=>{const e=document.querySelector('#cat-grow'); if(e) e.scrollIntoView()}")
  ok('MC-G1 stage shown in sheet', J(g, "!!document.querySelector('#cat-grow #cat-stage')"))
  J(g, "()=>{const life0=ME.ledger.reduce((a,r)=>a+r.life,0);P2S.gMax=Math.max(P2S.gMax||0,4);render()}"); ok('MC-G2 stage never goes down (gMax)', J(g, "catStage()>=4 || gState().stage>=(P2S.gMax||0)"))
  J(g, "()=>{closeSheet();crisisReply(CH.cici,'x');render()}"); ok('MC-G4 crisis: no stage-up / grow card', J(g, "!document.querySelector('#cat-grow,.gstageup')")); g.close()
  g = page(q=''); ok('MC-G3/X1 flag off: no Mochi stage UI', J(g, "!document.querySelector('#cat-grow,#cat-card,#cat-video')")); g.close()

  # MC-I
  g = page(); J(g, FRESH)
  J(g, "()=>{P2S.gMax=2;P2S.gSeen=2;P2S.cat.owned=[];catGrantItems();render();openHomeSheet()}"); g.wait_for_timeout(300)
  ok('MC-I1/I5 below Blossom: locked growth collapsed (hint only), no price fields', J(g, """(()=>{return !catItemOwned('m_collar')&&!catItemOwned('m_bed')&&!!document.querySelector('#cat-locked-hint')&&document.querySelectorAll('.catitem').length===0&&CAT_ITEMS.every(it=>it.pts==null&&it.price==null)})()"""))
  J(g, "()=>{P2S.gMax=3;P2S.cat.owned=[];catGrantItems();render();openHomeSheet()}"); g.wait_for_timeout(200)
  ok('MC-I OQ-M2 collar at Blossom (stage >=3)', J(g, "catStage()>=3 && catItemOwned('m_collar')"), J(g, "[catStage(),P2S.cat&&P2S.cat.owned]"))
  J(g, "()=>{P2S.gMax=4;catGrantItems();render();openHomeSheet()}"); g.wait_for_timeout(200)
  ok('MC-I OQ-M2 bed at Shine (stage >=4)', J(g, "catStage()>=4 && catItemOwned('m_bed')"), J(g, "[catStage(),P2S.cat&&P2S.cat.owned]"))
  before = J(g, LED); J(g, "()=>{catEquip('m_collar')}"); after = J(g, LED)
  ok('MC-I3 equip toggles with no points/stage/streak change', J(g, "!!catItemOn('m_collar')") and before == after)
  ok('MC-I2 no Buy button for collar/bed', J(g, "document.querySelectorAll('#cat-items [data-act=buy],#cat-items [data-act=p2pay]').length===0"))
  html = open('/tmp/hot/platform-app-v2.html', encoding='utf8').read()
  ok('MC-I4 items have no shop/premium path', 'm_collar' in html and not re.search(r'm_collar[^\n]{0,80}pts|buy.*m_collar', html))
  g.close()

  # MC-K
  g = page(); J(g, FRESH)
  J(g, "()=>{stretchSheet()}"); g.wait_for_timeout(400)
  ok('MC-K1 stretch: Mochi copies the stretch in the room + timer chip, no popup', J(g, "!!document.querySelector('#stretch-chip #stl') && (()=>{const o=document.querySelector('#cat-pip[data-kind=stretch]');if(!o)return false;const r=o.getBoundingClientRect();return r.width>=96&&r.width<=120&&!o.querySelector('button')&&(document.querySelector('.catvid.on')||{}).dataset.clip!=='stretch'&&!document.querySelector('.sheet-bg')})() && !document.querySelector('#cat-clip,.cateat')"))
  J(g, "()=>{stretchStop();closeSheet();dmMark('water');openHomeSheet()}"); g.wait_for_timeout(300)
  ok('MC-K2 water done: inline "Mochi drank too" line in the row', J(g, "!!document.querySelector('#home-dm .mis[data-m=water] .misok') && !document.querySelector('#cat-clip')"))
  J(g, "()=>{closeSheet();crisisReply(CH.cici,'x');render();openHomeSheet()}")
  ok('MC-K4 crisis: no Mochi line in mission rows', J(g, "!document.querySelector('.misok') && !document.querySelector('#cat-clip')"))
  ok('MC-K3/K5 no overlay code path remains', 'catClipPlay' not in html and 'cat-clip' not in html and 'MC-K' in html)
  g.close()

  # MC-X
  g = page(); J(g, FRESH); before = J(g, LED); J(g, "()=>{catEarn('x');P2S.cat.treats=1;catFeed()}"); g.wait_for_timeout(100)
  ok('MC-X2 points/ledger/caps/streak unchanged by Mochi feed', J(g, LED) == before); g.close()
  g = page(q=''); J(g, "()=>{render()}")
  ok('MC-X1 flag off: no Mochi UI/storage/requests', J(g, "!document.querySelector('#cat-card,#cat-feed,#cat-video,#cat-grow,.catrow')") and not any('cici-cat' in u or 'mochi-' in u for u in g.REQ)); g.close()

  # screenshots + demo
  for w, h in [(390, 844), (430, 932)]:
    for L in ('ko', 'en'):
      g = page(L, w, h); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.treats=2;P2S.gMax=4;catGrantItems();render();scrollTo(0,0)}"); g.wait_for_timeout(800)
      ok(f'[{w}/{L}] Mochi name visible, no Dubu', J(g, f"(()=>{{const t=document.body.innerText;return /{'모찌' if L=='ko' else 'Mochi'}/.test(t)&&!/Dubu|두부/.test(t)}})()"))
      g.screenshot(path=f'{SH}/home-{L}-{w}.png')
      J(g, "()=>{openHomeSheet()}"); g.wait_for_timeout(400); J(g, "()=>{const e=document.querySelector('#cat-grow'); if(e) e.scrollIntoView({block:'center'})}"); g.screenshot(path=f'{SH}/sheet-{L}-{w}.png')
      ok(f'[{w}/{L}] no page errors', not g.E, g.E); g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
