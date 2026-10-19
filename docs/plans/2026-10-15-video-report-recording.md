# Video Report Recording Plan (v3 — full app tour)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record a ~3 min report video covering all screens of `platform-app.html`, including the updated character features (full-width video hero, outfit switching across 3 outfits).

**Tech Stack:** Chrome, QuickTime Player / OBS / Loom, DevTools console

**Structure (~14 scenes, ~3 min):**
- Act 1 — First launch: Intro · Onboarding · +50 🪙 · Log in
- Act 2 — Home tab: full-width video hero · level bar · mission card
- Act 3 — Cici's Look tab: 3 outfits · video switches · locked outfits · meta bar
- Act 4 — Outfit propagates: Home + Cici tab update to match chosen outfit
- Act 5 — Missions: Stretch · Attend · New place · coins accumulate

---

### Task 1: Setup before recording

- [ ] **Step 1: Open `bao-cao-platform.html` in Chrome**

- [ ] **Step 2: Open DevTools console, dock to the right**

  `⌘⌥J` → ⋮ → Dock side → Dock to right

- [ ] **Step 3: Clear localStorage**

  ```
  DevTools → Application → Local Storage → delete key "cici.ob"
  ```

- [ ] **Step 4: Reset app state via console**

  ```js
  document.getElementById("appframe").src = "platform-app.html?lang=en";
  ```

  After the iframe loads:

  ```js
  const w = document.getElementById("appframe").contentWindow;
  w.ST.shopCoins = 70; w.ST.wear = "o1"; w.render();
  ```

- [ ] **Step 5: Set opening caption**

  ```js
  setCap("Cici · member app","Feature overview","Platform app — character · outfits · coins · missions.");
  ```

- [ ] **Step 6: Start screen recording** (capture phone + caption area only, not DevTools)

---

### Task 2: Act 1 — First launch (scenes 1–3)

- [ ] **Scene 1 — Intro (3s)**

  ```js
  setCap("Cici · member app","Feature overview","Platform app — character · outfits · coins · missions.");
  ```

  → Intro screen visible. Hold 3s.

- [ ] **Scene 2 — Onboarding + 50 🪙 (4s)**

  ```js
  setCap("🆕 Onboarding","Welcome + 50 🪙","Cici introduces key features. Shows once only — saved via localStorage.");
  ```

  → Scroll through 3 onboarding steps → tap **"Get started · +50 🪙"**. Coin pill floats up.

- [ ] **Scene 3 — Log in → Home (4s)**

  ```js
  setCap("Home","Logged in → Home","New nav bar: home · look · cici · you.");
  ```

  → Log in (phone + code) → Home. Point to the 4 nav tabs.

---

### Task 3: Act 2 — Home tab (scenes 4–5)

- [ ] **Scene 4 — Full-width character video (4s)**

  ```js
  setCap("🆕 Home","Full-width character video","Equipped outfit autoplays fullwidth. Transparent level bar at bottom.");
  ```

  → Point to video hero filling the full width, transparent level bar overlay at bottom, greeting pill.

- [ ] **Scene 5 — Mission card + coins (3s)**

  ```js
  setCap("🆕 Home","Daily missions + Cici Coins","3 daily missions. Current coin balance shown on card.");
  ```

  → Scroll down, point to mission card with 🪙 balance.

---

### Task 4: Act 3 — Cici's Look · 3 outfits (scenes 6–10)

- [ ] **Scene 6 — Enter Look tab (3s)**

  ```js
  setCap("🆕 Cici's Look","Dedicated nav tab","Tap the look tab → video hero + outfit grid.");
  ```

  → Tap **look** tab (shirt icon). Video hero + outfit grid appear.

- [ ] **Scene 7 — Outfit 1: Default (3s)**

  ```js
  setCap("Cici's Look","Default outfit — Clip 1","Default outfit: video clip 1 autoplays.");
  ```

  → Tap **Default** tile (o1). Video switches to clip 1.

- [ ] **Scene 8 — Outfit 2: Studio (3s)**

  ```js
  setCap("Cici's Look","Studio — Clip 2","Tap Studio → video switches instantly. Each outfit has its own clip.");
  ```

  → Tap **Studio** tile (o2). Video switches to clip 2.

- [ ] **Scene 9 — Outfit 3: Studio wrap top (3s)**

  ```js
  setCap("Cici's Look","Studio wrap top — video_9","Special outfit outside the 5 tiers. Tap → video_9.mp4 plays.");
  ```

  → Tap **Studio wrap top** tile. video_9.mp4 plays.

