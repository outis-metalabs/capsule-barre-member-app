# assets/cici-real — sources

All images and videos here are official Cici / Mochi art by the 3D Designer, made from the user's character sheet (supplied 2026-10-15 onward).

## cici-cat-petting.mp4 / .webm + cici-cat-poster.jpg (default Home loop)
- Preferred petting loop: `cici_mochi_petting_loop_tall` (also available as `_wide`). 720×1280, ~6.1 s, muted, ≤0.8 MB.
- Default Home background (muted, playsinline, loop; paused off-screen / tab hidden). Poster = still fallback (reduced motion, Save-Data, load error).
- Face ≈ 50% x, 42% y, head ≈ 29% of height → CICI_HOME face box x 235–485, y 352–723 (image px).

## Mood loops (wired 2026-10-16, tall → `cici-cat-<mood>.*`)
| Mood | Source | When |
|---|---|---|
| **lively** | `cici-cat-lively_tall` | Active (non-paused) streak |
| **hungry** | `cici-cat-hungry_tall` | After 18:00 home time, no self-care (not rest/paused) |
| **react** | `cici-cat-react_tall` | Tap / long-press the character |
| calm / napping / eating (Home loop) | petting (for now) | Crisis calm; rest/paused/broken streak; between feed overlay |

Crossfade between loops: ~400 ms dual-video opacity fade (`CICI_CAT.fadeMs`).

## Still awaiting 3D Designer redo (do not invent)
- **napping** Home loop (rest / paused / broken streak) — currently falls back to petting + CSS.
- **mochi-stretch** / **mochi-water** mission clips — slots exist; not wired to new files until redo is signed off.
- Young Women Panel review should wait until **all** clips (including nap / stretch / water) are in.

## dubu-eating.mp4 / .webm + dubu-eating-poster.jpg
- Official eating clip (from `dubu_eating_1x1`, 720×720, ~4 s). Feed overlay, then back to the Home loop.

## cici-sitting.webp / cici-home.webp
- Sitting cut-out for Cici's room; earlier tall still kept as fallback (Home uses the petting poster).

(The earlier AI-generated stand-in `cici-real-studio.webp` was removed.)
