# Member app — daily mission design

Two independent designers. This is what they agreed, with one correction: Hana never says she marks attendance. The studio does. Cheongdam stays at 2 until then.

## The feeling

Opening the app starts today's level. One board. One next tap. Hana says one short line. Everything else is the clubhouse.

## Today's board — 4 steps

| Step | Player sees | Button | Clears when | Pass |
|---|---|---|---|---|
| 1 Pick | No class yet | Book 7:00 | Seat is held | Still 2 |
| 2 Arrive | Booked. Check-in opens 6:30–6:55 | I'm here | She taps, or taps the "you're close" nudge | Still 2 |
| 3 Share here | Card: "I'm at Cheongdam · 7:00 Barre · Hana Lee" | Share / Not now | Card sent or skipped | Still 2 |
| 4 Clear | Only after the studio marks attended. Card: "Done · Barre with Hana" | Share / Skip | Card sent or skipped | Then 1, shown quietly, not as a prize |

Reformer pick sits inside Pick, not as its own life. If the class has numbered reformers, she locks one before the seat is held. Streak goes up only when step 4 is cleared or skipped. Booking does not add a day.

Hana, one line:

- Before pick: "Tonight's board is open."
- Before arrive: "See you at 7."
- After clear: "Board cleared. Rest well."

## Where things live

**On the quest** (the game): Today's board, book, reformer, waitlist ask, change time, cancel, I'm here, nearby nudge, share-here card, share-clear card.

**In the clubhouse** (the rest): Schedule, pass, studio switch, alerts, talk to Hana, extend or hold request, profile, account.

Tabs: Board · Schedule · Pass · Alerts · Me. Board is the default. Clubhouse screens never show a louder button than the quest button on the board.

## Screen map

| Screen | Why | One button | Next |
|---|---|---|---|
| Create | One form, then a code. Phone must already be on a contract | Join | Board |
| Log in | Phone, password, code | Enter | Board |
| Forgot | Code, then a new password | Send code | Log in |
| Board | Today's level | The next unfinished step | That step |
| Book | Group or private, this studio | Hold seat | Reformer if needed, else Board |
| Reformer | Six pads, no names, locks at 6:45 | Lock spot | Board |
| Waitlist | Full class. After 4:00pm this only asks | Ask to join | Board, "Asked". Not booked |
| Change time | One move | Move | Board |
| Cancel | Free until 4:00pm. After that the button is gone | Cancel seat | Board, step 1 empty |
| I'm here | Arrival only | I'm here | Share-here |
| You're close | One nudge in the arrival window | Open board | I'm here |
| Share here | Mid-level card | Send / Not now | Board |
| Share clear | End card. No "−1", no "you earned a session" | Send / Skip | Board done. Streak +1 |
| Schedule | Other days | Open class | Book, move, or cancel |
| Pass | Cheongdam 2 and Geumho 8, separate | Request extend or hold | Request |
| Studio switch | Two clubs | Train here | That studio's board |
| Alerts | Replies, offers, reminders | Open | The related screen |
| Talk to Hana | Book, how many left, extend. She does not edit the pass | Send | Stays, or opens Book / Pass |
| Request | Extend, hold, or a question for the owner | Send request | Pass. Date unchanged until the owner acts |
| Profile | Name, phone, log out | Save | Me |

## States

- **Empty:** "Nothing on the board. Want a seat?" Button: Find a class.
- **Paused:** She missed check-in, or cancel closed. "Board paused. Tomorrow is a new level." Streak unchanged.
- **Done:** Four steps filled. "Board cleared. Rest well." Link to schedule. Streak up.

## Visual system

Taken from the second designer so it is not a green-owl copy. The first designer matched the structure.

- Ground ivory `#F7F1EA`. Blush `#F6B1A6`. Navy `#2F3E46`. Button red-orange `#E05A53`.
- The mission is one ticket: rounded, a bite out of the left edge, navy outline, blush shadow.
- Four beads on the ticket. Done = red-orange. Current = blush ring. Later = empty.
- Hana stands at the bottom-left of the ticket, about 96px. One line in a pill. Never a paragraph.
- Streak sits top-right, outside the ticket, labeled `DAY 4`. Not a flame. Not the word "left".
- "Cheongdam · 2 left" sits top-left, under the studio name, outside the ticket. Tap opens Pass. It never animates as a reward and never sits on a share card as a prize.

## Refused

- Chests, coins, or prizes that look like sessions.
- Streak and "2 left" in the same chip.
- Merging Geumho and Cheongdam.
- Self-cancel after 4:00pm, or a waitlist that books her.
- A quiz or a spin before she can book.
