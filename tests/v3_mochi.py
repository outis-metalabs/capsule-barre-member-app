"""platform-app-v3.html — Mochi v3 (user brief 2026-10-16): hunger shown at the bowl, streak moods, visit treats with an arrival moment,
growth look + collar/bed in the room, missions with Mochi (stretch on the lap, water at her bowl). Phase 2 is on by default in v3.
Usage: v3_mochi.py [base_url] [shots_dir]"""
ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/v3-mochi'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:320]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={seenLook:0};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;ST.catMis=null;ST.catGrew=false;CH.cici.gate=false;ME.streak=12;ME.paused=false;closeSheet();render()}"
TOP = "(()=>{const v=[...document.querySelectorAll('.catvid')].filter(v=>+getComputedStyle(v).opacity>0.5).sort((a,b)=>(+getComputedStyle(b).zIndex||0)-(+getComputedStyle(a).zIndex||0))[0];return v?v.dataset.clip:null})()"
LINE = "document.querySelector('#cat-line')?document.querySelector('#cat-line').innerText:''"
SAD = re.compile(r"\b(sad|cry|crying|sick|lonely|starv\w*|guilt|forgot|forget)\b|슬퍼|울어|아파|배고파 죽|buồn|khóc|ốm", re.I)
SRC = open(os.path.join(ROOT, 'platform-app-v3.html'), encoding='utf8').read()
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang='en', q='', reduced=False):
    c = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce' if reduced else 'no-preference'); g = c.new_page(); g.E = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.C = []; g.on('console', lambda m: g.C.append(m.text) if m.type == 'error' else None)
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(600)
    g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render()}}"); g.wait_for_timeout(300); return g
  J = lambda g, s: g.evaluate(s)

  g = page(); J(g, FRESH); g.wait_for_timeout(600)
  ok('V3-0 Phase 2 on by default (no ?phase2=1), ?phase2=0 turns it off', J(g, "P2()") and 'q == null ? true' in SRC)
  ok('V3-0 no console errors / no 404 probes on load', not g.E and not g.C, g.E + g.C)

  # 1. Hunger at the bowl
  J(g, "()=>{P2S.cat.demoHour=18;render()}"); g.wait_for_timeout(900)
  ok('V3-1 hungry after 18:00 -> Cici + Mochi by her empty bowl (room-hungrybowl clip), no thought bubble, no bowl badge', J(g, "catHungry() && catMood()==='hungry'") and J(g, TOP) == 'hungry-room' and J(g, "!document.querySelector('#cici-real .cathbub') && !document.querySelector('#cat-room-bowl')"), [J(g, TOP)])
  for L in ('en', 'vi', 'ko'):
    J(g, f"()=>{{setLang('{L}');render()}}"); tx = J(g, LINE); ok(f'V3-1 [{L}] hunger copy is gentle, never sad: "{tx[:40]}"', tx and not SAD.search(tx), tx)
  J(g, "()=>{setLang('en');render()}"); g.screenshot(path=f'{SH}/hungry.png')
  J(g, "()=>{P2S.cat.treats=1;P2S.cat.earned=1;catRefreshUi()}"); J(g, "()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(700)
  ok('V3-1 feed while hungry: eats at the bowl first (square close-up as a rounded card)', J(g, "ST.catEat==='eat'") and J(g, TOP) == 'eating' and J(g, "(()=>{const v=document.querySelector('.catvid.on.sq');if(!v)return false;const r=v.getBoundingClientRect();return Math.abs(r.width-r.height)<2&&r.width<340&&parseFloat(getComputedStyle(v).borderRadius)>=20})()"), [J(g, "ST.catEat"), J(g, TOP)])
  g.screenshot(path=f'{SH}/feed-eat.png'); g.wait_for_timeout(3500)
  ok('V3-1 ... then Cici pets her', J(g, "ST.catEat==='pet'") and J(g, TOP) == 'petting' and 'petting' in J(g, LINE).lower(), [J(g, "ST.catEat"), J(g, TOP), J(g, LINE)])
  g.wait_for_timeout(2800); ok('V3-1 ... then the happy loop (room-play when on), hunger cleared, no popup', J(g, "ST.catEat==='play' && !catHungry() && !document.querySelector('.wtoast.in,.modal,.sheet')") and J(g, TOP) == J(g, "CAT_OPT['room-play']?'room-play':'room-happy'"), [J(g, "ST.catEat"), J(g, TOP)])
  ok('V3-1 happy-loop copy matches a content cat (eyes closed), not "playful"', 'playful' not in J(g, LINE).lower(), J(g, LINE))
  g.wait_for_timeout(3200); ok('V3-1 back to the mood loop', J(g, "!ST.catEat && catMood()!=='hungry'"))
  # not hungry: PR #37 eat clip plays once, then happy
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;P2S.cat.treats=1;P2S.cat.earned=1;render()}"); g.wait_for_timeout(500); J(g, "()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(500)
  ok('V3-1 feed when not hungry: fish arc, then Mochi eats from Cici\'s hand (room-eat, once)', J(g, "ST.catEat==='feed'") and J(g, TOP) == 'room-eat' and J(g, "(()=>{const v=document.querySelector('.catvid[data-clip=\"room-eat\"]');return !!v&&!v.loop})()"), [J(g, "ST.catEat"), J(g, TOP)])
  g.wait_for_timeout(4600); ok('V3-1 ... then happy (room-play when on)', J(g, "ST.catEat==='play'") and J(g, TOP) == J(g, "CAT_OPT['room-play']?'room-play':'room-happy'"), [J(g, "ST.catEat"), J(g, TOP)])
  ok('V3-1 toast sits under the glass card on Home (never over the greeting)', J(g, "(()=>{const t=document.querySelector('#toast'),c=document.querySelector('#hb-bubble');if(!t||t.hidden)return 'hidden';return t.getBoundingClientRect().top>=c.getBoundingClientRect().bottom})()") in (True, 'hidden'))

  # 2. Streak moods
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;ME.streak=3;render()}"); g.wait_for_timeout(700)
  ok('V3-2 streak 3: lively loop, purring copy', J(g, "catMood()==='lively'") and J(g, TOP) == 'lively' and 'purr' in J(g, LINE).lower(), [J(g, "catMood()"), J(g, LINE)])
  J(g, "()=>{ME.streak=12;render()}"); g.wait_for_timeout(700)
  ok('V3-2 streak 7+: play tier (room-play slot; lively until the clip lands) + on-a-roll copy', J(g, "catMood()==='play' && catClipName('play')===(CAT_OPT['room-play']?'room-play':'lively')") and ('roll' in J(g, LINE).lower() or 'playing' in J(g, LINE).lower()), [J(g, "catMood()"), J(g, LINE)])
  J(g, "()=>{ST.miss.rest=true;P2S.cat.demoHour=19;render()}"); g.wait_for_timeout(700)
  ok('V3-2 rest day: napping on Cici\'s lap, no hunger', J(g, "catMood()==='napping' && !catHungry()") and J(g, TOP) == 'napping' and 'nap' in J(g, LINE).lower(), [J(g, "catMood()"), J(g, LINE)])
  J(g, "()=>{ST.miss.rest=false;P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(500); J(g, "()=>catReact('tap')"); g.wait_for_timeout(1200)
  ok('V3-2 tap: react clip holds (still on it after 1.2 s, not a flicker)', J(g, "catMood()==='react'") and J(g, TOP) == 'react', [J(g, "catMood()"), J(g, TOP)])
  g.wait_for_timeout(2200); ok('V3-2 tap: back to the mood loop after ~2.9 s', J(g, "catMood()!=='react'"))

  # 3. Visit treats + arrival moment
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(400)
  led = J(g, "JSON.stringify([ME.ledger.length,ME.streak,gState().stage])")
  J(g, "()=>{catEarn('visit');catRefreshUi();catTreatArrive()}"); g.wait_for_timeout(150)
  ok('V3-3 visit treat: fish flies into the Feed circle, nothing in the ledger', J(g, "!!document.querySelector('.catfish') && catDay().treats===1") and J(g, "JSON.stringify([ME.ledger.length,ME.streak,gState().stage])") == led)
  g.wait_for_timeout(1300); ok('V3-3 ... badge pops to 1, fresh flag cleared', J(g, "document.querySelector('#cat-feed .catbadge').innerText==='1' && !(P2S.cat.fresh>0)"))
  J(g, "()=>{ST.tab='you';ST.page=null;render();catEarn('visit')}"); ok('V3-3 treat earned off-Home waits (fresh=1)', J(g, "P2S.cat.fresh===1"))
  J(g, "()=>{ST.tab='home';render()}"); g.wait_for_timeout(1000)
  ok('V3-3 ... and plays its arrival when Home opens', J(g, "!(P2S.cat.fresh>0) && catDay().treats===2"))
  ok('V3-3 demo scan toast mentions the treat', 'catVisitLine()' in SRC and 'treat && !catCrisis()' in SRC)
  J(g, "()=>{P2S.cat.treats=1;catRefreshUi();openHomeSheet()}"); g.wait_for_timeout(400); J(g, "()=>document.querySelector('#cat-feedbtn').click()"); g.wait_for_timeout(300)
  ok('V3-3 Feed from the sheet closes the sheet so the moment is visible', J(g, "!document.querySelector('.sheet') && !!ST.catEat"))
  g.wait_for_timeout(9000)

  # 4. Growth look + collar / bed in the room
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(300)
  ok('V3-4 kitten at Seed/Sprout; sheet card shows the look', J(g, "catLook()==='kitten'") and J(g, "(()=>{openHomeSheet();const t=document.querySelector('#cat-grow').innerText;closeSheet();return /Kitten/.test(t)})()"))
  J(g, "()=>{openHomeSheet()}"); ok('V3-4 growth track Kitten → Young cat → Fluffy cat with the current one marked', J(g, "(()=>{const c=[...document.querySelectorAll('#cat-looks .chip')];return c.length===3&&c[0].classList.contains('on')&&c[0].getAttribute('aria-current')==='true'})()")); J(g, "()=>closeSheet()")
  TO = lambda n: J(g, f"()=>{{let i=0;while(gState().stage<{n}&&i++<200)ME.ledger.push({{id:'TS'+i+'_'+Math.random(),delta:0,life:100,reason:'t',t:PV.now()}});render()}}")
  TO(2); g.wait_for_timeout(2100)
  ok('V3-4 Bud -> young cat look; collar granted AT BUD; -cat clip has the collar baked in, so NO 2D overlay', J(g, "catStage()===2 && catLook()==='cat' && catItemOwned('m_collar') && catItemOn('m_collar') && !catItemOwned('m_bed')") and J(g, "[...document.querySelectorAll('video[id^=cat-video]')].some(v=>/-cat\\.(webm|mp4)/.test(v.currentSrc)&&getComputedStyle(v).opacity>0.5)") and J(g, "(()=>{const c=document.querySelector('#cat-layer .catcollar');return !c||!c.classList.contains('on')})()"), J(g, "[catStage(),catLook(),P2S.cat.owned]"))
  J(g, "()=>{openHomeSheet()}"); HINT = J(g, "(document.querySelector('#cat-locked-hint')||{}).innerText||''"); J(g, "()=>closeSheet()")
  ok('V3-4 sheet hint: collar at Bud, bed at Blossom', 'Collar at Bud, bed at Blossom' in HINT, HINT)
  ok('V3-4 one-time "grew" moment in the card, no modal', J(g, "ST.catGrew===true && /grew/i.test(document.querySelector('#cat-line').innerText) && !document.querySelector('.modal,.wtoast.in')"), J(g, LINE))
  g.screenshot(path=f'{SH}/grew-collar.png')
  J(g, "()=>{catEquip('m_collar')}"); g.wait_for_timeout(400); ok('V3-4 Take off hides the collar in place (no re-render)', J(g, "!catItemOn('m_collar') && !document.querySelector('#cat-layer .catcollar.on')"))
  J(g, "()=>{catEquip('m_collar')}"); TO(3); g.wait_for_timeout(1200)
  ok('V3-4 Blossom -> still young cat, bed granted (next reward) and on the floor (visible, above the tab bar)', J(g, "catStage()===3 && catLook()==='cat' && catItemOwned('m_bed') && catItemOn('m_bed')") and J(g, "(()=>{const b=document.querySelector('#cat-layer .catbed');if(!b||!b.classList.contains('on'))return false;const r=b.getBoundingClientRect(),n=document.querySelector('nav.tabs,#tabs').getBoundingClientRect();return r.left>=0&&r.top>600&&r.top<n.top})()"), J(g, "[catStage(),P2S.cat.owned]"))
  TO(4); g.wait_for_timeout(1200)
  ok('V3-4 Shine -> stays young cat until CAT_LOOK_READY.fluffy (never younger), -cat clip, collar + bed kept, no new item', J(g, "catLook()==='cat' && catStage()===4 && [...document.querySelectorAll('video[id^=cat-video]')].some(v=>/-cat\\.(webm|mp4)/.test(v.currentSrc)) && catItemOwned('m_collar') && catItemOwned('m_bed') && P2S.cat.owned.length===2"), J(g, "P2S.cat.owned"))
  ok('V3-4 look variants are a drop-in slot (-cat / -fluffy) behind CAT_LOOK_READY', "CAT_LOOK_READY" in SRC and 'catVarPath' in SRC and J(g, "catClipSrc('lively').mp4.endsWith('cici-cat-lively-cat.mp4')"))
  J(g, "()=>{P2S.cat.demoHour=18;render()}"); g.wait_for_timeout(1800)
  ok('V3-4 Shine hungry: young-cat hungry clip (room-hungrybowl is kitten-only), no 2D collar', J(g, TOP) == 'hungry' and J(g, "!document.querySelector('#cat-layer .catcollar.on')"), [J(g, TOP), J(g, "[...document.querySelectorAll('#cat-layer .on')].map(e=>e.className)")])

  # 5. Missions with Mochi (kitten stage again: fresh member)
  J(g, 'localStorage.clear()'); g.goto(U); g.wait_for_timeout(900); J(g, "()=>{setLang('en');ST.tab='home';ST.page=null;render()}")
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;render();stretchSheet()}"); g.wait_for_timeout(1800)
  ok('V3-5 stretch: room clip (Mochi stretches on the lap) + timer chip, no sheet', J(g, TOP) == 'room-stretch' and J(g, "!!document.querySelector('#stretch-chip #stl') && !document.querySelector('.sheet')"))
  J(g, "()=>finishStretch()"); g.wait_for_timeout(300); ok('V3-5 stretch done: one toast with points · Mochi line · treat', J(g, "(()=>{const t=document.querySelector('#toast');return !t.hidden&&/\\+10/.test(t.innerText)&&/Mochi/.test(t.innerText)&&/treat/.test(t.innerText)})()"), J(g, "document.querySelector('#toast').innerText"))
  J(g, "()=>{openHomeSheet()}"); g.wait_for_timeout(500); J(g, "()=>document.querySelector('[data-act=dmwater]').click()"); g.wait_for_timeout(1800)
  ok('V3-5 water: room-waterbowl clip, caption = Cici holds her water while Mochi laps from her bowl (no sip), sheet closed', J(g, TOP) == 'room-waterbowl' and 'holds her water' in J(g, LINE) and 'sip' not in J(g, LINE).lower() and J(g, "!document.querySelector('.sheet') && !document.querySelector('#cat-pip')") and 'bowl' in J(g, LINE).lower(), [J(g, TOP), J(g, LINE)])
  g.screenshot(path=f'{SH}/water.png'); g.wait_for_timeout(4200)
  ok('V3-5 water ends: back to the mood loop; mission row shows the quiet inline line', J(g, "!ST.catMis") and J(g, "(()=>{openHomeSheet();const r=document.querySelector('#home-dm .mis[data-m=water] .misok');const t=r&&r.innerText;closeSheet();return !!t&&/bowl/i.test(t)})()"))
  ok('V3-5 slots for the combined Cici+Mochi water clip and the play clip exist', J(g, "'room-waterbowl' in CAT_OPT && 'room-play' in CAT_OPT && 'napping-bed' in CAT_OPT"))

  # Fixes
  ok('FIX caption "Earn a treat" not truncated', J(g, "(()=>{P2S.cat.treats=0;catRefreshUi();const c=document.querySelector('#cat-fab-empty').parentElement.querySelector('.v2cap');return c.scrollWidth<=c.clientWidth+1})()"))
  J(g, "()=>{P2S.cat.crisisAt=PV.now();P2S.cat.crisisOk=0;render()}"); g.wait_for_timeout(300)
  ok('CRISIS: calm loop, no Feed circle, no collar/bed, no hunger', J(g, "catCrisis() && catMood()==='calm' && !document.querySelector('#cat-feed,#cat-fab-empty') && !document.querySelector('.catwear.on') && !catHungry()"))
  ok('no page errors', not g.E, g.E[:3]); g.close()

  # reduced motion: still image, overlays still placed, no fx
  g = page(reduced=True); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;render()}"); g.wait_for_timeout(400)
  ok('REDUCED MOTION: hungry shows the bowl poster still (no video), no animation', J(g, "(()=>{const i=document.querySelector('#cici-real img.catstill');return !!i&&/hungrybowl_tall-poster/.test(i.getAttribute('src'))&&!document.querySelector('#cici-real video')})()"), J(g, "[...document.querySelectorAll('#cici-real img,#cici-real video')].map(e=>e.tagName+' '+e.className+' '+(e.getAttribute('src')||e.poster))"))
  J(g, "()=>{P2S.cat.treats=1;catRefreshUi();document.querySelector('#cat-feed').click()}"); g.wait_for_timeout(300)
  ok('REDUCED MOTION: feed works without the fx', J(g, "catDay().treats===0 && !document.querySelector('.catfish,.catheart')"))
  ok('no page errors (reduced motion)', not g.E, g.E[:3]); g.close()

  # KO + VI copy sweep
  for L in ('ko', 'vi'):
    g = page(L); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(300)
    lines = [J(g, LINE)]
    J(g, "()=>{ST.miss.rest=true;render()}"); lines.append(J(g, LINE)); J(g, "()=>{ST.miss.rest=false;P2S.cat.demoHour=18;render()}"); lines.append(J(g, LINE))
    J(g, "()=>{ST.catEat='eat';catRefreshUi()}"); lines.append(J(g, LINE)); J(g, "()=>{ST.catEat='feed';catRefreshUi()}"); lines.append(J(g, LINE)); J(g, "()=>{ST.catEat=false;ST.catGrew=true;catRefreshUi()}"); lines.append(J(g, LINE))
    ok(f'[{L}] every Mochi line localised, gentle, no leftover English/Dubu', all(l and not SAD.search(l) and not re.search(r'Dubu|두부', l) for l in lines) and (L != 'ko' or not any(re.search(r'[A-Za-z]{4,}', l.replace('Cici', '').replace('Mochi', '')) for l in lines)), lines)
    g.screenshot(path=f'{SH}/grew-{L}.png'); g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
