# assets/cici-real — sources

All images and videos here are official Cici / Mochi art by the 3D Designer, made from the user's character sheet (supplied 2026-10-15 onward).

## cici-cat-petting.mp4 / .webm + cici-cat-poster.jpg (default Home loop)
- Preferred petting loop: `cici_mochi_petting_loop_tall` (also available as `_wide`). 720×1280, ~6.1 s, muted, ≤0.8 MB.
- Default Home background (muted, playsinline, loop; paused off-screen / tab hidden). Poster = still fallback (reduced motion, Save-Data, load error).
- Face ≈ 50% x, 42% y, head ≈ 29% of height → CICI_HOME face box x 235–485, y 352–723 (image px).

## Mood loops (tall → `cici-cat-<mood>.*`)
| Mood | Source | When |
|---|---|---|
| **lively** | `cici-cat-lively_tall` | Active (non-paused) streak |
| **napping** | `cici-cat-napping_tall` | Rest day / paused / broken streak |
| **hungry** | `cici-cat-hungry_tall` | After 18:00 home time, no self-care (not rest/paused) |
| **react** | `cici-cat-react_tall` | Tap / long-press the character |
| calm / eating (Home loop) | petting | Crisis calm; between feed overlay |

Crossfade between Home loops: ~400 ms dual-video opacity fade (`CICI_CAT.fadeMs`).

## Mission clips (square overlays, ≤1 MB)
| Clip | Source | When |
|---|---|---|
| **cici-room-stretch_tall** | 3D Designer native-tall room loop (old cropped `mochi-stretch` removed 2026-10-16) | Stretch mission (in the room) |
| **mochi-water** | `mochi-water_square` (also wide available) | Drink-water mission **starts** |

One-shot overlay, then back to the Home loop. Still under reduced motion / Save-Data. Suppressed in crisis.

## dubu-eating.mp4 / .webm + dubu-eating-poster.jpg
- Official eating clip (from `dubu_eating_1x1`, 720×720, ~4 s). Feed overlay, then back to the Home loop.

## cici-sitting.webp / cici-home.webp
- Sitting cut-out for Cici's room; earlier tall still kept as fallback (Home uses the petting poster).

(The earlier AI-generated stand-in `cici-real-studio.webp` was removed.)

## v3 (platform-app-v3.html, 2026-10-16)
Mochi's state is shown in the scene: hungry = `cici-cat-hungry` (the bowl close-up, unused in v2), feed while hungry = `dubu-eating` → petting → `cici-room-happy_tall`;
feed otherwise = `cici-room-eat_tall` (once) → happy; water mission = `mochi-water` full scene (rounded square). Square close-ups are never cover-cropped.
New optional slots (flags `CAT_OPT` / `CAT_LOOK_READY` in the HTML; no probing by default): `cici-room-play_tall`, `cici-room-hungrybowl_tall`, `cici-room-waterbowl_tall`,
`cici-cat-napping-bed`, and `-cat` / `-fluffy` growth variants of every clip. Brief + prompts: `docs/mochi-v3-videos.md`.

## Panel review (2026-10-16)
Full set wired: petting + lively + napping + hungry + react + stretch + water + eating.
Panel must-fixes on #32: first-treat on-ramp, one overlay at a time, short sheet (hide empty room / collapse locked growth).
