# Member App — Feature list and screens

**Product:** Capsule Barre / AICC Member App v1
**System of record:** `aicc-center`. The app shows what the server returns and sends requests into the same services the desk uses.
**Date:** 9 Oct 2026
**Companion docs:** `BA.md` (rules R1–R18, decisions D1–D4, checks A1–A18), `PLAN.md` (API and build order), `UX.md` (visual rules), `app.html` (prototype)

The phone never calculates remaining sessions, refunds, or attendance. One line, once: a session is spent only when the studio marks the class attended.

---

## 1. Feature map

| # | Area | Feature | v1 | Rules | API (`/api/public/v1`) | In prototype |
|---|---|---|---|---|---|---|
| F1 | Account | Create account — one form, then 6-digit code. Only a phone the studio already has | ✔ | R1, D1 | `auth/member/activate`, `auth/member/verify` | ✔ |
| F2 | Account | Log in — phone + password, then code | ✔ | R1, D1 | `auth/member/login`, `auth/member/verify` | ✔ |
| F3 | Account | Forgot password — code, then new password | ✔ | R1, D1 | `auth/member/reset`, `auth/member/verify` | ✔ |
| F4 | Account | Stay logged in; log out; session expiry re-prompts for password | ✔ | R1 | token refresh | partial (log out) |
| F5 | Studios | Switch studio — each a scoped session with its own balance | ✔ | R2 | `auth/member/switch` | ✔ |
| F6 | Today | Class card — time, teacher, reformer, deadline, now / after-class count | ✔ | R3, R12 | `me/reservations`, `me/memberships` | ✔ |
| F7 | Today | Empty state — balance line, one suggestion, Book a class | ✔ | R3 | — | ✔ |
| F8 | Today | Cross-studio hint — "You have class at Cheongdam" when viewing Geumho | ✔ | R2 | — | ✔ |
| F9 | Book | Group classes by day — open / full / may-not-run, taken of capacity | ✔ | R4, R6, R12 | `classes?type=group` | ✔ |
| F10 | Book | Private sessions by day — instructor, open / taken | ✔ | R4, R5 | `classes?type=private` | ✔ |
| F11 | Book | Week strip — days with sessions enabled, others dimmed | ✔ | R4 | `classes?from&to` | ✔ |
| F12 | Book | Book a class — source `MEMBER`, idempotent | ✔ | R5 | `POST reservations` | ✔ |
| F13 | Book | Reformer pick — six pads, taken closed, no names, mine until 6:45pm | ✔ | R8 | `POST reservations` with `spot` | ✔ |
| F14 | Book | Waitlist — join, see place in line, leave | ✔ | R6, R7 | `POST reservations` → `WAITLIST`, `DELETE` | ✔ (join) |
| F15 | Book | Waitlist offer — seat opens; before deadline: accept / pass; after deadline: ask, never auto-book | ✔ | R7 | notification + `POST reservations/{id}/accept` | ✔ (banner) |
| F16 | Manage | Change time — one move, not cancel + rebook | ✔ | R11 | `POST reservations/{id}/move` | ✔ |
| F17 | Manage | Cancel free before deadline — actor is the member | ✔ | R9 | `DELETE reservations/{id}` | ✔ |
| F18 | Manage | Cancel after deadline — refused in app, "contact the studio" | ✔ | R10 | error `CANCELLATION_DEADLINE_PASSED` | ✔ (4:30pm state) |
| F19 | Arrival | I'm here — in-app button 6:30–6:55 with active booking | ✔ | R13, R14 | `POST reservations/{id}/presence` source `TAP` | ✔ |
| F20 | Arrival | Arrival nudge — opt-in location; one notification when close; tap on it is the check-in | ✔ | R13a | same, source `NUDGE` | ✔ |
| F21 | Arrival | iBeacon as the nudge trigger | v2 | R13a | phone-side only | — |
| F22 | Schedule | Upcoming — booked and waitlisted, this studio | ✔ | R5 | `me/reservations?upcoming` | ✔ |
| F23 | Schedule | History — attended, cancelled, no-show, timeline | ✔ | R3 | `me/reservations?past` | ✔ |
| F24 | Pass | Current pass — remaining / total, expiry, meter | ✔ | R3, R15 | `me/memberships` | ✔ |
| F25 | Pass | Previous passes and usage per pass | ✔ | R3 | `me/memberships?all`, `me/attendance` | ✔ |
| F26 | Pass | Hold / extend request → owner to-do; expiry unchanged | ✔ | R16 | `POST requests` | ✔ (Ask) |
| F27 | Alerts | In-app activity list with read / unread | ✔ | R17, D4 | `me/notifications` | ✔ |
| F28 | Alerts | Push — booked, changed by studio, class cancelled, 1 day and 3 hours before, expiry, waitlist offer, studio reply | ✔ | R17, D4 | `me/push-token` | partial |
| F29 | Alerts | Per-type toggles | ✔ | R17 | `me/notification-settings` | display only |
| F30 | Ask | Studio request form — the confirm step behind the assistant's extend / hold card and the Pass screen's button, and the late-cancel path. Types: extend, hold, question → owner task; reply arrives as alert. Not a separate menu entry | ✔ | R16, R18 | `POST requests` | ✔ |
| F31 | Ask | Assistant — typed sentence → one card from the real schedule or pass; the tap on the card is the action. Intents v1: book, check balance, what's on, cancel, extend/hold. Never books or edits a pass by itself; unknown input → "I can book, check, or send a request" | ✔ | R18 | `assistant/interpret` → card; `assistant/act` only after the tap, which calls the normal book/cancel/request API | ✔ |
| F32 | You | Profile — name, phone (self fields) | ✔ | R1 | `me`, `PATCH me/profile` | ✔ (display) |
| F33 | You | Studios list with balances | ✔ | R2 | `auth/member/login` response | ✔ |
| F34 | You | Arrival setting — location on / off | ✔ | R13a | phone-side | ✔ |
| F35 | You | Legal — terms, privacy, location use | ✔ | — | static | ✔ |
| F36 | System | Error states — full, expired, exhausted, duplicate, deadline, offline | ✔ | R5, R10 | error codes | — |
| F37 | System | Korean copy | v1 after English accept | — | — | — |
| F38 | Streak | Streak screen — the week, separate from Today. Grows when the board is cleared, not when a session is spent | ✔ | — | phone-side | ✔ |
| F39 | Friends | Friends — your code, an incoming ask, who already went | ✔ | — | phone-side | ✔ |
| F40 | Friends | Add a friend — type their code. A wrong code finds nobody | ✔ | — | phone-side | ✔ |
| F41 | Share | Share check-in — the phone share sheet. Studio, class, day. Not a friend in the app. No pass number | ✔ | — | phone share sheet | ✔ |
| F42 | Share | Share result — the phone share sheet. Done card, day only. Not a friend in the app | ✔ | — | phone share sheet | ✔ |
| F43 | Share | Share streak — the phone share sheet. The number only. Not a friend in the app | ✔ | — | phone share sheet | ✔ |
| F44 | Share | Share code — the phone share sheet with the code. The app does not pick a friend | ✔ | — | phone share sheet | ✔ |

