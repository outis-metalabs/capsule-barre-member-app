# Member App — analysis and development plan

Working draft, 2026-10-08. English. The phone UI is a proposal, not a production app, and it does not call the server.

Open the proposal: http://127.0.0.1:8766/app.html
Same file: `member-app-proposal/app.html` (`index.html` is the earlier slideshow draft, kept for reference)

## 1. What this is

AICC today is the **admin system** in `aicc-center`. The owner runs the studio from the web app under `/store`: members, passes, classes, the timetable, reservations, money, payroll, and the daily to-do list.

The Member App is a second product for the person who takes class. It does not keep its own ledger. Every member, pass, booking, and session count stays in `aicc-center`. The app only shows what that system returns and sends requests into the same booking code the desk already uses.

This draft covers the member list only: sign in, home, schedule, group and private booking, cancel, pass history, alerts, profile, and a natural-language assistant. It is not the instructor app, and it is not the old 46-screen Pilagram member app.

The clickable proposal is an appointment card, not a menu. On class day the screen is the class: time, instructor, reformer, cancel deadline, and what the balance will be after she attends. "I'm here" appears only from 6:30pm and does not spend a session; with location allowed, the phone sends one notification when she is close and the tap on it is the check-in. A full class is a numbered waitlist. Changing time is one move.

The click-through is one person, Mina Park, at two Capsule Barre studios:

| Studio | Pass | What she sees |
|---|---|---|
| Geumho (opens here) | 8 of 20 left, until 12 Nov 2026 | No class booked |
| Cheongdam | 2 of 10 left, until 14 Oct 2026 | She books Thu 8 Oct 7:00pm — still before expiry — then cancels in time |

After both the booking and the cancel, Cheongdam still shows **2 left**. A session is spent only when the class is marked attended, and that happens in the admin system, not in the phone.

## 2. Analysis of aicc-center

Stack: NestJS, MySQL, TypeORM on the API; Next.js on the staff web app. Staff calls are under `/v1/...`, scoped to the studio on the staff login. The client is not allowed to send a studio id and be trusted.

### What the admin system already owns

| Admin screen | API that exists now | Who can call it |
|---|---|---|
| Members | `/v1/store/members` — create, search, detail, phone, consent | Staff |
| Passes | `/v1/memberships` — issue, hold, unhold, transfer, cancel | Staff |
| Classes and timetable | `/v1/store/classes`, `/v1/store/schedule` | Staff |
| Reservations | `/v1/store/reservations` — list, create, cancel, confirm, move | Staff with class-write permission |
| Attendance and session spend | Instructor class confirmation, not a member button | Staff / instructor |
| Money, refunds, payroll, expenses, bookkeeping | `payment`, `payroll`, `expense`, `bookkeeping` | Staff only |
| Owner to-do list | `store-task` | Staff |

Those staff screens already live in `aicc-center/frontend/src/pages/store/` (`members`, `classes`, `schedule`, `tasks`, `instructors`, `products`, `payroll`, `refund`, and the rest).

A reservation row is `store_reservation`: one studio, one class session, one member, one pass. The same member cannot hold two active rows for the same session. Status is `REQUESTED`, `CONFIRMED`, `ATTENDED`, `CANCELED`, `NO_SHOW`, or `WAITLIST`. Who created it is recorded separately (`DESK`, `MEMBER`, or `INSTRUCTOR`). Who cancelled it is also separate, and the server derives that from the login. The desk is not allowed to type "the member cancelled" into the request, because that choice changes whether a session comes back.

Session balance is not stored on the reservation. It changes only when attendance is confirmed, inside the membership ledger. Booking does not subtract. An in-time cancel does not add a session back, because the booking never took one.

### What is not built

There is no member login and no `/api/public/v1`. `ReservationSource` already has the value `MEMBER`, but only the desk calls the reservation API today. A member token cannot be issued, so the phone cannot book, cancel, or read its own pass.

A staff login is one studio. Mina at Geumho and Cheongdam is two member rows, not one account with a studio id in the body. Switching studio has to mean a new login scoped to the other studio.

The assistant endpoints (`/assistant/interpret`, `/assistant/act`) are not implemented. The owner to-do list they would write into does exist.

`billing` in this repo is the product's own subscription. It is not member checkout. Do not put pass purchases in the first member app.

### What the member app must never do

1. Compute sessions left, refunds, or payroll.
2. Send `storeId` and expect the server to obey it.
3. Call `/v1/store/reservations` with a staff token. That path records the cancel as the studio.
4. Change a pass from the assistant. "Can I extend my Cheongdam pass?" becomes an owner to-do. The expiry stays 14 Oct.
5. Store a copy of members, passes, or bookings. If the app is deleted and reinstalled, nothing is lost except unread alerts.

## 3. Development plan

Build the API in `aicc-center`. Build the phone UI in a new repo. Do not put the member screens inside the admin app. An app-store release must not be tied to a ledger deploy.

### Step 1 — Member API on the admin system

