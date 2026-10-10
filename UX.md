# Capsule Barre — Member App UX

Daylight studio companion for Mina Park, Thu 8 Oct 2026. English. Prototype: `app.html`.
Accepted by three independent UX reviews (round 3). Polished 9 Oct 2026 with the mobile-app-ui-design pass.

## Structure

Four tabs. Bell and menu in the header. Nothing else competes.

| Tab | Job | What you notice first |
|---|---|---|
| **Today** | The class, or how to get one | The time, in Bebas Neue |
| **Book** | Group / Private, week strip, this studio's list | Open slots, by time |
| **Schedule** | Upcoming, waitlist, then history | A timeline, not a list of identical cards |
| **You** | Pass, alerts, ask, studios, log out | Remaining sessions as a number |

Header: studio pill (Geumho ▾ / Cheongdam ▾), remaining chip, bell, menu. The menu repeats You's rows for people who look up before they look down.

## Account

Two screens, then in.

1. **Form** — Log in / Create account toggle. Create: name, phone, password, confirm, terms. Log in: phone, password, Forgot link. Terms and Privacy links sit outside the checkbox label.
2. **Code** — six boxes, auto-advance, paste fills all six, backspace clears the previous box. `000000` is wrong, by design.
3. **Forgot** — code first, then new password + confirm, then in.

Unknown phone is refused on the form, before any code is sent.

## The one evening

1. **Geumho, 9:41am** — 8 of 20, until 12 Nov. No class today. One card suggests Cheongdam 7:00pm; it is a suggestion, not a booking.
2. **Switch to Cheongdam** — 2 of 10, until 14 Oct. Separate balance, separate session.
3. **Book** — Thu 7:00pm Barre, Hana Lee, 6 of 8. "Free until 4:00pm" and "Here from 6:30" on the row. 8:00pm is full: "You'd be 2nd." Sat 9:00am Kids Barre: "May not run."
4. **Reformer** — six pads, two taken, no names. Yours until 6:45pm.
5. **Today, booked** — time hero, teacher, reformer. Now **2** / After class **1**. Meter does not move. Change time and Cancel free sit at the bottom.
6. **Lobby, 6:40pm** — the clock control outside the phone. "I'm here" appears and takes the thumb zone. With location allowed, a notification drops in instead and asks. One tap either way, one rise, "You're here · see you at 7." Still 2 left.
7. **Ask** — "Can I extend my Cheongdam pass?" goes to the studio. The screen still says 14 Oct.

Change time is one move (Thursday 7:00 → Saturday 10:00), never cancel + rebook.

## Arrival nudge

Opt-in, from the morning card: "Get a nudge when you arrive." One system prompt. Then, only 6:30–6:55 with a booking, when the phone senses the studio it sends one notification: **You're at Cheongdam. Say you're here?** — I'm here / Not yet. The tap on the notification is the check-in. The phone asks; it does not decide.

Trigger is a geofence in v1 (no hardware). An iBeacon can replace it in v2 if "close" turns out to mean the cafe next door. Location off → the in-app tap. Neither path spends a session.

## Ask (assistant)

Jay's request, 9 Oct. A text field at the bottom, four example chips when empty. Every answer is one card that names its source — "From Cheongdam's schedule", "From your passes" — with at most two buttons. The first button runs the normal flow: book opens the reformer pick, cancel opens the confirm sheet, extend opens the request. Balance and what's-on cards are read-only. Unknown input gets a help card. The assistant never books, cancels, or edits a pass on its own; the tap on the card is the action, and that tap calls the same API as the button elsewhere.

## Visual rules

- Paper `#f3f2ee`, ink `#12110f`, one accent: oxidized red `#b8422e`.
- The accent appears on the primary button, the after-class number, and the meter. Nowhere else.
- IBM Plex Sans for UI, IBM Plex Mono for numbers, Bebas Neue for the class time only.
- Four sizes: 28 / 15 / 12, plus the 96px time. Two weights: 500 and 700.
- 8-point grid. Tap targets ≥ 44px. Primary action in the thumb zone; a disabled button is never parked there.
- Soft shadows tinted with the accent on the balance card only. Everything else is flat on paper.
- Buttons, one system: **primary** = oxidized red fill, one per screen (Book, Use reformer, Move, Log in, I'm here). **Secondary** = outline on paper (Change time, Cancel free, Keep Thursday, Log out). **Tertiary** = red text link (Back, Forgot password). **State** = green fill, not tappable (You're here). **Selection** = ink fill (chosen reformer, chosen day, Group/Private). Ink is never an action colour. In a destructive sheet the safe choice is the primary ("Keep it" red, "Cancel class" outline). The Ask AI thread is the one exception to "one primary per screen": each card carries its own red action, because the card is the screen.
- Values outweigh labels: **8** / 20, not "Pass: 8 of 20."

## Two moments

- **Booked** — a toast, "See you at 7," and the Today tab. No confetti.
- **You're here** — the green bar rises once and stops. The meter stays where it was.

## Refused in the UI

Shop, reviews, signup for strangers, payment, streaks, free chat, bluetooth diagram, a seat map with names, fake iOS chrome, wellness beige, purple gradients, Inter/Roboto, lecturer copy inside buttons, and any sentence about sessions being spent — that truth sits once in the side note, outside the phone.
