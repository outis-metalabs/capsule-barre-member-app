# AICC Member App — source analysis

**Date:** 2026-10-08  
**Scope:** member-facing product only; `aicc-center` remains the admin system and system of record.  
**Evidence:** `aicc-center` at `260d9741e126303e00fbc8e657b80b3a0473f89e`, Jay's `aicc_mvp` documents, `memberApp.pdf`, and `브로셔.pdf`.

## Executive conclusion

`aicc-center` is already a serious staff/store operating system. It owns the records the Member App needs: member identity, enrollments, membership balances, classes, sessions, reservations, attendance, notices, tasks, money, and audit-sensitive rules.

It is **not** currently a member backend. Its authentication subjects are `User` accounts for staff; `store_member` is a separate entity and has no member-facing principal. Its `/store/*` routes are staff-scoped and must not be opened to members. There is no public member login, public member serializer, public class/reservation façade, member notification ownership, or member support ownership in this checkout.

The correct architecture is therefore:

```text
Member App (new aicc-crm repo)
        │ generated client, fixed aicc-contracts version
        ▼
Public member façade in aicc-center
        │ member identity + store scope + redacted response
        ▼
Existing services (one booking / membership / attendance rule set)
        ▼
MySQL system of record owned by aicc-center
```

The biggest work is not drawing mobile screens. It is creating a safe member principal and a public façade without creating a second ledger or a second reservation implementation.

## 1. Repository boundary and architecture

### `aicc-center` owns

Root `CLAUDE.md` explicitly assigns these to this repository:

- member master and enrollment
- membership products, remaining sessions, expiry, holds, transfers, cancellation
- class definitions and materialized sessions
- reservation creation, confirmation, cancellation, movement, waitlist
- attendance confirmation and session deduction
- payment, refund, deferred revenue, payroll, expenses, bookkeeping
- store tasks and operational notices

The root guard explicitly excludes member/instructor app screens, member login/signup, and React Native/Expo code. The Phase 2 plan assigns those to a separate `aicc-crm` repository.

### Current stack

- Backend: NestJS + TypeScript + TypeORM + MySQL
- Staff frontend: Next.js Pages Router
- Auth: Passport/JWT for `User` subjects
- Storage/notifications: MinIO, SMS, mail, push infrastructure
- Staff routes use the global `/v1` prefix and store-scoped guards

### Existing staff entry points

| Capability | Current evidence | Current boundary |
|---|---|---|
| Member master | `backend/src/modules/store-member/store-member.controller.ts:78-550`; `services/store-member.service.ts`; `services/store-member.serializer.ts` | Staff `/store/members` only |
| Membership ledger | `backend/src/modules/membership/membership.controller.ts:62-218`; `membership.service.ts`; `membership-view.serializer.ts` | Staff; balances and revenue are server-owned |
| Classes/timetable | `backend/src/modules/timetable/controllers/timetable.controller.ts`; `store-class*.controller.ts`; `services/store-class-open.service.ts` | Staff/store scope |
| Reservation lifecycle | `backend/src/modules/timetable/controllers/store-reservation.controller.ts`; `services/store-reservation-{create,cancel,confirm,move,list}.service.ts` | Staff write permission today |
| Attendance | `membership/services/membership-attendance.service.ts`; instructor confirmation flow | Staff/instructor; this is the only balance-spend boundary |
| Tasks | `backend/src/modules/store-task/` | Owner/operator only |
| Notifications | `backend/src/modules/notification/` | `User`-scoped, not `store_member`-scoped |
| Support | `backend/src/modules/support-ticket/` | `User` owner/role model, not member-ready |
| Staff UI | `frontend/src/pages/store/{members,classes,schedule,lessons,tasks,...}` | Admin/staff web app |

## 2. Domain rules the Member App must preserve

### Balance and money

1. A reservation does **not** deduct a session.
2. The authoritative deduction occurs when attendance becomes `ATTENDED` through the attendance/membership ledger.
3. `PERIOD` memberships do not burn session counts in the same way as count-based memberships.
4. Money is integer KRW and remains server-calculated.
5. The app never calculates remaining sessions, refunds, payroll, deferred revenue, or pass expiry.

Relevant evidence: root `CLAUDE.md` domain rules; `membership/CLAUDE.md`; `membership/services/membership-attendance.service.ts`; `membership/services/deferred-revenue.service.ts`.

### Reservation lifecycle

Current `StoreReservation` is `store_reservation` with a unique `(sessionId, memberId)` constraint. It stores `storeId`, `sessionId`, `memberId`, chosen `membershipId`, status, cancellation metadata, tri-state `remainingRestored`, and a source enum (`DESK`, `MEMBER`, `INSTRUCTOR`).

Current implementation status values are:

- `REQUESTED`
- `CONFIRMED`
- `ATTENDED`
- `CANCELED`
- `NO_SHOW`
- `WAITLIST`

The public contract draft uses `CANCELLED_BY_MEMBER` / `CANCELLED_BY_STORE` naming. Before implementation, `aicc-contracts` must define the public projection and map it to the internal enum rather than exposing internal names by accident.

Cancellation is an update that preserves history; it is not a delete. `canceledBy` is derived from the authenticated actor, not accepted from the request body. Deadline, membership eligibility, capacity, weekly quota, and conflict rules are server decisions.

### Tenant and privacy boundaries

