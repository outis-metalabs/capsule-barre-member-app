"""Cue Book with Cici member UI (CB-2..CB-8) on platform-app-v2.html, using PR #33's API and real lessons.js (basic-01).
Audio is stubbed (no network playback). Usage: cue_book_ui.py [base_url]"""
import sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app-v2.html'
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
STUB = """()=>{window.__played=[];window.__paused=0;HTMLMediaElement.prototype.play=function(){__played.push([this.src,this.playbackRate]);return Promise.resolve()};HTMLMediaElement.prototype.pause=function(){__paused++}}"""
TAG = """async()=>{await __plat.cueBook.load();const up=B.find(b=>b.store==='capsule'&&b.svc==='barre'&&b.status==='confirmed'&&!bkStarted(b));const past=B.find(b=>b.pv==='demo-past');
 __plat.cueBook.tagSession(up.store,up.svc,up.d,up.m,'basic-01');__plat.cueBook.tagSession(past.store,past.svc,past.d,past.m,'basic-01');window.__up=up;window.__past=past;render();}"""
with sync_playwright() as p:
  br = p.chromium.launch()
  def pg(q, lang='en'):
    g = br.new_context(viewport={'width': 390, 'height': 844}).new_page(); g.E = []; g.on('pageerror', lambda e: g.E.append(str(e)))
    g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(400); g.evaluate(STUB); g.evaluate(f"setLang('{lang}')"); return g
  g = pg('?phase2=1'); J = g.evaluate
  J("()=>{const b=B.find(x=>x.pv==='demo-past');ME.att[b.id]={store:'capsule',t:PV.now()};openBookings('up')}")
  ok('CB-2 flag off: no cue UI in bookings', g.locator('.cuebook').count() == 0)
  J("openBookings('past')"); ok('CB-2 flag off: no practice card', g.locator('.cuepractice').count() == 0)
  J("()=>{ST.page=null;ST.tab='home';render();openHomeSheet()}"); ok('CB-2 flag off: no Home card', g.locator('#cue-home').count() == 0)
  g = pg('?phase2=1&cueBook=1'); J = g.evaluate
  J("openBookings('up')"); ok('CB-2 untagged: no cue UI', g.locator('.cuebook').count() == 0)
  J(TAG); J("openBookings('up')")
  ok('CB-3 tagged booked class: exactly one "Today\'s cues with Cici" section, in its row', g.locator('.cuebook').count() == 1 and J("!!document.querySelector('#bk-'+__up.id+' .cuebook')") and "Today's cues with Cici" in g.locator('.cuebook h3').inner_text())
  c = g.locator('.cuebook')
  ok('CB-3 5 positions in order with image', J("[...document.querySelectorAll('.cuebook .cuepos')].map(e=>+e.dataset.pos).join()") == '0,1,2,3,4' and J("[...document.querySelectorAll('.cuebook .cuepos img')].every((im,i)=>im.getAttribute('src')===CUE.lessons['basic-01'].positions[i].image&&/^https:/.test(im.src))"))
  ok('PO: KR-only name when nameEn is null', c.locator('.cuepos b').first.inner_text() == '1. ' + J("CUE.lessons['basic-01'].positions[0].nameKr"))
  ok('CB-3 each cue shows EN and KR', J("[...document.querySelectorAll('.cuebook .cue')].every(e=>e.querySelector('.cue-en').innerText&&e.querySelector('.cue-ko').innerText)") and c.locator('.cue').count() == J("CUE.lessons['basic-01'].cues.length"))
  ok('CB-5 nothing autoplays', J("__played.length") == 0)
  ok('CB-6 accessible names', c.get_by_role('button', name='Play cue 1 normal', exact=True).count() == 1 and c.get_by_role('button', name='Play cue 1 slow', exact=True).count() == 1)
  c.get_by_role('button', name='Play cue 1 normal', exact=True).click(); c.get_by_role('button', name='Play cue 2 slow', exact=True).click(); g.wait_for_timeout(100)
  P = J("__played")
  ok('CB-5 Normal plays 1x, Slow plays the same kind of file at 0.75x; a new cue stops the current one', len(P) == 2 and P[0][1] == 1 and P[1][1] == 0.75 and J("__paused") >= 1 and P[1][0] == J("CUE.lessons['basic-01'].cues.filter(c=>c.position>=0).sort((a,b)=>a.position-b.position)[1].audioSlowUrl"), P)
  ph = c.locator('.cue[data-n="8"]')
  ok('PO placeholder: text, disabled buttons, "Audio coming soon"', ph.locator('.cue-en').is_visible() and ph.locator('button[disabled]').count() == 2 and ph.locator('.cuest').inner_text() == 'Audio coming soon')
  ph.locator('[data-sp=normal]').click(force=True); g.wait_for_timeout(50); ok('PO placeholder never plays', len(J("__played")) == 2)
  J("()=>{HTMLMediaElement.prototype.play=function(){return Promise.reject(new Error('x'))}}")
  c.get_by_role('button', name='Play cue 3 normal', exact=True).click(); g.wait_for_timeout(100)
  ok('CB-6 audio fails: message, cue text still visible', c.locator('.cue[data-n="3"] .cuest').inner_text() != '' and c.locator('.cue[data-n="3"] .cue-en').is_visible() and c.locator('.cue[data-n="3"] .cue-ko').is_visible())
  g.context.set_offline(True); c.get_by_role('button', name='Play cue 4 normal', exact=True).click(); g.wait_for_timeout(100)
  ok('CB-6 offline shows Retry', c.locator('.cue[data-n="4"] [data-act=cueretry]').count() == 1)
  g.context.set_offline(False); J(STUB); c.locator('.cue[data-n="4"] [data-act=cueretry]').click(); g.wait_for_timeout(100)
  ok('CB-6 Retry plays the cue', len(J("__played")) == 1)
  J("openBookings('past')"); ok('CB-4 no practice card before store confirmation', g.locator('.cuepractice').count() == 0)
  J("()=>{ME.att[__past.id]={store:'capsule',t:PV.now()};openBookings('past')}")
  ok('CB-4 practice card in My bookings after store-confirmed visit', g.locator('#cue-bk-' + str(J('__past.id'))).count() == 1)
  J("()=>{ST.page=null;ST.tab='home';render();openHomeSheet()}"); ok('CB-4 practice card on Home', g.locator('#cue-home').count() == 1)
  J("()=>{closeSheet();ME.att[__past.id].t=PV.now()-13*DAY;openBookings('past')}"); ok('CB-4 still in My bookings on day 13', g.locator('.cuepractice').count() == 1)
  J("()=>{ME.att[__past.id].reversed=true;openBookings('past')}"); ok('CB-4 reversed visit: no card', g.locator('.cuepractice').count() == 0)
  J("()=>{const b=B.find(x=>x.store==='spa'&&x.d===-6);ME.att[b.id]={store:'spa',t:PV.now()};openBookings('past')}"); ok('CB-2 untagged confirmed visit: no card', g.locator('.cuepractice').count() == 0)
  ok('no page errors', not g.E, g.E)
  for L, title, slow, soon in (('ko', 'Cici와 함께하는 오늘의 큐', '느리게', '오디오 준비 중'), ('vi', 'Gợi ý động tác hôm nay cùng Cici', 'Chậm', 'Sắp có âm thanh')):
    h = pg('?phase2=1&cueBook=1', L); h.evaluate(TAG); h.evaluate("openBookings('up')"); s = h.locator('.cuebook')
    ok(f'CB-8 [{L}] UI strings localized', s.locator('h3').inner_text() == title and s.locator('[data-sp=slow]').first.inner_text() == slow and s.locator('.cue[data-n="8"] .cuest').inner_text() == soon)
    ok(f'CB-8 [{L}] cue content stays EN + KR', s.locator('.cue-en').first.inner_text() == h.evaluate("CUE.lessons['basic-01'].cues.find(c=>c.position===0).en") and s.locator('.cue-ko').first.is_visible())
    ok(f'CB-6 [{L}] accessible name unchanged', s.get_by_role('button', name='Play cue 1 normal', exact=True).count() == 1)
    ok(f'[{L}] Cici in Latin letters, never 씨씨', '씨씨' not in s.inner_text() and 'Cici' in h.evaluate("CUEUI_STR.ko.cueTitle"))
  br.close()
print(f'{sum(R)}/{len(R)} passed'); sys.exit(0 if all(R) else 1)
