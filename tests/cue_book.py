"""Cue Book with Cici foundation (CB-1 flag off, CB-2 class->lesson tagging, CB-10 lesson content map).
Usage: cue_book.py [base_url]   e.g. python3 -m http.server 8894 in the repo root, then cue_book.py http://localhost:8894/platform-app-v2.html"""
import sys, re
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app-v2.html'
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:300]}')))
CUE_TXT = re.compile(r'Cue Book|cue book|큐북|lesson-0|basic-\d\d|flow-\d\d')
with sync_playwright() as p:
  b = p.chromium.launch()
  def page(q=''):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); g.E = []; g.net = []
    g.on('pageerror', lambda e: g.E.append(str(e))); g.on('request', lambda r: g.net.append(r.url))
    g.goto(U); g.evaluate('localStorage.clear()'); g.net.clear(); g.goto(U + q); g.wait_for_timeout(300); return g
  J = lambda g, js: g.evaluate(js)

  # ---- CB-1: flag off by default -> nothing rendered, requested or stored
  g = page()
  ok('CB-1 flag exists and is off by default', J(g, "FLAGS.cueBook===false && __plat.cueBook.enabled()===false"))
  for r in ['tab:home', 'tab:cici', 'tab:discover', 'tab:you', 'store:capsule']:
    J(g, f"()=>go('{r}')"); g.wait_for_timeout(60)
    ok(f'CB-1 off: no Cue Book UI on {r}', not CUE_TXT.search(g.inner_text('body')))
  J(g, "()=>{const b=B.find(x=>x.store==='capsule'&&!x.past);return __plat.cueBook.tagSession(b.store,b.svc,b.d,b.m,'flow-07')}")
  ok('CB-1 off: tagging refused', J(g, "__plat.cueBook.tagSession('capsule','barre',1,420,'flow-07').err")=='off')
  ok('CB-1 off: load() resolves null without a fetch', J(g, "__plat.cueBook.load().then(x=>x===null)"))
  g.wait_for_timeout(200)
  ok('CB-1 off: lessons.js never requested', not any('cue-book' in u for u in g.net), [u for u in g.net if 'cue' in u])
  ok('CB-1 off: content map not in memory', J(g, "typeof window.CUE_BOOK_LESSONS==='undefined'"))
  ok('CB-1 off: lesson/booking API returns null/false', J(g, "B.every(x=>__plat.cueBook.getLessonForBooking(x.id)===null && __plat.cueBook.forBooking(x.id)===null) && __plat.cueBook.listLessons().length===0"))
  ok('CB-1 off: no cb.cueTags in localStorage', J(g, "localStorage.getItem('cb.cueTags')===null"))
  ok('CB-1 off: no page errors', not g.E, g.E)

  # ---- flag on
  g = page('?cueBook=1')
  ok('flag on via ?cueBook=1', J(g, "__plat.cueBook.enabled()===true"))
  ok('flag on: still no fetch until the UI asks', not any('cue-book' in u for u in g.net))
  n = J(g, "__plat.cueBook.load().then(m=>Object.keys(m||{}).length)")
  ok('flag on: load() fetches lessons.js once', n == 24 and sum('cue-book/lessons.js' in u for u in g.net) == 1, [n, g.net])
  J(g, "__plat.cueBook.load()"); g.wait_for_timeout(100)
  ok('flag on: second load() does not refetch', sum('cue-book/lessons.js' in u for u in g.net) == 1)

  # ---- CB-10: content map shape
  shape = J(g, r"""()=>{const L=__plat.cueBook.listLessons(), bad=[];
    const ids=L.map(l=>l.id), want=[...Array(12)].map((_,i)=>'basic-'+String(i+1).padStart(2,'0')).concat([...Array(12)].map((_,i)=>'flow-'+String(i+1).padStart(2,'0')));
    if (JSON.stringify(ids)!==JSON.stringify(want)) bad.push(['ids',ids]);
    for (const l of L) { if (!['basic','flow'].includes(l.track) || l.id!==l.track+'-'+String(l.number).padStart(2,'0') || !l.title) bad.push([l.id,'head']);
      if (l.positions.length!==5) bad.push([l.id,'pos']);
      for (const p of l.positions) if (!/^https:\/\//.test(p.image) || !p.nameKr || !('nameEn' in p)) bad.push([l.id,'p',p]);
      if (!l.cues.length) bad.push([l.id,'nocues']);
      for (const c of l.cues) { if (!c.en || !c.kr || !c.audioNormalUrl || !c.audioSlowUrl || !(c.position>=0&&c.position<5)) bad.push([l.id,'c',c]);
        if (c.audioPlaceholder !== /^placeholder:\/\//.test(c.audioNormalUrl)) bad.push([l.id,'ph',c]); } }
    return {bad, n:L.length, basic:__plat.cueBook.listLessons('basic').length, flow:__plat.cueBook.listLessons('flow').length,
      real:L.flatMap(l=>l.cues).filter(c=>!c.audioPlaceholder).length};}""")
  ok('CB-10 24 lessons: basic-01..12 + flow-01..12, no 1:1', shape['n'] == 24 and shape['basic'] == 12 and shape['flow'] == 12)
  ok('CB-10 every lesson: track, number, title, 5 positions (image, nameKr, nameEn key), cues with EN/KR/normal+slow audio', not shape['bad'], shape['bad'][:3])
  ok('CB-10 real webbook audio used where it exists', shape['real'] > 0)
  ok('CB-10 webbook mapping: flow-01 = webbook lesson 13', J(g, "__plat.cueBook.getLesson('flow-01').bookNumber===13 && __plat.cueBook.getLesson('basic-01').positions[0].nameKr==='누워서 갈비뼈로 호흡 느끼기'"))
  ok('CB-10 invalid ids return null', J(g, "['one-01','basic-13','flow-00','basic-1','',null,'BASIC-01'].every(i=>__plat.cueBook.getLesson(i)===null)"))

  # ---- CB-2: class -> lesson tagging
  bk = J(g, "(()=>{const b=B.find(x=>x.store==='capsule'&&!x.past&&x.status==='confirmed');return {id:b.id,store:b.store,svc:b.svc,d:b.d,m:b.m}})()")
  ok('CB-2 untagged session -> no lesson', J(g, f"__plat.cueBook.getLessonForBooking({bk['id']})===null && __plat.cueBook.forBooking({bk['id']}).lessonId===null"))
  r = J(g, f"__plat.cueBook.tagSession('capsule','{bk['svc']}',{bk['d']},{bk['m']},'flow-07')")
  ok('CB-2 studio tags the session with flow-07', r.get('ok') and r['lessonId'] == 'flow-07', r)
  ok('CB-2 booking in that session gets the lesson', J(g, f"__plat.cueBook.getLessonForBooking({bk['id']}).id==='flow-07'"))
  ok('CB-2 booking id may be a string', J(g, f"__plat.cueBook.getLessonForBooking('{bk['id']}').id==='flow-07'"))
  ok('CB-2 other sessions stay untagged', J(g, f"B.filter(x=>x.id!=={bk['id']}&&!(x.store==='capsule'&&x.svc==='{bk['svc']}'&&x.d==={bk['d']}&&x.m==={bk['m']})).every(x=>__plat.cueBook.getLessonForBooking(x.id)===null)"))
  for args, err in [("'capsule','barre',1,420,'flow-13'", 'lesson'), ("'capsule','barre',1,420,'one-01'", 'lesson'), ("'salon','cut',1,840,'flow-01'", 'not_class'),
                    ("'capsule','yoga',1,420,'flow-01'", 'svc'), ("'nope','barre',1,420,'flow-01'", 'store'), ("'capsule','barre',1,1440,'flow-01'", 'time')]:
    ok(f'CB-2 validation: tagSession({args}) -> {err}', J(g, f"__plat.cueBook.tagSession({args}).err") == err)
  ok('CB-2 tag persisted (flag on)', 'flow-07' in (J(g, "localStorage.getItem('cb.cueTags')") or ''))
  g.reload(); g.wait_for_timeout(300); J(g, "__plat.cueBook.load()"); g.wait_for_timeout(200)
  ok('CB-2 tag survives reload', J(g, f"__plat.cueBook.getLessonForBooking({bk['id']})?.id==='flow-07'"))
  ok('CB-2 clearing the tag -> no lesson', J(g, f"__plat.cueBook.tagSession('capsule','{bk['svc']}',{bk['d']},{bk['m']},null).ok && __plat.cueBook.getLessonForBooking({bk['id']})===null"))

  # ---- storeConfirmedVisit
  ok('storeConfirmedVisit false before the studio confirms', J(g, f"__plat.cueBook.storeConfirmedVisit({bk['id']})===false && __plat.cueBook.forBooking({bk['id']}).storeConfirmedVisit===false"))
  conf = J(g, r"""()=>{const P=__plat.pv, b=B.find(x=>x.pv==='demo-past')||B.find(x=>x.store==='capsule'&&x.status==='confirmed'); const now=__plat.PV.now();
    if(!__plat.BKREG[b.id]) P.pvBook(b.id,{store:b.store,member:P.ME().id,start:now-50*60000,end:now});
    const r=P.confirmVisit(P.ME(),b.id,'staff:capsule-desk'); return {r, v:__plat.cueBook.storeConfirmedVisit(b.id)}}""")
  ok('storeConfirmedVisit true after staff confirm (points engine)', conf['r'].get('ok') and conf['v'] is True, conf)
  ok('storeConfirmedVisit false for unknown booking', J(g, "__plat.cueBook.storeConfirmedVisit(99999)===false && __plat.cueBook.forBooking(99999)===null"))
  ok('flag on: no page errors', not g.E, g.E)
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
