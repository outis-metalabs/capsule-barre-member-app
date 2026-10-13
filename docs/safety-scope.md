# Nari prototype: fixed safety scope (PR #10)

Status: accepted by the user on 2026-10-13. The prototype (`platform-app.html`) is a **demo**. Its safety handling is keyword and concept rules in the browser, with no AI model. It guarantees the concepts and the curated test set below, and nothing more. The production app will use a server-side AI classifier (see `docs/production-safety.md`).

## What the prototype guarantees

Every message, in the Ask and Book chats and at any length, goes through the safety check before small talk, FAQs, cancel/move or booking. Precedence: crisis > urgent > results claim > health > skin > normal.

| Category | Reply | Concepts covered (EN, VI with and without tone marks, KO) |
|---|---|---|
| Crisis | Fixed caring copy (Version A, no phone number, staff alerts off). Overdose adds a "get medical help" card | Suicide or self-harm said outright or indirectly; wanting to stop living or hating being alive; wanting to sleep forever or not wake up; methods (hanging, rope, noose, pills, jumping, bridges, roofs or ledges, cutting, burning, deliberately scratching until it bleeds); goodbye notes and "last message"; "tonight I do it" or "I've made up my mind"; giving belongings away; someone else (a child, partner or friend) wanting to die |
| Crisis check-in | Crisis copy plus "Are you okay right now?" with "I'm not okay" or "I meant something else" | Risk words outside a clear service phrase (die, disappear, note, bridge, jump, burn, cut, meds; chết, biến mất, tuyệt mệnh; 죽, 유서, 옥상, 긋) |
| Urgent | "Stop and get medical help right away" card | Breathing, choking, chest pain or pressure, collapse or unresponsiveness, seizures, stroke signs, heavy bleeding, allergic reactions, head injury with vomiting or confusion, heatstroke, labour or waters breaking, bleeding in pregnancy, swallowed batteries, magnets or a fistful of pills, electrocution, broken or deformed bones (including "gay chan" without tone marks), falls from a height, numb legs after a fall (never books), worst-ever headache, emergency-number requests |
| Health | "See a doctor or your instructor" and a "Still book it (after checking)" chip. Never starts a booking by itself | Pregnancy, injuries (including a pinched nerve), conditions (heart murmur or heart disease, hip/knee replacement, shingles, sunburn blisters, vertigo, pacemaker, hernia, varicose veins, diabetes and others), medication, fever, a child's illness, allergies |
| Skin | Dermatologist or therapist line plus a consultation chip | Rashes, hives, breakouts, moles that change, infected ingrown hairs, blisters |
| Results claim | "I can't promise results". Health-condition cures also get the medical line | Whitening, weight or size loss, "forever" or "guaranteed", curing or fixing a condition (arthritis, scoliosis, migraines) |
| Normal | Books or answers | Bookings (including next to everyday idioms like "dead tired", "to die for", "legs are dead", "killing me", "dying for", "chết mê", "mệt muốn chết", "đẹp muốn xỉu", "더워/좋아 죽겠어"), FAQs (hours, open late, payments incl. MoMo, parking, passes), small talk |

Backstop: a permanent **"Hurt or in danger? Get help now"** bar sits above every Ask/Book input and opens the urgent or crisis reply in two taps. A message that Nari doesn't understand gets a neutral question with a "Someone is hurt / I need help" chip, never booking chips. The You tab shows "Demo safety: prototype only" in EN, VI and KO.

## Curated test set (regression, must stay 100%)

All reviewer sets to date, run in both chats:

| Set | Source | Runs (inputs × Ask and Book chats) |
|---|---|---|
| f135322 safety | `pr10-f135322/safety.py` | 304 |
| 6d43d31 unseen | `pr10-6d43d31/unseen_cases.py` | 430 |
| 597fd4a fresh | `pr10-597fd4a/fresh_cases.py` | 460 |
| 6052b80 fresh (R5) | `pr10-6052b80/fresh_cases.py` | 460 |
| 7b77a95 R6 | `pr10-7b77a95/r6_cases.py` | 460 |
| 7b77a95 R7 | `pr10-7b77a95/r7_cases.py` | 460 |
| Designer held-out sets | `pr10fix6/held5.json`, `held6.json` | 430 + 446 |
| Crisis acceptance criteria (AC1–AC7, AC9, AC10) | `pr10fix7/ac.py` | 18 crisis threads × 4 turns, plus idiom negatives |
| In-app selfTest (595), flows (160), false-positive sweep (760 normal), long messages, Get help bar, UI sweeps at 320 and 390px | `pr10fix6/old/`, reviewer `reg/` | — |

A legacy harness label (6d43d31 expected "urgent" for "I want to kill myself", "tôi muốn tự tử" and "죽고 싶어") is superseded by the crisis category. Those inputs now get the crisis reply, which is the intended behaviour, and "tắm trắng" gets the no-promise line. These 8 runs are counted as correct.

## Crisis reply: acceptance criteria
- AC1 to AC6, AC9 and AC10 are enforced by the app and checked by `ac.py`.
- AC7: crisis escalations are logged in memory (`SAFETY_LOG`). Each entry has a timestamp, member, store and category (plus an overdose flag), and never the message text. No staff alert is sent (`CRISIS_STAFF_ALERT = false`), and the log isn't shown in the member app. Restricting access to authorised staff needs a server, so it's covered in `docs/production-safety.md`.
- AC5 follow-up line (after a crisis reply, when the member doesn't ask to book): PO-approved fixed text in `CRISIS_FOLLOWUP`. VI and KO still need native-speaker review.
- AC8 (tel: link) is dropped.

## Out of scope (not guaranteed)

- **Phrasing that isn't in the concept list or the curated set.** Across seven rounds the catch rate on fresh, unseen crisis wording was 55–80%. The prototype doesn't claim to catch new phrasings; the Get help bar is the backstop.
- Sarcasm, idioms that aren't in the list above, code-switching inside a single word, typos that break a keyword, and other languages.
- Context across several messages (each message is checked on its own).
- Known accepted quirks: "my feet are killing me" with no other words starts a foot-massage booking (harmless). Some idioms said with no service word get the neutral "didn't get that" question, not a booking.
- Crisis hotline numbers: not shown (user rule). VI and KO crisis copy still needs native-speaker review before release.

## Accepted misses
None. Every curated set passes at this commit (see the PR comment for numbers).
