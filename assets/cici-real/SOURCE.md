# assets/cici-real — sources

All images and videos here are official Cici art by the 3D Designer, made from the user's character sheet (supplied 2026-10-15).

## cici-home.webp (original notes)
- Official full-screen Home image, tall native 1080×1920 (from cici_home_tall.jpg), WebP quality 82.
- Used full-bleed on the platform-app-v2.html Home (object-fit cover, object-position 50% 35%).
- Head box ≈ x 354–720, y 540–975 (image px); plain wall top-left down to ≈28% (the glass card sits there).
- To swap: replace this file and update CICI_HOME in platform-app-v2.html (w, h, face box). The face-not-covered test reads that config.

## cici-cat-petting.mp4 / .webm + cici-cat-poster.jpg (Mochi, 모찌; asset filenames still use "dubu" from the original delivery)
- Official 3D Designer loop of Cici petting her cat Mochi (from cici_dubu_petting_tall, 720×1280, 6.5 s, no audio; mp4 792 KB, webm 314 KB). Supplied 2026-10-15.
- The v2 Home background (muted, playsinline, loop; paused off-screen / tab hidden). The poster is the still fallback (reduced motion, Save-Data, load error).
- Face ≈ 50% x, 42% y, head ≈ 29% of the height → CICI_HOME face box x 235–485, y 352–723 (image px). The face-not-covered test reads CICI_HOME.
- Lively and napping loops don't exist yet: CICI_CAT.clips maps them to "petting" with CSS cues. To swap, add cici-cat-<name>.webm/.mp4 and point the mood at it.

## dubu-eating.mp4 / .webm + dubu-eating-poster.jpg
- Official 3D Designer clip of Mochi eating (from dubu_eating_1x1, 720×720, 4 s, no audio). Plays in a small overlay after Feed, then the Home loop resumes.

## cici-home.webp (previous still)
- No longer referenced by the Home (the Mochi/petting poster replaced it); kept as an official fallback image.

## cici-sitting.webp
- Official transparent cut-out of Cici sitting (446×594); the small Cici in Cici's room on the v2 Home sheet.

(The earlier AI-generated stand-in render cici-real-studio.webp was removed: wrong face, not official.)