A thin public controller. It checks that the phone belongs to a member the studio already created, then calls the existing reservation, class, and membership services. It does not copy capacity rules, pass selection, or weekly limits.

| Call | What it does |
|---|---|
| `POST /api/public/v1/auth/member/activate` | Create account. Phone must already be a `store_member`; unknown phone is refused. Sets password, then sends a code |
| `POST /api/public/v1/auth/member/login` | Phone + password, then a code to that phone. Returns a token for one studio, and the list of studios on that phone |
| `POST /api/public/v1/auth/member/verify` | The 6-digit code for activate, login, or reset. Rate-limited |
| `POST /api/public/v1/auth/member/reset` | Forgot password. Code first, then the new password |
| `POST /api/public/v1/auth/member/switch` | Studio id must be one of that list. Returns a new token. Anything else is rejected |
| `POST /api/public/v1/reservations/{id}/presence` | "I'm here" from the app (source `TAP`) or from the arrival notification (source `NUDGE`). Accepted only 6:30–6:55 with an active booking. Records presence; never attendance. The nudge trigger (geofence v1, iBeacon v2) lives on the phone, not in this API |
| `GET /api/public/v1/me` | Name and phone. Not owner notes |
| `PATCH /api/public/v1/me/profile` | Name and phone only |
| `GET /api/public/v1/me/memberships` | Product name, remaining, total, expiry |
| `GET /api/public/v1/classes` | Bookable sessions. Spots taken is allowed. Price, payroll, and room yield are not |
| `POST /api/public/v1/reservations` | Same create service as the desk. Source `MEMBER`. Idempotency key required |
| `POST /api/public/v1/reservations/{id}/cancel` | Member is the cancel actor. Deadline comes from studio settings |
| `GET /api/public/v1/me/reservations` | This member, this studio only |

Done when: a member token cannot read the other studio, cannot cancel as the studio, and cannot change `remainingSessions`. Sending the same book request twice with the same idempotency key creates one row. The staff app still works if nobody ever installs the member app.

### Step 2 — The phone app, separate repo

New repo. React Native (Expo), unless the first version is a phone website. Screens match this proposal, in this order, because this is the order that stops the owner typing bookings:

1. Sign in and studio switch
2. Home and pass history
3. Group booking, schedule, in-time cancel, and the error codes (`CLASS_SESSION_FULL`, `MEMBERSHIP_EXPIRED`, `MEMBERSHIP_EXHAUSTED`, `RESERVATION_ALREADY_EXISTS`, `CANCELLATION_DEADLINE_PASSED`)
4. Private lesson
5. Alerts. Push can use the existing notification setup. Read/unread is the only state stored with the app
6. Profile
7. Assistant last

Done when: the Cheongdam story in the mock runs on the real API with test members, and the balance is still 2 after book and after cancel.

### Step 3 — Assistant

The assistant is in the first release. It still ships after Step 2's booking works, because every card button calls the booking, cancel, and request APIs from Step 1 — the assistant adds interpretation, not new writes. The app sends the sentence to the admin system. The admin system returns a card, never a free paragraph. The prototype shows the five v1 intents.

- Clear request with several times → open the normal book screen with those filters filled in. The assistant does not book.
- One exact class, and she confirms the card → the normal book API runs.
- Policy question, including extending a pass → a to-do on the owner's list, and a card that says it was sent. The pass does not change.

### Step 4 — Korean copy, then Capsule Barre

Translate after this English flow is accepted. The beta target: members book in the app instead of calling the studio, and the owner's proxy bookings drop. Do not start the binary until Step 1 has stopped changing.

## 4. Out of scope

- Instructor app, attendance check, payroll
- Paying for a pass inside the app
- The old Pilagram center app
- A second database of members or bookings
- Any code change inside `aicc-center` in this round

## 5. Files

| File | Role |
|---|---|
| `member-app-proposal/app.html` | Clickable proposal (tab app, account flow, live clock) |
| `member-app-proposal/ANALYSIS.md` | Source analysis of `aicc-center` |
| `member-app-proposal/FEATURES.md` | Full feature list F1–F37, screens S1–S25, notifications N1–N7, navigation |
| `member-app-proposal/AICC_CENTER_CHANGES.md` | Exact changes to `aicc-center` per layer, with file references, migrations, security proofs, and build order |
| `member-app-proposal/plan.html` | The whole plan as one page: summary, repos, today, features, screens, flows, server changes, order, proofs, decisions, gaps |
| `member-app-proposal/FLOWS.md` | Registration desk → app activation, and the pass lifecycle from both sides; decisions OD-1–OD-9 (confirmed 9 Oct 2026); gaps G1–G17 |
| `member-app-proposal/BA.md` | Rules R1–R18, decisions D1–D4, demo checks A1–A18 |
| `member-app-proposal/UX.md` | Visual rules and what the UI refuses |
| `member-app-proposal/index.html` | Earlier slideshow draft, superseded |
| `member-app-proposal/PLAN.md` | This analysis and plan |
