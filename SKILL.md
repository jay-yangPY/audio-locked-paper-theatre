---
name: audio-locked-paper-theatre
description: Plan, validate, and deliver narration-locked editorial paper-collage explainers of 60 seconds or longer, with no hard upper duration limit. Use when the final voice track must control a fixed paper-theatre timeline with independent visual assets, deterministic captions and semantic marks, sourced BGM, a first-40-second proof gate, duration-scaled whole-film QA, native 3:4/4:3 covers, and a release package. Works in Codex and equivalent file-and-command-capable agents; image generation is optional when lawful user-supplied or local assets are available. Do not use for a single short B-roll clip or a presenter-led advertisement.
---

# Audio-Locked Paper Theatre

Build long-form editorial paper-collage explainers around the accepted real voice track. The voiceover is the only master timeline; music remains secondary. A fixed theatre holds the scene while independent semantic objects enter, interact, create a visible consequence, and settle.

Read [references/workflow.md](references/workflow.md) completely before planning, rendering, reviewing, or accepting an episode. Read [references/sources-and-license-boundary.md](references/sources-and-license-boundary.md) before importing any outside method, demo, code, or template.
Read [references/runtime-compatibility.md](references/runtime-compatibility.md) before selecting an asset-generation mode. When the episode uses the bright editorial identity, read [references/bright-papercraft-presentation.md](references/bright-papercraft-presentation.md).

## Boundaries

Do not copy protected templates, fonts, visual systems, private media, credentials, or user-specific absolute paths into a public Skill. Do not call a manifest `PASS` a visual acceptance. Never let an attractive prop replace the real action target, let a result appear without a producer, or call unrelated icons a source decomposition.

## Non-negotiable contract

- Lock facts and beginner clarity before visual production. A first-draft model and an editing model may assist, but the human owns the final wording.
- Give the owner a timed TTS SRT that preserves natural punctuation. After the real voice returns, create a separate screen-caption SRT timed to that audio. Never overwrite or substitute one for the other.
- Treat the returned voice waveform, wording, speed, pauses, and duration as authoritative. Do not accelerate it or close silence unless explicitly requested.
- Keep the paper stage fixed outside declared chapter transitions. Animate explanatory objects, not the whole canvas.
- Plan roughly 12–18 countable independent subject/state assets per finished minute. Screenshot crops, decoration, recolours, repeated arrows, and crops from a flattened scene do not count.
- Keep one complete meaning in one theatre. Aim for a real visible semantic change every 3–7 seconds and a new knowledge state every 20–30 seconds.
- Use deterministic post-production for exact captions, labels, numerals, arrows, circles, masks, z-order, and motion paths.
- Bind every semantic mark to a measured `target_id` and target bounds. Inspect all marks, not only examples the user notices.
- Register every circle, arrow, underline, spotlight, or magnifier in `semantic-focus.json`. Its measured centre must resolve to the intended target within the declared tolerance and pass original-size pixel review.
- Register each spoken unit as `actor_id -> target_id -> action -> visible_result -> closing_state`, plus the exact forbidden misread. For scan, inspect, crop, and screenshot actions, the target must be the real primary subject.
- Require physical machines to declare hard masks and output ports. A scan beam stays inside the intersection of the visible subject and mask on every sample; a receipt or result must visibly emerge from its registered producer port.
- A three-layer explanation must decompose one registered source into three or more layers that share the same `source_id`. Three adjacent icons are not a decomposition.
- Run a muted-frame review that names the main subject, action, visible result, and relation to the spoken line. Missing or ambiguous answers reject the state.
- Forbid mirror, reflection, tiling, looping, and stretch padding. Every transformed viewport stays inside valid source pixels; use a separate close-stage composition when it cannot.
- Treat a mascot or digital person as a role-based actor. It appears only to answer, react, point, demonstrate, or cause an event.
- Register every visible text, numeral, icon, badge, button, and card child with `center_in_parent`. Geometry centre and final-pixel optical centre must both pass.
- The first 40 seconds prove the mechanism; they do not approve the complete film. A global route defect rejects the whole sample and returns to the last approved keyframe or production contract.
- There is no 240-second ceiling. After proof approval, finish the complete requested episode; use 45–60 second chapters only as internal construction units, not as repeated user approval gates. Scale asset counts, original-size review frames, and dense crops with total duration.
- Generate 3:4 and 4:3 covers as independent AI-native compositions. Verify exact text, optical centring, phone-size readability, platform UI overlap, anatomy, and focal-point occlusion.
- Keep `OWNER_PREVIEW_ALLOWED`, `PUBLISHED`, and `MARKET_VALIDATED` as separate states.
- Record the exact BGM source and SHA-256 in `background-music.json`. If the owner asks for a previous track, verify exact hash equality before rendering.
- Select one asset mode in `asset-generation.json`. Use `builtin_imagegen` only when the current runtime actually exposes image generation; otherwise use `user_supplied` or `local_library` and record provenance.
- When a finished video shows a Skill name or repository URL, render the exact strings deterministically, protect them from foreground objects, and validate the full `https://github.com/owner/repository` URL.

## Workflow

```text
draft
→ fact and beginner review
→ human script lock
→ punctuated timed TTS SRT
→ real voice return and master lock
→ separate real-audio screen captions
→ sentence-to-visual map, object registry, semantic-action manifest, physical occlusion contract
→ first-40-second proof
→ after proof approval, complete the full episode in internal 45–60 second construction chapters
→ fresh whole-film gates
→ optional user-owned 3.5–4.5 second brand tail
→ independent native 3:4 and 4:3 covers
→ final package
```

Copy [assets/episode-template.json](assets/episode-template.json) into the project as `episode.json`. Copy the semantic action, object registry, occlusion, silent-review, motion-ledger, semantic-focus, asset-generation, and background-music templates from `assets/`, then replace the example values with measured episode evidence. Validate after every state change:

```bash
python scripts/validate_episode.py /absolute/path/to/episode.json --stage plan
python scripts/validate_episode.py /absolute/path/to/episode.json --stage script
python scripts/validate_episode.py /absolute/path/to/episode.json --stage audio
python scripts/validate_episode.py /absolute/path/to/episode.json --stage front40
python scripts/validate_episode.py /absolute/path/to/episode.json --stage final
python scripts/validate_episode.py /absolute/path/to/episode.json --stage deliver
```

Structural `PASS` is necessary but never replaces original-size visual review, semantic-mark inspection, optical-centre review, whole-film decoding, or an independent steward verdict.

## Quality Gate

A release candidate needs passing structural validation, rendered-pixel review, semantic-action review, physical-boundary review, silent-readability review, old-failure regression, whole-film decoding, and an independent steward verdict. Preserve `OWNER_PREVIEW_ALLOWED`, owner acceptance, publication, and market validation as separate states.

After changing the workflow or validator, run the cases in [examples/retest-prompts.md](examples/retest-prompts.md) and the automated tests.
