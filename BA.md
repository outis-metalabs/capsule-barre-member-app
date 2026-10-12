# Member App — Business Analysis

**Product:** Capsule Barre / AICC Member App (Phase 2 member scope only)  
**Audience:** Owner, product owner, engineering lead  
**Date:** 8 Oct 2026  
**Persona day:** Thu 8 Oct 2026, 9:41am  
**System of record:** `aicc-center` (NestJS + staff Next.js). Member App is a separate client.

This document defines what the member product must do for one real evening. It does not invent staff endpoints that do not exist, and it does not move money, session balance, refunds, or attendance confirmation into the phone.

---

## 1. Problem and success

### Problem

Mina Park already takes class. The studio already knows her. Today she books and changes by calling or messaging the desk. The owner types the booking into `aicc-center`. That work is correct for the ledger, but it is slow for Mina and expensive for the studio.

Tonight she wants Cheongdam 7:00pm Barre with Yuna Choi. Her Cheongdam pass still has **2 of 10** sessions and expires **14 Oct 2026**. Free cancel ends at **4:00pm**. Arrival check-in opens at **6:30pm**. She also holds Geumho **8 of 20** until **12 Nov 2026**. Those are two studio memberships, not one wallet.

### What “good” means for Mina (one evening)

1. She signs in with the phone number Cheongdam already registered. No open signup.
2. She switches to Cheongdam, sees 2 left and the 14 Oct expiry, and books 7:00pm without calling.
3. She picks a reformer. Other members’ names are hidden. The choice locks at 6:45pm.
4. After booking, the pass still shows **2**. Nothing spent.
5. If she cancels before 4:00pm, the pass still shows **2**. Nothing restored, because nothing was taken.
6. If 8:00pm is full, she can join waitlist as **2nd** and see her place. The app does not auto-book her after the free-cancel deadline.
7. If she asks to extend the pass, the request goes to the owner’s to-do. Expiry stays 14 Oct on screen.
8. From 6:30pm, if she is still booked, **I’m here** records presence only. It does not spend a session.

### What “good” means for the owner

1. Proxy booking volume drops because members create and cancel their own rows through the same reservation services the desk already uses.
2. Session spend remains instructor/admin confirmation only. The phone never invents a balance.
3. Cancel actor is the member when she cancels in app. The desk does not fake “member cancelled.”
4. Policy exceptions (extend/hold) become owner tasks, not silent ledger edits.
5. Staff app keeps working even if nobody installs the member app.

Success for this proposal is not marketplace growth. Success is: Mina books and manages tonight without the desk typing, and Cheongdam still shows **2** after book and after in-time cancel.

---

## 2. Actors and what each is allowed to change

| Actor | Identity today | May change | Must never change |
|---|---|---|---|
| **Mina (store member)** | Phone already on a `store_member` row per studio. Not a staff `User`. | Own profile name/phone (self fields only); create/cancel/move/waitlist own reservations; pick own reformer/spot before lock; mark “I’m here” presence in window; register push token; mark alerts read locally; send constrained assistant requests | Remaining sessions; refunds; attendance spend; other members’ data; arbitrary `storeId`; pass expiry/hold/extend; payroll; class capacity rules |
| **Desk / owner (staff User)** | Existing staff login scoped to one studio | Create members and passes; run timetable; confirm/cancel/move as studio; confirm attendance (spend); decide extend/hold/refund; resolve under-minimum classes; handle late cancels | Nothing required from the member app. Staff APIs stay staff-only |
| **Instructor** | Staff/instructor principal in admin system | Confirm class attendance (authoritative spend); operational class notes in admin | Member pass purchase; member login; member-facing free chat |
| **Member App client** | Holds member token for one studio at a time | Display server values; send booking/cancel/move/waitlist/presence/assistant requests; store read/unread and local settings | Local calculation of remaining sessions, refunds, or “what balance will be” except by showing server-provided fields; calling `/v1/store/*` with a staff token |
| **aicc-center server** | System of record | Capacity, eligibility, deadlines, cancel actor, waitlist promotion policy, attendance spend, task creation for escalations | Trusting client-sent studio scope or client-sent cancel-actor claims |

Rule of thumb: if the value affects money, remaining sessions, or audit, only `aicc-center` writes it.

---

## 3. Journey — Cheongdam evening (Thu 8 Oct 2026)

Clock anchors used below:

