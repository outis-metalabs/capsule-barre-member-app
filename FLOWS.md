# Member App — Registration and Pass flows

**Date:** 9 Oct 2026 · **Basis:** `aicc-center` desk behaviour verified in code on this date; planned server changes in `AICC_CENTER_CHANGES.md`; rules in `BA.md`; screens in `FEATURES.md`.
Persona anchors: Cheongdam **2 of 10**, ends **14 Oct 2026**; Geumho **8 of 20**, ends **12 Nov 2026**. Two memberships, never one wallet.

One line that governs both flows: the phone shows server values and sends requests into the same services the desk uses. A session is spent only when the studio marks the class attended.

`Where`: **desk** = staff web · **app** = member app · **server** = `aicc-center` · **cron** = scheduled job · **in person** = off-system.

---

## Flow 1 — Registration at the desk → app activation

### What happens

A person walks in or phones. The desk agrees a product and takes a signed paper contract. The owner photographs it; `POST /store/contracts/extract` reads the fields (name, product, amount, sessions, months, expiry, pay method, phone) with a confidence score and **creates nothing**. In the issue wizard the owner confirms the fields; quick-add creates the `store_member` (or reuses one, on a duplicate-phone warning); the issue step writes the `membership` and its payment rows in one transaction. The desk then says: *install the app, tap Create account, type this phone and your name, then the code we text you.* In the app, activation matches phone **and** name against a live `store_member`, the code proves the phone, and she lands on her studio seeing the pass the desk just issued. If the same phone is enrolled at Geumho too, one account appears with two studio sessions.

### Three consent axes — they are not the same thing

| Axis | Where | Needed for the app? |
|---|---|---|
| Operational SMS opt-out | `store_member.smsOptOut` | Only for the SMS **fallback** when she has no device. Not for push |
| Marketing (+ night) | `marketingConsentAt`, 2-year reconfirm | **No.** A member who never gave marketing consent still gets booking, reminder, and expiry push |
| App push | `member_device` + per-type toggles in the app (new) | This is the app's own channel |
| Health | separate sensitive table | Never shown in the app |

The activation / login code is transactional authentication: it sends regardless of opt-out or marketing state.

### Steps

| # | Step | Who | Where | Recorded | Member sees | Ref |
|---|---|---|---|---|---|---|
| 1 | Enquiry; product agreed; paper contract signed | prospect, desk | in person | nothing | — | — |
| 2 | Photograph contract, run extraction | owner | desk → server | audit/ledger row only; **no member, no membership** | — | verified |
| 3 | Confirm fields; quick-add member with live duplicate check | owner | desk → server | `POST /store/members {name, phone?, birthDate?}` → one `store_member`; `publicId` (D2) | — | R1, D2 |
| 4 | Issue the pass with payment | owner | desk → server | `POST /memberships` → `membership` ACTIVE, remaining = total, expiry server-derived from `validMonths`, deferred revenue + payment rows, idempotent | — | R3 |
| 5 | **"Install the app" message** (new) | server, on issue | server → SMS | `SmsType.MEMBER_APP_INVITE`: store link + "create account with this phone and your name". Operational, exempt from marketing consent, once per phone | — | G16 |
| 6 | Consents, if the studio wants SMS fallback or marketing | owner | desk → server | separate PATCHes; **not required for the app** | — | R17 |
| 7 | Create account | member | app → server | `POST /v1/member/auth/activate {phone, name, password}` → canonical phone + normalised name must match ≥1 `store_member` with `ended=false`; else 404 `MEMBER_NOT_REGISTERED` before any code is sent. Creates `member_account` PENDING + OTP | S2 form → "Get code" | F1, R1, D1 |
| 8 | Enter code | member | app → server | `verify {phone, code, ACTIVATE}` → account ACTIVE; tokens for one studio + `studios[]` (every non-ended `store_member` on that phone) | S3 → Today | F1 |
| 9 | See the pass | member | app → server | `GET /v1/member/memberships` | S19: 2 of 10 · ends 14 Oct — exactly as issued | R3 |
| 10 | Two studios: switch | member | app → server | `switch {storeId ∈ studios[]}` → new scoped tokens; else 403 | S21; the other balance, never merged | R2 |