Not building: pass purchase, ClassPass-style credits, reviews, body charts, nearby-studio shop, free chat, beacon-required check-in, instructor app. See `BA.md` §6. Streak, friends, and share (F38–F44) are in the Hana prototype. A share card never shows the pass as a prize. Share is the phone sheet, not a person in the app.

---

## 2. Screens

Numbering is for reference. "Thumb" = the primary action sits at the bottom of the screen.

### Account

**S1 · Welcome / Log in**
Log in / Create account toggle. Phone, password, Forgot password link. Thumb: **Log in**.
States: empty, error (wrong password, unknown phone, locked after 5 tries).
→ S3 on success.

**S2 · Create account**
Same screen, Create tab. Name, phone, password, confirm, terms checkbox. Terms and Privacy links outside the label. Thumb: **Get code**.
States: field errors inline; unknown phone → "Use the phone on your contract" before any code is sent.
→ S3.

**S3 · Code**
Six boxes, auto-advance, paste fills all, backspace clears the previous box. Resend after 30 s. Thumb: **Continue**.
States: wrong code, expired code, too many attempts.
→ S5 (login / create) or S4 (forgot).

**S4 · New password**
New password, confirm. Thumb: **Save and log in**. → S5.

### Today

**S5 · Today — empty**
Header: studio pill, remaining chip, bell, menu. "No class today." Balance line. One suggestion row (next open class here, or the other studio's class). Thumb: **Book a class**.

**S6 · Today — booked**
Kicker (Tonight · Cheongdam), time hero, class · teacher · reformer. Balance card: tags (Free until 4:00pm, Here from 6:30, confirmed), Now / After class, meter.
Before the window: "Get a nudge when you arrive" card (or "We'll ask when you're close" if on). Thumb: **Change time**, **Cancel free**.
In the window (6:30–6:55): Thumb: **I'm here**. If location on, the nudge notification (N1) appears instead.
After check-in: green "You're here · see you at 7". Still N left.
After deadline, before window: "Free cancel ended 4:00pm · contact the studio". No cancel button.
States: requested (studio confirms), confirmed, waitlisted (place in line), class may not run, class cancelled by studio.

**S7 · Today — class at the other studio**
S5 plus a row "You have class at Cheongdam · 7:00pm → Open". Tapping switches studio and opens S6.

### Book

**S8 · Book — Group**
Group / Private segment. Week strip. Rows by time: time large, class · teacher · taken of capacity, status tag (Open / Full → Waitlist / May not run). Open rows show deadline and arrival window tags.
Tap Open → S10 (if reformer class) or confirm sheet (S11). Tap Full → S12.
States: no classes that day; all full; membership expired or exhausted (rows visible, booking refused with reason).

**S9 · Book — Private**
Same frame. Rows by instructor and time. Open / Taken. Tap Open → S11.

**S10 · Reformer pick**
Kicker (Thu · 7:00pm), "Pick a reformer", "Yours until 6:45pm". 3×2 pads: taken closed, mine filled. Thumb: **Use reformer N**. → books, toast, S6.

**S11 · Confirm (sheet)**
Class, time, teacher, deadline, "Still N left after booking". Thumb: **Book**. Private also shows duration.
Errors: `CLASS_SESSION_FULL`, `MEMBERSHIP_EXPIRED`, `MEMBERSHIP_EXHAUSTED`, `RESERVATION_ALREADY_EXISTS`, weekly limit — each a sentence and one action.

**S12 · Waitlist**
"8:00pm · full". "Join the line?" / "You're 2nd". Thumb: **Join waitlist** / **Leave**.
Copy never says a session is held.

**S13 · Waitlist offer (sheet, from N3)**
"A spot opened at 8:00pm." Before deadline: **Take it** / **Pass**. After deadline: adds "Free cancel has ended for this class" and still asks. Timer: offer expires in 30 min, then next in line.

### Manage

**S14 · Change time (sheet)**
"One move." Target slot list filtered to the same class type, this studio, this week. Thumb: **Move**. Keeps reformer if the target has it.

**S15 · Cancel (sheet)**
Before deadline: "Cancel Thursday 7:00? Still N left." **Cancel class** / Keep.
After deadline: "Free cancel ended at 4:00pm. The studio can help." **Ask the studio** / Close. No cancel.

### Schedule

**S16 · Schedule**
Studio-scoped. Timeline rail: upcoming (confirmed, requested, waitlist with place), then history (attended, cancelled, no-show). Tap upcoming → S6. Tap past → S17.

**S17 · Class detail (past)**
Date, time, teacher, reformer, status, which pass it used. No actions.

### You

**S18 · You**
Avatar initials, name, phone. Rows: Pass (N left · product · expiry), Alerts (count), Ask (one entry: book, check, extend or hold), Studios (balances), Arrival (location on/off), Legal. Thumb: **Log out**.

**S19 · Pass**
Balance card: product name, **N / total** large, until date, meter. Previous passes. Usage list (attended sessions, which class). Thumb: **Ask to extend or hold** → S22.

**S20 · Alerts**
Activity list newest first, unread dot. Types: booked, moved, cancelled, studio changed class, class cancelled, reminder, expiry, waitlist place / offer, arrived, studio reply. "Notify me" toggles per type.

**S21 · Studios (sheet)**
Geumho · 8 of 20 · instructors. Cheongdam · 2 of 10 · instructors. Tap → switch, header updates, S5/S6 for that studio.

**S22a · Ask (assistant)**
Input at the bottom, four example chips when empty. Each answer is one card with a kicker that names its source ("From Cheongdam's schedule", "From your passes") and at most two buttons. The first button runs the normal flow: book → S10 reformer; cancel → S15 confirm; extend → S22. Balance and schedule cards are read-only with an "Open" link. Unknown input → help card. No free text back, no memory beyond the session.
Server: `assistant/interpret` returns `{intent, card}`; the app renders it. `assistant/act` is called only from the card's button and maps to the same reservation/request services as the buttons elsewhere.

**S22 · Request to the studio** (reached from S22a's extend/hold card, S19's button, or S6's late-cancel card — never from the menu)
Request type chips: Extend pass, Hold pass, Question. One text line, prefilled from the card that opened it. "The studio replies in Alerts. Your pass still ends 14 Oct." Thumb: **Send to Cheongdam**.
Sent state: "Sent to Cheongdam", tag "Still ends 14 Oct". Reply arrives in S20.

**S23 · Arrival setting**
"Get a nudge when you arrive." Explains: location only 6:30–6:55 with a class, one notification, never spends a session. Toggle. System location prompt on first enable.

**S24 · Legal (sheet)**
Terms, Privacy, Location use. Static text.

**S25 · Profile edit**
Name, phone (self fields only). Phone change re-verifies with a code.

### Streak, friends, share

These are their own screens. They are not states of Today. The left list has one row each.

**S26 · Streak**
Back. The number. One line: it grows when today's board is cleared, not from the pass. Seven days: filled, today, ahead. Thumb: **Share my streak** → S29.

**S27 · Friends**
Back. Your code on its own line. An incoming ask (Accept / Not now, same size). People, name then what they did. Thumb: **Add a friend**. Secondary: **Share my code** → S32.

**S28 · Add a friend**
Their code. Thumb: **Send ask**. A wrong code finds nobody. Back to S27.

**S29 · Share check-in**
The card: "I'm at Cheongdam", class, teacher, day. No remaining sessions. Thumb: **Share**. That opens the phone's share sheet (Messages, KakaoTalk, Instagram, Copy). The app has no "send to a friend". Secondary: **Not now**.

**S30 · Share result**
Same frame. Card: "Done · Barre", teacher, studio, day. The pass is not on the card. **Share** opens the same phone sheet.

**S31 · Share streak**
Same frame. Card is the number and "Day streak". **Share** opens the phone sheet.

**S32 · Share code**
Same frame. Card is the code. **Share** opens the phone sheet. The app does not choose who receives it.

### Notifications (outside the app)

**N1 · Arrival nudge** — "You're at Cheongdam. Barre at 7:00 with Yuna Choi. Say you're here?" Actions: **I'm here** / Not yet. Only 6:30–6:55 with an active booking, once per class.
**N2 · Reminders** — 1 day before, 3 hours before (the 3-hour one lands just before the 4:00pm deadline: "Free cancel until 4:00pm").
**N3 · Waitlist offer** — "A spot opened at 8:00pm. Take it?" Opens S13.
**N4 · Studio changed / cancelled class** — opens S6 or S16.
**N5 · Expiry** — 7 days and 1 day before. Opens S19.
**N6 · Studio reply** — opens S20.
**N7 · Booked / moved / cancelled confirmations** — silent in-app unless the desk did it.

### System states

| State | Where | What she sees |
|---|---|---|
| Offline | any | Last server data with a "Showing saved · 9:41" line; book/cancel disabled |
| Session expired | any | S1 with phone filled, password only |
| Membership expired | S6, S8 | Rows visible; book → "Pass ended 14 Oct · Ask the studio" |
| Membership exhausted | S8 | "0 left · Ask the studio" |
| Class may not run | S8, S6 | Tag; booking allowed; studio decides |
| Class cancelled by studio | S6 | "Cancelled by the studio · still N left" + Book a class |
| Requested, not yet confirmed | S6 | Tag "Waiting for the studio"; no reformer yet |

---

## 3. Navigation

```
S1 Welcome ─┬─ S2 Create ── S3 Code ── S5/S6 Today
            ├─ S1 Login ── S3 Code ── S5/S6 Today
            └─ Forgot ── S3 Code ── S4 New password ── S5/S6

Tabs: Today (S5/S6/S7) · Book (S8/S9) · Schedule (S16) · You (S18)

Today ── Change time S14 · Cancel S15 · Nudge card S23 · I'm here · Streak S26 · Friends S27
Streak ── Share S31
Friends ── Add S28 · Share code S32
Today, after check-in ── Share check-in S29 · Share result S30
Book ── Open → S10 Reformer → booked → Today
     ── Open (private / no reformer) → S11 Confirm → Today
     ── Full → S12 Waitlist → Schedule
Schedule ── upcoming → Today · past → S17
You ── S19 Pass → S22 Ask · S20 Alerts · S21 Studios · S23 Arrival · S24 Legal · S25 Profile

Header: studio pill → S21 · bell → S20 · menu → Pass / Alerts / Ask / Studios
Notifications: N1 → I'm here · N2 → Today · N3 → S13 · N4 → Today/Schedule · N5 → Pass · N6 → Alerts
```

Depth never exceeds three taps from a tab. No screen requires the back button to finish a task.

---

## 4. Prototype coverage

`app.html` has S1–S6, S7, S8–S10, S12, S13 (as a banner), S14 (fixed target), S15 (confirm sheet; 4:30pm late state), S16, S18–S24 (S23 as a card and a row), N1 and N3 as in-phone banners.

Not in the prototype: S11 confirm sheet (reformer screen plays that role), S17 past detail, S25 profile edit, N2, N4–N6, offline and expired states. These are spec-only and listed in §2 so engineering does not have to guess.

Verified 9 Oct 2026 by two independent UX/UI testers, two passes each (`qa-a-*`, `qa-b-*`, `qa-a2-*`, `qa-b2-*`). All four verdicts: accept with fixes; every listed fix applied and re-verified in the browser. Known demo limits, not defects: one persona (a new account lands on Mina's data); the prototype is a single HTML file, so a cached older copy must be hard-reloaded — version the deploy URL.

Requests: a member sees past requests and the studio's reply under You → Your requests, from the Ask AI screen, and from the sent state. A second extend/hold request while one is waiting is refused with "Already asked". The assistant's book card knows when tonight is already booked and offers Open tonight / Change time instead.

---

## 4a. Questions the owner will ask

The demo does not answer these on screen; the documents do.

| Question | Answer | Where |
|---|---|---|
| How does a brand-new person start? | They don't, in the app. The desk registers the phone first; "Create account" then activates it. Unknown phone is refused on the form | BA R1, D1 |
| How do they buy or renew a pass? | At the desk. No in-app purchase in v1; "Ask the studio" sends extend/hold requests to the owner's to-do | BA §6, R16 |
| What happens after 4:00pm if they want out? | The cancel button is gone; the card says "Free cancel ended" and offers Ask the studio. The desk decides | BA R10, F18 |
| What does "I'm here" do for me? | Marks presence on the desk list. It does not mark attended and does not spend a session | BA R13, R15 |
| When exactly is a session spent? | When the instructor or desk marks the class attended in `aicc-center`. Never from the phone | BA R15, A15 |
| How does waitlist promotion work? | A seat opens → one notification with Take it / Pass, 30-minute window, then next in line. After 4:00pm it still asks, never auto-books | BA R7, F15 |

---

## 5. v2 candidates

- iBeacon as the nudge trigger (F21)
- Assistant that returns cards (F31)
- Instructor profile pages (read-only, from the 2019 IA)
- Family / child booking under one phone, if Kids Barre keeps running
- Apple Wallet / Google Wallet pass with remaining count

Each stays behind the same rule: the phone shows, the studio spends.
