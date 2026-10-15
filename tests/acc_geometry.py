"""acc-fix geometry: for every pose x full-body placement x outfit (x Phase 2 hair, when present), no accessory box
intersects the top 35% of Cici's figure bbox, and nothing overlays the cut-out except at the frame corners.
Small avatars: the badge sits in the bottom-right corner, clear of the face. Usage: acc_geometry.py [base_url]"""
import sys
from playwright.sync_api import sync_playwright
U = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8894/platform-app.html'
R = []; ok = lambda n, c, d='': (R.append(c), print(('PASS ' if c else 'FAIL ') + n + ('' if c else f' :: {d}')))
JS = r"""async () => {
  const P = window.__plat, poses = Object.keys(CUT_SZ), bbox = {};
  for (const n of poses) { const im = new Image(); im.src = CUT + n + '.webp'; await im.decode();
    const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight; const x = c.getContext('2d'); x.drawImage(im, 0, 0);
    const d = x.getImageData(0, 0, c.width, c.height).data; let l = 1e9, t = 1e9, r = -1, b = -1;
    for (let y = 0; y < c.height; y++) for (let X = 0; X < c.width; X++) if (d[(y * c.width + X) * 4 + 3] > 24) { if (X < l) l = X; if (X > r) r = X; if (y < t) t = y; if (y > b) b = y; }
    bbox[n] = { W: c.width, H: c.height, l, t, r, b }; }
  const fig = (fr, n) => { const B = bbox[n], s = Math.min(fr.width / B.W, fr.height / B.H), ox = fr.left + (fr.width - B.W * s) / 2, oy = fr.top + fr.height - B.H * s;
    return { left: ox + B.l * s, top: oy + B.t * s, right: ox + B.r * s, bottom: oy + B.b * s }; };
  const hit = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
  const out = [];
  const check = (where, frameSel) => { document.querySelectorAll(frameSel).forEach(fe => { const fr = fe.getBoundingClientRect(); if (!fr.width) return;
    const accs = [...fe.querySelectorAll('.wear-acc,.p2hair,.p2acc')].filter(e => e.getBoundingClientRect().width);
    for (const n of poses) { const f = fig(fr, n), head = { ...f, bottom: f.top + 0.35 * (f.bottom - f.top) };
      for (const a of accs) { const r = a.getBoundingClientRect();
        const corner = (r.right >= fr.right - 2 || r.left <= fr.left + 2) && (r.bottom >= fr.bottom - 2 || r.top <= fr.top + 2) && r.width <= 40 && r.height <= 40;
        if (hit(r, head)) out.push([where, n, a.className.baseVal || a.className, 'head']);
        else if (hit(r, f) && !corner) out.push([where, n, a.className.baseVal || a.className, 'body']); } } }); };
  const avatar = (where, sel) => document.querySelectorAll(sel).forEach(av => { const A = av.getBoundingClientRect();
    av.querySelectorAll('.wear-acc,.p2hair,.p2acc').forEach(a => { const r = a.getBoundingClientRect(); if (!r.width) return;
      const face = { left: A.left + A.width * .2, right: A.right - A.width * .2, top: A.top, bottom: A.top + A.height * .6 };
      if (hit(r, face) || r.width > A.width * .45) out.push([where, 'avatar', a.className.baseVal || a.className, 'face']); }); });
  return { out, check, avatar, bbox };
}"""
with sync_playwright() as p:
  b = p.chromium.launch()
  for q in ['', '?phase2=1']:
    for lang in ['en', 'ko']:
      g = b.new_page(viewport={'width': 390, 'height': 844}); g.goto(U + q); g.evaluate('localStorage.clear()'); g.goto(U + q); g.wait_for_timeout(300)
      p2 = g.evaluate("!!(window.__plat && __plat.P2S) && P2()")
      if q and not p2: g.close(); continue
      g.evaluate(f"()=>{{setLang('{lang}');ME.unlocked=['o2','o3','o4','o5'];render()}}")
      hairs = g.evaluate("typeof P2_HAIR!=='undefined' ? P2_HAIR.map(h=>h[0]) : [null]") if p2 else [None]
      bad = []
      for o in ['o1', 'o2', 'o3', 'o4', 'o5', 'wrap', 'lan']:
        for h in hairs:
          g.evaluate(f"()=>{{ST.wear='{o}';{'P2S.char.hair=%r;' % h if h else ''}closeSheet();document.querySelectorAll('.munlock').forEach(e=>e.remove());go('tab:home')}}")
          shots = [('home', '#home-cici .cpic')]
          g.evaluate("()=>{ST.tab='you';ST.page='look';render()}"); 
          r1 = g.evaluate("(" + JS + ")().then(k=>{k.check('look','#view .cpic, #p2-preview');k.check('room','#p2-room #p2-preview, #p2-room .p2wrap');k.avatar('you','.cav-h');return k.out})")
          g.evaluate("()=>{ST.page=null;go('tab:you')}"); r2 = g.evaluate("(" + JS + ")().then(k=>{k.avatar('you-prof','.cav-h');return k.out})")
          g.evaluate("()=>go('tab:cici')"); r3 = g.evaluate("(" + JS + ")().then(k=>{k.avatar('cici-tab','.cav-h');k.check('cici-tab','.nhero, .chome .cpic');return k.out})")
          g.evaluate("()=>go('tab:home')"); r4 = g.evaluate("(" + JS + ")().then(k=>{k.check('home','#home-cici .cpic');k.check('notes','#home-notes, .notes');return k.out})")
          n = int(o[1]) if o[0] == 'o' else 2
          g.evaluate(f"()=>{{ME.notices.push({{k:'outfitUnlocked',played:false,v:{{lvl:{n},item:'{o}'}}}});maybeUnlock()}}")
          r5 = g.evaluate("(" + JS + ")().then(k=>{k.check('unlock','#unl-box .cpic');return k.out})")
          for rr in (r1, r2, r3, r4, r5): bad += [(o, h) + tuple(x) for x in rr]
      tag = f"[{lang}{' phase2' if p2 else ''}]"
      ok(f'{tag} no accessory over the head (top 35%) or body, any pose/placement/outfit{"/hair" if p2 else ""}', not bad, bad[:6])
      g.evaluate("()=>{ST.wear='o2';document.querySelectorAll('.munlock').forEach(e=>e.remove());go('tab:home')}")
      ok(f'{tag} Home shows the unlock as an icon inside the Wearing pill', g.locator('#home-wear .wear-acc').count() == 1 and g.locator('#home-cici .cpic .wear-acc').count() == 0)
      g.close()
  b.close()
print(f'{sum(R)}/{len(R)}'); sys.exit(0 if all(R) else 1)
