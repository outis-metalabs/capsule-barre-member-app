# Investor demo — Cici member app v3

**URL:** `platform-app-v3.html?show=1` (add `&lang=ko`, `&lang=en` or `&lang=vi` to force a language).
Serve the repo folder (e.g. `python3 -m http.server 8765`) and open `http://localhost:8765/platform-app-v3.html?show=1&lang=ko`.

`?show=1` is a presentation preset, nothing else changes:
- **Curated state on every load** (reloading = reset): noon, 7-day streak so Mochi is playing, one fresh treat waiting (it drops into the Feed circle as the room opens), today's missions 0/3, the barre class tomorrow 07:00 already booked.
- **Clips prefetched** so every crossfade is instant on first play.
- **Laptop / projector (≥ 900 px wide):** a dark stage with a phone frame around the app and the Cici brand panel on the left. On a phone it is just the app.
- Glass card and action circles ease in on the first paint.

## Flow (≈ 4 minutes)

1. **Home** — "This is Mina's home. Cici is her companion across every store she belongs to; Mochi is Cici's cat." Mochi is playing because Mina is on a 7-day streak. Tap Mochi once: she reacts, hearts, the line says so.
2. **Feed** — tap the fish circle (간식 주기). Mochi takes the fish from Cici's hand, Cici pets her, then the play loop. "Treats come only from missions and store-confirmed visits — nothing is for sale."
3. **Missions** — tap the 미션 circle. The Today sheet: three missions, Mochi, next class, level. Tap **완료** on 물 한 잔 마시기: the sheet slides away, Cici sips and Mochi laps from her bowl, one toast with points + a treat, and the sheet comes back with the row ticked. (Optional: **시작** on 2분 스트레칭 — Cici stretches, Mochi copies on her lap; tap 완료 to skip the timer.)
4. **Book in two taps** — the centre calendar button opens the smart Book sheet: a search bar on top (type `네일` — the nail bar appears with "가입하고 예약"; type anything Cici-ish and hand it to her), then **다시 예약** rows (your usual, next open slot, pass balance) → tap the barre row → the review → 예약하기. Point at the review: exact price or pass, dated free-cancel deadline, no-show rule, points. Confetti, Naver/Kakao map links, calendar, **되돌리기**. Scroll the sheet once to show **내 매장** (next open slot on every row) and **주변의 다른 매장** (join & book in one go). "A brand-new member sees nearby places here instead of an empty list."
5. **Cici books by chat** — Cici tab, type `모레 오전 7시 바레 예약해줘`. Cici reads the time, shows the inline review, one tap books. Then `취소 규정 알려줘` — every store's policy in one answer. Then `모찌 배고파?` — she answers in character.
6. **A court, not a class** — Discover → Sunrise Pickleball Club → court rental: day chips, open times right there, options folded into one line, live price for 90 min + paddles.
7. **Growth** — 나 tab → **Cici와 모찌**: the pair photo, stage, stat bars already at 1/1/1 from Mina's three store-confirmed visits, "꽃봉오리까지 N포인트 · 꽃봉오리에서 청소년 고양이가 돼요", then **Cici의 방** with 꾸미기 / 아이템 샵 (points-only items, "never for sale" copy) and Mochi's growth track (아기 고양이 → 청소년 고양이). (If you want to show her grow: `?show=1&demo=1` adds demo controls; in the console `ME.ledger.push({id:'D',delta:0,life:1500,reason:'t',t:PV.now()});render()` moves Mina to Bud — Mochi becomes a young cat with a collar, the room updates live; the outfit unlock waits until Mochi's "grew" moment ends.)
8. **Notifications** — bell: messages from her places first, then delivered vs held-by-your-rules with the reason (Mina opted in at Capsule Barre and Soom Spa, so you can point at "하루 추천 1개 제한"); settings: caps per store, "따뜻하게, 죄책감 없이" tone. "Marketing is opt-in per place; the member decides."

## Tips
- Reload to reset between runs. The language button (top right) switches EN / VI / KO live — everything, including Cici's chat lines, is localised.
- Keep the browser at 100% zoom; the frame is designed for 1280×800 and up.
- If the room is dark on first load, give the video half a second — it is loading the first clip; after that every switch is a crossfade.
- The Korean copy was reviewed by a three-person native panel on 2026-10-16 (see `docs/`), all majors fixed the same day.
- A four-reviewer solution review followed the same day (safety routing, store status, growth surfaces, booking copy, i18n); every finding is fixed and covered by `tests/v3_review_fixes.py`. The staff "Mark attended" tool is hidden from members; add `&storeConfirm=1` if you want to show the store side.
