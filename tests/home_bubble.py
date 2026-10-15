"""platform-app-v2.html: Home bubble + daily missions (phase2) and the realistic Cici Home (default in v2). Usage: home_bubble.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app-v2.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/home-bubble'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
A11Y = r"""(sel)=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};
 const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;const m=c.match(/[\d.]+/g);if(m&&(m.length<4||+m[3]>.5))return c}return 'rgb(255,255,255)'};
 return [...document.querySelectorAll(sel)].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect(),a=lum(getComputedStyle(e).color),b=lum(bg(e));return {t:e.innerText.trim().slice(0,30),h:Math.round(r.height),w:Math.round(r.width),c:+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)}})}"""
GRANT = "__plat"
with sync_playwright() as p:
  b = p.chromium.launch()
  V1 = U.replace('platform-app-v2.html', 'platform-app.html')
  def page(q='?phase2=1', lang='ko', w=390, v1=False):
    c = b.new_context(viewport={'width': w, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.E = E
    u = V1 if v1 else U; g.goto(u + q); g.evaluate('localStorage.clear()'); g.goto(u + q); g.wait_for_timeout(300); g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render()}}"); return g
  J = lambda g, js: g.evaluate(js)
  # --- flag off: nothing new
  g = page('', 'ko'); ok('flag off: no bubble, no daily mission card, no real figure', J(g, "!document.querySelector('#hb-bubble,#home-dm,#cici-real')") and J(g, "!!document.querySelector('#home-mis')")); g.close()
  # --- greeting per language + a11y
  for L, hi in [('ko', '미나님~'), ('en', 'Hi Mina!'), ('vi', 'Chào Mina!')]:
    g = page(lang=L); t = g.inner_text('#hb-bubble')
    ok(f'[{L}] glass card greets by name ({hi}) + one bold line', t.startswith(hi) and len(g.inner_text('#hb-line')) >= 5, t)
    a = g.evaluate(A11Y, '#hb-bubble .hbt, #hb-bubble .hbhi, #hb-bubble .hbgo, #home-dm b, #home-dm .sub, #home-dm .mt, #home-dm .btn')
    ok(f'[{L}] AA contrast on bubble + mission card text', all(x['c'] >= 4.5 for x in a), [x for x in a if x['c'] < 4.5])
    tg = g.evaluate(A11Y, '#hb-bubble .hbgo, #home-dm .btn')
    ok(f'[{L}] 44px targets (chevron + mission buttons)', all(x['h'] >= 44 and x['w'] >= 44 for x in tg), tg)
    ok(f'[{L}] chevron has a localized accessible name', bool(g.get_attribute('#hb-bubble .hbgo', 'aria-label')))
    hd = g.inner_text('#dm-head'); ok(f'[{L}] mission header localized 0/3', {'ko': '오늘의 미션 0/3 완료', 'en': "Today's missions 0/3 done", 'vi': 'Nhiệm vụ hôm nay 0/3 xong'}[L] == hd, hd)
    ok(f'[{L}] progress bar + small cheering Cici + 3 missions (stretch, water, book)', J(g, "(()=>{const c=document.querySelector('#home-dm');return !!c.querySelector('.dmbar[role=progressbar][aria-valuenow=\"0\"]')&&!!c.querySelector('.dmcici')&&[...c.querySelectorAll('.mis')].map(m=>m.dataset.m).join()==='stretch,water,book'})()"))
    v = g.inner_text('#view'); ok(f'[{L}] no "coins pending" migration card (#24 check)', not re.search(r'coins? (are|is) pending|đang chờ|대기 중', v, re.I))
    if L in ('ko', 'en'): g.screenshot(path=f'{SH}/home-{L}-390.png'); g.screenshot(path=f'{SH}/home-full-{L}-390.png', full_page=True)
    ok(f'[{L}] no page errors', not g.E, g.E); g.close()
  # --- card line priority (v2 full-screen Home): today's class -> today's missions
  g = page(lang='en')
  ok('card: missions line with a berry highlight (n/3) when no class today; chevron opens the sheet', J(g, "document.querySelector('#hb-bubble').dataset.k") == 'missions' and J(g, "document.querySelector('#hb-line em').innerText") == '0/3' and J(g, "document.querySelector('#hb-bubble .hbgo').dataset.act") == 'hbsheet')
  ok('card: at most one secondary row (streak)', J(g, "document.querySelectorAll('#hb-bubble .hbsec').length") <= 1)
  g.click('#hb-bubble .hbgo'); g.wait_for_timeout(700); ok('chevron -> scrolls to the Today sheet', J(g, "Math.abs(document.querySelector('#home-sheet').getBoundingClientRect().top) < 120"))
  J(g, "()=>{scrollTo(0,0);const n=nowMin(),d=Math.floor(n/1440),m=Math.min(1439,n%1440+30);B.push({id:990001,store:'capsule',svc:B.find(x=>x.store==='capsule').svc,d,m,status:'confirmed',rids:[],source:'app'});render()}"); g.wait_for_timeout(200)
  ok("priority 1: today's class beats missions (time highlighted); chevron -> that booking", J(g, "document.querySelector('#hb-bubble').dataset.k") == 'class' and J(g, "document.querySelector('#hb-bubble .hbgo').dataset.id") == '990001' and bool(J(g, "document.querySelector('#hb-line em').innerText")), g.inner_text('#hb-bubble'))
  g.screenshot(path=f'{SH}/bubble-today-class-en-390.png')
  g.click('#hb-bubble .hbgo'); g.wait_for_timeout(300); ok("chevron -> manage today's booking sheet", J(g, "!!document.querySelector('.sheet')")); g.close()
  # --- missions: bonus, cap, stats, streak
  g = page(lang='en')
  s0 = J(g, "(()=>{const P=__plat.pv,m=P.ME();return {b:P.bal(m),l:P.life(m),st:__plat.gStats(m).st,streak:m.streak,act:!!(m.days&&m.days[dayKey(m,__plat.PV.now())])}})()")
  g.click('[data-act=dmwater]'); g.wait_for_timeout(200)
  s1 = J(g, "(()=>{const P=__plat.pv,m=P.ME();return {b:P.bal(m),st:__plat.gStats(m).st,streak:m.streak,act:!!(m.days&&m.days[dayKey(m,__plat.PV.now())])}})()")
  ok('water: +10 mission points, +1 glow, counts the streak day', s1['b'] - s0['b'] == 10 and s1['st']['glow'] - s0['st']['glow'] == 1 and s1['act'] and not s0['act'], [s0, s1])
  ok('card shows 1/3 and the bar moves', g.inner_text('#dm-head') == "Today's missions 1/3 done" and J(g, "document.querySelector('.dmbar').getAttribute('aria-valuenow')") == '1')
  g.click('[data-act=stretch]'); g.click('[data-act=stretchdone]'); g.wait_for_timeout(200)
  s2 = J(g, "(()=>{const P=__plat.pv,m=P.ME();return {b:P.bal(m),st:__plat.gStats(m).st}})()")
  ok('stretch: +10, +1 strength', s2['b'] - s1['b'] == 10 and s2['st']['str'] - s1['st']['str'] == 1, [s1, s2])
  g.click('#home-dm [data-act=bk]'); g.click('#bk-places [data-s=salon]'); g.click('#bk-svcs .svc >> nth=0'); g.click('.sheet .slot:not([disabled]) >> nth=0'); g.click('.sheet [data-act=dobook]'); g.wait_for_timeout(400)
  s3 = J(g, "(()=>{const P=__plat.pv,m=P.ME();return {b:P.bal(m),bon:m.ledger.filter(r=>r.reason==='mission_bonus').length,st:__plat.gStats(m).st}})()")
  ok(f'book a class completes 3/3 -> +30 bonus once, no extra stat', s3['b'] - s2['b'] == 30 and s3['bon'] == 1 and s3['st'] == s2['st'], [s2, s3])
  J(g, "closeSheet();ST.tab='home';ST.page=null;render()"); g.wait_for_timeout(200)
  ok('card: 3/3 + bonus earned', g.inner_text('#dm-head') == "Today's missions 3/3 done" and '+30' in g.inner_text('#dm-sub'))
  g.screenshot(path=f'{SH}/missions-done-en-390.png')
  r = J(g, "(()=>{const P=__plat.pv,m=P.ME(),b=P.bal(m),r=P.pvMission(m,'water');dmMark('water');dmMark('book');return {pts:r.pts,msg:r.msg,d:P.bal(m)-b,bon:m.ledger.filter(r=>r.reason==='mission_bonus').length}})()")
  ok('existing mission cap still holds (3rd mission today = 0, missionCap) and the bonus is never re-awarded', r['pts'] == 0 and r['msg'] == 'missionCap' and r['d'] == 0 and r['bon'] == 1, r)
  r = J(g, "(()=>{const m=__plat.pv.ME(),k=dayKey(m,__plat.PV.now()),st=__plat.gStats(m).st.glow;__plat.pv.pvMission(m,'water');return __plat.gStats(m).st.glow-st})()")
  ok('growth AC: +1 per stat per day (a 2nd water today adds no glow)', r == 0, r)
  J(g, "()=>{__plat.PV.srvOff+=864e5;ST.tab='home';render()}")
  ok('next day: missions reset to 0/3, bonus available again', g.inner_text('#dm-head') == "Today's missions 0/3 done")
  ok('no page errors (missions)', not g.E, g.E); g.close()
  # --- crisis: no bubble, no nudges, no cheering
  for L in ('ko', 'en'):
    g = page(lang=L); J(g, "()=>{CH.cici.gate=true;CH.cici.msgs.push({who:'cici',text:'x',care:true});ST.tab='home';render()}")
    ok(f'[{L}] crisis: no bubble, no daily-mission nudge card, no cheering Cici, no hint', J(g, "!document.querySelector('#hb-bubble,#home-dm,.dmcici,#g-hint')"))
    ok(f'[{L}] crisis: actions ignored (dmwater)', J(g, "(()=>{const b=__plat.pv.bal(__plat.pv.ME());document.body.insertAdjacentHTML('beforeend','<button id=x data-act=dmwater>x</button>');document.querySelector('#x').click();return __plat.pv.bal(__plat.pv.ME())===b})()"))
    g.close()
  # --- v2 Home image slot (placeholder until the official image); the rest of the app is not restyled vs platform-app.html
  for L in ('ko', 'en'):
    g = page('?phase2=1', L); g.wait_for_timeout(600)
    has = J(g, "(()=>{const i=document.querySelector('#cici-real video, #cici-real img');return i?{ok:i.tagName==='VIDEO'?(i.readyState>=1&&i.poster.includes(CICI_HOME.src)):(i.complete&&i.naturalWidth>0),src:i.currentSrc||i.getAttribute('src')}:null})()")
    ok(f'[{L}] Home image slot loads (CICI_HOME)', has and has['ok'], has)
    J(g, "()=>{ST.tab='you';ST.page='points';render()}"); a = g.inner_html('#view')
    g2 = page('?phase2=1', L, v1=True); J(g2, "()=>{ST.tab='you';ST.page='points';render()}"); b2 = g2.inner_html('#view')
    ok(f'[{L}] real: the rest of the app is not restyled (Points page identical to platform-app.html)', a == b2)
    J(g, "()=>{ST.tab='home';ST.page=null;render();scrollTo(0,0)}"); g.wait_for_timeout(400); g.screenshot(path=f'{SH}/home-real-{L}-390.png')
    ok(f'[{L}] real: no page errors', not g.E, g.E); g.close(); g2.close()
  print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