### Edge cases

| Case | What happens | Handling |
|---|---|---|
| Phone already exists in **this** studio | Quick-add warns; server does not block | Desk reuses the existing row. Activation picks the **newest non-ended** row when several match; two rows with the same phone **and** name is a desk clean-up task (G6) |
| Phone exists in the **other** studio | Expected | One `member_account`, `studios[]` lists both |
| Phone typo at the desk / OCR misread | Activation fails, or the code goes to a stranger | Desk corrects `store_member.phone` **before** activation; the invite SMS (step 5) surfaces the typo early |
| Phone corrected at the desk **after** activation | Would break the account ↔ member link | New desk action **"Relink app account"**: sets the new phone on `member_account`, re-syncs linked rows, audit entry; member confirms with a code on the new number (G2) |
| Member changes number in the app | `PHONE_CHANGE` OTP to the new number; updates account + all linked rows | Reject if the new number already belongs to another account |
| Lost phone / number unreachable | Every login needs a code | Desk relink after identity check; never "text the dead number" (G8) |
| Member **ended** at one studio | Activation ignores ended rows; `studios[]` omits that studio | If ended **after** activation: server revokes that studio's session; app shows "studio no longer available" (G4) |
| Member **anonymised** (PIPA) | Name/phone nulled | Anonymisation also revokes `member_account` + refresh tokens for that studio (G3) |
| Children / siblings on a parent's phone | Bulk sibling issue creates several rows sharing the parent's phone; phone+name cannot pick a child | v1: desk books children; the parent's own account sees only the parent's passes. v2: guardian link (G5) |

### Decisions — confirmed 9 Oct 2026

| # | Decision | Decided |
|---|---|---|
| OD-1 | Does `smsOptOut` suppress the activation/login code? | **No** — it is authentication, not marketing |
| OD-2 | Name match strictness | Normalise whitespace, then exact. No fuzzy match. Copy: "use the name on your contract" |
| OD-3 | Which studio opens first | The studio of the most recently active membership; switch offered |
| OD-4 | Duplicate phone in one studio | Server stays non-blocking; quick-add defaults to **use existing** on phone + name match |
| OD-5 | Capture consent at registration for the app? | No change — the app needs none of the three |

---

## Flow 2 — Pass lifecycle, both sides

### What happens

A pass is issued ACTIVE with `remaining = total` and a server-derived expiry. Booking and cancelling never touch `remaining`; the only deduction is the instructor or owner marking the class **attended**, which drops it by one and recognises revenue. When the pass runs low or nears expiry, the 01:00 cron raises a reminder task; the owner approves it and the member hears by push (or SMS if she has no device). She can ask to **hold** or **extend**, but those are requests that become owner tasks — the app never changes the pass and the on-screen expiry stays where it is until the owner acts. The owner can hold a pass only if it is ACTIVE, has balance, is not expired, and has **no upcoming bookings**; releasing it extends expiry by exactly the days held. At 04:17 a cron flips expired passes to EXPIRED and recognises the remaining revenue; `remaining` is kept as history. Renewal is a new membership row. Several active passes are consumed earliest-expiry-first. Transfer moves a pass within the studio; same-day cancel voids the sale; refunds run in the payment module. The app shows all of this read-only.

### Transitions

