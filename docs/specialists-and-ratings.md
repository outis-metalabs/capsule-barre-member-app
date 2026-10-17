# Specialists, classes and ratings: how a member chooses

Design note, 2026-10-17. Question from the owner: "In a store, the member needs to know which specialist is better, by rating or by booking success. Some stores have no specialist selector. A gym has public and private classes. Give the best UI and UX."

## 1. What exists today

- Stores have a `kind`: `class` (timetable with a teacher per class), `appt` (salon, skin, spa with a `staff` list), `rental` (courts). The Book sheet shows a "Teacher / Therapist / Staff" chip row with "Anyone" when a store has more than one person.
- Ratings are **store-level**: after an attended visit the member rates the visit (stars, tags, note). The public average shows on Discover once a store has 5 ratings. The staff member is recorded on the rating but is only visible to the store owner.
- Nothing tells a member who Yuna or Linh is, how many people they have served, or whether people come back to them.

## 2. Four store shapes, one rule

| Shape | Examples | What the member picks | Who is shown |
|---|---|---|---|
| **Class, public** | barre, yoga, reformer | a time on the timetable | the teacher of that class, as information, not a choice |
| **Class, private** (1:1 or 1:2) | PT, private barre, private yoga | a teacher first, then a time | the teacher, as the product |
| **Specialist appointment** | hair, skin, spa, nails | a service, optionally a person, then a time | the person, as a choice with "Anyone" first |
| **Court / room rental** | pickleball, tennis, futsal, practice rooms | a date, a time, then a **court number** when courts differ | the courts, as a choice with "Any court" first; no people |
| **No selector** | a one-person shop, a spa that assigns on arrival, identical rooms | a time | nobody; the store assigns |

The rule: **a person is shown only where choosing them changes the booking.** Public classes and resource stores never show a selector. The teacher name on a public class is a label on the slot, not a step.

Stores declare this in their setup, not the app: `staffChoice: "none" | "optional" | "required"` and, for classes, a `private: true` flag on the class type. The app renders the right flow from that. A store with `staffChoice: "none"` never shows people, and ratings there stay at store level.

## 3. What "better" means, and what we may show

Members ask "who is good?". Three honest signals, in order of trust:

1. **Rebook rate.** Of members who had this person once, how many booked them again within 90 days. This is the strongest "they were worth it" signal and cannot be gamed by a single review.
2. **Visits.** How many confirmed visits this person has had on the platform (not bookings: no-shows and cancels do not count). Shown as a rounded number: "120+ visits".
3. **Rating.** Average stars from post-visit ratings, shown only with 10 or more ratings in the last 12 months. Below that, "New here" and no number.

Why not raw booking counts: a long-serving person always wins on volume, a new good one never catches up. Rebook rate and a recency-weighted rating let a new person surface in weeks.

**Guard rails** (Korea: a public score on a named worker is a labour and privacy issue):
- The store owner turns person-level display on per person; it is off by default. The person can ask for it to be off.
- Stars show only at 10+ ratings; tags show only the top three positive tags ("꼼꼼해요", "설명이 좋아요"); free-text notes never show on a person, only to the owner.
- The rating sheet asks about the **visit**; the person is attributed from the booking, never chosen by the rater.
- The page never ranks people against each other. Cards are ordered by availability (soonest free first) with "Anyone" first, never by score.

## 4. UI

### 4a. Store page, "Team" section (appointment stores and private classes)

Between About and Policies. Horizontal cards, 150 px wide, scroll-snap, "Anyone" is not a card here.

```
Team · 3 people
┌───────────┐ ┌───────────┐ ┌───────────┐
│  (photo)  │ │  (photo)  │ │  (photo)  │
│ Linh      │ │ Khôi      │ │ Mina K.   │
│ Senior    │ │ Stylist   │ │ Colour    │
│ colourist │ │           │ │ specialist│
│ ★4.8 (64) │ │ New here  │ │ ★4.6 (23) │
│ 82% rebook│ │ 40+ visits│ │ 71% rebook│
│ Free 14:00│ │ Free 11:30│ │ Free Thu  │
│ [ Book ]  │ │ [ Book ]  │ │ [ Book ]  │
└───────────┘ └───────────┘ └───────────┘
```

