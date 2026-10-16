"""v3: Mochi never looks younger as the member levels up. Walks Seed -> Sprout -> Bud -> Blossom -> Shine and checks the look rank
(catLook + the clip actually painted) never goes down; checks the CAT_LOOK_READY combinations. Usage: v3_look_monotonic.py [base_url]"""
import sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8897/platform-app-v3.html'
R = []; ok = lambda n, c, d='': (R.append(bool(c)), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {str(d)[:400]}')))
RANK = {'kitten': 0, 'cat': 1, 'fluffy': 2}
SRCLOOK = "(()=>{const v=[...document.querySelectorAll('.catvid')].filter(v=>+getComputedStyle(v).opacity>0.5);return v.map(v=>{const n=v.currentSrc.split('/').pop();return /-fluffy\\./.test(n)?'fluffy':/-cat\\./.test(n)?'cat':'kitten'})})()"
with sync_playwright() as p:
  b = p.chromium.launch()
  for ready in ({'cat': True, 'fluffy': False}, {'cat': False, 'fluffy': False}):
    for L in ('en', 'ko'):
      g = b.new_page(viewport={'width': 390, 'height': 844}); J = g.evaluate; E = []; g.on('pageerror', lambda e: E.append(str(e)))
      g.goto(U); J('localStorage.clear()'); g.goto(U); g.wait_for_timeout(900)
      J(f"()=>{{setLang('{L}');CAT_LOOK_READY.cat={str(ready['cat']).lower()};CAT_LOOK_READY.fluffy=false;P2S.cat={{seenLook:0}};P2S.cat.demoHour=12;ME.streak=3;ME.ledger=[];P2S.gMax=0;render()}}"); g.wait_for_timeout(1200)
      t = f"{L} cat={ready['cat']}"; hist = []
      for st in range(5):
        J(f"()=>{{let i=0;while(gState().stage<{st}&&i++<300)ME.ledger.push({{id:'M'+i+'_'+Math.random(),delta:0,life:100,reason:'t',t:PV.now()}});render()}}"); g.wait_for_timeout(2200)
        for mood, js in (('lively', "ME.streak=3"), ('napping', "ME.streak=0")):
          J(f"()=>{{{js};catSyncMood(true);catRefreshUi()}}"); g.wait_for_timeout(2500)
          lk, srcs, s = J("catLook()"), J(SRCLOOK), J("catStage()"); hist.append((s, mood, lk, srcs))
          ok(f'[{t}] stage {s} {mood}: painted clip look matches catLook ({lk} / {srcs})', srcs and all(x == lk for x in srcs), (lk, srcs))
      ok(f'[{t}] walk covers all five stages', sorted({h[0] for h in hist}) == [0, 1, 2, 3, 4], [h[0] for h in hist])
      rk = [max(RANK[x] for x in h[3]) for h in hist]
      ok(f'[{t}] look rank never goes down Seed->Shine: {[(h[0], h[2]) for h in hist]}', all(rk[i] <= rk[i + 1] for i in range(len(rk) - 1)), rk)
      ok(f'[{t}] Shine look = {"cat" if ready["cat"] else "kitten"} while fluffy clips are not ready', hist[-1][2] == ('cat' if ready['cat'] else 'kitten'), hist[-1])
      ok(f'[{t}] no page errors', not E, E[:2]); g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
