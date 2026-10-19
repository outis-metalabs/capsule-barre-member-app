const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const APP = "http://127.0.0.1:8767";
const OUT = "/Users/josh/Downloads/aicc_mvp/capsule-barre-member-app/bao-cao-platform-v3.mp4";
const PAUSE = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader"],
  });
  const ctx = await browser.newContext({
    viewport: { width: 430, height: 1112 },
    deviceScaleFactor: 1,
    recordVideo: { dir: "/tmp/pwvideo/", size: { width: 430, height: 1112 } },
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));

  console.log("Loading...");
  await page.goto(`${APP}/bao-cao-platform.html`, { waitUntil: "domcontentloaded" });
  const appFL = page.frameLocator("iframe#appframe");
  await appFL.locator("#app").waitFor({ state: "visible", timeout: 15000 });
  const fr = page.frames().find((f) => f.url().includes("platform-app"));
  if (!fr) throw new Error("iframe missing");
  await fr.addStyleTag({ content: ":root{--ox:#E98597;--ok:#2e6b52}::-webkit-scrollbar{width:0;height:0}" });

  // Reset to fresh state with demo data
  await fr.evaluate(() => {
    try { localStorage.removeItem("cici.ob"); } catch (e) {}
    ST.firstRun = true;
    ST.page = "onboard";
    ST.tab = "home";
    ST.store = null;
    ST.shopCoins = 70;
    ST.wear = "o1";
    ME.unlocked = ME.unlocked || [];
    if (!ME.unlocked.includes("o2")) ME.unlocked.push("o2"); // Studio unlocked for demo
    ST.owned = ST.owned || [];
    if (!ST.owned.includes("wrap")) ST.owned.push("wrap");   // Wrap top owned for demo
    // Force first upcoming booking to today so check-in button shows
    const bk = B.find(b => b.status === "confirmed");
    if (bk) bk.d = 0;
    render();
  });
  await PAUSE(800);

  async function cap(kicker, title, line) {
    await page.evaluate(([k, t, l]) => setCap(k, t, l), [kicker, title, line]);
  }
  async function clk(sel, timeout = 8000) {
    const el = appFL.locator(sel).first();
    await el.waitFor({ state: "visible", timeout });
    await el.evaluate((node) => {
      if (node.closest(".sheet") || node.closest("nav.tabs") || node.closest("header.top")) return;
      const r = node.getBoundingClientRect();
      if (r.top < 76 || r.bottom > window.innerHeight - 120) node.scrollIntoView({ block: "center" });
    });
    await el.click({ timeout });
    console.log(" ✓", sel.slice(0, 72));
  }
  async function clkForce(sel, timeout = 8000) {
    const el = appFL.locator(sel).first();
    await el.waitFor({ state: "attached", timeout });
    await el.evaluate((node) => {
      const r = node.getBoundingClientRect();
      if (r.top < 76 || r.bottom > window.innerHeight - 120) node.scrollIntoView({ block: "center" });
    });
    await PAUSE(300);
    await el.click({ force: true, timeout });
    console.log(" ✓ (force)", sel.slice(0, 72));
  }
  async function top() { await fr.evaluate(() => window.scrollTo(0, 0)); }
  async function show(sel) {
    await fr.evaluate((s) => { const el = document.querySelector(s); if (el) el.scrollIntoView({ block: "center" }); }, sel);
  }
  async function xclose() {
    await fr.evaluate(() => {
      const btn = document.querySelector('.sheet [data-act="close"]') || document.querySelector('.sheet button.icb');
      if (btn) btn.click();
    });
    await PAUSE(400);
  }
  async function say(text) {
    const box = appFL.locator("#in-cici");
    await box.waitFor({ state: "visible", timeout: 6000 });
    await box.click();
    await box.fill(text);
    await box.press("Enter");
  }
  async function back() {
    await fr.evaluate(() => {
      const btn = document.querySelector('header [data-act="back"]') || document.querySelector('[data-act="back"]');
      if (btn) btn.click();
    });
    await PAUSE(400);
  }
  async function shot(name, kicker, title, line, fn, ms = 2800) {
    console.log("BEAT", name);
    await cap(kicker, title, line);
    if (fn) await fn();
    await PAUSE(ms);
  }

  // ── ACT 1 — FIRST LAUNCH ─────────────────────────────────────────────

  // S1 — Intro
  await shot("s1-intro",
    "Cici · member app", "Feature overview",
    "Platform app — character · outfits · coins · missions.",
    null, 3000);

  // S2 — Onboarding + 50 🪙
  await shot("s2-onboard",
    "🆕 Onboarding", "Welcome + 50 🪙",
    "Cici introduces key features. Shows once only — saved via localStorage.",
    async () => {
      await fr.evaluate(() => window.scrollTo({ top: 400, behavior: "smooth" }));
      await PAUSE(900);
      await fr.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
      await PAUSE(500);
      await clk("[data-act='onboard-done']");
    }, 3500);

  // S3 — Home (nav bar visible)
  await shot("s3-home",
    "Home", "Logged in → Home",
    "New nav bar: home · look · cici · you.",
    async () => { await top(); },
    3500);

  // ── ACT 2 — HOME TAB ─────────────────────────────────────────────────

  // S4 — Full-width character video
  await shot("s4-video-hero",
    "🆕 Home", "Full-width character video",
    "Equipped outfit autoplays fullwidth. Transparent level bar at bottom.",
    async () => { await top(); await show("#home-cici"); },
    4000);

  // S5 — Mission card
  await shot("s5-missions",
    "🆕 Home", "Daily missions + Cici Coins",
    "3 daily missions. Coin balance shown on card.",
    async () => { await show("#home-mis"); },
    3000);

  // S6 — Next class + check-in
  await shot("s6-next-class",
    "Home", "Next class · check-in",
    "Upcoming booking. Check-in shows a QR code for the desk.",
    async () => {
      await show("#home-next");
      await PAUSE(600);
      if (await appFL.locator("[data-act='checkin']").count() > 0) {
        await clk("[data-act='checkin']");
      } else {
        await clk("[data-act='managebk']");
      }
    }, 3500);
  await xclose();

  // S7 — Manage booking
  await shot("s7-manage",
    "Home", "Manage booking",
    "Reschedule or cancel. Free cancel window, late fee, and no-show policy shown.",
    async () => {
      await show("#home-next");
      await clk("[data-act='managebk']");
    }, 3500);
  await xclose();

  // ── ACT 3 — BOOKINGS ─────────────────────────────────────────────────

  // S8 — Bookings list
  await shot("s8-bookings",
    "My bookings", "Upcoming bookings",
    "All upcoming bookings: barre, hair, skincare. Each shows the date and manage options.",
    async () => { await clk("[data-act='mybk']"); await top(); },
    3500);

  // S9 — Past + rate
  await shot("s9-past",
    "My bookings", "Past visits · rate",
    "Past visits: Attended, Cancelled, No-show. Rate a recent visit privately.",
    async () => {
      if (await appFL.locator("[data-act='bkseg'][data-v='past']").count() > 0) {
        await clk("[data-act='bkseg'][data-v='past']");
        await PAUSE(600);
        if (await appFL.locator("[data-act='rate']").count() > 0) {
          await clk("[data-act='rate']");
          await PAUSE(600);
          if (await appFL.locator("[data-act='rstar'][data-v='5']").count() > 0) {
            await clk("[data-act='rstar'][data-v='5']");
          }
        }
      }
    }, 3500);
  if (await appFL.locator(".sheet").count() > 0) await xclose();

  // ── ACT 4 — CICI CHAT ─────────────────────────────────────────────────

  // S10 — Cici tab: hero + book again
  await shot("s10-cici-hero",
    "🆕 Cici tab", "Character reflects current outfit",
    "Cici tab hero image matches the equipped outfit. Book again chips below.",
    async () => {
      await clk("[data-act='tab'][data-v='cici']");
      await top();
    }, 3500);

  // S11 — Book again
  await shot("s11-book-again",
    "Cici", "Book again — one tap",
    "Book again chips let you re-book a favourite class instantly.",
    async () => {
      if (await appFL.locator("[data-act='nagain']").count() > 0) {
        await clk("[data-act='nagain']");
        await PAUSE(800);
      }
    }, 3500);
  // Confirm booking if shown, then undo
  if (await appFL.locator("[data-act='chatbook']").count() > 0) {
    await appFL.locator("[data-act='chatbook']").first().click();
    await PAUSE(1200);
    if (await appFL.locator("[data-act='succundo']").count() > 0) {
      await appFL.locator("[data-act='succundo']").first().click();
      await PAUSE(1000);
    }
  }

  // S12 — Ask a question
  await shot("s12-ask",
    "Cici", "Ask anything",
    "Ask opening hours, pricing, or policies. Cici answers from each studio's own info.",
    async () => {
      await clk("[data-act='tab'][data-v='cici']");
      await PAUSE(400);
      await say("what time does Capsule Barre open");
    }, 3500);

  // ── ACT 5 — YOU TAB ──────────────────────────────────────────────────

  // S13 — You profile
  await shot("s13-you",
    "You", "Profile — level, points, streak",
    "Your level, lifetime points, and streak. Wallet · Bookings · Cici's look · Shop tiles.",
    async () => {
      await clk("[data-act='tab'][data-v='you']");
      await top();
    }, 3500);

  // S14 — Points detail
  await shot("s14-points",
    "You", "Points · how they grow",
    "Points from confirmed visits, a new place, and missions. Not cash — saved for rewards.",
    async () => { await clk("[data-act='youpage'][data-v='points']"); await top(); },
    3500);
  await back();

  // S15 — Wallet
  await shot("s15-wallet",
    "You", "Wallet — passes stay at each place",
    "Capsule Barre class pass. Deposit tied to a booking. Store credit at each place.",
    async () => { await clk("[data-act='youpage'][data-v='wallet']"); await top(); },
    3500);
  await back();

  // ── ACT 6 — CICI SHOP ────────────────────────────────────────────────

  // Bump coins for shop demo
  await fr.evaluate(() => { ST.shopCoins = 360; render(); });
  await PAUSE(300);

  // S16 — Shop overview
  await shot("s16-shop",
    "Cici Shop", "Coins · backgrounds, frames, companions",
    "360 coins. Buy backgrounds, frames, and companions. Coins are separate from points.",
    async () => {
      await clk("[data-act='open-shop']");
      await top();
    }, 3500);

  // S17 — Backgrounds
  await shot("s17-backgrounds",
    "Cici Shop", "Eight backgrounds · common to epic",
    "Sakura 80 · Peach Dream 80 · Ocean Calm 120 · Aurora 200. Equip paints the page.",
    async () => {
      await clk("[data-act='shop-filter'][data-k='bg']");
      await PAUSE(600);
      await show("[data-act='buy-shopitem'][data-id='bg-sakura']");
      await clk("[data-act='buy-shopitem'][data-id='bg-sakura']");
      await PAUSE(700);
      if (await appFL.locator("[data-act='equip-shopitem'][data-id='bg-sakura']").count() > 0) {
        await clk("[data-act='equip-shopitem'][data-id='bg-sakura']");
      }
    }, 3500);

  // S18 — Background shows on home
  await shot("s18-bg-home",
    "Home", "Sakura background live on Home",
    "Leave the shop — Sakura blossom stays behind the cards on every tab.",
    async () => {
      await clk("[data-act='tab'][data-v='home']");
      await top();
    }, 3000);

  // S19 — Frame + companion
  await shot("s19-frame-companion",
    "Cici Shop", "Frame + companion",
    "Silver Ring frame on the avatar. Lucky Cat companion badge in the hero and HUD.",
    async () => {
      await clk("[data-act='tab'][data-v='you']");
      await PAUSE(300);
      await clk("[data-act='open-shop']");
      await clk("[data-act='shop-filter'][data-k='frame']");
      await PAUSE(500);
      if (await appFL.locator("[data-act='buy-shopitem'][data-id='frame-silver']").count() > 0) {
        await clk("[data-act='buy-shopitem'][data-id='frame-silver']");
        await PAUSE(600);
        if (await appFL.locator("[data-act='equip-shopitem'][data-id='frame-silver']").count() > 0) {
          await clk("[data-act='equip-shopitem'][data-id='frame-silver']");
        }
      }
      await PAUSE(400);
      await clk("[data-act='shop-filter'][data-k='companion']");
      await PAUSE(500);
      if (await appFL.locator("[data-act='buy-shopitem'][data-id='comp-cat']").count() > 0) {
        await clk("[data-act='buy-shopitem'][data-id='comp-cat']");
        await PAUSE(600);
        if (await appFL.locator("[data-act='equip-shopitem'][data-id='comp-cat']").count() > 0) {
          await clk("[data-act='equip-shopitem'][data-id='comp-cat']");
        }
      }
    }, 4000);

  // S20 — You profile with equipped items
  await shot("s20-you-equipped",
    "You", "Frame and companion on profile",
    "Back on You — Silver Ring frame on avatar, Lucky Cat badge, Sakura background.",
    async () => {
      await back();
      await top();
    }, 3000);

  // ── ACT 7 — CICI'S LOOK ──────────────────────────────────────────────

  // S21 — Look tab
  await shot("s21-look-tab",
    "🆕 Cici's Look", "Dedicated nav tab",
    "Tap the look tab → video hero + outfit grid.",
    async () => {
      await clk("[data-act='tab'][data-v='look']");
      await top();
    }, 3000);

  // S22 — Default (o1)
  await shot("s22-o1",
    "Cici's Look", "Default outfit — Clip 1",
    "Default outfit: video clip 1 autoplays in the hero.",
    async () => { await clk("[data-act='pvwear'][data-v='o1']"); },
    3000);

  // S23 — Studio (o2)
  await shot("s23-o2",
    "Cici's Look", "Studio — video switches instantly",
    "Tap Studio → video switches to Clip 3. Each outfit has its own clip.",
    async () => { await clk("[data-act='pvwear'][data-v='o2']"); },
    3000);

  // S24 — Studio wrap top
  await shot("s24-wrap",
    "Cici's Look", "Studio wrap top — video_9",
    "Special outfit outside the 5 tiers. Tap → video_9.mp4 plays.",
    async () => {
      await show("#look-tiles [data-v='wrap']");
      await clk("[data-act='pvwear'][data-v='wrap']");
    }, 3000);

  // S25 — Locked outfits + shop
  await shot("s25-locked",
    "Cici's Look", "Unlock by level · Shop",
    "Glow / Bloom / Icon unlock at levels 3–5. Bottom bar: outfit name + Shop.",
    async () => {
      await show("#look-tiles [data-v='o3']");
      await PAUSE(400);
      await clkForce("#look-tiles [data-v='o3']");
      await PAUSE(500);
      await show(".look-meta");
    }, 4000);

  // ── ACT 8 — OUTFIT PROPAGATES ────────────────────────────────────────

  // S26 — Home: video updates to wrap top
  await shot("s26-home-updated",
    "🆕 Home", "Outfit change → Home updates",
    "Back to Home — video hero now shows the wrap top clip.",
    async () => {
      await clk("[data-act='tab'][data-v='home']");
      await top();
      await show("#home-cici");
    }, 3500);

  // S27 — Cici tab: image updates
  await shot("s27-cici-updated",
    "🆕 Cici tab", "Character reflects current outfit",
    "Cici tab hero updates to match. Companion badge visible in hero.",
    async () => {
      await clk("[data-act='tab'][data-v='cici']");
      await top();
    }, 3500);

  // ── ACT 9 — SETTINGS ─────────────────────────────────────────────────

  // S28 — Settings + language
  await shot("s28-settings",
    "Settings", "Language · notifications",
    "English, Vietnamese, Korean. Quiet hours 21:00–08:00. Mute by type or place.",
    async () => {
      await clk("[data-act='tab'][data-v='you']");
      await clk("[data-act='youpage'][data-v='settings']");
      await top();
    }, 3000);

  await shot("s28b-lang",
    "Settings", "Tiếng Việt · 한국어",
    "Language switch: same screens in Vietnamese and Korean.",
    async () => {
      await clk("[data-act='setlang'][data-v='vi']");
      await PAUSE(1000);
      await clk("[data-act='setlang'][data-v='ko']");
      await PAUSE(1000);
      await clk("[data-act='setlang'][data-v='en']");
    }, 3500);

  // S29 — Inbox
  await shot("s29-inbox",
    "Inbox", "Store messages in inbox",
    "Class reminders, studio replies, deposit confirmations. Marketing off by default.",
    async () => {
      await back();
      await top();
      await fr.evaluate(() => { ST.page = "notif"; ST.seenN = true; render(); window.scrollTo(0,0); });
    }, 3500);

  // ── ACT 10 — MISSIONS ────────────────────────────────────────────────

  // S30 — Stretch +10 🪙
  await shot("s30-stretch",
    "🆕 Missions", "Complete → earn coins",
    "Stretch: Start → Finish (demo). Confetti + +10 🪙 toast.",
    async () => {
      await clk("[data-act='tab'][data-v='home']");
      await show("#home-mis");
      await clk("[data-act='stretch']");
      await PAUSE(800);
      await clk("[data-act='stretchdone']");
    }, 3000);

  // S31 — Attend + New place Demo
  await shot("s31-attend-newplace",
    "🆕 Missions", "Demo › instant simulate",
    "Attend +20 🪙 · New place +30 🪙. No real booking needed.",
    async () => {
      await show("#home-mis");
      await clk("[data-act='attend-demo']");
      await PAUSE(1400);
      await clk("[data-act='newplace-demo']");
    }, 4000);

  // ── END ──────────────────────────────────────────────────────────────

  await shot("end",
    "feat/cici-gamification", "Summary",
    "Video hero · Outfit switching · Look tab · Coins · Missions.",
    async () => {
      await clk("[data-act='tab'][data-v='home']");
      await top();
    }, 4000);

  if (errors.length) console.log("PAGEERRORS", errors.slice(0, 6).join(" | "));
  else console.log("PAGEERRORS none");
  const vidPath = await page.video().path();
  await ctx.close();
  await browser.close();
  console.log("WEBM", vidPath);
  execFileSync("/opt/homebrew/bin/ffmpeg", ["-y", "-i", vidPath, "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", OUT], { stdio: "inherit" });
  console.log("DONE", OUT);
})().catch((e) => {
  console.error("FAIL:", e.stack || e.message);
  process.exit(1);
});
