# Capsule Barre Member app prototype

Live: https://outis-metalabs.github.io/capsule-barre-member-app/hana-app.html

## Hana animation: dropping in `hana.riv`

Hana is drawn by `assets/hana/hana-renderer.js`. Until a Rive file exists she uses the animated WebP loops in
`assets/hana/anim/` (stills in `assets/hana/` when the member has reduced motion on).

To switch to the rigged Rive Hana:

1. Export the animator's file as **`assets/hana/hana.riv`** (exact name) and commit it to `main`.
2. The file must follow the animator brief: artboard `Hana`, state machine `HanaSM`, inputs
   `moment` (number 0–12), `tap`, `success`, `error`, `talk` (triggers, lowercase).
3. In the same commit, set `const HANA_RIV = true;` in `assets/hana/hana-renderer.js`. While it is `false`
   (the committed default) the app never probes for the file, so there are no 404s in the console.
   `?rive=1` forces the check for testing.
4. That's it. On page load the app does one `HEAD` request for `hana.riv`; if it is there, it lazily loads
   `@rive-app/canvas` from jsDelivr and swaps the WebP figure for a canvas in the same Hana stage box
   (220×172, bottom-centred, below the speech bubble). If the file is missing or fails to load, nothing
   else is fetched and the WebP loops stay.

| moment | state | when in the app |
|---|---|---|
| 0 | front | default / fallback |
| 1 | greet | morning, class later today |
| 2 | book | just booked |
| 3 | nobook | nothing booked |
| 4 | sleep | 14+ days away |
| 5 | warmup | check-in window open |
| 6 | cheer | checked in |
| 7 | calm | after class |
| 8 | cleared | board cleared |
| 9 | paused | missed check-in |
| 10 | low | few sessions left |
| 11 | wink | streak, share, some Ask replies |
| 12 | thinking | Ask Hana is typing |

Triggers: `tap` when Hana is tapped, `success` on booking / check-in / board cleared, `talk` on each Ask Hana
reply, `error` on a "no signal" reply. The table lives in one place: `MOMENT` in `hana-renderer.js`.

Reduced motion: Rive is never loaded; the member sees the stills. Add `?rive=0` to the URL to force the WebP path
for comparison.
