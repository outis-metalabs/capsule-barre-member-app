# What to change in `aicc-center` for the Member App

**Date:** 9 Oct 2026 · **Basis:** code at `aicc-center` HEAD (NestJS 10, TypeORM 0.3, MySQL 8, 417 migrations), mapped file by file on this date. Line numbers are from that read.
**Companion docs:** `FEATURES.md` (F1–F37, S1–S25), `BA.md` (R1–R18, D1–D4, A1–A18), `PLAN.md`.

## 0. Position

`aicc-center` stays the system of record and grows **one new backend module**: `member-api`. The phone app lives in the separate repo Jay already named (`aicc-crm`) and owns no domain tables. Nothing member-facing is added to the staff Next.js app except the owner-side pieces listed in §9.

Why this is the right cut: the repo's own contract says member-app bookings and desk bookings "must pass through the same code" (`timetable/services/store-reservation-create.service.ts:90-97`), the enums for a member actor already exist (`ReservationSource.MEMBER`, `ReservationCancelActor.MEMBER`), and the deduction ledger has exactly one entrance — instructor confirmation (`membership/CLAUDE.md`, "Retired 라우트"). The member API adds callers to that machinery; it adds no second rules engine.

Routes mount under the existing global prefix as `/v1/member/*` (`main.ts:113`). The draft contract's `/api/public/v1/*` becomes a gateway alias if Jay wants that shape externally.

## 1. What exists and is reused untouched

| Need | Exists | Where |
|---|---|---|
| Book (capacity, duplicate, eligibility on session day, weekly quota, auto-confirm) | ✔ | `StoreReservationCreateService.create` / `locked` (`store-reservation-create.service.ts:102,136-337`) |
| Waitlist join + ordered promotion with the same eligibility | ✔ | `enqueue` (`:128`), `waitlist-promotion.ts:42` |
| Cancel deadline math | ✔ | `class-timing.util.ts:42` `isPastCancelDeadline`, setting `store_settings.cancelDeadlineHours` |
| Move as one operation, carrying makeup | ✔ | `store-reservation-move.service.ts:120` |
| Session spend only on ATTENDED, from instructor confirmation | ✔ | `membership-attendance.service.ts:83,242,299` → `DeferredRevenueService.recognizeOnAttended` |
| Remaining / total / expiry / hold on a pass | ✔ | `membership.entity.ts` (`remainingSessions`, `expiresAt`, `heldAt`, `status`) |
| Member master with phone and consents | ✔ | `store-member.entity.ts` (`phone`, `smsOptOut`, `marketingConsentAt`, `ended`) |
| Under-minimum flag | ✔ | `store_class.minEnroll`, `store_settings.minEnrollCount` |
| Presence that is not attendance | ✔ | `store_attendance_checkin` ("방문 기록일 뿐 차감이 아니다", `CheckinSource DESK|QR`) |
| Owner to-do list | ✔ | `store_task` with typed `context` JSON, unique `(storeId, type, refKey)` |
| SMS to members with opt-out | ✔ | `sms` module (PPURIO / NHN), `sms/messaging/recipient.ts` |
| Idempotency infrastructure | ✔ | `common/idempotency` (`@Idempotent`, `IdempotencyInterceptor`, `idempotency_record`) |
| Rate limiting, request ids, validation whitelist | ✔ | `ThrottlerGuard`, `RequestIdInterceptor`, `ValidationPipe({forbidNonWhitelisted})` |

## 2. What is missing (nothing member-facing exists)

- **No member principal.** `JwtStrategy.validate` loads a staff `User` and nothing else (`config/jwt/jwt.strategy.ts:27-38`). No member login, token, guard, or OTP — `otp.entity.ts` is `@ManyToOne(User)`.
- **No member actor wiring.** Create hardcodes `source: DESK` (`store-reservation-create.service.ts:306`); cancel hardcodes `STORE` / `CLOSURE` (`store-reservation-cancel.service.ts:189,273,417`). The documented rule "member app after deadline → 400, no deduction" (`reservation-cancel-actor.enum.ts:1-11`) has no code path.
- **Store scope comes from the staff user**, via `resolveStoreId(user)` and `StoreScopeGuard`; every service signature starts with `user: User`.
- **Notifications and push are staff-only**: `notification.userId` and `push_subscription.userId` are `@ManyToOne(User)`; delivery is Web Push / VAPID, not FCM/APNs.
- **No per-reformer seat.** Capacity is a count (`class-capacity.ts`, `session-seats.ts`); `store_reservation` has no spot column; no lock-time setting.
- **No arrival window settings**, no waitlist-offer concept (promotion is automatic on seat release), no member request entity, no public/opaque ids, no assistant endpoint.
- Idempotency records are keyed `(storeId, idemKey)` with `actorUserId` — a member needs its own actor axis.

