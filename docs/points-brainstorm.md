# Points: how they should be used and how the app should show them

Brainstorm, 2026-10-17. Two independent agents (a Business Analyst and a Product Owner) each used the prototype, wrote a position, answered each other's questions in a second round, and co-signed a v1. Screenshots: `/tmp/trial/points/ba/`, `/tmp/trial/points/po/`. Lead calls on the two residual disagreements are marked **Lead call**.

## 1. Diagnosis (both agreed)

- Earn is right: one currency, minted on confirmed visits not bookings, honest copy, sane caps.
- There is no burn. Vouchers are flagged off ("쿠폰이 곧 나와요"), cosmetics can drive the balance below zero, nothing a member wants costs points. 790P is a scoreboard.
- The headline balance is inflated: 640 of 790 is a migration grant; only 150P came from visits.
- Points are decoupled from money on both ends. A ₩35,000 cut and a ₩0 pass class mint the same ~55P. Nobody has said who funds the 포인트 부채 when an independent store's visit mints platform points.
- Points are invisible where motivation lives: Home shows streak only; the store page and Discover show nothing; Cici cannot answer "포인트 얼마 있어?" (she asks which store's prices).
- Three currencies (points, lifetime points, Mochi treats) plus paid cosmetics is two too many.

## 2. How points should be used

Ideas raised (name · who pays · member value · risk):

| Idea | Pays | Why member cares | Risk |
|---|---|---|---|
| 이용권·패키지 할인 (points off a pass/package purchase) | platform | money off the thing they already buy | cannibalises full-price buyers |
| 카운터 할인 코드 (show a code, store applies ₩ off, platform reimburses 1:1) | platform | works at any member store, incl. pay-at-store hair/spa | front-desk fraud, settlement rails |
| 예약금 대납 (points cover the deposit) | platform | removes upfront-cash friction | kills the no-show deterrent, book-burn-cancel abuse |
| 첫 방문 부스트 (bonus spendable at a new store) | platform / sponsor | cross-store discovery | one-and-done gaming |
| 마일스톤 바우처 (level-up / birthday ₩ voucher into Wallet) | platform / sponsor | status moment | devalues base earn if rich |
| 스폰서 카탈로그 (socks, protein, samples) | sponsor | aspirational, zero platform cost | feels like junk if irrelevant |
| 오프피크 더블 번 (2× value in slots the store wants filled) | store | outsized value on their schedule | trains deal-seeking |
| 매장 소모품 (grip socks, towel, locker) | store, low COGS | tangible at the desk | operational hassle |
| 모찌 꾸미기 (room items) | member sink | emotional | distracts from money value; keep tiny |
| 스트릭 보호권, 기부/팁, 친구 추천 매칭 | member / platform | niche | manipulation, labour/tax, referral fraud |

**Agreed burn model (co-signed).** One closed-loop 마일리지. Anchor **1P = ₩10**, so a 50-point visit reads as "₩500 off your next pass". Points are earned, never bought, non-transferable, non-refundable. That keeps them out of 선불전자지급수단 territory (no FSC registration, no 50% trust) and lets the UI say "₩7,900 상당" as long as "현금 환급 불가" is shown with it. Platform funds every redemption in v1 and reimburses the redeeming store 1:1 at settlement, netted against the platform fee. No earning-store clawback, no inter-store clearing. Store co-funding and proportional earn on high-ticket spend are v2 opt-ins.

- Earn: +50P per confirmed visit (1 per store per day, 2 a day), ×1.1 streak (×1.2 at 14 days), +80P first visit to a new store (4 a month), +10P per mission (2 a day, 60 a week).
- Burn surfaces live at launch: pass/package purchase in the Toss/Kakao sheet ("포인트로 ₩7,900 할인" toggle), and a counter code at any member store for pay-at-store services. Cosmetics stay as a small optional sink that can never take the balance below zero.
- **Lead call, deposits:** not a burn surface. The deposit exists to deter no-shows. Points discount the service or the pass, never the refundable deposit. (PO position; BA had allowed it.)
- Cap: ≤30% of a transaction and ≤₩20,000 per booking. Blended give-back ≤3% of attributed GMV, ~1% target. Per-member annual ceiling ≈ ₩30,000 equivalent.
- **Lead call, expiry:** design for 12-month rolling inactivity, any earn or burn resets, warnings at 30 and 7 days. The BA's reading is that the 5-year norm binds purchased 상품권/선불수단, not earned mileage. This needs counsel before launch; if counsel disagrees, fall back to 5 years and keep the loss-aversion nudge copy. (BA position; PO had conceded to 5 years.)
- Turn redemption on now. "곧 나와요" for months is worse than a thin burn surface.

## 3. How the app should show points

One spendable balance, everywhere, as `790P · ₩7,900 상당`. Lifetime points are hidden and only feed the level ladder, shown as progress ("레벨 3까지 710P"), never as a second wallet. Wallet is the primary home of the balance and the redeem action; Home and You mirror the number; chat answers it.

| Where | Member sees (KO) | Why |
|---|---|---|
| Home card line (replaces streak-only line) | `790P · 이용권 살 때 ₩7,900 할인` | the number where the eye lands first |
| You hub | profile card `레벨 2 · 단골 · 790P`; tile `포인트 · 790P · ₩7,900 상당` | status and spendable together; this tile replaces "Cici's style" |
| Wallet, top row | `포인트 790P · ₩7,900 상당 · 쓰기` | money instruments live here; points go beside store credit and deposits, not behind a history link |
| Booking confirm | keep `방문 시 약 55P 적립 · 방문을 확인하면 들어와요` | honest pre-commit expectation (already good) |
| Success sheet | `방문을 확인하면 55P가 들어와요. 다음 이용권에 ₩550 할인으로 쓸 수 있어요.` | tie earn to a spend value |
| Check-in | `방문 확인! +55P 들어왔어요 · 이제 845P예요` | the one moment points are actually credited; celebrate it |
| Pass checkout | toggle `포인트로 ₩7,900 할인 (최대 30%)` | burn lives where money moves |
| Store page, near "여기서 예약" | `방문하면 55P 적립 · 포인트 할인 가능` or `포인트 할인 준비 중` | sets per-store expectation at the point of intent |
| Cici chat | `지금 790P 있어요. 이용권이나 카운터에서 최대 ₩7,900 할인으로 쓸 수 있어요. 방문을 확인하면 55P가 더 들어와요.` + chip 포인트 쓰기 | the most-asked loyalty question must not dead-end |
| Notifications | `방문 확인! +55P 들어왔어요` / `안 쓰면 11월 30일에 ₩500이 사라져요` | earn receipt and loss-aversion nudge |
| Investor mode | points liability in ₩, breakage %, burn rate, redemption-driven rebookings | points are a balance-sheet item, not a vanity total |

Legal line, shown once on the Points page and the Wallet row detail: `현금 환급 불가 · 현금성 없음 · 양도 불가`.

## 4. Cut list

- Member-facing lifetime vs spendable split. Keep lifetime hidden as 등급용.
- Cosmetics that take the balance below zero and the "여기서 쓴 포인트는 바우처에 쓸 수 없어요" sub-ledger.
- Paid level outfits as the headline unlock. Outfits become free garnish at level-up.
- Mochi treats as a third currency. Keep as free engagement, never shown next to points.
- The "쿠폰이 곧 나와요" teaser. Ship burn or remove the promise.
- The migrated 640P shown as plain balance. Label it or exclude it from the spendable number.
- 근력/평온/광채 sub-scores (confirms the earlier PO review).

## 5. What this means for the prototype (implemented 2026-10-17, `tests/v3_points.py`)

1. Turn the rewards flag on and remove the "곧 나와요" card.
2. One balance label `{n}P · ₩{n×10} 상당`; hide lifetime; level shown as progress only.
3. Points tile on You (replaces "Cici's style"; look picker moves inside Cici & Mochi).
4. Wallet top row with 쓰기; pass checkout toggle with the 30% / ₩20,000 cap; counter code reuses the existing voucher code flow.
5. Check-in and success sheet copy; Home card line; store page line.
6. Chat intent for balance / "포인트로 뭐 할 수 있어?".
7. Notifications: earn receipt and expiry nudge.
8. Cosmetic purchases blocked below zero; treats moved off the points surfaces.
9. Investor mode: liability line.

Open for counsel: expiry window (12 months vs 5 years) and the exact wording of the 현금성 disclosure.

Implementation notes: `PT_VAL` (1P = 100 ₫ base = ₩10), `PTS_CAP` (30% / 200.000 ₫ base = ₩20,000), `ptsW()` / `balTx()` for the one-balance label, `ptsMaxOff()` for the checkout cap, `paySheet({ ptsOk })` (passes only; deposits pass `dep: true, ptsOk: false`), `ptsCodeSheet()` for the counter code, ledger reasons `spend_pass` / `spend_counter` (life 0, so levels never drop), `ME.lastSpend` resets the 12-month expiry clock, notification type `points` with live text (`txf`), `?realRewards=0` turns redemption off.
