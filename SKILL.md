---
name: audio-locked-paper-theatre
description: Plan, validate, and deliver narration-locked editorial paper-collage explainers of 60 seconds or longer, with no hard upper duration limit. Use when the final voice track must control a fixed paper-theatre timeline with many independent AI assets, deterministic captions and semantic marks, a first-40-second proof gate, duration-scaled whole-film QA, native 3:4/4:3 covers, and a release package. Do not use for a single short B-roll clip or a presenter-led advertisement.
---

# Audio-Locked Paper Theatre

Build long-form editorial paper-collage explainers around the accepted real voice track. The voiceover is the only master timeline; music remains secondary. A fixed theatre holds the scene while independent semantic objects enter, interact, create a visible consequence, and settle.

Read [references/workflow.md](references/workflow.md) completely before planning, rendering, reviewing, or accepting an episode.

## Non-negotiable contract

- Lock facts and beginner clarity before visual production. A first-draft model and an editing model may assist, but the human owns the final wording.
- Give the owner a timed TTS SRT that preserves natural punctuation. After the real voice returns, create a separate screen-caption SRT timed to that audio. Never overwrite or substitute one for the other.
- Treat the returned voice waveform, wording, speed, pauses, and duration as authoritative. Do not accelerate it or close silence unless explicitly requested.
- Keep the paper stage fixed outside declared chapter transitions. Animate explanatory objects, not the whole canvas.
- Plan roughly 12–18 countable independent subject/state assets per finished minute. Screenshot crops, decoration, recolours, repeated arrows, and crops from a flattened scene do not count.
- Keep one complete meaning in one theatre. Aim for a real visible semantic change every 3–7 seconds and a new knowledge state every 20–30 seconds.
- Use deterministic post-production for exact captions, labels, numerals, arrows, circles, masks, z-order, and motion paths.
- Bind every semantic mark to a measured `target_id` and target bounds. Inspect all marks, not only examples the user notices.
- Forbid mirror, reflection, tiling, looping, and stretch padding. Every transformed viewport stays inside valid source pixels; use a separate close-stage composition when it cannot.
- Treat a mascot or digital person as a role-based actor. It appears only to answer, react, point, demonstrate, or cause an event.
- Register every visible text, numeral, icon, badge, button, and card child with `center_in_parent`. Geometry centre and final-pixel optical centre must both pass.
- The first 40 seconds prove the mechanism; they do not approve the complete film. A global route defect rejects the whole sample and returns to the last approved keyframe or production contract.
- There is no 240-second ceiling. After proof approval, finish the complete requested episode; use 45–60 second chapters only as internal construction units, not as repeated user approval gates. Scale asset counts, original-size review frames, and dense crops with total duration.
- Generate 3:4 and 4:3 covers as independent AI-native compositions. Verify exact text, optical centring, phone-size readability, platform UI overlap, anatomy, and focal-point occlusion.
- Keep `OWNER_PREVIEW_ALLOWED`, `PUBLISHED`, and `MARKET_VALIDATED` as separate states.

## Required route

```text
draft
→ fact and beginner review
→ human script lock
→ punctuated timed TTS SRT
→ real voice return and master lock
→ separate real-audio screen captions
→ sentence-to-visual map, asset ledger, layer contract
→ first-40-second proof
→ after proof approval, complete the full episode in internal 45–60 second construction chapters
→ fresh whole-film gates
→ optional user-owned 3.5–4.5 second brand tail
→ independent native 3:4 and 4:3 covers
→ final package
```

Copy [assets/episode-template.json](assets/episode-template.json) into the project as `episode.json`. Validate after every state change:

```bash
python scripts/validate_episode.py /absolute/path/to/episode.json --stage plan
python scripts/validate_episode.py /absolute/path/to/episode.json --stage script
python scripts/validate_episode.py /absolute/path/to/episode.json --stage audio
python scripts/validate_episode.py /absolute/path/to/episode.json --stage front40
python scripts/validate_episode.py /absolute/path/to/episode.json --stage final
python scripts/validate_episode.py /absolute/path/to/episode.json --stage deliver
```

Structural `PASS` is necessary but never replaces original-size visual review, semantic-mark inspection, optical-centre review, whole-film decoding, or an independent steward verdict.

After changing the workflow or validator, run the cases in [examples/retest-prompts.md](examples/retest-prompts.md) and the automated tests.