- [ ] **Scene 10 — Locked outfits + Meta bar + Shop (4s)**

  ```js
  setCap("Cici's Look","Unlock by level · Shop","Glow/Bloom/Icon unlock at levels 3–5. Bottom bar: outfit name + Shop.");
  ```

  → Tap **Glow** (locked — lock icon shows) → point to meta bar → tap **Shop**.

---

### Task 5: Act 4 — Outfit propagates (scenes 11–12)

- [ ] **Scene 11 — Home after outfit change (3s)**

  ```js
  setCap("🆕 Home","Outfit change → Home updates","Back to Home — video hero now shows the wrap top clip.");
  ```

  → Tap **home** tab. Video hero plays the wrap top clip.

- [ ] **Scene 12 — Cici tab: outfit image (3s)**

  ```js
  setCap("🆕 Cici tab","Character reflects current outfit","Cici tab hero image updates to match the equipped outfit.");
  ```

  → Tap **cici** tab. Hero image = wrap top outfit.

---

### Task 6: Act 5 — Missions + Coins (scenes 13–14)

- [ ] **Scene 13 — Stretch +10 🪙 (3s)**

  ```js
  setCap("🆕 Missions","Complete → earn coins","Stretch: Start → Finish (demo). Confetti + +10 🪙 toast.");
  ```

  → Home tab → tap **Start** on Stretch → **Finish**. Confetti + toast.

- [ ] **Scene 14 — Attend + New place Demo › (4s)**

  ```js
  setCap("🆕 Missions","Demo › instant simulate","Attend +20 🪙 · New place +30 🪙. No real booking needed.");
  ```

  → **Demo ›** on Attend → +20 toast → **Demo ›** on New place → +30 toast.

---

### Task 7: End + export

- [ ] **Step 1: Ending caption (4s)**

  ```js
  setCap("feat/cici-gamification","Summary","Video hero · Outfit switching · Look tab · Coins · Missions.");
  ```

- [ ] **Step 2: Stop recording → Trim → Export**

  Save as: `bao-cao-platform-v3.mp4` · H.264 · 1080p · ~12 MB

---

## Cheatsheet — paste one line at a time

```js
// SETUP
document.getElementById("appframe").src = "platform-app.html?lang=en";
// after load:
// const w = document.getElementById("appframe").contentWindow;
// w.ST.shopCoins = 70; w.ST.wear = "o1"; w.render();

// ACT 1
// S1:  setCap("Cici · member app","Feature overview","Platform app — character · outfits · coins · missions.");
// S2:  setCap("🆕 Onboarding","Welcome + 50 🪙","Cici introduces key features. Shows once only — saved via localStorage.");
// S3:  setCap("Home","Logged in → Home","New nav bar: home · look · cici · you.");

// ACT 2
// S4:  setCap("🆕 Home","Full-width character video","Equipped outfit autoplays fullwidth. Transparent level bar at bottom.");
// S5:  setCap("🆕 Home","Daily missions + Cici Coins","3 daily missions. Current coin balance shown on card.");

// ACT 3 — OUTFITS
// S6:  setCap("🆕 Cici's Look","Dedicated nav tab","Tap the look tab → video hero + outfit grid.");
// S7:  setCap("Cici's Look","Default outfit — Clip 1","Default outfit: video clip 1 autoplays.");
// S8:  setCap("Cici's Look","Studio — Clip 2","Tap Studio → video switches instantly. Each outfit has its own clip.");
// S9:  setCap("Cici's Look","Studio wrap top — video_9","Special outfit outside the 5 tiers. Tap → video_9.mp4 plays.");
// S10: setCap("Cici's Look","Unlock by level · Shop","Glow/Bloom/Icon unlock at levels 3–5. Bottom bar: outfit name + Shop.");

// ACT 4 — PROPAGATION
// S11: setCap("🆕 Home","Outfit change → Home updates","Back to Home — video hero now shows the wrap top clip.");
// S12: setCap("🆕 Cici tab","Character reflects current outfit","Cici tab hero image updates to match the equipped outfit.");

// ACT 5 — MISSIONS
// S13: setCap("🆕 Missions","Complete → earn coins","Stretch: Start → Finish (demo). Confetti + +10 🪙 toast.");
// S14: setCap("🆕 Missions","Demo › instant simulate","Attend +20 🪙 · New place +30 🪙. No real booking needed.");

// END: setCap("feat/cici-gamification","Summary","Video hero · Outfit switching · Look tab · Coins · Missions.");
```