- **9:41am** — story start
- **4:00pm** — free cancel deadline for tonight’s class
- **6:30pm** — I’m-here window opens
- **6:45pm** — reformer/spot lock (15 minutes before class)
- **6:55pm** — I’m-here window closes (5 minutes before class)
- **7:00pm** — Barre with Yuna Choi

### Step 0 — Account

Three paths, all gated by the phone the studio already has on file:

- **Create account** — one form (name, phone, password, confirm, terms), then a 6-digit code. This is activation of an existing `store_member`, not open signup. An unknown phone is refused on the form.
- **Log in** — phone + password, then the code.
- **Forgot password** — code, then set a new password.

**Business rule:** only a studio-registered phone can activate. First studio opened is Geumho (her default/home in the story). Cheongdam is available because the same phone is enrolled there as a separate member row.

### Step 1 — Home at Geumho

She sees Geumho pass **8 of 20**, expiry 12 Nov, and no class booked for today at Geumho.

**Business rule:** home is studio-scoped. Switching studio means a new scoped session, not a client-chosen `storeId` on every call.

### Step 2 — Switch to Cheongdam

She opens Capsule Barre Cheongdam. Pass shows **2 of 10**, expiry **14 Oct 2026** (warn state).

**Business rule:** Geumho and Cheongdam are two memberships / two member rows. The app never merges balances.

### Step 3 — Open book / schedule for tonight

Bookable list shows **7:00pm Barre · Yuna Choi · 6 of 8** with free cancel until 4:00pm. **8:00pm** is full and offers waitlist.

**Business rule:** spots taken and capacity are server facts. Price, payroll, and room yield are not shown. If enrolled count is under the studio minimum, member sees a clear “class may not run” warning before commit; the phone does not cancel the class.

### Step 4 — Choose 7:00pm and pick reformer

Six reformers. Taken spots are closed. Other members’ names are not shown. She selects a free reformer.

**Business rule:** spot selection is hers until **6:45pm**. After lock, change requires studio handling (or is refused in app). Spot map never exposes other members’ identities.

### Step 5 — Confirm booking

Status becomes confirmed (or requested→confirmed per studio setting). Source is `MEMBER`. Cheongdam pass still **2**.

**Business rule:** booking does not deduct a session. Duplicate book for the same session is rejected (`RESERVATION_ALREADY_EXISTS` or equivalent). Idempotent retry creates one row.

### Step 6a — Happy path continues toward class

Through the afternoon the today card is the product: time, instructor, reformer, cancel deadline, and server-stated “after attend” remaining if provided. At 9:41am, I’m here is closed.

### Step 6b — Optional: change time (one move)

From the booking detail she moves to another eligible slot (story example: Sat 10 Oct 10:00 private). This is **one move**, not cancel + rebook.

**Business rule:** server updates the existing reservation via move semantics. Client must not invent a cancel-then-create path that can strand capacity or double-book under retry.

### Step 6c — Optional: in-time cancel

Before 4:00pm she cancels tonight. Status becomes canceled by member. Pass still **2**.

**Business rule:** in-time member cancel does not restore a session because booking never took one. After 4:00pm the app refuses with `CANCELLATION_DEADLINE_PASSED`; late handling stays at the desk.

### Step 6d — Optional: waitlist on full 8:00pm

She joins waitlist and sees **You are 2nd.** Joining does not hold a session.

**Business rule:** if a seat opens **before** the cancel deadline, she is offered the seat and must still want it. After 4:00pm the app asks; it does **not** auto-book her into a class she can no longer leave for free.

### Step 7 — Alerts

She receives/reads: booked, waitlist place, expiry warning, cancel-deadline reminder (~3 hours before), class changed if the studio changes it. Read/unread can live on device; ledger state does not.

### Step 8 — Arrival (“I’m here”)

From **6:30pm to 6:55pm**, if she still has an active booking, the today card shows **I’m here**. Tapping it records presence only. Outside the window the button is not shown at all; Change time and Cancel take its place.

**Optional nudge (addendum 9 Oct 2026):** if she has allowed location, the phone watches for the studio during the arrival window only. When it senses she is close, it sends **one notification**: “You’re at Cheongdam. Say you’re here?” with an **I’m here** action. Tapping the notification records presence; dismissing it records nothing. The phone asks, it does not decide. If location is off, denied, or nothing fires, the in-app **I’m here** button is the fallback.