| # | Transition | Trigger | Recorded | Member sees | App must not | Ref |
|---|---|---|---|---|---|---|
| T1 | **Issued → ACTIVE** | owner, desk | `membership` ACTIVE, remaining = total, expiry derived, deferred revenue, payments | S19: N / total, expiry, meter | Show price or deferred revenue | R3 |
| T2 | **Book** | member, app | `store_reservation` source MEMBER; capacity, eligibility on class date, weekly quota, duplicate check; idempotent; **no deduction** | S6 confirmed; remaining unchanged; "after class" is a server projection | Deduct; compute a balance | R5 |
| T3 | **Cancel in time** | member, app | canceledBy MEMBER; remaining unchanged | Cancelled; remaining unchanged | "Restore" a session | R9 |
| T4 | **Attended → remaining − 1** | instructor / owner, desk | `membership_attendance` ATTENDED; `recognizeOnAttended` | Next refresh shows the new remaining; S17 shows which pass a past class used | Offer any button that decrements | R15 |
| T5 | **Low balance / expiring soon** | 01:00 cron → owner approves | `store_task REG_REMINDER` (PERIOD 0–7 days to expiry; COUNT remaining ≤ 3 or 0–7 days; TRIAL excluded; suppressed if a newer pass exists) → push to device, else SMS | S20 notice; S19 meter in warn; Ask-AI balance card offers extend / hold | Time the reminder itself; nag a TRIAL | R17, G10 |
| T6 | **Hold requested → HELD** | member asks (app); owner holds (desk) | `member_request HOLD` + `store_task MEMBER_REQUEST`; owner: `POST …/hold` — needs ACTIVE, balance > 0, not expired, **no seated reservations** → HELD, `heldAt` | "Sent — pass still ends 14 Oct"; after the owner acts: HELD, booking blocked | Hold herself; imply it took effect | R16 |
| T7 | **Released** | owner, desk | `unhold` → expiry + exactly the days held; ACTIVE | New expiry, from the server | Compute the new date | — |
| T8 | **Extend requested → extended** (new) | member asks (app); owner extends (desk) | `member_request EXTEND` + task; owner: **`POST …/extend {days \| newExpiresAt, reason}`** (new, owner-only, audit-logged) | "Sent — still ends 14 Oct" → later: new expiry + alert "Cheongdam extended your pass to 28 Oct" | Change expiry; promise an outcome | G1 |
| T9 | **EXPIRED** | 04:17 cron | ACTIVE → EXPIRED where `expiresAt < today`; remaining kept as history. Reads refuse the pass from the day after expiry even before the cron | "Ended 14 Oct · 3 unused · Ask the studio"; booking refused `MEMBERSHIP_EXPIRED` | Treat `status = ACTIVE` as usable; zero the count; imply unused sessions are refundable | R3 |
| T10 | **Renewed** | owner, desk | A **new** `membership` row. Several active passes: earliest expiry first (null last), then id; eligibility by class type on the class date | Current and previous passes, each with its own remaining; "used next" label from the server | Merge balances; let her choose the pass; compute the order | G15 |
| T11 | **Transferred** | owner, desk | Moves to another member in the studio; no fee; remaining unchanged | Pass disappears; appears for the recipient once they activate | Start a transfer; reveal the other member | G12 |
| T12 | **Voided same day** | owner, desk | Payments voided; status VOID | Pass gone from current; "voided" in history | Show VOID as usable | G11 |
| T13 | **Refunded** | owner, desk (payment module) | refund = max(0, paid − used × base price − penalty); deferred revenue released; remaining unchanged | Read-only "refunded"; questions go to Ask | Calculate or show the formula | G11 |

### Extend: why it needs its own operation

Today expiry moves only by releasing a hold (+ the days held) or by a refund. "Extend by 7 days" expressed as a hold means the pass is frozen for 7 real days — booking blocked — and it is refused outright whenever she has a class booked. The member asked to use the pass *later*, not to be stopped *now*. So: `POST /memberships/:id/extend {days | newExpiresAt, reason}`, owner-only, audit-logged, reachable from the request's reply box. Until it ships, the owner's only real lever is issuing a new pass; the app shows expiry unchanged until the owner acts either way.

### Hold: what the member does not see