## 3. Changes, by layer

### 3.1 Member identity and auth (new module `member-api/auth`) — F1–F4, R1, D1

New tables:

| Table | Columns (key ones) | Note |
|---|---|---|
| `member_account` | `id`, `phone` (canonical, unique), `passwordHash`, `status`, `failedLogins`, `lockedUntil`, `createdAt` | One account per phone. Not a `User`. Hash with the same lib the `user` module uses |
| `member_account_otp` | `accountId?`, `phone`, `purpose` (ACTIVATE / LOGIN / RESET / PHONE_CHANGE), `codeHash`, `expiresAt`, `attempts`, `consumedAt` | Separate from the staff `otp` table on purpose. Sent through the existing `sms` module with a new `SmsType.MEMBER_OTP` |
| `member_refresh_token` | `accountId`, `tokenHash`, `storeId`, `expiresAt`, `revokedAt` | Per-studio sessions |

Endpoints:

| Route | Behaviour |
|---|---|
| `POST /v1/member/auth/activate` | Body `phone, name, password`. Phone (canonical) must match ≥1 `store_member` with `ended=false` **and the name must match** that row — otherwise 404 `MEMBER_NOT_REGISTERED`. Creates `member_account` in `PENDING`, sends code |
| `POST /v1/member/auth/login` | `phone, password` → if valid, sends code. Lockout after N failures (`ThrottlerGuard` bucket + `lockedUntil`) |
| `POST /v1/member/auth/verify` | `phone, code, purpose` → on success returns member access + refresh tokens **for one studio** plus `studios[]` (every `store_member` row on that phone: `storeId`, store name, `publicMemberId`) |
| `POST /v1/member/auth/reset` | code first, then `newPassword` |
| `POST /v1/member/auth/switch` | `storeId` must be in the account's list → new token pair; anything else 403 |
| `POST /v1/member/auth/refresh`, `POST /v1/member/auth/logout` | standard |

Token: a **second Passport strategy** `member-jwt` with payload `{ typ: 'member', sub: accountId, storeId, memberId }`. `JwtStrategy` already rejects by `typ` (`jwt.strategy.ts:23`) — add the symmetric rejection so a member token can never pass a staff guard and vice versa. New `MemberAuthGuard` + `@MemberScope()` decorator returning `{ accountId, storeId, memberId }`. **No route in `member-api` reads `storeId` from body or query.**

### 3.2 Actor abstraction in the reservation services — R5, R9, R10, R11, D3

This is the only refactor of existing code, and it is small: the services take `user: User` only to call `resolveStoreId(user)` and to stamp `source` / `canceledBy`.

- Introduce `ReservationActor = { storeId, kind: 'DESK'|'MEMBER'|'CLOSURE', userId?, memberId? }`.
- `StoreReservationCreateService.create(actor, dto, clock, mode)`: `source` from `actor.kind` instead of the hardcoded `DESK` (`:306`); when `actor.kind === 'MEMBER'`, enforce `dto.memberId === actor.memberId` (the member can only book herself) and require `Idempotency-Key`.
- `StoreReservationCancelService.cancel(actor, id, dto)`: add the member branch next to `applyDeskCancelPolicy` (`:485`): before deadline → `canceledBy = MEMBER`, `remainingRestored = true` (nothing was deducted); after deadline → **400 `CANCELLATION_DEADLINE_PASSED`, no state change** — exactly what the enum doc specifies. The member DTO has no `waiveDeduction` / `acknowledgeLateDeduction` (the global `forbidNonWhitelisted` pipe will reject them anyway).
- `StoreReservationMoveService.move(actor, id, dto)`: member path adds "source session still before its cancel deadline" → else 400 `MOVE_DEADLINE_PASSED`. Everything else (capacity, quota, makeup carry) unchanged.
- Confirm and Absence stay desk-only; no member route.
- Keep the existing desk controllers unchanged by building `actor` from `user` inside them. All existing e2e specs (`store-reservation-*`, `store-waitlist-*`) must pass with zero edits — that is the acceptance test for this refactor.