Trigger options for “close”:

| Trigger | Precision | Cost | Verdict |
|---|---|---|---|
| Geofence (OS region) | About a block | No hardware | **v1.** Enough, because the member confirms |
| iBeacon (Bluetooth) | Inside the room | One beacon per studio, Bluetooth on, Android background limits | **v2** if the desk sees false nudges from next door. iOS region monitoring wakes the app reliably; Android is weaker |
| Studio Wi‑Fi | Joined the network | None | Rejected, spoofable |
| Door QR / NFC | At the door | Sticker | Desk fallback, still a gesture |

**Business rule:** presence ≠ attendance spend. Nudge tap and in-app tap are the same presence write with a different source. Instructor/admin confirmation spends the session later. Sensing runs only 6:30–6:55 with an active booking; the app does not track location at any other time. Silent auto check-in is rejected: a wrong “here” from the cafe next door is worse than a tap.

### Step 9 — Extend / hold request (assistant or request card)

She asks: “Can I extend my Cheongdam pass? I’m away next week.” App sends a constrained request. Owner gets a to-do. UI still shows expiry **14 Oct**.

**Business rule:** assistant never mutates membership. Escalation creates/reopens a store task through existing task machinery.

### Step 10 — After class (out of member write path)

If she attended and the studio confirms attendance, balance becomes 1. That confirmation is not a member-app button in this scope.

---

## 4. Rules table

| # | Trigger | Who decides | What the member sees | What the server does | What must never happen |
|---|---|---|---|---|---|
| R1 | Phone login | Server match to existing `store_member` | Welcome / studio list she belongs to | Issue member token for one studio; list eligible studios on that phone | Open signup; treating staff `User` as member; trusting unverified phone |
| R2 | Studio switch | Server | Other studio’s pass and schedule only after switch | Mint/replace scoped token; reject studio outside her list | Client sending arbitrary `storeId` on book/cancel |
| R3 | View pass | Server ledger | Product name, remaining/total, expiry exactly as returned | Read membership projection | Client computing remaining; showing payment method, discounts, deferred revenue |
| R4 | List classes | Server timetable + redaction | Time, class, instructor, taken/capacity, cancel deadline, under-minimum warning | Return member-safe class projection | Showing payroll, room yield, owner notes |
| R5 | Book group/private | Server reservation create | Confirmed/requested card; balance unchanged | Create reservation, source `MEMBER`, enforce capacity/eligibility/quota/conflict; require idempotency key | Deducting a session on book; second active row for same session |
| R6 | Class full | Server capacity | Waitlist CTA with place in line when joined | Create/maintain waitlist position | Fake “booked” while waitlisted; holding a session for waitlist |
| R7 | Waitlist promotion | Server policy + member confirmation rules | Offer / ask; never silent trap after deadline | Promote only under policy; after cancel deadline require explicit accept and do not auto-book into non-free-cancel seat | Auto-booking after 4:00pm without consent |
| R8 | Pick reformer/spot | Member until lock; server after | Personal map; taken seats closed; no other names | Persist spot; lock at T-15; hide other member identities | Leaderboard of who sits where; changing spot after lock in app |
| R9 | Cancel in time | Server deadline + member actor | Cancelled; remaining unchanged | Cancel with actor=member; keep history | Client “restoring” a session; desk-looking cancel actor from member token |
| R10 | Cancel after deadline | Server | Deadline passed; contact studio / no self-cancel | Reject `CANCELLATION_DEADLINE_PASSED` | App silently canceling late |
| R11 | Change time | Server move service | Updated booking in one step | Move existing reservation | Cancel+rebook as two member calls for the same intent |
| R12 | Under minimum | Studio policy / server flag | “Class may not run” before commit and on card | Expose status; studio decides cancel/run | Member app canceling the class for everyone |
| R13 | I’m here in window | Member + server presence write | Button only 6:30–6:55 while booked | Record presence with source `TAP` or `NUDGE` | Spending a session; showing button all day; beacon as required path |
| R13a | Arrival nudge (opt-in) | Member permission + member tap + server window check | One-time location prompt; one notification when close with an I’m here action; fallback to in-app tap | Accept `NUDGE` presence only inside window with active booking; else ignore. Geofence in v1, iBeacon in v2 if needed | Silent auto check-in; sensing outside the window; marking attended from a nudge; refusing the tap when location is off; more than one nudge per class |
| R14 | I’m here outside window / no booking | Server | Button not shown; Change / Cancel occupy that space | Reject presence write | Back-dating presence; QR as the only happy path; a disabled button parked in the thumb zone |
| R15 | Attendance confirmed | Instructor/admin | Later pass refresh shows new remaining | Ledger spend on `ATTENDED` | Member button that decrements remaining |
| R16 | Extend/hold request | Owner via task | “Sent to studio”; expiry unchanged | Create owner to-do; no membership mutation | Assistant/expiry edit from phone |
| R17 | Alerts | Server events + app read state | Booked, changed, reminder, expiry, waitlist, escalation ack | Emit member-addressable notices | Storing member notices under a random staff `user_id` |
| R18 | Assistant ask | Server interpret/act | Cards only (handoff filters, confirm, escalated, info, unavailable) | Interpret; optionally run normal book API after confirm; escalate to task | Free-form instructor chat; assistant directly editing passes |

