"""platform-app-v3.html — the centre Book button opens a smart sheet (design review 2026-10-16): Book again (one tap → review),
My places with next open slot + pass balance, More places near you (join & book); a member with no places gets the nearby list, never a dead end.
Usage: v3_book_sheet.py [base_url] [shots_dir]"""
import sys, os
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/platform-app-v3.html'
SH = sys.argv[2] if len(sys.argv) > 2 else '/tmp/v3shots/booksheet'; os.makedirs(SH, exist_ok=True)
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:320]}')))
with sync_playwright() as p:
  b = p.chromium.launch()
  for L in ('ko', 'en', 'vi'):
    c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); E = []; g.on('pageerror', lambda e: E.append(str(e))); J = g.evaluate
    g.goto(U + '?lang=' + L); J('localStorage.clear()'); g.goto(U + '?lang=' + L); g.wait_for_timeout(600)
    g.click('#tabs .tfab'); g.wait_for_timeout(400)
    ok(f'[{L}] Book sheet: Book again first (≤3 rows, each with store · next slot), then My places, then More places', J("document.querySelectorAll('#bk-again .svc').length") in (1, 2, 3) and J("(()=>{const o=[...document.querySelectorAll('.sheet .stack')].map(e=>e.id);return o.indexOf('bk-again')<o.indexOf('bk-places')&&o.indexOf('bk-places')<o.indexOf('bk-more-places')})()"), J("[...document.querySelectorAll('.sheet .stack')].map(e=>e.id)"))
    ok(f'[{L}] every My-places row shows the next open slot; the pass store shows the balance', J("[...document.querySelectorAll('#bk-places .svc')].every(r=>/\\d\\d:\\d\\d/.test(r.innerText))") and J("/6/.test(document.querySelector('#bk-places [data-s=capsule]').innerText)"), J("[...document.querySelectorAll('#bk-places .svc')].map(r=>r.innerText.replace(/\\n/g,' '))"))
    ok(f'[{L}] More places: nearest un-joined stores with distance and a Join & book tag, plus Find places', J("document.querySelectorAll('#bk-more-places .svc').length") == 2 and J("[...document.querySelectorAll('#bk-more-places .svc')].every(r=>/km/.test(r.innerText)&&r.querySelector('.tag'))") and J("!!document.querySelector('#bk-more-places [data-v=\"tab:discover\"]')"))
    if L == 'ko': ok('[ko] copy is Korean (no English leftovers in the rows)', not J("/Next open|left on your pass|Join & book/.test(document.querySelector('.sheet').innerText)"), J("document.querySelector('.sheet').innerText.slice(0,200)"))
    g.screenshot(path=f'{SH}/book-{L}.png')
    n0 = J("B.filter(b=>b.status==='confirmed').length")
    g.click('#bk-again .svc >> nth=0'); g.wait_for_timeout(400)
    ok(f'[{L}] Book again → straight to the review (two taps to book), pass applied', J("!!document.querySelector('.sheet [data-act=dobook]') && /₩0/.test(document.querySelector('.sheet .tot').innerText)"), J("document.querySelector('.sheet .tot')?.innerText"))
    g.click('.sheet [data-act=dobook]'); g.wait_for_timeout(400)
    ok(f'[{L}] … and it books', J("B.filter(b=>b.status==='confirmed').length") == n0 + 1)
    J("closeSheet()"); J("()=>{Object.keys(S).forEach(k=>S[k].joined=false);render()}"); g.click('#tabs .tfab'); g.wait_for_timeout(400)
    ok(f'[{L}] new member (no places): nearby list with Join & book, no dead-end text', J("!!document.querySelector('#bk-noplace') && document.querySelectorAll('#bk-more-places .svc').length===4 && document.querySelectorAll('#bk-again .svc').length===0"))
    g.click('#bk-more-places .svc >> nth=0'); g.wait_for_timeout(400)
    ok(f'[{L}] tapping a nearby place opens Join & book with the next slot', J("!!document.querySelector('.sheet #jb-go, .sheet [data-act=dobook]')"))
    if L == 'ko': g.screenshot(path=f'{SH}/book-new-ko.png')
    ok(f'[{L}] no page errors', not E, E[:2]); c.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
