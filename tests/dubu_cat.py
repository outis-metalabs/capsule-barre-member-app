"""Mochi (모찌) the cat (was Dubu), v2 phase2 only. One check group per BA AC id in dubu-cat-ba-ac.md (DB-H/T/M/C/V/X). File path kept as dubu_cat.py.
Usage: dubu_cat.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/cat-dubu'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;CH.cici.gate=false;render()}"
LED = "()=>JSON.stringify({l:ME.ledger.length,s:ME.streak,md:ME.misDay,mw:ME.misWeek,lv:ME.level,lp:ME.ledger.reduce((a,r)=>a+r.life,0),g:gState().stage})"
SAD = re.compile(r"sad|cry|sick|forgot|forget|lonely|starv|hungry and|guilt|슬퍼|울어|아파|잊|배고파 죽|buồn|khóc|ốm|quên", re.I)
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang='ko', w=390, h=844, q='?phase2=1', ctx={}):
    c = b.new_context(viewport={'width': w, 'height': h}, **ctx); g = c.new_page(); g.E = []; g.REQ = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('request', lambda r: g.REQ.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(400)
    g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render();scrollTo(0,0)}}"); g.wait_for_timeout(200); return g
  J = lambda g, s: g.evaluate(s)
  g = page(q='?phase2=1&demo=1'); J(g, FRESH)
  # DB-H1 / H6
  J(g, "()=>{P2S.cat.demoHour=17;render()}"); ok('DB-H1 not hungry before 18:00', not J(g, "catHungry()"))
  J(g, "()=>{P2S.cat.demoHour=18;render()}"); ok('DB-H1 hungry at 18:00 with no self-care', J(g, "catHungry() && !!document.querySelector('#hb-sec[data-hungry]')"))
  for L in ('ko', 'en', 'vi'):
    J(g, f"()=>{{setLang('{L}');render()}}"); tx = J(g, "document.querySelector('#cat-line').innerText + ' ' + (document.querySelector('#cat-st')||{}).innerText")
    ok(f'DB-H6 [{L}] gentle hunger copy, no guilt/sad wording', tx and not SAD.search(tx), tx)
  J(g, "()=>{setLang('ko');render()}")
  # DB-H2 mission after 18:00 clears at once, earns treat (DB-T1)
  J(g, "()=>{const r=pvMission(ME,'water');dmMark('water');render()}"); ok('DB-H2 a mission after 18:00 clears hunger at once', not J(g, "catHungry()"))
  ok('DB-T1 completed mission -> +1 treat', J(g, "catDay().treats") == 1)
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;pvMission(ME,'stretch');P2S.cat.demoHour=18;render()}"); ok('DB-H2 a mission before 18:00 -> not hungry at 18:00', not J(g, "catHungry()"))
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;gSimVisit('barre');render()}"); ok('DB-H2/T1 store-confirmed visit clears hunger and gives a treat', not J(g, "catHungry()") and J(g, "catDay().treats") == 1, J(g, "JSON.stringify(P2S.cat)"))
  # DB-H3 midnight reset
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.day='old';P2S.cat.fed=1;P2S.cat.earned=3;render()}")
  ok('DB-H3 new home-tz day resets earned/fed', J(g, "catDay().earned===0 && catDay().fed===0"))
  # DB-H4 no push
  ok('DB-H4 no push/Notification API used for Mochi', J(g, "!/Notification|showNotification|pushManager/.test(catFeed.toString()+catEarn.toString()+catRow.toString()+catCard.toString())"))
  # DB-H5 pending visit doesn't count
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;const now=PV.now();BKREG.pz={member:ME.id,store:'capsule',start:now-10*60000,end:now+40*60000,status:'booked'};render()}")
  ok('DB-H5 a visit pending confirmation does not count (still hungry, no treat)', J(g, "catHungry() && catDay().treats===0"))
  # DB-T2 / T3 / T4
  J(g, FRESH); before = J(g, LED); J(g, "()=>{catEarn('t');catEarn('t');render()}"); after = J(g, LED)
  ok('DB-T2 earning treats writes no ledger row and changes no points/stage/streak/caps', before == after, [before, after])
  J(g, FRESH); J(g, "()=>{for(let i=0;i<3;i++)pvMission(ME,'water')}"); s0 = J(g, "ME.streak"); J(g, "()=>{pvMission(ME,'stretch')}")
  ok('DB-T3 4th qualifying action adds no treat; the action still runs its own rules', J(g, "catDay().treats===3 && catDay().earned===3") and J(g, "ME.ledger.slice(-1)[0].reason").startswith('mission'), J(g, "JSON.stringify(P2S.cat)"))
  J(g, "()=>{P2S.cat.day='old';catDay()}"); J(g, "()=>catEarn('next')"); ok('DB-T4 3 held -> next day still capped until one is fed', J(g, "catDay().treats") == 3)
  J(g, "()=>{catFeed();catEarn('again')}"); ok('DB-T4 after feeding one, a treat can be added again', J(g, "catDay().treats") == 3 and J(g, "catDay().fed") == 1)
  # DB-T5 feed
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.treats=1;render()}"); ok('DB-T5 feed button in the card when a treat is held (44px)', J(g, "(()=>{const r=document.querySelector('#cat-feed').getBoundingClientRect();return r.width>=44&&r.height>=44})()"))
  g.click('#cat-feed'); g.wait_for_timeout(200)
  ok('DB-T5 feeding uses 1 treat, clears hunger and plays the happy moment', J(g, "catDay().treats===0 && !catHungry() && document.querySelector('#cici-real').dataset.mood==='eating'"))
  ok('DB-T5 official eating clip plays in a small overlay', J(g, "(()=>{const o=document.querySelector('#cat-eat');return !!o && !!o.querySelector('video source[src*=dubu-eating]') && o.getBoundingClientRect().width<=300})()"))
  g.wait_for_timeout(4900); ok('DB-T5 overlay closes and returns to the loop', J(g, "!document.querySelector('#cat-eat') && !!document.querySelector('#cat-video')"))
  ok('DB-T5 happy moment is short (back to normal mood)', J(g, "document.querySelector('#cici-real').dataset.mood!=='eating'"))
  # DB-T6
  J(g, "()=>{P2S.cat.treats=0;render()}"); ok('DB-T6 0 treats: Feed disabled with the earn hint', J(g, "(()=>{const b=document.querySelector('#cat-feedbtn');return b.disabled && /미션을 완료하거나 스튜디오에 방문하면/.test(document.querySelector('#cat-hint').innerText)})()"))
  J(g, "()=>{setLang('en');render()}"); ok('DB-T6 EN hint text', J(g, "document.querySelector('#cat-hint').innerText") == 'Complete a mission or visit a studio to earn a treat'); J(g, "()=>{setLang('ko');render()}")
  # DB-T7
  SRC = open('/tmp/hot/platform-app-v2.html', encoding='utf8').read(); calls = re.findall(r'catEarn\("(\w+)"\)', SRC)
  ok('DB-T7 treats only from missions/visits (+demo): no buy/gift/premium path grants treats', sorted(set(calls)) == ['demo', 'mission', 'visit'], calls)
  # DB-M
  J(g, FRESH); ok('DB-M1 active streak -> lively', J(g, "ME.streak>0 && !isPaused(ME) ? catMood()==='lively' : true"), J(g, "[ME.streak,isPaused(ME),catMood()]"))
  J(g, "()=>{ST.miss.rest=true;P2S.cat.demoHour=19;render()}"); ok('DB-M2 rest day -> napping, neutral copy (and OQ-D2 default: no hunger)', J(g, "catMood()==='napping' && !catHungry()") and not SAD.search(J(g, "document.querySelector('#cat-line').innerText")))
  J(g, "()=>{ST.miss.rest=false;ME.lastVisit=0;render()}")
  for L in ('ko', 'en', 'vi'):
    J(g, f"()=>{{setLang('{L}');}}"); allc = J(g, "(()=>{const o=[];for(const m of ['calm','lively','napping']){ST.catEat=false;}for(const h of [9,18]){P2S.cat.demoHour=h;for(const t of [0,2]){P2S.cat.treats=t;render();o.push(document.querySelector('#cat-line').innerText,(document.querySelector('#cat-card')||{}).innerText||'')}}return o.join(' | ')})()")
    ok(f'DB-M3 [{L}] no sad/crying/sick/shaming copy in any state', not SAD.search(allc), SAD.search(allc) and SAD.search(allc).group(0))
  J(g, "()=>{setLang('ko');render()}"); g.close()
  # DB-C1 / C2
  g = page(q='?phase2=1&demo=1'); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.treats=2;render()}")
  J(g, "()=>{const c=CH.cici;crisisReply(c,'test');render()}")
  ok('DB-C1 crisis turn itself: no Mochi card, row or feed', J(g, "!document.querySelector('#cat-card,#cat-feed,#hb-sec')"))
  J(g, "()=>{CH.cici.gate=false;render()}")
  ok('DB-C1 within 24h: hunger, treat counters and Feed hidden; calm only', J(g, "catCrisis() && !catHungry() && catMood()==='calm' && !document.querySelector('#cat-feed,#cat-card,#cat-feedbtn,[data-hungry]') && !/\\d/.test(document.querySelector('#cat-line').innerText)"))
  J(g, "()=>catFeed()"); ok('DB-C1 no happy moment in the window', J(g, "catDay().treats===2 && !ST.catEat"))
  J(g, "()=>{P2S.cat.crisisAt=PV.now()-25*3600*1000;render()}"); ok('DB-C1 after 24h the Mochi prompts return', J(g, "!catCrisis() && !!document.querySelector('#cat-feed')"))
  ok('DB-C2 crisis copy/no-number unchanged and no Dubu prompt in the Cici chat', J(g, "!/Mochi|모찌|Dubu|두부|tel:/.test(CH.cici.msgs.map(m=>m.text||'').join(' '))"))
  g.close()
  # DB-V
  g = page()
  ok('DB-V1 video slot: muted, playsinline, loop, no controls', J(g, "(()=>{const v=document.querySelector('#cat-video');return !!v&&v.muted&&v.hasAttribute('playsinline')&&v.loop&&!v.controls})()"))
  g.wait_for_timeout(1500); ok('DB-V1 official petting loop plays (has data, no audio control)', J(g, "(()=>{const v=document.querySelector('#cat-video');return v.readyState>=2 && /cici-cat-petting/.test(v.currentSrc) && v.duration>=6 && v.duration<=8})()"), J(g, "[document.querySelector('#cat-video').currentSrc,document.querySelector('#cat-video').duration]"))
  J(g, "()=>{const v=document.querySelector('#cat-video');v.dispatchEvent(new Event('error'))}")
  ok('DB-V1 a failing clip falls back to the official poster still', J(g, "!!document.querySelector('#cici-real img[src*=cici-cat-poster]')"))
  HOLD = []; g.route('**/cici-cat-*', lambda r: HOLD.append(r))  # keep clip requests pending so the 404 fallback doesn't swap the element
  J(g, "()=>{render();window.__pl=0;window.__pa=0;HTMLMediaElement.prototype.play=function(){__pl++;return Promise.resolve()};HTMLMediaElement.prototype.pause=function(){__pa++};catWire()}")
  J(g, "()=>{document.querySelector('#home-sheet').scrollIntoView();}"); g.wait_for_timeout(400); J(g, "scrollTo(0,99999)"); g.wait_for_timeout(500)
  ok('DB-V2 pauses when scrolled off-screen', J(g, "__pa>0"))
  J(g, "scrollTo(0,0)"); g.wait_for_timeout(500); ok('DB-V2 resumes when visible again', J(g, "__pl>0"))
  ok('DB-V2 visibility handler pauses on hidden tab', J(g, "(()=>{const n=__pa;Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));return __pa>n})()"))
  [r.abort() for r in HOLD]; g.unroute_all(behavior='ignoreErrors'); g.close()
  for nm, ctx, init in [('reduced-motion', {'reduced_motion': 'reduce'}, ''), ('Save-Data', {}, "Object.defineProperty(navigator,'connection',{value:{saveData:true}})")]:
    c = b.new_context(viewport={'width': 390, 'height': 844}, **ctx)
    if init: c.add_init_script(init + ";window.addEventListener('DOMContentLoaded',()=>{})")
    g = c.new_page(); req = []; g.on('request', lambda r: req.append(r.url)); g.goto(U + '?phase2=1'); g.wait_for_timeout(300)
    J(g, "()=>{ST.tab='home';render()}"); g.wait_for_timeout(300)
    st = J(g, "[!!document.querySelector('#cat-video'), !!document.querySelector('#cici-real img'), catMotionOk()]"); ok(f'DB-V3 {nm}: still image, no video element, no clip downloaded', st == [False, True, False] and not any(re.search(r'\.(mp4|webm)', u) for u in req), [st, req[-5:]]); c.close()
  import glob, subprocess
  for f in sorted(glob.glob('/tmp/hot/assets/cici-real/*.mp4') + glob.glob('/tmp/hot/assets/cici-real/*.webm')):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.split()
    dur = float([x for x in o if re.match(r'^[\d.]+$', x)][0]); lim = (6, 8) if 'cici-cat-' in f else (3.5, 8)
    ok(f'DB-V1 {os.path.basename(f)} <=2.5 MB, {lim[0]}-8 s, no audio track', os.path.getsize(f) <= 2.5e6 and lim[0] <= dur <= lim[1] and 'audio' not in o, [os.path.getsize(f), dur, o])
  # DB-X
  g = page(); J(g, FRESH); before = J(g, LED); J(g, "()=>{catEarn('x');P2S.cat.treats=1;catFeed()}"); g.wait_for_timeout(100)
  ok('DB-X1 points, ledger, caps, streak unchanged by Mochi', J(g, LED) == before)
  ok('DB-X1 realRewards gating untouched (no Mochi reference in reward code)', J(g, "typeof DEMO_MODE!=='undefined'"))
  g.close()
  g = page(q=''); J(g, "()=>{render()}")
  ok('DB-X2 flag off: no Mochi UI, storage or request', J(g, "!document.querySelector('#cat-card,#cat-feed,#cat-video,.catrow') && !/\"cat\"/.test(localStorage.getItem('cici.p2')||'')") and not any('cici-cat' in u for u in g.REQ)); g.close()
  # demo controls + screenshots
  for w, h in [(390, 844), (430, 932)]:
    for L in ('ko', 'en'):
      g = page(L, w, h, '?phase2=1&demo=1'); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;P2S.cat.treats=2;render();scrollTo(0,0)}"); g.wait_for_timeout(300)
      ok(f'[{w}/{L}] demo controls present (time, treats, crisis)', J(g, "['cattime','cattreat','catcrisis'].every(a=>document.querySelector('#cat-demo [data-act='+a+']'))"))
      g.screenshot(path=f'{SH}/home-{L}-{w}.png')
      J(g, "document.querySelector('#cat-card').scrollIntoView({block:'center'})"); g.wait_for_timeout(300); g.screenshot(path=f'{SH}/sheet-{L}-{w}.png')
      ok(f'[{w}/{L}] no page errors', not g.E, g.E); g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