---

## 5. Screen inventory (journey + profile / pass / alerts)

Only screens needed for the Cheongdam evening story and the adjacent pass/profile/alert surfaces.

| Screen | Purpose in story | Rules enforced on screen |
|---|---|---|
| **Account** | Create (form + code), log in (phone + password + code), forgot (code + new password). Studio-registered phone only | R1 |
| **Home / today card** | Studio-scoped home; if booked, the card is the product (time, instructor, reformer, deadline, now / after-class count, I’m here or nearby state) | R2, R3, R12, R13, R13a, R14 |
| **Studio switch** | Move Geumho ↔ Cheongdam with server-scoped session | R2 |
| **Book / class list** | Tonight’s bookable classes; full class → waitlist entry; under-minimum warning | R4, R5, R6, R12 |
| **Reformer / spot pick** | Choose seat before lock; hide other names | R8 |
| **Booking confirm** | Show held booking; remaining unchanged | R5, R15 (display only) |
| **My schedule** | Upcoming/canceled bookings for this studio | R5, R9, R11 |
| **Booking detail** | Cancel in time, change time as one move, deadline copy | R9, R10, R11, R12 |
| **Waitlist status** | Visible place in line; stay/leave; no silent auto-book after deadline | R6, R7 |
| **Pass history** | Current/past passes; server remaining/expiry | R3, R15 |
| **Alerts** | Booked, waitlist, expiry, reminders, escalation ack; local read/unread | R17 |
| **Assistant (constrained)** | Natural-language entry that returns cards; extend request → owner task | R16, R18 |
| **Profile / settings** | Name/phone self fields; alert toggles; studios list; logout | R1, R2, R17 |

Not in this inventory: instructor app, nearby studio shop, in-app checkout, body charts, reviews, open marketplace browse.

---

## 6. Explicit non-goals

Out of scope for this member proposal:

1. ClassPass-style credits or cross-studio shared credit wallets
2. Open signup / acquiring people the studio has not registered
3. Reviews, social feed, streaks, body charts
4. Nearby-studio shop or discovery marketplace
5. In-app pass purchase or payment checkout
6. Free-form instructor chat
7. Face-scan doors or Bluetooth/beacon as the primary check-in UX
8. Instructor app, payroll, refund calculation, attendance spend UI for members
9. Copying the 2019 46/51-screen Pilagram member IA as the build backlog
10. A second database of members, passes, or reservations in the app repo
11. Calling staff `/v1/store/*` APIs with a member client
12. Any claim that public member endpoints already exist in `aicc-center` today — they do not

---

## 7. Open decisions that would block a build

These are unresolved in implementation today. Recommendations are normative for this BA so engineering is not blocked by blank cells.

### D1 — Member identity

**Issue:** Staff auth is `User`. `store_member` has no login. 2019 mocks used phone+password; the Phase 2 direction is phone verification against a studio-registered number.

**Recommendation:** phone + password, with an OTP against the studio-registered phone on every create, login, and password reset. The password is the member’s; the OTP proves the phone is still the one on the contract. No public self-signup: “Create account” activates an existing `store_member` and is refused for an unknown phone. One phone may map to multiple studio memberships; each studio requires a scoped member session. Rate-limit challenges; lock out abuse. (Revised 9 Oct 2026 from OTP-only, after the two-screen account flow was accepted.)

### D2 — Public IDs

