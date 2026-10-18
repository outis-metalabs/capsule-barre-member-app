"""v4 Helen: Cici IS the animal. Six locked files.
Usage: v4_helen.py [base] [shots_dir]  base e.g. http://localhost:8899/"""
ROOT = __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import sys, os
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8899/"
if not BASE.endswith("/"):
    BASE += "/"
SH = sys.argv[2] if len(sys.argv) > 2 else "/tmp/v4shots"
os.makedirs(SH, exist_ok=True)
R = []
ok = lambda n, c, d="": (R.append(bool(c)), print(("PASS " if c else "FAIL ") + n + ("" if c else f" :: {str(d)[:320]}")))
ANIMALS = [("bori", "Bunny"), ("mimi", "Cat"), ("gomi", "Bear"), ("ppiyo", "Chick"), ("mongi", "Puppy"), ("pengo", "Penguin")]
FRESH = "()=>{const dk=dayKey(ME,PV.now());delete ME.days[dk];P2S.dm=null;P2S.cat={seenLook:0,demoHour:12};ST.miss.rest=false;ST.catEat=false;ST.catReact=null;ST.catMis=null;ME.streak=12;ME.paused=false;setLang('en');ST.tab='home';ST.page=null;closeSheet();render()}"

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={"width": 390, "height": 844})
    g = c.new_page()
    g.E, g.NF = [], []
    g.on("pageerror", lambda e: g.E.append(str(e)))
    g.on("response", lambda r: r.status >= 400 and "pastel" in r.url and g.NF.append(r.url))
    J = lambda s: g.evaluate(s)

    # chooser
    g.goto(BASE + "platform-app-v4.html")
    g.wait_for_timeout(400)
    n = J("document.querySelectorAll('a.cast').length")
    ok("V4-hub six animal cards", n == 6, n)

    for aid, kind in ANIMALS:
        g.E.clear(); g.NF.clear()
        g.goto(BASE + f"platform-app-v4-{aid}.html")
        g.evaluate("localStorage.clear()")
        g.goto(BASE + f"platform-app-v4-{aid}.html")
        g.wait_for_timeout(700)
        J(FRESH)
        g.wait_for_timeout(500)
        ok(f"V4-{aid} title is {kind}", kind.lower() in J("document.title").lower(), J("document.title"))
        ok(f"V4-{aid} lock + Cici name", J(f"HELEN_LOCK==='{aid}' && helenChar()==='{aid}' && MOCHI()==='Cici'"))
        src = J("document.querySelector('#cici-real img.helen-still')?.src || ''")
        ok(f"V4-{aid} Home art is {aid}", f"pastel/{aid}/" in src, src)
        ok(f"V4-{aid} no page errors", not g.E, g.E)
        g.screenshot(path=f"{SH}/{aid}-home.png")

    # bori feed still works, copy says Cici not Bori
    g.goto(BASE + "platform-app-v4-bori.html")
    g.evaluate("localStorage.clear()")
    g.goto(BASE + "platform-app-v4-bori.html")
    g.wait_for_timeout(500)
    J(FRESH)
    J("()=>{P2S.cat.treats=1;P2S.cat.earned=1;render()}")
    g.wait_for_timeout(300)
    J("()=>document.querySelector('#cat-feed').click()")
    g.wait_for_timeout(600)
    line = J("document.querySelector('#cat-line')?.innerText || ''")
    ok("V4-bori feed copy names Cici, not Bori", "Cici" in line and "Bori" not in line, line)
    ok("V4-bori v3 tabs still there", J("!!document.querySelector('nav.tabs') && !!document.querySelector('#hb-bubble')"))
    ok("V4 no pastel 404s", not g.NF, g.NF[:4])
    g.close(); b.close()
print(f"{sum(R)}/{len(R)}")
sys.exit(0 if all(R) else 1)