### 3.3 Member read projections — F6–F11, F22–F25, R3, R4

Read-only routes under `MemberAuthGuard`, every query filtered by `(storeId, memberId)` from the token:

| Route | Source | Deliberately omitted |
|---|---|---|
| `GET /v1/member/me` | `store_member` self fields | `managerName`, health, consents detail |
| `GET /v1/member/memberships?all` | `membership` | prices, `deferredRevenueRemaining`, `serviceItemsSnapshot`, payroll basis |
| `GET /v1/member/classes?from&to&type` | `store_class_session` + `effectiveCapacity` + `minEnroll` | instructor payroll, room yield, owner notes. Returns `taken/capacity`, `mayNotRun`, `cancelDeadlineAt`, `arrivalWindow`, `spotLockAt` |
| `GET /v1/member/reservations?upcoming|past` | `store_reservation` + `membership_attendance` status | other members' rows |
| `GET /v1/member/requests`, `GET /v1/member/notifications` | new tables (§3.6, §3.7) | — |

**Opaque ids (D2):** add a `publicId CHAR(36)` (UUID v7) column with a unique index to `store_member`, `membership`, `store_reservation`, `store_class_session`, backfilled by migration. Member routes accept and return only `publicId`; the mapping happens inside `member-api`. Staff routes keep integers.

### 3.4 Member write routes — F12–F17, R5–R11

| Route | Calls | Rules added at this layer |
|---|---|---|
| `POST /v1/member/reservations` | `create(actor, {sessionId, memberId: actor.memberId, rejectIfFull:false})` | `Idempotency-Key` required; `source=MEMBER`; full → WAITLIST with position returned |
| `DELETE /v1/member/reservations/{id}` | `cancel(actor, id, {reason?})` | member branch of §3.2 |
| `POST /v1/member/reservations/{id}/move` | `move(actor, id, {sessionId})` | member branch |
| `DELETE /v1/member/waitlist/{id}` | cancel on a WAITLIST row | always allowed |
| `POST /v1/member/reservations/{id}/accept` | §3.5 | — |

Error codes surfaced unchanged from the services: `CLASS_SESSION_FULL`, `MEMBERSHIP_NOT_AVAILABLE`, `MEMBERSHIP_EXPIRED`, `WEEKLY_LIMIT_EXCEEDED`, `RESERVATION_ALREADY_EXISTS`, `CLASS_SESSION_STARTED`, plus the two new ones above.

**Idempotency:** extend `idempotency_record` with `actorKind` + `actorMemberId` (nullable) and make the unique key `(storeId, actorKind, actorId, idemKey)`. The interceptor already reads the header; only the key derivation changes.

### 3.5 Waitlist offer after the deadline — F15, R7

Today `promoteNextWaitlist` confirms the next member automatically when a seat frees (`waitlist-promotion.ts:42`). That is right before the cancel deadline and wrong after it (she would be booked into a class she can no longer leave for free).

- New table `waitlist_offer` (`reservationId`, `offeredAt`, `expiresAt`, `status OPEN|ACCEPTED|PASSED|EXPIRED`).
- In `promoteNextWaitlist`: if `now` is past the session's cancel deadline **and** the candidate reservation has `source=MEMBER`, create an `OPEN` offer and a member notification instead of confirming; a scheduled job expires offers after `store_settings.waitlistOfferMinutes` (new, default 30) and moves to the next in line. Desk-sourced waitlist rows keep today's behaviour.
- `POST /v1/member/reservations/{id}/accept` → confirms through the normal path; `…/pass` → closes the offer and promotes the next.

### 3.6 Presence — F19–F20, R13, R13a, R14

Reuse `store_attendance_checkin` (it is exactly "visit, not deduction"):

- Extend `CheckinSource` with `MEMBER_TAP` and `MEMBER_NUDGE`; add nullable `reservationId`.
- `POST /v1/member/reservations/{id}/presence` with `{ source }`: accepted only when the reservation is CONFIRMED/REQUESTED for today and `now` is inside `[startAt − arrivalOpenMin, startAt − arrivalCloseMin]`; else 400 `ARRIVAL_WINDOW_CLOSED`. Writes nothing to `membership_attendance`.
- New `store_settings` columns (nullable, like the rest): `arrivalOpenMin` (30), `arrivalCloseMin` (5), `spotLockMin` (15), `waitlistOfferMinutes` (30), `memberAppEnabled`.
- Desk list: the existing schedule/session screens read `store_attendance_checkin` already; show the source so the desk sees "here (app)".

