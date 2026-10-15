"""P2-X1/X2: with FLAGS.phase2 off the app matches the base build (feat/cici-polish 1dd438e) screen by screen.
Usage: phase2_flagoff.py [branch_url] [base_url]. Only diff allowed: the KO name 씨씨 → Cici (user decision)."""
import sys, json
from playwright.sync_api import sync_playwright
NEW = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
BASE = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:8895/platform-app.html'
R = []; ok = lambda n, c, d='': (R.append(c), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {d}')))
SCREENS = [('tab:home', None), ('tab:cici', None), ('tab:places', None), ('tab:you', None), ('tab:you', 'points'), ('tab:you', 'settings'), ('tab:you', 'wallet'), ('tab:you', 'look'), ('store:capsule', None), ('inbox', None)]
norm = lambda t: t.replace('씨씨', 'Cici')
def snap(b, url, lang):
  c = b.new_context(viewport={'width': 390, 'height': 844}); g = c.new_page(); net = []
  g.on('request', lambda r: net.append(r.url.split('/')[-1]) if not r.url.startswith('data:') else None)
  g.goto(url); g.wait_for_timeout(300); g.evaluate(f"()=>{{setLang('{lang}');render()}}"); out = {}
  for r, pgn in SCREENS:
    g.evaluate(f"()=>{{go('{r}');{f'ST.page={json.dumps(pgn)};render();' if pgn else ''}}}"); g.wait_for_timeout(80)
    g.evaluate("document.querySelectorAll('#view .nbook').forEach(e=>e.remove())")  # booking-sheet PR: notification Book links are not Phase 2
    out[f'{r}/{pgn}'] = norm(g.inner_text('#view')) + '|TABS|' + norm(g.inner_text('#tabs'))
  keys = sorted(g.evaluate('Object.keys(localStorage)')); c.close(); return out, keys, sorted(set(net))
with sync_playwright() as p:
  b = p.chromium.launch()
  for lang in ['en', 'vi', 'ko']:
    a, ka, na = snap(b, BASE, lang); n, kn, nn = snap(b, NEW, lang)
    for k in a: ok(f'X1 [{lang}] {k} identical to base', a[k] == n[k], next((f'base:{x!r} new:{y!r}' for x, y in zip(a[k].split('\n'), n[k].split('\n')) if x != y), 'len'))
    ok(f'X2 [{lang}] same localStorage keys as base, no cici.p2', ka == kn and 'cici.p2' not in kn, [ka, kn])
    ok(f'X2 [{lang}] same network requests as base', na == nn, set(na) ^ set(nn))
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