- Resolve store scope from the authenticated principal; never trust a `storeId` from URL/body/query.
- Member access must be “this member in this studio,” not “any row with this integer member id.”
- Internal integer IDs must not be exposed if the public contract follows the existing `API_CONTRACT_V1.md` requirement for opaque public IDs.
- Member responses must use explicit allowlists. The draft contract exposes member name/contact, pass name/remaining/expiry, instructor profile/schedule, and class name/time/capacity/instructor; it excludes owner notes, churn/risk scores, cumulative paid amount, payment method, discount, deferred revenue, instructor rates, and room economics.
- Health data, anonymization, PIPA deletion, and staff operational notes remain separate from the member app's first release.

## 3. What is present vs absent

| Member requirement | Present in admin repo | Gap for Member App |
|---|---|---|
| Existing member record | `store_member` CRUD and serializer | No member identity/token/linking model |
| Phone/profile | Staff detail and consent APIs | No `/me` projection or verified self-edit flow |
| Current/previous passes | Membership ledger and view serializer | No member-scoped read façade |
| Class availability | Timetable/class/open-class logic | No member-safe projection |
| Group/private booking | One robust reservation service; `ReservationSource.MEMBER` exists | No member-authenticated caller or idempotency façade |
| Schedule/history | Staff reservation list | No member-only list/detail projection |
| Cancel/change | Staff cancel/move services with deadline/history rules | No member actor and contract-aligned public action |
| Attendance/spend | Instructor/staff flow | Correctly not a member action |
| Push/in-app alerts | Notification infrastructure for `User` | Member is not a `User`; app-owned read state and principal mapping required |
| Owner escalation | Store task system | No member-safe assistant endpoint or task creation adapter |
| Support | Authenticated User support tickets | No member owner/author model |
| App settings | None as member domain data | App repo can own local settings/read state |
| Payment | Admin payment/refund | Explicitly out of Phase 2 member scope |

## 4. Public contract status and corrections

`aicc_mvp/00_MASTER/API_CONTRACT_V1.md` is a design source, not an implemented API. It reserves:

- `POST /auth/member/login`
- `POST /auth/token/refresh`
- `GET /me`
- `PATCH /me/profile`
- `GET /me/memberships`
- `GET /me/memberships/{id}/history`
- `GET /classes`
- `GET /classes/{id}/slots`
- `POST /reservations`
- `DELETE /reservations/{id}`
- `GET /me/reservations`
- assistant interpret/act/thread
- push-token and notifications

Important implementation decisions still required:

1. **Member authentication:** Jay's RFP says phone verification; the 2019 `memberApp.pdf` shows phone + password, signup OTP, forgot password, and password reset. The proposal should modernize this to phone verification/OTP first, not silently revive the old password flow. The contract needs the exact challenge, rate-limit, session, and recovery behavior.
2. **Multi-studio switching:** the RFP requires a store-switch UI, but the contract's every-request `storeId` scope rule does not define a switch endpoint. Choose one explicit model before coding: an account-level identity with a server-issued scoped token per selected studio, or a single aggregate token with server-resolved active studio. The client must never choose arbitrary store IDs.
3. **Cancel shape:** the current staff API uses `POST /store/reservations/:id/cancel`; the public contract draft says `DELETE /reservations/{id}`. Keep the public contract as the decision point and map it to the existing cancellation service. Do not invent a second cancel implementation solely to match a UI.
4. **Public IDs:** the contract requires UUID v7/opaque IDs while current internal entities use integer PKs. Decide the public identifier strategy before exposing routes.
5. **Notifications:** a member is not currently a `User`. Do not insert member notices under a staff `user_id`. Add a principal/link table or a member notification projection deliberately.
6. **Assistant escalation:** current tasks are owner-facing and use durable task uniqueness/audit rules. `ESCALATED` must create/reopen a task through the existing task service, not a new free-form inquiry table.

## 5. Historical reference analysis

### `memberApp.pdf` — Pilagram, 2019, 51 mobile mockup pages

Useful product signals:

- onboarding/login is phone-centric
- signup uses phone verification and consent
- home summarizes the current pass, studio schedule, quick booking, and today's schedule
- “More” contains schedule, passes, alerts, center introduction, profile/phone, notification settings, terms, and logout
- the member experience is fundamentally schedule + pass + booking, not accounting

Do not copy directly:

- old password-based signup/reset screens as the default auth model
- the old visual language and 2019 copy
- center-admin and instructor screens into the member app
- any old data model assumptions that conflict with the current SoR and balance rules

### `브로셔.pdf` — Pilagram business brochure, 2019, 14 pages

The business pain points are still relevant: frequent schedule changes, duplicate/missed bookings, complicated passes, member contact administration, attendance friction, revenue visibility, and instructor-payroll effort. The brochure positions the system as an easy operating layer for studio owners and promises member booking/change plus chatbot support.

Use this as positioning, not as a requirements list. The current AICC plan deliberately narrows scope and keeps revenue/payroll/admin records in the center system. Beacon auto-attendance, member body charts, historical medical-style records, and in-app payment should not be smuggled into the first Member App because they are either out of Phase 2 or privacy/domain-risk heavy.

## 6. Proposal UI recommendation

The proposal uses an **editorial studio companion** direction rather than copying the old blue/pink Pilagram mockups:

- warm paper background and dark ink for a premium wellness/editorial tone
- clay action color for booking, moss for healthy/active states, amber for expiry
- Fraunces display typography + Outfit UI typography
- a phone frame beside an implementation note so Jay can see the member value and the admin-system consequence at the same time
- top story rail: sign in → studio switch → home/pass → book → confirmation → schedule → cancel → alerts → assistant → profile

The memorable interaction is the **two-studio switch**. It demonstrates that one member can see two scoped ledgers without letting the app choose an arbitrary store.

The proposal deliberately demonstrates the most important system truth: booking and cancellation leave the balance at 2; attendance is the event that spends a session.
