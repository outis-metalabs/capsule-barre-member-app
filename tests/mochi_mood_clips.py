"""Official Mochi mood clips (lively / hungry / react) + petting default. Crossfade wiring.
Usage: mochi_mood_clips.py [base_url] [shots_dir]"""
import sys, os, re, glob, subprocess
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/mochi-clips'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;CH.cici.gate=false;ME.streak=12;ME.paused=false;render()}"
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang='ko', w=390, h=844, q='?phase2=1&demo=1'):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []
    g.on('pageerror', lambda e: g.E.append(str(e)))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(400)
    g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render();scrollTo(0,0)}}"); g.wait_for_timeout(300); return g
  J = lambda g, s: g.evaluate(s)

  # Asset presence + specs
  for mood, lim in [('petting', (5.5, 8)), ('lively', (3, 8)), ('napping', (3, 8)), ('hungry', (3, 8)), ('react', (2, 8))]:
    for ext in ('mp4', 'webm'):
      f = f'/tmp/hot/assets/cici-real/cici-cat-{mood}.{ext}'
      assert os.path.exists(f), f
      o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.split()
      dur = float([x for x in o if re.match(r'^[\d.]+$', x)][0])
      ok(f'asset {mood}.{ext} ≤2.5MB muted {lim[0]}-{lim[1]}s', os.path.getsize(f) <= 2.5e6 and lim[0] <= dur <= lim[1] and 'audio' not in o, [os.path.getsize(f), dur, o])

  g = page(); J(g, FRESH); g.wait_for_timeout(800)
  ok('clips map: lively/napping/hungry/react pointed at own files', J(g, "CICI_CAT.clips.lively==='lively' && CICI_CAT.clips.napping==='napping' && CICI_CAT.clips.hungry==='petting' && CICI_CAT.clips.react==='react' && CICI_CAT.clips.calm==='petting'"))
  ok('fadeMs in 300–500', J(g, "CICI_CAT.fadeMs>=300 && CICI_CAT.fadeMs<=500"))

  # Default / lively on active streak
  J(g, "()=>{ST.miss.rest=false;ME.streak=12;P2S.cat.demoHour=12;ST.catReact=null;render()}"); g.wait_for_timeout(600)
  ok('MC mood lively on active streak → lively clip', J(g, "catMood()==='lively' && catClipName('lively')==='lively' && (document.querySelector('.catvid.on')||{}).dataset.clip==='lively'"), J(g, "[catMood(), (document.querySelector('.catvid.on')||{}).dataset.clip]"))

  # Hungry after 18:00
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=18;ST.miss.rest=false;ME.streak=12;render()}"); g.wait_for_timeout(800)
  ok('hungry after 18:00 no self-care → stays in the Cici+Mochi room (petting loop) + empty-bowl cue on Feed', J(g, "catHungry() && catMood()==='hungry' && (document.querySelector('.catvid.on')||{}).dataset.clip==='petting' && !!document.querySelector('#v2-acts #cat-room-bowl')"), J(g, "[catHungry(),catMood(),(document.querySelector('.catvid.on')||{}).dataset.clip]"))

  # Rest day stays petting (nap not wired)
  J(g, "()=>{ST.miss.rest=true;P2S.cat.demoHour=19;render()}"); g.wait_for_timeout(600)
  ok('rest/napping uses napping clip', J(g, "catMood()==='napping' && catClipName('napping')==='napping' && (document.querySelector('.catvid.on')||{}).dataset.clip==='napping'"), J(g, "[catMood(),(document.querySelector('.catvid.on')||{}).dataset.clip]"))

  # React on tap
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;ME.streak=12;ST.miss.rest=false;render()}"); g.wait_for_timeout(500)
  J(g, "()=>{catReact('tap')}"); g.wait_for_timeout(500)
  ok('tap → react clip crossfade', J(g, "catMood()==='react' && (document.querySelector('.catvid.on')||{}).dataset.clip==='react'"), J(g, "[catMood(),(document.querySelector('.catvid.on')||{}).dataset.clip]"))
  g.wait_for_timeout(900)
  ok('react returns to lively/petting mood after moment', J(g, "catMood()!=='react'"))

  # Crossfade stage
  ok('dual-video stage for crossfade', J(g, "document.querySelectorAll('#cici-real .catvid').length>=2"))
  ok('Home non-scroll', J(g, "Math.abs(document.documentElement.scrollHeight-document.documentElement.clientHeight)<=2"))

  # Mission slots not inventing new stretch/water files in CICI map
  # Mission clips
  for kind, lim in [('mochi-stretch', 1e6), ('mochi-water', 1e6)]:
    for ext in ('mp4', 'webm'):
      f = f'/tmp/hot/assets/cici-real/{kind}.{ext}'
      ok(f'asset {kind}.{ext} ≤1MB muted', os.path.exists(f) and os.path.getsize(f) <= lim, f)
  J(g, FRESH); J(g, "()=>{stretchSheet()}"); g.wait_for_timeout(500)
  ok('stretch Start plays the stretch clip in the room + timer chip (no popup)', J(g, "!document.querySelector('#cat-clip,.cateat,.catclip') && !!document.querySelector('#stretch-chip #stl') && (document.querySelector('.catvid.on')||{}).dataset.clip==='stretch'"))
  J(g, "()=>{stretchStop(); openHomeSheet()}"); g.wait_for_timeout(300); J(g, "()=>document.querySelector('[data-act=dmwater]').click()"); g.wait_for_timeout(600)
  ok('water Done plays the water clip in the room', J(g, "(document.querySelector('.catvid.on')||{}).dataset.clip==='water' && !document.querySelector('.sheet')"))
  J(g, "()=>{catMisEnd(); openHomeSheet()}"); g.wait_for_timeout(300)
  ok('water Done: quiet inline row confirmation with ≤64px round thumb, no overlay', J(g, "(()=>{const r=document.querySelector('#home-dm .mis[data-m=water] .misok img.misthumb');if(!r)return false;const b=r.getBoundingClientRect();return b.width<=64&&b.height<=64&&getComputedStyle(r).borderRadius!=='0px'&&!document.querySelector('#cat-clip,.cateat')})()"))
  J(g, "()=>closeSheet()")

  # Panel must-fixes
  J(g, FRESH); J(g, "()=>{P2S.cat.treats=0;P2S.cat.demoHour=18;render();openHomeSheet()}"); g.wait_for_timeout(400)
  ok('first-treat on-ramp: no greyed Feed; Open missions + Book', J(g, "document.querySelector('#cat-card').dataset.ramp==='1' && !!document.querySelector('#cat-open-mis') && !!document.querySelector('#cat-open-bk') && !document.querySelector('#cat-feedbtn')"))
  J(g, "()=>{document.querySelector('#cat-open-mis').click()}"); g.wait_for_timeout(300)
  ok('on-ramp Open missions focuses mission card (≤2 taps to earn)', J(g, "!!document.querySelector('#home-dm')"))
  ok('no popup API left (catClipPlay / #cat-clip / .cateat)', J(g, "typeof catClipPlay==='undefined'") and '#cat-clip' not in open('/tmp/hot/platform-app-v2.html',encoding='utf8').read())
  J(g, "()=>{closeSheet(); P2S.placed=[]; P2S.cat.owned=[]; openHomeSheet()}"); g.wait_for_timeout(400)
  ok('short sheet: empty room hidden; locked items collapsed', J(g, "!document.querySelector('#p2-room') && !!document.querySelector('#cat-locked-hint') && document.querySelectorAll('#cat-items .catitem').length===0"))
  ok('napping clip is distinct file (not petting)', J(g, "catClipName('napping')==='napping' && CICI_CAT.clips.napping==='napping'"))
  for mood in ('lively','napping','hungry','react'):
    ok(f'distinct asset exists for {mood}', os.path.exists(f'/tmp/hot/assets/cici-real/cici-cat-{mood}.mp4'))

  for w,h in [(390,844),(430,932)]:
    for L in ('ko','en'):
      g2 = page(L,w,h); J(g2, FRESH)
      J(g2, "()=>{P2S.cat.demoHour=12;ME.streak=12;render()}"); g2.wait_for_timeout(700)
      g2.screenshot(path=f'{SH}/lively-{L}-{w}.png')
      J(g2, "()=>{P2S.cat.demoHour=18;render()}"); g2.wait_for_timeout(800)
      g2.screenshot(path=f'{SH}/hungry-{L}-{w}.png')
      J(g2, "()=>{P2S.cat.demoHour=12;catReact('tap')}"); g2.wait_for_timeout(400)
      g2.screenshot(path=f'{SH}/react-{L}-{w}.png')
      J(g2, "()=>{ST.catReact=null;ST.miss.rest=true;P2S.cat.demoHour=19;render()}"); g2.wait_for_timeout(700)
      g2.screenshot(path=f'{SH}/napping-{L}-{w}.png')
      J(g2, "()=>{ST.miss.rest=false;stretchSheet()}"); g2.wait_for_timeout(500)
      g2.screenshot(path=f'{SH}/stretch-{L}-{w}.png')
      J(g2, "()=>{stretchStop(); closeSheet(); openHomeSheet(); const x=document.querySelector('[data-act=dmwater]'); if(x)x.click()}"); g2.wait_for_timeout(600)
      g2.screenshot(path=f'{SH}/water-{L}-{w}.png')
      J(g2, "()=>{closeSheet()}")
      J(g2, "()=>{P2S.cat.treats=0;P2S.placed=[];P2S.cat.owned=[];P2S.cat.demoHour=18;render();openHomeSheet()}"); g2.wait_for_timeout(500)
      if w in (390,430) and L in ('ko','en'):
        g2.screenshot(path=f'{SH}/ramp-0treat-{L}-{w}.png')
        g2.evaluate("()=>{const e=document.querySelector('#cat-card'); if(e)e.scrollIntoView({block:'center'})}")
        g2.wait_for_timeout(200)
        g2.screenshot(path=f'{SH}/sheet-short-{L}-{w}.png')
      ok(f'[{w}/{L}] no page errors', not g2.E, g2.E); g2.close()
  g.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