**Issue:** Internal entities use integer PKs. Contract requires opaque public IDs (UUID v7 / opaque strings).

**Recommendation:** Keep integers internal. Expose opaque public IDs on the public façade only. Member app never sees sequential member/reservation integers. Map public↔internal only inside `aicc-center`.

### D3 — Cancel API shape

**Issue:** Staff path is `POST /store/reservations/:id/cancel`. Draft public contract shows `DELETE /reservations/{id}`.

**Recommendation:** Public surface uses `DELETE /api/public/v1/reservations/{id}` (contract-aligned). Implementation must call the **existing** cancel service with actor derived from the member principal. Do not accept `canceledBy` from the client body. Do not build a second cancel rules engine. Move/change remains a separate explicit action (one move), not delete+create.

### D4 — Notification principal

**Issue:** Current notification infrastructure is `User`-scoped. A member is not a staff user.

**Recommendation:** Introduce a member notification principal (link table or member-targeted projection) keyed to `store_member` + studio scope. Push token registration binds to that principal. Never insert member alerts under a staff `user_id`. App may own read/unread locally; durable event history remains server-addressable to the member principal.

### Related build constraint (not optional)

Public member façade must wrap existing reservation/membership/class services. `ReservationSource.MEMBER` already exists as a value; member-authenticated callers do not. Until D1–D4 are implemented in `aicc-center`, the phone UI is a proposal only.

---

## 8. Acceptance checks a PO can use in a demo

Use Mina Park, Thu 8 Oct 2026. Cheongdam pass starts at **2 of 10**, expiry **14 Oct 2026**.

| # | Demo check | Pass if |
|---|---|---|
| A1 | Sign in with studio-registered phone | She enters the product; unknown phone is refused; no signup form |
| A2 | Switch Geumho → Cheongdam | Balances stay separate (8/20 vs 2/10); no client-typed studio id |
| A3 | Book Cheongdam 7:00pm Barre · Yuna Choi | Booking succeeds; remaining still **2** |
| A4 | Pick reformer | Taken seats blocked; other names hidden; selection visible on today card |
| A5 | Retry same book with same idempotency key | Still one reservation |
| A6 | Open full 8:00pm waitlist | Shows place in line (e.g. 2nd); remaining still **2** |
| A7 | Waitlist after cancel deadline behavior | App asks / does not silently auto-book into a non-free-cancel seat |
| A8 | Change time as one move | One booking updated; no cancel+rebook residue |
| A9 | Cancel before 4:00pm | Cancel succeeds as member; remaining still **2** |
| A10 | Cancel after 4:00pm | App refused with deadline code; no local forge-cancel |
| A11 | Under-minimum class | Member sees “may not run” warning; she cannot cancel the whole class |
| A12 | 9:41am today card | I’m here hidden/closed |
| A13 | 6:30–6:55pm with active booking | I’m here available; tap records presence only; remaining still **2** |
| A14 | Extend request | Owner to-do created; on-screen expiry remains **14 Oct** |
| A15 | Staff attendance later (admin system) | Only then may remaining become 1; member app never decremented it itself |
| A16 | Security boundary | Member token cannot read the other studio’s rows, cannot call staff store APIs, cannot change `remainingSessions` |
| A17 | Arrival nudge, opt-in | With location allowed, being close at 6:40pm shows one notification; tapping I’m here on it records presence as `NUDGE`; “Not yet” records nothing; at 9:41am or with no booking nothing fires; with location denied the in-app tap still works; remaining still **2** |
| A18 | Create account with unknown phone | Form refuses before sending a code; no `store_member` is created |

**Demo script (happy path, 3 minutes):** Sign in → switch to Cheongdam → book 7:00pm → pick reformer → show remaining still 2 → cancel in time → show remaining still 2 → rebook → advance clock to 6:30 → I’m here → show remaining still 2 → show owner task from extend ask.

---

## Document control

| Field | Value |
|---|---|
| In scope | Account (create / log in / forgot), studio switch, today, schedule, group/private book, cancel/change, waitlist, spot pick, presence (tap or opt-in geofence), pass history, alerts, profile, constrained ask |
| SoR | `aicc-center` |
| Client | Separate member app repo; proposal UI is not production |
| Evidence basis | Current staff APIs for members/memberships/classes/reservations/attendance exist; public member login/API do not |
| Non-negotiable | Phone does not calculate money, remaining sessions, refunds, or attendance spend |
