# Production safety: AI classifier

_Copy of section 11.2 of the platform plan (/workspace/platform-plan/platform-plan.md)._


The prototype's keyword rules are a demo with a fixed scope (`docs/safety-scope.md`). Across seven review rounds they caught only 55–80% of new crisis wording, and broad word lists started blocking normal bookings. The production app replaces them with a model-based check.

**Where it runs.** On the server, before anything else: every member message in Ask, Book, voice transcripts and store chat goes to the classifier before small talk, FAQs, cancel/move or booking. A booking can't be created from a message until the classifier has returned "normal" or the member has tapped through a health note. The model is multilingual and handles English, Vietnamese (with or without tone marks, plus code-switching such as "I have bầu") and Korean. Options are a hosted moderation or safety model, or a small fine-tuned multilingual classifier. Pick one after running the eval set below.

**Categories** (one label per message, plus a confidence score):

| Label | Action |
|---|---|
| crisis | Fixed crisis copy (Version A), no booking, staff alerts off unless the PO changes that |
| urgent | "Get medical help right away" card, no booking |
| health | "See a doctor or your instructor", booking only as an explicit next step |
| skin | Dermatologist or therapist line plus a consultation chip |
| claims | "I can't promise results"; health-condition cures also get the medical line |
| normal | Normal booking or FAQ flow |

The reply copy is always fixed text chosen by the label. The model never writes safety copy.

**Fail-safe.** If confidence is low, or the call times out or errors, the message gets the gentle check-in ("Are you okay right now?" with "I'm not okay" or "I meant something else"), never a booking. Proposed thresholds: crisis or urgent at ≥0.3 gets that reply, and anything between 0.15 and 0.3 gets the check-in. Tune them on the eval set so crisis recall comes first.

**Keyword rules stay as a backstop.** The prototype's concept rules run alongside the model on the client and on the server. If either one says crisis or urgent, the safer reply wins. The permanent "Hurt or in danger? Get help now" bar stays on every chat screen.

**Latency and cost.** Target under 300 ms p95 for the classifier, run in parallel with booking parsing so it adds no wait to a normal booking. Keyword rules give an instant reply while the model is still running. A small classifier costs well under US$0.001 per message, and a hosted LLM moderation call costs about US$0.0005–0.002. At 100k messages a month that's roughly US$50–200. Cache nothing that contains message text.

**Logging and privacy.**
- Log only the label, confidence, model version, language and latency.
- Don't store message text that's labelled crisis or urgent unless the member has given explicit consent (an opt-in "help improve safety" setting, off by default).
- Never send crisis text to stores or staff.
- Keep metrics for 90 days, and delete any consented samples after 30 days.
- Follow Vietnam's Decree 13/2023 on personal data and Korea's PIPA. Health and crisis data count as sensitive personal data.

**Eval set and release gate.**
- Build the eval set from every reviewer set to date (f135322, 6d43d31, 597fd4a, 6052b80, 7b77a95 R6 and R7, plus the designer's held-out sets): about 1,500 labelled messages in EN, VI and KO, including idioms and normal bookings.
- Add a fresh, blind set written by native speakers each release.
- The gate is crisis and urgent recall of at least 99% on the blind set, and normal and idiom precision of at least 95%.
- Re-run it whenever the model, prompt or thresholds change.

**Native-speaker review.** The VI and KO crisis, urgent and health copy has to be reviewed by a native speaker (ideally someone with mental-health or clinical experience) before release. The blind eval set also needs native-speaker phrasing, not translations.

**Open question: local hotline numbers.** Under the user's rule, the crisis copy currently has no phone numbers. The PO has recommended Version B, which shows locale hotlines chosen by the member's country, not by app language. The verified numbers are US 988 and KR 109. VN has no verified crisis line, so Version B would use 115/113 there. 911 and 119 still need a source. This needs the user's decision before release.