Geofence / iBeacon live in the phone app; the server only sees the two sources.

### 3.7 Member notifications — F27–F29, R17, D4

The existing `Notification` / `PushSubscription` are staff `User`-keyed and Web Push; do not overload them.

- New tables: `member_notification` (`accountId`, `storeId`, `type`, `title`, `body`, `data JSON`, `readAt`, `dedupeKey` unique) and `member_device` (`accountId`, `platform`, `token`, `lastSeenAt`); `member_notification_setting` (`accountId`, `storeId`, `booked`, `studioChanges`, `dayBefore`, `hoursBefore`).
- Delivery: FCM (Android) / APNs via FCM. `backend/AGENTS.md` lists Firebase Admin as a dependency — confirm it is actually wired before relying on it; if not, add `firebase-admin` behind an env flag like VAPID is.
- Emitters, all post-commit like `WaitlistPromotionNotifier`: reservation create/cancel/move (member or desk), `closeSession` / session edit (studio changes), waitlist offer, request reply, scheduled reminders (1 day, 3 h before — the 3 h one is the cancel-deadline reminder), expiry (7 d, 1 d). One cron module in `member-api`.
- Read/unread is stored server-side here (the phone may cache it); SMS stays the fallback for members with no device.

### 3.8 Requests to the studio — F26, F30, R16

- New table `member_request` (`accountId`, `storeId`, `memberId`, `membershipId?`, `type EXTEND|HOLD|QUESTION`, `text`, `status WAITING|REPLIED|CLOSED`, `reply`, `repliedByUserId`, `repliedAt`).
- `POST /v1/member/requests` creates the row **and** a `store_task` with `type='MEMBER_REQUEST'`, `refKey=request.publicId`, `context.memberIds=[memberId]` — so it lands on the owner's existing to-do list with no new list to build. Duplicate open request of the same type for the same membership → 409 `REQUEST_ALREADY_OPEN`.
- Staff side: `POST /v1/store/tasks/{id}/reply` (new) writes `reply`, sets `REPLIED`, resolves the task, emits a member notification. The request never mutates `membership`; if the owner then holds, they use the existing hold route.
- **Extend needs a new owner-side operation** (`FLOWS.md` G1): today expiry moves only via unhold (+ days held) or refund, and expressing "extend 7 days" as a hold freezes the pass and is refused whenever she has a booking. Add `POST /memberships/{id}/extend { days | newExpiresAt, reason }`, owner-only (`STORE_MEMBERS` write), `audit_log` entry, reachable from the reply box. The member projection then shows the new expiry; the app never changes it.

### 3.8a Registration-side additions (`FLOWS.md` Flow 1)

- `SmsType.MEMBER_APP_INVITE`, sent once per phone when a membership is issued to a member with no `member_account`: store link + "create account with this phone and your name". Operational, exempt from marketing consent (G16).
- Desk action **Relink app account** (`POST /v1/store/members/{id}/app-account/relink`): updates `member_account.phone` after identity check, re-syncs linked `store_member` rows, audit entry, code to the new number (G2, G8).
- Anonymisation and enrolment-end also revoke the account's tokens for that studio and drop it from `studios[]` (G3, G4).
- Activation picks the newest non-ended `store_member` when several rows share phone + name (G6); the code always sends regardless of `smsOptOut` (G7).
- Member projection carries `type` (COUNT / PERIOD / TRIAL), a single `displayStatus` (ACTIVE · HELD · EXPIRED · VOID · REFUNDED · ENDED), and, per upcoming class, the pass that will be used (G9, G11, G15).

### 3.9 Reformer / spot — F13, R8

There is no seat position today; capacity is a count. Two options, decide before build:

| Option | Change | Trade |
|---|---|---|
| **A. Add positions (recommended if Capsule Barre numbers its reformers)** | `store_class.spotCount?` (null = unnumbered); `store_reservation.spotNo?` with unique `(sessionId, spotNo)` where status is active; member `PATCH …/spot` allowed until `startAt − spotLockMin`; desk can override | Additive migration; the capacity math stays count-based (`spotCount` must be ≤ effective capacity) |
| **B. Ship v1 without spot pick** | Nothing | Prototype screen S10 becomes "booked, seat assigned at the desk" |

The rest of the plan does not depend on this choice.

### 3.10 Profile — F32, S25

