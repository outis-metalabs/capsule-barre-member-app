"""platform-app-v3.html — UI polish round (user 2026-10-17): Home card one stat row + one-line Next; Up next row is one tappable row (Check in only on
the day, no "Confirmed" tag); success sheet with a small Cici, one earn line in ₩, three links on one row; Discover as compact rows with 96 px thumbnails;
store page with a swipeable multi-photo gallery (counter + dots), no empty-state cards (Buy a pass row, Up next only when booked, composer behind one row).
Usage: v3_ui_polish.py [base_url] [shots_dir]"""
import sys, os, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/polish'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:360]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q='?lang=ko', w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}); g = c.new_page(); g.E = []; g.NF = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('response', lambda r: r.status >= 400 and g.NF.append(r.url))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(700); return g
  for L in ('en', 'ko'):
    g = page(f'?lang={L}'); J = g.evaluate
    # ---- Home card (real clock; a same-day class switches the card to its class layout, which is fine but not what this checks)
    J("()=>{upcoming().forEach(b=>{if(b.d===todayIdx())b.d=todayIdx()+1});render()}"); g.wait_for_timeout(200)
    ok(f'[{L}] Home card: membership + points pills on one row, both fully visible; Next on one line, nothing cut', J("(()=>{const m=document.querySelector('#hb-mem'),p=document.querySelector('#hb-pts'),n=document.querySelector('#v2-next');return !!m&&!!p&&Math.abs(m.getBoundingClientRect().top-p.getBoundingClientRect().top)<2&&m.scrollWidth<=m.clientWidth&&!!n&&n.scrollWidth<=n.clientWidth&&n.getBoundingClientRect().height<24})()"))
    ok(f'[{L}] Home card is under 210 px tall', J("document.querySelector('#hb-bubble').getBoundingClientRect().height") < 210, J("document.querySelector('#hb-bubble').getBoundingClientRect().height"))
    # ---- Up next row
    J("()=>{NOWX=360;upcoming().forEach(b=>{if(b.d===todayIdx())b.d=todayIdx()+1});ST.tab='you';ST.page=null;render()}"); g.wait_for_timeout(200) # pin 06:00 so a booking moved to "today 07:00" stays upcoming whatever the wall clock says
    ok(f'[{L}] Up next: one tappable row (service · store / when · who · chevron), no Confirmed tag, no Check in for a later day', J("(()=>{const u=document.querySelector('#you-next .up');if(!u)return false;const r=u.querySelector('.uprow');return !!r&&r.dataset.act==='managebk'&&!u.querySelector('[data-act=checkin]')&&!/Confirmed|확정/.test(u.innerText)&&/ · /.test(r.querySelector('b').innerText)&&!!u.querySelector('.ico')})()"), J("document.querySelector('#you-next .up')?.innerText"))
    J("()=>{const b=upcoming()[0];b.d=todayIdx();render()}"); g.wait_for_timeout(200)
    ok(f'[{L}] Up next on the day: Check in button beside the row', J("(()=>{const u=document.querySelector('#you-next .up');return !!u&&!!u.querySelector('[data-act=checkin].upci')})()"))
    g.screenshot(path=f'{SH}/upnext-{L}.png', clip={'x': 0, 'y': 420, 'width': 390, 'height': 180})
    # ---- success sheet
    J("()=>{const b=upcoming()[0];b.d=todayIdx()+1;ST.tab='home';render();success(upcoming().find(x=>x.store==='salon')||upcoming()[0], ()=>{})}"); g.wait_for_timeout(300)
    ok(f'[{L}] success sheet: Cici image ≤ 120 px wide and inside its box; text takes the rest', J("(()=>{const p=document.querySelector('#bk-confirm .pic'),i=p&&p.querySelector('img'),t=document.querySelector('#bk-confirm .txt');return !!p&&p.getBoundingClientRect().width<=120&&i.getBoundingClientRect().width<=p.getBoundingClientRect().width+1&&t.getBoundingClientRect().width>200})()"))
    ok(f'[{L}] success sheet: one earn line with P and ₩, no "saved in My bookings" filler', J("/\\d+P/.test(document.querySelector('#bk-earn').innerText) && /₩[\\d,]+/.test(document.querySelector('#bk-earn').innerText)") and not J("/saved in My bookings|내 예약에 저장됐어요/.test(document.querySelector('#bk-confirm').innerText)"), J("document.querySelector('#bk-earn').innerText"))
    ok(f'[{L}] success sheet: three links (view · Naver map · KakaoMap) on ONE row', J("(()=>{const ls=[...document.querySelectorAll('#bk-links .link')];return ls.length===3&&new Set(ls.map(l=>Math.round(l.getBoundingClientRect().top))).size===1})()"), J("[...document.querySelectorAll('#bk-links .link')].map(l=>[l.innerText,Math.round(l.getBoundingClientRect().top)])"))
    g.screenshot(path=f'{SH}/success-{L}.png'); J("closeSheet()")
    # ---- Discover
    J("()=>{ST.tab='discover';ST.page=null;ST.store=null;render()}"); g.wait_for_timeout(400)
    ok(f'[{L}] Discover: compact rows with a 96 px square thumbnail, name + meta beside it, next-slot chip; a row is under 130 px', J("(()=>{const c=document.querySelector('#dres > .dcard'),p=c.querySelector('.dphoto'),r=p.getBoundingClientRect();return Math.round(r.width)===96&&Math.round(r.height)===96&&!!c.querySelector('.dtxb .dname')&&!!c.querySelector('.dmeta')&&c.getBoundingClientRect().height<130&&c.querySelector('.dtxb').getBoundingClientRect().left>r.right})()"), J("document.querySelector('#dres > .dcard')?.getBoundingClientRect().height"))
    ok(f'[{L}] Discover: the slot chip says what it is (Next free · [service ·] day time), prefers a slot from 09:00, and never truncates', J("(()=>{const cs=[...document.querySelectorAll('#dres > .dcard')];return cs.length>0&&cs.every(c=>{const b=c.querySelector('.dslot');if(!b)return true;const sp=b.querySelector('.dslott'),tx=b.innerText,ok=/^(Next free|가장 빠른 자리|Còn chỗ) · /.test(tx)&&sp.scrollWidth<=sp.clientWidth+1;const sid=c.id.slice(3),m=/(\\d\\d):(\\d\\d)$/.exec(tx);const mins=m?+m[1]*60+ +m[2]:0;const anyLate=[0,1,2,3,4,5,6].some(d=>slotsFor(sid,S[sid].svcs[0].id,d,{len:60,party:4}).some(q=>q.left!==0&&q.m>=540));return ok&&(!anyLate||mins>=540)})})()"), J("[...document.querySelectorAll('#dres .dslot')].map(b=>[b.innerText,b.scrollWidth,b.clientWidth])"))
    ok(f'[{L}] Discover: five rows fit in the first screen', J("[...document.querySelectorAll('#dres > .dcard')].filter(c=>c.getBoundingClientRect().top<844).length") >= 5)
    g.screenshot(path=f'{SH}/discover-{L}.png')
    # ---- store page
    J("()=>{ST.store='capsule';render()}"); g.wait_for_timeout(500)
    ok(f'[{L}] store page: multi-photo gallery with counter 1/N and dots; swiping updates the counter', J("(()=>{const t=document.querySelector('#st-gal .galtrack');if(!t||t.children.length<2)return false;const n0=document.querySelector('#st-galn').innerText;t.scrollTo({left:t.clientWidth,behavior:'instant'});return n0==='1/'+t.children.length})()") and (g.wait_for_timeout(300) or True) and J("document.querySelector('#st-galn').innerText") == J("'2/'+document.querySelectorAll('#st-gal .himg').length") and J("document.querySelectorAll('#st-galdots i.on').length") == 1, J("document.querySelector('#st-galn')?.innerText"))
    ok(f'[{L}] store page (joined, has a pass): pass card with a Buy a pass row inside, Up next with the booking, Inbox with a message row (no composer until tapped)', J("!!document.querySelector('#st-passbuy') && !!document.querySelector('#view .up .uprow') && !!document.querySelector('#st-msg') && !document.querySelector('#view form[data-form=store]')"))
    ok(f'[{L}] store page: no empty-state copy', not J("/No passes here|이용권이 없어요|Nothing booked yet|아직 예약이 없어요|No messages yet|메시지가 없어요/.test(document.querySelector('#view').innerText)"), J("document.querySelector('#view').innerText.slice(-300)"))
    g.click('#st-msg'); g.wait_for_timeout(200)
    ok(f'[{L}] Message row opens the composer with focus', J("!!document.querySelector('#sm-capsule') && document.activeElement.id==='sm-capsule'"))
    J("()=>{ST.stMsg=null;S.yoga.joined=true;ST.store='yoga';render()}"); g.wait_for_timeout(400)
    ok(f'[{L}] store page (joined, nothing yet): single Buy a pass row, no Up next section, no pass/inbox empty cards', J("(()=>{const hs=[...document.querySelectorAll('#view h2')].map(h=>h.innerText);return !!document.querySelector('#st-passbuy')&&!hs.some(h=>/Up next|다가오는 예약/.test(h))&&!hs.some(h=>/passes|이용권·크레딧/.test(h))})()"), J("[...document.querySelectorAll('#view h2')].map(h=>h.innerText)"))
    g.screenshot(path=f'{SH}/store-yoga-{L}.png', full_page=True)
    ok(f'[{L}] no page errors / 4xx', not g.E and not g.NF, (g.E, g.NF)); g.context.close()
  b.close()
print(f'\n{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