Tap a card: a sheet with photo, role, years, specialties ("balayage, curly hair"), languages, the three signals with their definitions in one line each, the top three tags, and **Book with Linh** which opens the Book sheet with the person preselected. No reviews text.

### 4b. Book sheet step 2 (appointment store)

Replace the name chips with person rows. "Anyone" is first and preselected, because it gives the soonest time.

```
Who
● Anyone · soonest, the store assigns        14:00 today
○ Linh · Senior colourist · ★4.8 · 82% rebook   Thu 11:00
○ Khôi · Stylist · New here                      15:30 today
```

Each row carries the person's next free time for the chosen service, so the trade-off (sooner vs. the person you want) is visible before the day picker. Picking a person filters the slots. The confirm sheet names the person, or says "Assigned by the store on arrival" for Anyone.

### 4c. Public class (timetable)

No person step. The slot row already says "07:00 Barre · Yuna". Add a small tap target on the teacher name that opens the same person sheet (read-only, no Book button inside, since the time is the choice). The timetable can be filtered by teacher from a chip only when the store has set `staffChoice: "optional"`.

### 4d. Private class (gym PT, private barre)

Private classes live in the Services list as their own rows: "Private barre · 1:1 · 50 min · ₩80,000 · from Yuna or Jiwoo". Tapping opens the Book sheet with the Team rows first (section 4b), then the day and the person's open times. The member cannot book "Anyone" for a private class if the store sets `staffChoice: "required"`.

### 4e. No selector

Resource stores and stores with `staffChoice: "none"` show nothing about people. The store page has no Team section; the confirm sheet says "Therapist assigned by the store". Their ratings stay at store level, exactly as today. The rate sheet asks only "How was your visit?" with no name.

### 4f. Court stores: picking the court number

Courts are resources, not people, but members still want to choose: outdoor vs indoor, lights, surface, the court next to the clubhouse, "our usual court". Today the Book sheet folds court / length / players / paddles into one collapsed options line with "Any court" chips. That hides the choice. Proposal:

```
Sat 19 Oct   [Today] [Tomorrow] [Sat] [Sun] …
18:00 · 90 min                         3 of 4 courts free
19:30 · 90 min                         1 of 4 courts free
21:00 · 90 min                         Full
─────────────────────────────────────────────────────
18:00 · which court?
● Any court · the club assigns, cheapest                ₩30,000
○ Court 1 · outdoor · lit · near the desk               ₩30,000
○ Court 2 · outdoor · lit                               ₩30,000
○ Court 3 · indoor · ac                              +₩4,000
   Court 4 · indoor · ac · taken 18:00–19:30
```

- **Time first, then court.** Members think "Saturday evening" before "Court 3". Each time row says how many courts are free, so a full slot is never a surprise after picking a court.
- **Court rows appear under the chosen time**, free ones selectable, taken ones greyed with who-when ("taken 18:00–19:30"), never hidden, so the member sees why. "Any court" is first and preselected; it is also the cheapest when courts carry a surcharge.
- **Courts carry attributes** the store sets: indoor/outdoor, lights, surface, a surcharge, a photo, a note ("near the desk"). Identical courts show as plain numbers.
- **Usual court.** If the member booked the same court three times, that court's row says "your usual" and is preselected instead of Any.
- **Court-first entry** also exists for members who care: the store page lists courts as cards (photo, attributes, "next free 18:00"); tapping a card opens the Book sheet with that court preselected and only its open times.
- **No selector variant.** A store with identical courts sets `courtChoice: "none"`: the time rows stay, the court section never appears, and the confirm sheet says "Court assigned on arrival" with the number shown on the check-in code once the club allocates it.
- **Confirm and after.** The confirm sheet, success sheet, My bookings row and check-in code all show the court number ("Court 3 · indoor"). A court change by the club sends a notification ("Your 18:00 game moved to Court 2, same price").
- **Rating.** Court stores rate the visit and, optionally, the court ("lights were dim") as a tag the club sees; no public per-court score.

Data per court: `{ id, n, indoor, lit, surface, surcharge, photo, note }`; booking carries `court` (id or null for assigned); `courtChoice: "none" | "optional"` on the store.

