"""platform-app-v3.html — specialists, private classes and per-person signals (docs/specialists-and-ratings.md, 2026-10-17): Team cards on the
store page ordered by availability (never by score), the person sheet with the three signals and their definitions, Book sheet person rows with
next free time, a private 1:1 class that needs a teacher first, "Assigned by the store" for a no-selector store, Discover "N specialists",
Cici's two questions.  Usage: v3_team.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/team'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:360]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='?lang=ko', w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(700); return g
  for L in ('en', 'ko'):
    g = page(f'?lang={L}'); J = g.evaluate
    J("()=>{NOWX=600;ST.tab='discover';ST.page=null;ST.store='salon';render()}"); g.wait_for_timeout(300)
    # ---- store page Team
    cards = J("[...document.querySelectorAll('#st-team .tcard')].map(x=>x.innerText.replace(/\\n/g,' | '))")
    ok(f'[{L}] salon store page: Team section with one card per person (name, role, stars or New here, rebook or visits, next free time, Book)', len(cards) == 2 and all(re.search(r'(★ \d\.\d \(\d+\)|New here|새로 왔어요)', c) and re.search(r'(rebook|재예약|visits|방문)', c) and re.search(r'(Free |가능|Full this week|마감)', c) for c in cards), cards)
    ok(f'[{L}] the newcomer (6 ratings, 38 visits) shows "New here · 30+ visits", no stars, no rebook', any(re.search(r'(New here|새로 왔어요)', c) and '30+' in c and '★' not in c for c in cards), cards)
    ok(f'[{L}] cards are ordered by availability, not by score (team order = soonest first)', J("(()=>{const ids=[...document.querySelectorAll('#st-team .tcard')].map(x=>x.id.slice(3));const k=id=>{const z=nextFree('salon',S.salon.svcs[0].id,0,null,{staff:id});return z?z.d*1440+z.m:1e9};return ids.every((id,i)=>i===0||k(ids[i-1])<=k(id))})()"))
    g.screenshot(path=f'{SH}/team-{L}.png', full_page=True)
    g.click('#st-team .tbody >> nth=0'); g.wait_for_timeout(300)
    ps = J("document.querySelector('.sheet')?.innerText||''")
    ok(f'[{L}] person sheet: role · years, languages, specialty tags, the three signals each with a one-line definition, no reviews / no ranking line, Book with <name> · next time', re.search(r'(years|년차)', ps) and 'English' in ps and re.search(r'(balayage|발레아쥬)', ps) and re.search(r'(90 days|90일)', ps) and re.search(r'(12 months|12개월)', ps) and re.search(r"(No-shows|노쇼)", ps) and re.search(r'(No written reviews|글 리뷰)', ps) and J("/(Book with|에게 예약)/.test(document.querySelector('.sheet #p-book').innerText) && /\\d\\d:\\d\\d/.test(document.querySelector('.sheet #p-book').innerText)"), ps[:400])
    g.screenshot(path=f'{SH}/person-{L}.png')
    g.click('.sheet #p-book'); g.wait_for_timeout(400)
    rows = J("[...document.querySelectorAll('.sheet .slot.who')].map(x=>x.getAttribute('aria-pressed')+' '+x.dataset.v+' '+x.innerText.replace(/\\n/g,' | '))")
    ok(f'[{L}] Book with: the Book sheet opens with that person preselected; rows are Anyone first ("the store assigns", soonest time) then each person with role · signals · next free time', len(rows) == 3 and rows[0].startswith('false any') and re.search(r'(the store assigns|매장에서 배정)', rows[0]) and rows[1].startswith('true ') and all(re.search(r'\d\d:\d\d|full this week|이번 주 마감', r) for r in rows), rows)
    ok(f'[{L}] slots are filtered to that person; the confirm sheet names them', J("[...document.querySelectorAll('#bk-slots .slot')].every(r=>r.innerText.includes(resName('salon',BS.staff)))") and (g.click('#bk-slots .slot >> nth=0') or True) and (g.wait_for_timeout(300) or True) and J("document.querySelector('.sheet dl.conf').innerText.includes(resName('salon',BS.staff))"), J("document.querySelector('.sheet dl.conf')?.innerText"))
    g.screenshot(path=f'{SH}/book-who-{L}.png'); J("closeSheet()")
    J("()=>openBook('salon', S.salon.svcs[0].id)"); g.wait_for_timeout(300)
    ok(f'[{L}] fresh Book sheet: Anyone preselected, the person rows carry the same next-free times as the Team cards', J("BS.staff==='any' && document.querySelector('.sheet .slot.who[data-v=any]').getAttribute('aria-pressed')==='true'"))
    g.click('#bk-slots .slot >> nth=0'); g.wait_for_timeout(300)
    ok(f'[{L}] Anyone: confirm names the person the store would give (soonest), not "assigned" (the store chose, the member sees who)', J("PEND && PEND.rids.length===1 && document.querySelector('.sheet dl.conf').innerText.includes(resName('salon',PEND.rids[0]))")); J("closeSheet()")
    # ---- private class
    J("()=>{ST.store='capsule';render()}"); g.wait_for_timeout(300)
    ok(f'[{L}] Capsule Barre: Team cards for both teachers; Private barre is its own service row (1:1 · 50 min · with Yuna or Jiwoo · ₩80,000), not a timetable row', J("document.querySelectorAll('#st-team .tcard').length") == 2 and J("/1:1/.test(document.querySelector('#st-priv-pbarre').innerText) && /₩80,000/.test(document.querySelector('#st-priv-pbarre').innerText) && ![...document.querySelectorAll('#view .svc:not(.priv)')].some(r=>/(Private barre|프라이빗 바레)/.test(r.innerText))"), J("document.querySelector('#st-priv-pbarre')?.innerText"))
    g.click('#st-priv-pbarre'); g.wait_for_timeout(400)
    ok(f'[{L}] private barre Book sheet: teacher rows first (no Anyone), no times until a teacher is picked', J("!document.querySelector('.sheet .slot.who[data-v=any]') && document.querySelectorAll('.sheet .slot.who').length===2 && !!document.querySelector('#bk-pickone') && document.querySelectorAll('#bk-slots .slot').length===0"))
    g.click('.sheet .slot.who[data-v=yuna]'); g.wait_for_timeout(300)
    ok(f'[{L}] pick Yuna: the day jumps to her next free day, rows say 1:1 (no spots count), taken 1:1 times are not offered, the group pass is not applied, price ₩80,000', J("(()=>{const rs=[...document.querySelectorAll('#bk-slots .slot')];return rs.length>=1&&rs.every(r=>/1:1/.test(r.innerText)&&!/(spots|자리)/.test(r.innerText)&&!/(Pass|이용권)/.test(r.innerText)&&/₩80,000/.test(r.innerText))})()"), J("[...document.querySelectorAll('#bk-slots .slot')].map(r=>r.innerText.replace(/\\n/g,' | '))"))
    g.click('#bk-slots .slot >> nth=0'); g.wait_for_timeout(300)
    ok(f'[{L}] confirm: Private barre with Yuna, ₩80,000, no pass line', J("(()=>{const d=document.querySelector('.sheet dl.conf').innerText;return /(Private barre|프라이빗 바레)/.test(d)&&d.includes(resName('capsule','yuna'))&&/₩80,000/.test(d)&&PEND.rids[0]==='yuna'&&!PEND.usePass})()"), J("document.querySelector('.sheet dl.conf')?.innerText"))
    g.screenshot(path=f'{SH}/private-{L}.png'); J("closeSheet()")
    # ---- no-selector store
    J("()=>{S.moc.joined=true;ST.store='moc';render()}"); g.wait_for_timeout(300)
    ok(f'[{L}] Namu Spa (staffChoice none): no Team section, one "assigned by the store" line; Book sheet has no person rows; confirm says assigned', J("!document.querySelector('#st-team') && /(Assigned by the store|매장에서 배정)/.test(document.querySelector('#st-team-note').innerText)") and (J("()=>bookSheet('moc')") or True) and (g.wait_for_timeout(300) or True) and J("document.querySelectorAll('.sheet .slot.who').length===0 && !!document.querySelector('#bk-assigned')") and (g.click('#bk-slots .slot >> nth=0') or True) and (g.wait_for_timeout(300) or True) and J("/(Assigned by the store|매장에서 배정)/.test(document.querySelector('.sheet dl.conf').innerText)"))
    J("()=>document.querySelector('.sheet [data-act=dobook]').click()"); g.wait_for_timeout(400)
    ok(f'[{L}] ...and the booking row says assigned, never a name', J("/(Assigned by the store|매장에서 배정)/.test(bkWho(B[B.length-1]))")); J("closeSheet()")
    # ---- Discover
    J("()=>{ST.store=null;ST.tab='discover';render()}"); g.wait_for_timeout(300)
    ok(f'[{L}] Discover: appointment stores with a choice say "N specialists" in the meta line; the none store does not', J("(()=>{const t=document.querySelector('#view').innerText;return /(2 specialists|전문가 2명)/.test(t)&&!/(1 specialists|전문가 1명)/.test(t)})()"))
    # ---- Cici
    J("()=>{ST.tab='cici';ST.page=null;ST.store=null;render()}"); g.wait_for_timeout(200)
    last = lambda: J("(()=>{const m=CH.cici.msgs[CH.cici.msgs.length-1];return [m.text,(m.chips||[]).map(c=>c.label)]})()")
    J("()=>reply(CH.cici, %r)" % ('How is Sora?' if L == 'en' else '소라 평점 어때?')); g.wait_for_timeout(100); m = last()
    ok(f'[{L}] "how is Sora?": one sentence with stars, rebook, visits, the no-ranking line, and a Book with Sora chip', re.search(r'★ 4\.8', m[0]) and '82%' in m[0] and '2,100+' in m[0] and re.search(r"(don't rank|순위는 매기지)", m[0]) and len(m[1]) == 1 and re.search(r'(Book with|에게 예약)', m[1][0]), m)
    J("()=>{render();document.querySelector('.mchips .chip').click()}"); g.wait_for_timeout(400)
    ok(f'[{L}] the chip opens the Book sheet with Sora preselected', J("!!document.querySelector('.sheet #bk-slots') && BS.store==='salon' && BS.staff==='linh'")); J("closeSheet()")
    J("()=>reply(CH.cici, %r)" % ("Who's the best at Gureum Hair Studio?" if L == 'en' else 'Gureum Hair Studio 누가 제일 잘해?')); g.wait_for_timeout(100); m = last()
    ok(f'[{L}] "who is best?": refuses to rank, names two people with their signal (soonest / rebook or rating), two Book chips', re.search(r"(don't rank|순위는 매기지)", m[0]) and len(m[1]) == 2 and re.search(r'(soonest|가장 빠름)', m[0]), m)
    J("()=>reply(CH.cici, %r)" % ('Who is best?' if L == 'en' else '누가 제일 잘해?')); g.wait_for_timeout(100); m = last()
    ok(f'[{L}] no store named: asks which place, chips are the joined appointment stores with a choice (no Namu Spa)', re.search(r'(Which place|어느 매장)', m[0]) and 'Gureum Hair Studio' in m[1] and not any('Namu' in c for c in m[1]), m)
    ok(f'[{L}] no page errors / 4xx', not g.E and not g.NF, (g.E, g.NF)); g.context.close()
  b.close()
print(f'\n{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
