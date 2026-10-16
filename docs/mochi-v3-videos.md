# Mochi v3 — video brief for the 3D Designer

`platform-app-v3.html` shows Mochi's state **in the scene** (no popups, no text-only moods). Everything below works today with the clips already in `assets/cici-real/`; the clips in this brief make each moment look the way the brief describes instead of falling back.

Same rules as the existing set: made from the official Cici / Mochi character sheet, same room, bench and light as `cici_mochi_petting_loop_tall`; muted; no text or UI baked in; **first frame = last frame** so loops and dip-cuts are clean; tall = 720×1280, square close-up = 720×720; ≤1 MB each as `.webm` + `.mp4` + `-poster.jpg` (first frame).

Drop the files in `assets/cici-real/` with the exact names below, then flip the matching flag in `platform-app-v3.html` (`CAT_OPT` / `CAT_LOOK_READY`) in the same commit. Until the flag is on, the app never requests the file (no 404s). `?catprobe=1` probes for the files instead, for a quick local check.

## A. Scene clips (one each)

| # | File (`.webm` / `.mp4` / `-poster.jpg`) | Flag | Used when | Falls back to | Prompt |
|---|---|---|---|---|---|
| A1 | `cici-room-play_tall` | `CAT_OPT["room-play"]` | 7+ day streak (Mochi "plays when you're on a roll"), and the last beat of the feed sequence | `cici-cat-lively_tall` | Tall loop, 5–6 s. Cici sits on the bench as in the petting loop, smiling. Mochi on her lap bats at a small pink feather toy Cici dangles from her right hand; Mochi's paw swipes up twice, tail flicks, ears forward, eyes bright. Cici's face stays in the same spot as the petting loop (nothing over her face). Starts and ends on the petting first frame. |
| A2 | `cici-room-hungrybowl_tall` | `CAT_OPT["hungry-room"]` | Hungry (after 18:00 with no self-care). Today the app cuts to the close-up `cici-cat-hungry_tall`, which already shows Mochi at the empty bowl; this clip keeps Cici in frame | `cici-cat-hungry_tall` (close-up) | Tall loop, 5–6 s. Same bench and framing as the petting loop, but Mochi is **not** on Cici's lap: she sits on the floor at bottom-left beside her empty pink bowl, looks up at Cici, then at the bowl, tail curled, one small hopeful blink. Cici looks down at her with a soft smile, hands resting in her lap. Gently cute, never sad — no drooping ears, no tears. Starts and ends on the petting first frame pose for Cici. |
| A3 | `cici-room-waterbowl_tall` | `CAT_OPT["room-waterbowl"]` | "Drink a glass of water" mission (Cici sips, Mochi laps from her bowl). Today the app cuts to the square close-up `mochi-water` | `mochi-water` (close-up) | Tall clip, 4 s, plays while the mission confirms. Same framing as `cici-room-water_tall`: Cici lifts a glass and sips with eyes closed; Mochi is on the floor at bottom-left lapping water from her pink bowl, small tongue flicks, tiny water ripples. Starts and ends on the petting first frame. |
| A4 | `cici-cat-napping-bed` | `CAT_OPT["napping-bed"]` | Rest / paused days once the member has earned the cosy bed (Shine stage). Today Mochi naps on Cici's lap and a 2D bed is drawn on the floor | `cici-cat-napping_tall` | Tall loop, 5–6 s. Cici sits as in the petting loop, eyes half closed, calm smile, hands in her lap. Mochi is curled up asleep in a round pink cat bed on the floor at bottom-left (soft pink rim, cream cushion), slow breathing, one ear twitch. Starts and ends on the petting first frame pose for Cici. |

## B. Growth looks (the same clips, Mochi older)

Mochi grows with Cici on the Seed → Shine track: **kitten** (Seed, Sprout — today's clips) → **young cat** (Bud, Blossom) → **fluffy cat** (Shine). Each look is a variant of an existing clip with the suffix `-cat` or `-fluffy`, e.g. `cici-cat-petting-cat.mp4`, `cici-cat-petting-fluffy.mp4`. Set `CAT_LOOK_READY.cat` / `.fluffy` to `true` once a **full set** for that look exists (the app switches all clips of a look together so Mochi never changes age mid-session).

Minimum set per look (8 clips): `cici-cat-petting`, `cici-cat-lively`, `cici-cat-napping`, `cici-cat-react`, `cici-cat-hungry`, `cici-room-happy_tall`, `cici-room-eat_tall`, `cici-room-stretch_tall`. Nice to have: `cici-room-water_tall`, `dubu-eating`, `mochi-water`, plus any A-clips above.

Prompt per look (append to each existing clip's prompt):

- **young cat** (`-cat`): "Mochi is now a slim young cat, about 1.5× the kitten's size: longer body and legs, ears proportionally smaller, same cream tabby colouring, same big dark eyes. She still fits on Cici's lap. Wearing a soft pink collar with a small gold bell." *(The collar is earned at Blossom, which is inside this look; if you prefer collar-less variants, add `-nocollar` versions and tell us.)*
- **fluffy cat** (`-fluffy`): "Mochi is now a full-grown, very fluffy cream tabby cat, about 2× the kitten's size, long plush fur, a big fluffy tail, calm half-lidded eyes, same gentle expression. She fills Cici's lap. Wearing the soft pink collar with a gold bell."

## C. What stays 2D in the app (no video needed)

- The **collar** and **bed** are drawn in the scene on the lap clips (anchored per clip in `CAT_ANCH` / `CAT_BED`) until the B-variants with the collar baked in land. They are hidden on the close-ups, where Mochi moves too much for an overlay.
- Treat arrival (fish drops into the Feed circle), hearts, the "Mochi grew" line and the stage track in the sheet.

## Priority

1. A1 play loop (the streak moment is the one most members will see daily).
2. B young-cat set (first growth members reach).
3. A3 water, A2 hungry-with-Cici, A4 bed nap.
4. B fluffy set.