`PATCH /v1/member/me` updates `name` on the current studio's `store_member` row only; phone change goes through `PHONE_CHANGE` OTP and then updates `member_account.phone` and each linked `store_member.phone`, with an `audit-log` entry per row (the module exists).

### 3.11 Assistant — F31, R18

`POST /v1/member/assistant/interpret` `{ text }` → `{ intent, card }` where `card` is one of the five shapes the prototype renders (book / balance / schedule / cancel / request / help). v1 is a deterministic parser over the member's own data (today's sessions, memberships, open reservation, open requests) — no model call needed for these five intents; put an LLM behind a feature flag later only for phrasing, never for deciding. There is **no `act` endpoint**: the card's button calls the ordinary route from §3.4 / §3.8. That keeps every write on one audited path.

## 4. Security boundaries to prove in e2e (maps to BA A16, A18)

1. A member token on any `/v1/store/*` route → 401 (strategy `typ` check).
2. A staff token on any `/v1/member/*` route → 401.
3. Member token for studio A reading studio B's rows → 403 / empty, including after `switch`.
4. `storeId`, `memberId`, `canceledBy`, `remainingRestored`, `status` in any member body → 400 (whitelist pipe).
5. Cancel after deadline → 400 and the reservation row is unchanged; no `membership_attendance` row, `remainingSessions` unchanged.
6. Same `Idempotency-Key` twice on create → one `store_reservation` row.
7. Activate with a phone that is not a `store_member` → 404, no `member_account` row.
8. Presence outside the window → 400, no `store_attendance_checkin` row; inside → one row, `membership_attendance` untouched.
9. `remainingSessions` is identical before and after every member write in the suite; it changes only in the existing `payroll-class-confirmation` specs.

## 5. Migrations (all additive; `synchronize` stays false)

New tables: `member_account`, `member_account_otp`, `member_refresh_token`, `member_device`, `member_notification`, `member_notification_setting`, `member_request`, `waitlist_offer`.
New columns: `publicId` on 4 tables; `store_settings.arrivalOpenMin / arrivalCloseMin / spotLockMin / waitlistOfferMinutes / memberAppEnabled`; `store_attendance_checkin.reservationId` + enum values; `idempotency_record.actorKind / actorMemberId` + new unique key; optional `store_class.spotCount`, `store_reservation.spotNo`.
Numbering: next free global max in `backend/src/migrations/` (currently `1794000000153`), one lane per PR as `backend/AGENTS.md` prescribes.

## 6. Owner-side changes in the staff web (small)

1. **Settings**: the five new policy fields next to `cancelDeadlineHours`.
2. **Tasks**: `MEMBER_REQUEST` card with the member's text and a reply box (§3.8).
3. **Reservations / schedule**: show `source` (desk · app) and `canceledBy` (member · studio); show presence source.
4. **Members**: "App account" badge and a "reset app password" action (sends the reset code).
5. **Class**: `spotCount` if option A.

## 7. Order of work

| Step | Scope | Size | Done when |
|---|---|---|---|
| 1 | §3.2 actor refactor | S | All existing timetable e2e pass unchanged; desk behaviour byte-identical |
| 2 | §3.1 auth + §3.3 reads + `publicId` | M | A1, A2, A16, A18 pass; the app can log in and see both passes |
| 3 | §3.4 writes + idempotency | M | A3, A5, A8, A9, A10 pass; Cheongdam shows 2 after book and cancel on real data |
| 4 | §3.6 presence + settings + §6.1 | S | A12, A13 |
| 5 | §3.8 requests + §6.2 | S | A14 |
| 6 | §3.7 notifications | M | Booked / reminder / change / reply arrive on a device |
| 7 | §3.5 waitlist offer | M | A6, A7 |
| 8 | §3.11 assistant | S | Five intents return cards on real data |
| 9 | §3.9 spot (if option A) | S | A4 |

Steps 2–5 are what makes the owner stop typing bookings; 6–9 are what makes the app pleasant. Korean copy and the app-store build start after step 3 stops changing.

## 8. Not changing

The deduction path (`markAttended` → `recognizeOnAttended`), the eligibility/quota/capacity rules, the expiry cron, the desk controllers' contracts, the staff JWT, the `otp` table, the Web Push channel, payroll, billing, refunds. If a member feature seems to need any of these to change, the feature is wrong. (The one membership write added is the owner-only `extend` in §3.8 — a desk operation with audit, not a member one.)
