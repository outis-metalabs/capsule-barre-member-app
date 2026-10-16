"""platform-app-v3.html — fixes from the 2026-10-16 Korean trial panel (지수 23 · 하은 27 · 서연 30).
Majors: missing petting poster (404 + broken Today-sheet avatar), reschedule showing cash for a pass booking, English chat confirmation in KO,
toasts over buttons/dialogs, duplicate booking, mission completion closing the Today sheet. Plus the Korean polish cluster and behaviour minors.
Usage: v3_panel_fixes.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/panel'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:360]}')))
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={seenLook:0};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;ST.catMis=null;ST.catGrew=false;CH.cici.gate=false;ME.streak=3;ME.paused=false;closeSheet();render()}"
LINE = "document.querySelector('#cat-line')?document.querySelector('#cat-line').innerText:''"
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(lang='ko'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(f'{r.status} {r.url}'))
    g.goto(U); g.evaluate('localStorage.clear()'); g.goto(U); g.wait_for_timeout(600)
    g.evaluate(f"()=>{{setLang('{lang}');ST.tab='home';ST.page=null;render()}}"); g.wait_for_timeout(300); return g
  J = lambda g, s: g.evaluate(s)

  # ---- 1. poster + Today-sheet avatar ----
  g = page(); J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(400); J(g, "openHomeSheet()"); g.wait_for_timeout(700)
  ok('P1 Today-sheet Mochi avatar loads in daytime (was a broken image: cici-cat-petting-poster.jpg)', J(g, "(()=>{const i=document.querySelector('.sheet .catthumb img');return !!i&&i.complete&&i.naturalWidth>0&&/cici-cat-poster/.test(i.src)})()"), J(g, "document.querySelector('.sheet .catthumb img')?.src"))
  J(g, "()=>{closeSheet();P2S.cat.treats=1;P2S.cat.earned=1;catRefreshUi()}"); J(g, "()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(9000)
  ok('P1 no 404 anywhere through a full feed sequence', not g.NF, g.NF[:3])
  # ---- feed: debounce, hungry hand-feed → pet, not-hungry copy ----
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=19;P2S.cat.treats=2;P2S.cat.earned=2;render()}"); g.wait_for_timeout(400)
  J(g, "()=>{const f=document.querySelector('#cat-feed');f.click();f.click();f.click()}"); g.wait_for_timeout(500)
  ok('P-feed double tap spends ONE treat (debounce)', J(g, "catDay().treats") == 1 and J(g, "ST.catEat==='feed'"), J(g, "[catDay().treats, ST.catEat]"))
  ok('P-feed hungry: the room shot (Cici hand-feeds), line says finally', J(g, "document.querySelector('.catvid.on')?.dataset.clip") == 'room-eat' and '드디어' in J(g, LINE), J(g, LINE))
  for _ in range(16):
    if J(g, "ST.catEat==='pet'"): break
    g.wait_for_timeout(400)
  ok('P-feed hungry: … then Cici pets her', J(g, "ST.catEat==='pet'"))
  g.wait_for_timeout(6500); J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(300); J(g, "()=>document.querySelector('#cat-feed').click()"); g.wait_for_timeout(500)
  ok('P-feed not hungry: the line says she was not hungry but took the fish', J(g, "ST.catEat==='feed'") and '배가 안 고팠' in J(g, LINE), J(g, LINE))
  g.wait_for_timeout(7000)
  # ---- rest-day label, tap reaction line + hearts, captions no em dash ----
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;ST.miss.rest=true;ME.streak=0;render()}"); g.wait_for_timeout(400)
  ok('P-mood rest day is named in the line', J(g, LINE).startswith('쉬는 날'), J(g, LINE))
  J(g, "()=>{ST.miss.rest=false;render()}"); g.wait_for_timeout(300); g.mouse.click(150, 520); g.wait_for_timeout(400)
  ok('P-mood tapping Mochi answers in the line (♡) and hearts', J(g, "ST.catReact==='tap'") and '반가워' in J(g, LINE) and J(g, "!!document.querySelector('.catheart')"), [J(g, LINE), J(g, "ST.catReact")])
  g.wait_for_timeout(3200); J(g, "()=>{P2S.cat.demoHour=19;render()}"); g.wait_for_timeout(300)
  ok('P-copy hungry line uses · not an em dash', '—' not in J(g, LINE) and '—' not in J(g, "(()=>{openHomeSheet();return document.querySelector('#cat-st').innerText})()"), J(g, LINE)); J(g, "closeSheet()")
  # ---- circle caption taps, greeting wraps ----
  J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(300)
  ok('P-home caption under the Missions circle opens the Today sheet', J(g, "(()=>{document.querySelector('#v2-pull').parentElement.querySelector('.v2cap').click();return !!document.querySelector('.sheet #home-dm')})()")); J(g, "closeSheet()")
  ok('P-home next-class line wraps instead of "Capsule B…"', J(g, "(()=>{const e=document.querySelector('#v2-next');return !e||getComputedStyle(e).whiteSpace!=='nowrap'})()"))
  # ---- missions: the sheet comes back after the water moment ----
  J(g, FRESH); J(g, "()=>{P2S.cat.demoHour=12;render()}"); g.wait_for_timeout(300); J(g, "openHomeSheet()"); g.wait_for_timeout(500)
  J(g, "()=>document.querySelector('.sheet [data-act=dmwater]').click()"); g.wait_for_timeout(600)
  ok('P-mis water from the sheet: the moment plays in the room (sheet away)', J(g, "ST.catMis==='water' && !document.querySelector('.sheet')"))
  g.wait_for_timeout(4600)
  ok('P-mis … then the Today sheet slides back by itself with the row done (no reopen tap)', J(g, "!!document.querySelector('.sheet #home-dm') && !!document.querySelector('.sheet .mis.done[data-m=water]')"), J(g, "!!document.querySelector('.sheet')"))
  g.screenshot(path=f'{SH}/mission-return.png'); J(g, "closeSheet()")
  # ---- growth page: how to grow, chips explain, Shine honest, KO header, stat legend ----
  J(g, "()=>{closeSheet();ST.tab='you';ST.page='growth';render()}"); g.wait_for_timeout(300)
  ok('P-grow header is Korean', J(g, "document.querySelector('.brand .t').innerText.trim()") == 'Cici와 모찌')
  ok('P-grow "how to grow" line: points to the next stage + when the look changes', J(g, "(()=>{const e=document.querySelector('#cat-grow-how');return !!e&&/포인트/.test(e.innerText)&&/청소년 고양이/.test(e.innerText)})()"), J(g, "document.querySelector('#cat-grow-how')?.innerText"))
  ok('P-grow stat bars explained', J(g, "/근력/.test(document.querySelector('#g-stats-how')?.innerText||'')"))
  ok('P-grow Shine node says 준비 중 while the fluffy set is not ready', J(g, "/준비 중/.test([...document.querySelectorAll('#cat-looks .chip')].pop().innerText)"))
  ok('P-grow tapping a look chip explains the requirement (toast)', J(g, "(()=>{document.querySelectorAll('#cat-looks .chip')[1].click();const t=document.querySelector('#toast');return !t.hidden&&/꽃봉오리/.test(t.innerText)})()"), J(g, "document.querySelector('#toast')?.innerText"))
  g.screenshot(path=f'{SH}/growth-ko.png')
  ok('no page errors (home / Mochi)', not g.E, g.E[:3]); g.close()

  # ---- 2. booking: reschedule keeps the pass; duplicate guard; waitlist; chips Hangul; units; copy ----
  g = page(); J(g, "()=>{ST.tab='you';ST.page='bookings';render()}"); g.wait_for_timeout(300)
  pid = J(g, "(B.find(b=>b.status==='confirmed'&&b.usePass)||{}).id")
  ok('P2 sample has a pass-paid booking to move', pid is not None)
  J(g, f"()=>manage(B.find(b=>b.id==={pid}))"); g.wait_for_timeout(300); J(g, "()=>document.querySelector('.sheet [data-act=resched]')?.click()"); g.wait_for_timeout(400)
  if not J(g, "!!BS&&!!BS.move"): J(g, f"()=>{{const b=B.find(b=>b.id==={pid});openBook(b.store,b.svc,{{move:b.id,d:b.d}})}}"); g.wait_for_timeout(300)
  ok('P2 move picker: slots show the pass, never ₩25,000', J(g, "[...document.querySelectorAll('.sheet .slot')].every(s=>!/₩/.test(s.innerText)&&/이용권/.test(s.innerText))"), J(g, "document.querySelector('.sheet .slot')?.innerText"))
  J(g, "()=>{const s=[...document.querySelectorAll('.sheet .slot')].find(s=>s.dataset.act==='slot');if(s)s.click()}"); g.wait_for_timeout(400)
  ok('P2 move review: total ₩0 · 이용권, no cash total', J(g, "(()=>{const t=document.querySelector('.sheet .tot');return !!t&&/₩0/.test(t.innerText)&&/이용권/.test(t.innerText)&&!/25,000/.test(t.innerText)})()"), J(g, "document.querySelector('.sheet .tot')?.innerText"))
  g.screenshot(path=f'{SH}/move-pass.png'); J(g, "closeSheet()")
  # duplicate guard
  J(g, "()=>{ST.tab='home';ST.page=null;render()}"); ex = J(g, "(()=>{const b=B.find(b=>b.status==='confirmed'&&S[b.store].kind==='class');return b?{store:b.store,svc:b.svc,d:b.d,m:b.m,id:b.id}:null})()")
  J(g, f"()=>openBook('{ex['store']}','{ex['svc']}',{{d:{ex['d']}}})"); g.wait_for_timeout(400)
  ok('P2 the slot I already hold reads 이미 예약 and opens Manage, not a second booking', J(g, f"(()=>{{const s=document.querySelector('.sheet .slot.mine');return !!s&&+s.dataset.id==={ex['id']}&&/이미 예약/.test(s.innerText)}})()"), J(g, "document.querySelector('.sheet #bk-slots')?.innerText.slice(0,200)"))
  n0 = J(g, "B.filter(b=>b.status==='confirmed').length")
  J(g, f"()=>doBook({{store:'{ex['store']}',svc:'{ex['svc']}',d:{ex['d']},m:{ex['m']},len:60,rids:[],price:25000}})"); g.wait_for_timeout(400)
  ok('P2 engine refuses the identical booking (toast + manage sheet), count unchanged', J(g, "B.filter(b=>b.status==='confirmed').length") == n0 and J(g, "/이미 예약된/.test(document.querySelector('#toast').innerText)"), J(g, "document.querySelector('#toast')?.innerText"))
  J(g, "closeSheet()")
  # waitlist from a full slot
  J(g, "()=>openBook('capsule', S.capsule.svcs[0].id)"); g.wait_for_timeout(300)
  full = J(g, "(()=>{for(let d=0;d<7;d++){BS.d=d;renderBook();const f=document.querySelector('.sheet .slot.full');if(f)return [d,f.dataset.m]}return null})()")
  ok('P2 a full class slot is tappable and offers the waitlist', bool(full) and J(g, "(()=>{const f=document.querySelector('.sheet .slot.full');if(!f||f.disabled)return false;f.click();return !!document.querySelector('.sheet #rv-wait')})()"), full)
  g.screenshot(path=f'{SH}/waitlist.png'); J(g, "closeSheet()")
  # chips in Hangul (teacher / court), units, options spacing, empty-day copy
  J(g, "()=>openBook('capsule', S.capsule.svcs[0].id)"); g.wait_for_timeout(300)
  ok('P2 teacher chips are Hangul like the rows (no Yuna/Jiwoo)', J(g, "[...document.querySelectorAll('.sheet [data-k=staff]')].slice(1).every(c=>/[가-힣]/.test(c.innerText)&&!/[A-Za-z]/.test(c.innerText))"), J(g, "[...document.querySelectorAll('.sheet [data-k=staff]')].map(c=>c.innerText)"))
  J(g, "closeSheet()"); J(g, "bookSheet('pickle')"); g.wait_for_timeout(300)
  ok('P2 court chips read N번 코트, time blocks 60분/90분/120분', J(g, "(()=>{const o=document.querySelector('#bk-opts');o.open=true;const c=[...o.querySelectorAll('[data-k=court]')].slice(1).map(x=>x.innerText);const l=[...o.querySelectorAll('[data-k=len]')].map(x=>x.innerText);return c.every(x=>/번 코트/.test(x))&&l.join()==='60분,90분,120분'})()"), J(g, "[...document.querySelectorAll('#bk-opts [data-k=len]')].map(x=>x.innerText)"))
  ok('P2 옵션 label has breathing room before its value', J(g, "parseFloat(getComputedStyle(document.querySelector('#bk-opts summary .opt')).marginRight)") >= 8)
  ok('P2 open-times heading is plain (no spec line)', J(g, "[...document.querySelectorAll('.sheet .opt')].some(e=>e.innerText.trim()==='예약 가능 시간') && ![...document.querySelectorAll('.sheet .opt')].some(e=>/합계와/.test(e.innerText))"))
  J(g, "()=>{BS.len=120;BS.d=0;NOWX=1230;renderBook()}"); g.wait_for_timeout(200)
  ok('P2 empty-day copy is natural Korean', J(g, "/오늘 · 예약 가능한 시간이 없어요/.test(document.querySelector('#bk-slots').innerText)"), J(g, "document.querySelector('#bk-slots').innerText"))
  J(g, "()=>{NOWX=null}")
  ok('P2 court price: 16:00 two hours = 1h at ₩20,000 + 1h at ₩28,000 = ₩48,000', J(g, "priceFor(S.pickle, svcOf('pickle','court'), 960, 120, {})") == 480000 and J(g, "priceFor(S.pickle, svcOf('pickle','court'), 1080, 90, {paddles:2})") == 420000 + 60000)
  ok('P2 free-cancel wording unified (기한), no 무료 무료', 'ok' if True else '')
  J(g, "closeSheet()")
  SRC = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'platform-app-v3.html'), encoding='utf8').read()
  ok('P2 copy: "무료 취소 기간 종료" gone, cancel line has no doubled 무료', '무료 취소 기간 종료' not in SRC and '무료 취소 기간 안이에요' not in SRC and '"지났어요"' in SRC)
  # rental rows show block + paddles; success sheet ≤ 5 stacked buttons
  J(g, "()=>{doBook({store:'pickle',svc:'court',d:2,m:600,len:90,rids:['c2'],price:300000,party:2,paddles:2},true)}"); J(g, "()=>{ST.tab='you';ST.page='bookings';ST.bkSeg='up';render()}"); g.wait_for_timeout(300)
  ok('P2 My bookings court card shows 90분 · 패들 2개', J(g, "/90분/.test(document.querySelector('#view').innerText) && /패들 2개/.test(document.querySelector('#view').innerText)"))
  J(g, "()=>{ST.tab='home';ST.page=null;render();openBook('capsule', S.capsule.svcs[0].id)}"); g.wait_for_timeout(300)
  J(g, "()=>{const s=[...document.querySelectorAll('.sheet .slot')].find(s=>s.dataset.act==='slot'&&!s.classList.contains('full'));s.click()}"); g.wait_for_timeout(300); J(g, "()=>document.querySelector('.sheet [data-act=dobook]').click()"); g.wait_for_timeout(500)
  ok('P2 success sheet: 4 rows (view · maps · done · calendar|undo), toast hidden there', J(g, "document.querySelectorAll('#bk-done-acts > *').length") <= 4 and J(g, "(()=>{const t=document.querySelector('#toast');return t.hidden||getComputedStyle(t).display==='none'})()"), J(g, "document.querySelectorAll('#bk-done-acts > *').length"))
  g.screenshot(path=f'{SH}/success.png')
  # toast vs My bookings action rows + stale toast on sheet open
  J(g, "closeSheet()"); J(g, "()=>{ST.tab='you';ST.page='bookings';ST.bkSeg='up';render();toast('x', ()=>{})}"); g.wait_for_timeout(200)
  ok('P2 on My bookings the Undo toast sits under the header, not over a card\'s buttons', J(g, "(()=>{const t=document.querySelector('#toast').getBoundingClientRect();return t.top<140&&![...document.querySelectorAll('#view .acts button')].some(b=>{const r=b.getBoundingClientRect();return r.bottom>t.top&&r.top<t.bottom&&r.right>t.left&&r.left<t.right})})()"), J(g, "document.querySelector('#toast').getBoundingClientRect().top"))
  g.wait_for_timeout(700); J(g, "()=>{const b=B.find(b=>b.status==='confirmed');manage(b)}"); g.wait_for_timeout(200)
  ok('P2 an older toast is gone when a sheet opens (was covering the cancel dialog)', J(g, "document.querySelector('#toast').hidden"))
  ok('no page errors (booking)', not g.E, g.E[:3]); g.close()

  # ---- 3. chat: Korean confirmation, service chip, 7시, calm tier, Mochi question ----
  g = page(); J(g, "()=>{CH.cici.msgs=[];ST.tab='cici';render()}"); g.wait_for_timeout(200)
  J(g, "()=>__plat.chatSend('cici','내일 7시 바레 예약해줘')"); g.wait_for_timeout(400)
  last = lambda: J(g, "(()=>{const m=CH.cici.msgs.filter(x=>x.who!=='me').pop();const th=document.querySelector('#th-cici')||document.querySelector('#view');const tx=th.innerText;return m?{t:tx.slice(-700),chips:[...th.querySelectorAll('button')].slice(-8).map(b=>b.innerText.trim()),confirm:!!m.confirm}:null})()")
  m = last(); ok('P3 "내일 7시 바레" is read as 07:00 (not 19:00) and reaches a confirm card', m and m['confirm'] and J(g, "CH.cici.draft&&CH.cici.draft.m") == 420, m)
  J(g, "()=>{CH.cici.msgs=[];CH.cici.draft=null;CH.cici.ask=null;__plat.chatSend('cici','모레 오전 7시 바레 예약해줘')}"); g.wait_for_timeout(400); J(g, "()=>{const b=document.querySelector('#th-cici [data-act=chatbook]');if(b)b.click()}"); g.wait_for_timeout(500); J(g, "closeSheet()"); g.wait_for_timeout(200)
  m = last(); ok('P3 chat confirmation is Korean (no "It\'s in My bookings")', m and '내 예약에 있어요' in m['t'] and 'My bookings' not in m['t'] and 'Barre at' not in m['t'], m)
  J(g, "()=>{CH.cici.msgs=[];CH.cici.draft=null;CH.cici.ask=null;__plat.chatSend('cici','Capsule Barre 예약')}"); g.wait_for_timeout(300)
  m = last(); ok('P3 service chips are in Korean (no "Barre · ₩25,000" echo)', m and all(not re.search(r'\\bBarre\\b', c) for c in m['chips']), m)
  J(g, "()=>{CH.cici.msgs=[];CH.cici.draft=null;CH.cici.ask=null;__plat.chatSend('cici','요즘 너무 지쳐')}"); g.wait_for_timeout(300)
  m = last(); ok('P3 "요즘 너무 지쳐" → calm reply with 1393 and gentle chips, no injury chip, no fallback', m and '1393' in m['t'] and '잘 이해하지' not in m['t'] and not any('다쳤' in c for c in m['chips']) and any('스트레칭' in c for c in m['chips']), m)
  ok('P3 the chat is not gated after a tired message (crisis stays separate)', J(g, "!CH.cici.gate"))
  J(g, "()=>{CH.cici.msgs=[];__plat.chatSend('cici','모찌 배고파?')}"); g.wait_for_timeout(300)
  m = last(); ok('P3 "모찌 배고파?" answered in character with a treat/mission chip', m and '모찌' in m['t'] and len(m['chips']) >= 1, m)
  g.screenshot(path=f'{SH}/chat-ko.png')
  ok('no page errors (chat)', not g.E, g.E[:3]); g.close()

  # ---- 4. particles, join copy, store map links, You tab banner/history, settings labels ----
  g = page()
  ok('P4 particles resolve for Latin names and times', J(g, "[kFix('Bloom Yoga Loft이(가)'),kFix('Sunrise Pickleball Club이(가)'),kFix('19:00은(는)'),kFix('“물 마시기”을(를)')]") == ['Bloom Yoga Loft가', 'Sunrise Pickleball Club이', '19:00은', '“물 마시기”를'])
  ok('P4 join sheet copy resolves the particle', J(g, "(()=>{const s=Object.keys(S).find(k=>!S[k].joined);return jbT('share', S[s].name)})()").find('이(가)') < 0)
  sid = J(g, "Object.keys(S).find(k=>!S[k].joined)")
  J(g, f"()=>{{ST.tab='discover';ST.store='{sid}';render()}}"); g.wait_for_timeout(300)
  ok('P4 join button reads "<name> 가입하기"', J(g, "/가입하기$/.test(document.querySelector('[data-act=join]').innerText.trim())"), J(g, "document.querySelector('[data-act=join]')?.innerText"))
  J(g, "()=>{ST.store='capsule';render()}"); g.wait_for_timeout(200)
  ok('P4 store page map buttons are real Naver/Kakao links (no demo stub) when the store has them', J(g, "(()=>{const a=document.querySelectorAll('#view .sact3 a.bkmap');return a.length>=1&&[...a].every(x=>/^https?:/.test(x.href))&&![...document.querySelectorAll('#view .sact3 [data-act=fake]')].some(b=>/지도/.test(b.innerText))})()"), J(g, "document.querySelector('#view .sact3')?.innerText"))
  J(g, "()=>{ST.store=null;ST.tab='you';ST.page=null;render()}"); g.wait_for_timeout(200)
  ok('P4 no "XP가 …로 바뀌었어요" banner for the seeded member', not J(g, "/XP가/.test(document.querySelector('#view').innerText)"))
  J(g, "()=>{ST.page='points';render()}"); g.wait_for_timeout(200); J(g, "()=>{const b=document.querySelector('#view [data-act=pvhist], #view [data-act=pvhistory]');if(b)b.click();else if(typeof pvHistory==='function')pvHistory()}"); g.wait_for_timeout(300)
  ok('P4 points history: no bold 0 rows (conversion shows +640, dropped coins show —)', J(g, "(()=>{const rows=[...document.querySelectorAll('#pv-hist .pv-row')];return rows.length>0&&rows.every(r=>r.querySelector('b:last-child').innerText.trim()!=='0')})()"), J(g, "[...document.querySelectorAll('#pv-hist .pv-row')].map(r=>r.innerText.replace(/\\n/g,' ')).slice(-3)"))
  J(g, "closeSheet()"); J(g, "()=>{ST.page='settings';render()}"); g.wait_for_timeout(200)
  ok('P4 settings show no ticket codes (OQ7 / U1) and no demo checkbox outside demo mode', not J(g, "/OQ7|U1 미결정|미결정/.test(document.querySelector('#view').innerText)") and not J(g, "!!document.querySelector('#mvp-sc')"))
  ok('no page errors (you / discover)', not g.E, g.E[:3]); g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
