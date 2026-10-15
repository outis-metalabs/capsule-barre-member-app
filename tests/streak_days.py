"""Streak in DAYS (prototype-only change to points spec v4.1, pending BA AC update), streak card, share sheet, win toast currency.
Usage: streak_days.py [base_url] [shots_dir]"""
import sys, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/workspace/hana-shots/acc-fix'
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {d}')))
with sync_playwright() as p:
  b = p.chromium.launch(); NET = []
  def page(lang='en', q=''):
    g = b.new_page(viewport={'width': 390, 'height': 844}); E = []; g.on('pageerror', lambda e: E.append(str(e))); g.E = E
    g.on('request', lambda r: NET.append(r.url) if not r.url.startswith(('http://localhost', 'data:', 'blob:')) else None)
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(200); g.evaluate(f"()=>{{setLang('{lang}');render()}}"); return g
  J = lambda g, js: g.evaluate(js)
  g = page()
  ok('seed: Mina migrates to a 12-day streak', J(g, "ME.streak")==12)
  ok('multiplier milestones 7/14/30 -> x1.1/x1.2/x1.3', J(g, "[0,6,7,13,14,29,30,45].map(n=>mult({streak:n})).join()")=='1,1,1.1,1.1,1.2,1.2,1.3,1.3')
  # engine on a fresh member with a controllable clock
  eng = J(g, """(()=>{const P=__plat.PV||PV;const off0=PV.srvOff;const m=pvMember('t1',{});const D=86400000;const r={};
    const at=k=>{PV.srvOff=off0+k*D};
    at(0); pvMission(m,'stretch'); r.a=m.streak; pvMission(m,'rest'); r.b=m.streak;            // mission counts the day, once
    at(1); pvTick(m); r.c=m.streak; pvMission(m,'stretch'); r.d=m.streak;
    at(3); pvTick(m); r.e=m.streak; r.rest=Object.keys(m.rest).length;                          // day 2 missed -> rest day keeps it
    pvMission(m,'stretch'); r.f=m.streak;
    at(11); pvTick(m); r.g=m.streak;                                                             // many missed days -> reset
    PV.srvOff=off0; return r})()""")
  ok('a completed self-care mission counts the day (once per day)', eng['a']==1 and eng['b']==1, eng)
  ok('next day counts again', eng['c']==1 and eng['d']==2, eng)
  ok('1 free rest day per week keeps the streak alive', eng['e']==2 and eng['rest']>=1 and eng['f']==3, eng)
  ok('more missed days reset the streak', eng['g']==0, eng)
  ms = J(g, """(()=>{const off0=PV.srvOff,D=86400000,m=pvMember('t2',{});const seen=[];for(let k=0;k<31;k++){PV.srvOff=off0+k*D;pvTick(m);pvMission(m,'stretch');}PV.srvOff=off0;return [m.streak,m.msReached.join(),m.notices.filter(n=>n.k==='milestone').map(n=>n.v.n).join()]})()""")
  ok('milestones fire at 7 / 14 / 30 days', ms[0]==31 and ms[1]=='7,14,30' and ms[2]=='7,14,30', ms)
  ok('voucher minStreak gate in days (14)', J(g, "PV.defs.some(v=>v.minStreak===14)") and not J(g, "PV.defs.some(v=>v.minStreak>0&&v.minStreak<7)"))
  # copy: no weeks
  for L in ['en','vi','ko']:
    g2 = page(L); txt = ''
    for js in ["()=>{ST.tab='home';ST.page=null;render()}","()=>{ST.tab='you';ST.page=null;render()}","()=>{ST.tab='you';ST.page='points';render()}"]:
      J(g2, js); txt += g2.inner_text('#view')
    bad = re.findall(r'\d+-week streak|chuỗi \d+ tuần|\d+주 연속|weekly streak|주간 연속', txt, re.I)
    ok(f'[{L}] streak copy in days, no weeks (Home/You/Points)', not bad and re.search(r'12-day streak|Chuỗi 12 ngày|12일 연속', txt), bad)
    ok(f'[{L}] notification + reward copy in days', not re.search(r'week streak|tuần!|주 연속', J(g2, "JSON.stringify([PVT.milestone,PVT.needStreak,PVT.streak])") if J(g2, "typeof PVT!=='undefined'") else ''))
    g2.close()
  # streak card
  for L, big in [('en','12 days'),('ko','12일'),('vi','12 ngày')]:
    g = page(L); J(g, "()=>{ST.tab='you';ST.page='points';render()}")
    c = g.locator('#pv-streak'); ok(f'[{L}] Points page: streak card near the top', c.count()==1 and J(g, "document.querySelector('#view').innerHTML.indexOf('pv-streak') < document.querySelector('#view').innerHTML.indexOf('pv-level')"))
    ok(f'[{L}] big count "{big}" + Cici celebrating still', g.inner_text('#pv-sk-n')==big and g.locator('#pv-streak img.sk-cici').count()==1)
    ok(f'[{L}] 14 day dots + text alternative', g.locator('#pv-sk-dots .sk-d').count()==14 and len(g.get_attribute('#pv-sk-dots','aria-label'))>20)
    ok(f'[{L}] rest day shown as a calm moon dot', g.locator('#pv-sk-dots .sk-d.rest svg').count()>=1)
    ok(f'[{L}] multiplier chip uses mult() (x1.1 at 12 days)', '1.1' in g.inner_text('#pv-sk-mult'))
    hs = J(g, "[...document.querySelectorAll('#pv-streak button')].map(b=>b.getBoundingClientRect().height)"); ok(f'[{L}] 44px targets', all(h>=43.5 for h in hs), hs)
    g.wait_for_timeout(300); g.locator('#pv-streak').screenshot(path=f'{SH}/streak-card-{L}-390.png') if L!='vi' else None
    NET.clear(); g.click('#pv-share'); g.wait_for_timeout(200)
    sh = g.inner_text('.sheet')
    order = J(g, "[...document.querySelectorAll('#sk-sheet .stack button')].map(b=>b.id)")
    ok(f'[{L}] share sheet: KakaoTalk first, Instagram Story, Copy link', order==['sk-kakao','sk-ig','sk-copy'], order)
    ok(f'[{L}] "Demo, nothing is posted" note', g.locator('#sk-demo').count()==1)
    svg = J(g, "document.querySelector('#sk-card').outerHTML")
    ok(f'[{L}] share card: Cici + N-day streak + app name + referral link', 'cheer.webp' in svg and re.search(r'12-day streak|Chuỗi 12 ngày|12일 연속', svg) and 'Cici' in svg and 'cici.example/r/' in svg)
    ok(f'[{L}] no personal data by default (name, stores)', not re.search(r'Mina|미나|Capsule|Gureum|Soom|Glow|Sunrise', svg) and not J(g, "document.getElementById('sk-pii-sw').checked"))
    g.click('#sk-pii-sw'); svg2 = J(g, "document.querySelector('#sk-card').outerHTML"); ok(f'[{L}] opt-in toggle adds name/places to the card', 'Mina' in svg2 or '미나' in svg2)
    g.click('#sk-pii-sw')
    if L != 'vi': g.wait_for_timeout(300); g.screenshot(path=f'{SH}/streak-share-{L}-390.png')
    g.click('#sk-kakao'); ok(f'[{L}] KakaoTalk is a mock (message, nothing posted)', g.locator('#sk-msg').count()==1)
    g.click('#sk-copy'); ok(f'[{L}] Copy link: demo message', g.locator('#sk-msg').count()==1)
    ok(f'[{L}] share: no network calls', not NET, NET)
    a = J(g, """()=>{const L=c=>{c=c/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)};const lum=s=>{const m=s.match(/[\\d.]+/g).map(Number);return .2126*L(m[0])+.7152*L(m[1])+.0722*L(m[2])};const bg=e=>{for(;e;e=e.parentElement){const c=getComputedStyle(e).backgroundColor;if(c&&!/rgba\\(0, 0, 0, 0\\)|transparent/.test(c))return c}return 'rgb(255,255,255)'};
      return [...document.querySelectorAll('.sheet button, .sheet .tag, .sheet label, #pv-streak b, #pv-streak .tag')].filter(e=>e.offsetParent&&e.innerText.trim()).map(e=>{const a=lum(getComputedStyle(e).color),b=lum(bg(e));return [e.innerText.slice(0,16),(Math.max(a,b)+.05)/(Math.min(a,b)+.05)]}).filter(x=>x[1]<4.5)}""")
    ok(f'[{L}] AA contrast on card + share sheet', not a, a)
    ok(f'[{L}] no page errors', not g.E, g.E[:2]); g.close()
  # crisis: never
  g = page('en'); J(g, "()=>{go('tab:cici');__plat.chatSend('cici','i want to end my life')}"); J(g, "()=>{closeSheet();ST.tab='you';ST.page='points';render()}")
  ok('crisis turn: no Share my streak, share sheet never opens', g.locator('#pv-share').count()==0 and (J(g, "shareSheet()") or g.locator('#sk-sheet').count()==0)); g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