Hold is refused while she has seated reservations. The request reply should say so ("cancel your upcoming classes first, or we can"), and the server should return the block reason to the owner. `holdMaxDays` / `holdMaxCount` exist as settings but are not enforced today; the app shows no hold allowance.

### Specific cases

| Case | Behaviour |
|---|---|
| Several active passes | Server decides which pass a class will use; the member projection returns it per upcoming class (G15). The app labels, never computes |
| TRIAL | One session with a validity window; deducts like COUNT; excluded from reminders. On exhaustion the app routes to Ask — no in-app purchase |
| PERIOD passes | No session count. The app renders validity window + weekly frequency instead of N / total; the projection must carry `type` (G9) |
| Two studios | Fully independent lifecycles, reminders, holds, expiries; never merged |
| Midnight vs 04:17 | Between 00:00 and the cron the row is still ACTIVE but unusable. The app decides bookability from the server's eligibility / error, never from `status` |
| After expiry | Remaining shown as history, never as usable or refundable |
| VOID / refunded | The member projection exposes one display status — ACTIVE · HELD · EXPIRED · VOID · REFUNDED · ENDED — so the app never infers usability from `status` + date (OD-8) |
| Bookings on a pass that is transferred / voided / refunded | Transfer: bookings stay with the member. Void / refund: future bookings cancelled by the studio, member notified (G12) |

### Decisions — confirmed 9 Oct 2026

| # | Decision | Decided |
|---|---|---|
| OD-6 | Extend as a real operation, or as hold? | **Real operation** with reason and audit |
| OD-7 | Do expiry / low-balance pushes need owner approval like the SMS? | Operational pushes (booked, deadline, class change) fire automatically. Expiry / low-balance mirror the reminder rules and fire without approval; the SMS is suppressed when a device exists, so one channel per event |
| OD-8 | Terminal display status | Yes — one field in the member projection |
| OD-9 | "Used next" for several passes | Server returns it per class |

---

## Gaps — needed by the app, covered by neither today's code nor the earlier change list

| ID | Gap | Resolution | Type |
|---|---|---|---|
| G1 | No extend-expiry operation | `POST /memberships/:id/extend`, owner-only, audit | server |
| G2 | Desk phone correction after activation breaks the account link | Desk "Relink app account" with code on the new number + audit | server + desk |
| G3 | Anonymisation orphans the account | Anonymise also revokes account + tokens for that studio | server |
| G4 | Member ended after activation keeps a token | Server rejects; studio dropped from `studios[]`; app copy | server + app |
| G5 | Children on a parent's phone cannot activate | v1 desk books children; v2 guardian link | desk now, server v2 |
| G6 | Duplicate phone + name in one studio | Activation takes newest non-ended; quick-add defaults to reuse | server + desk |
| G7 | Does opt-out block the code? | No — authentication always sends | server policy |
| G8 | Account recovery with a lost number | Desk relink after identity check | server + desk |
| G9 | PERIOD passes have no count | App renders window + frequency; projection carries `type` | server + app |
| G10 | Double reminder (SMS + push) | One channel per event; push replaces SMS when a device exists | server + desk |
| G11 | Refund / void have no member-facing meaning | Display status field | server + app |
| G12 | Bookings on a transferred / voided / refunded pass | Defined above | server + app |
| G13 | Hold blocked by bookings is invisible to the member | Reply copy + block reason to the owner | app + server |
| G14 | Hold limits unenforced | Enforce and expose allowance, or show nothing quantitative | server (optional) |
| G15 | Which pass a booking will use | Per-class projection from the server | server + app |
| G16 | Nothing tells a new member the app exists | Issue-triggered "install the app" SMS, operational | server + desk |
| G17 | TRIAL exhaustion has no path | Clear trial status; Ask on exhaustion | app |

The prototype (`app.html`) shows COUNT passes only. G9 (PERIOD rendering) and the display-status states in T9–T13 are the two things it does not yet demonstrate.