### 4g. Discover

Unchanged: store-level rating and from-price. One addition for appointment stores: "3 specialists" in the meta line, so a member knows a choice exists before opening.

### 4h. Cici

"린 선생님 평점 어때?" answers with the three signals in one sentence and a "린으로 예약" chip. "누가 제일 잘해?" answers "순위는 보여주지 않아요. 가장 빨리 되는 분과 재예약률이 높은 분을 알려드릴게요" and lists two people.

## 5. Data

Per person: `{ id, n, photo, role, since (year), tags: ["balayage"], langs: ["ko","en"], display: false }` on the store. Per person stats, computed by the platform from confirmed visits and ratings: `visits`, `rebook90` (0–1), `avg12m`, `nRatings12m`, `topTags`. A rating row gets `staffId` from the booking at attend time. Rebook: a later confirmed visit with the same `staffId` by the same member within 90 days of a visit.

Thresholds: stars at `nRatings12m ≥ 10`; rebook rate at `visits ≥ 20`; otherwise "New here". Numbers are rounded (visits to 10s, rebook to whole percent).

## 6. What the prototype shows (sample data, implemented 2026-10-17)

- **Store setup flags** (`staffChoice`) on every appointment store and the class stores: the six appointment stores and Capsule Barre are `"optional"`; Namu Spa (`moc`) is `"none"` (assigns on arrival); Bloom Yoga Loft is `"none"` because it has one teacher. Profiles per person: role, since-year, specialty tags, languages, `display`, and sample platform stats (visits, rebook, avg, n). Live data is added on top: confirmed visits with that person and ratings attributed from the booking (`inst`, else the visit stars).
- **Private class**: Capsule Barre has `pbarre` (Private barre · 1:1 · 50 min · ₩80,000) as its own service row with a cap-1 schedule per teacher. The Book sheet shows the teacher rows first with no "Anyone", no times until a teacher is picked (then the day jumps to their next free day), rows say "1:1" instead of a spots count, a taken 1:1 time is simply not offered (no waitlist), the group pass never applies, the confirm sheet says "Format · 1:1".
- **Team section** on the store page (between About and Policies): cards ordered by soonest availability, stars only at 10+ ratings ("New here" below), rebook rate only at 20+ visits (else "N+ visits"), a Book button per person. The person sheet carries role · years, languages, tags, the three signals with their one-line definitions, the "no written reviews, no ranking" line, and "Book with <name> · next time". A `none` store shows one "Assigned by the store on arrival" line instead.
- **Book sheet** person rows: "Anyone · soonest, the store assigns" first and preselected, then each person with role · signals · next free time for that service. Picking a person filters the slots. Confirm, success, My bookings: the person's name, or "Assigned by the store on arrival" at a `none` store.
- **Discover** meta line: "N specialists" for appointment stores with a choice.
- **Cici**: "소라 평점 어때?" gives the three signals in one sentence plus "I don't rank people" and a Book-with chip; "누가 제일 잘해?" at a named store refuses to rank and offers two people (soonest, then highest rebook, else highest rating / the newcomer) with Book chips; with no store named it asks which place and lists only stores where a choice exists.
- **Court stores** (`tests/v3_courts.py`): time rows with "N of 4 courts free", court rows with attributes and surcharge under the chosen time, court-first entry from the store page, Rally Court Club as the `courtChoice: "none"` example, court number on confirm, success, My bookings and the check-in code, the "moved to Court 2" notification.
- Tests: `tests/v3_team.py` (40 checks, EN and KO).
- Not in the prototype: `staffChoice: "required"` for private classes (every private class in the sample requires a teacher anyway), the teacher-name tap target on public timetable rows (§4c), per-court rating tags (§4f), the store owner's per-person display switch UI.

## 7. Open questions for the owner

1. Does a person's rebook rate belong to them when they move to another store on the platform? (Proposal: yes, it is the person's, shown only where they currently work.)
2. May the store sort its Team by its own preference, or is availability order a platform rule? (Proposal: platform rule, availability order, no paid placement.)
3. Private classes: fixed price per person, or does the teacher set it? (Proposal: store sets per class type; a per-teacher surcharge is a v2.)
