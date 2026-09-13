# Narration-locked paper-theatre episode workflow

Use this route for editorial paper-collage explainers of 60 seconds or longer when the user approves the script, creates or supplies the final voiceover, and expects a complete locally assembled episode rather than three short generated clips. There is no hard upper duration limit; longer episodes scale through internal chapters and proportionally larger QA samples.

## Root contract

The voiceover is the only master timeline. The visual job is to make every complete spoken idea silently understandable through a stable theatre, independently layered AI assets, sequential cause-and-effect performance, deterministic typography, and verifiable semantic marks.

Do not mix this profile with the 30-second Flow/Gemini full-explainer defaults. Preserve the old route for short externally generated clips.

## Gate 1 — script, facts, and owner-controlled pacing

Use this sequence when the user selects it:

```text
external first draft
→ factual and beginner-clarity review
→ second-model structure and spoken-language optimization
→ human approval and version lock
→ timed editor-import file
```

- A model name describes a role, not a quality guarantee. The first drafter proposes; the optimizer repairs facts, structure, rhythm, examples, and spoken clarity; the human owns the locked wording.
- Before human approval, test whether a beginner can restate the mechanism without seeing the draft.
- The owner selects the voice, speaking speed, and pauses while generating narration in the editor. Do not reject or reshape a script through a fixed characters-per-second or playback-speed threshold.
- After the owner returns the generated narration, its real waveform, wording, pauses, and duration become authoritative. The production side must not change playback speed, close pauses, or time-compress the recording unless the owner explicitly requests it. If the spoken wording differs from the locked text, update the transcript and subtitle source to match the audio.
- The formal editor handoff is two distinct assets. The editor-TTS SRT preserves natural punctuation, timecodes, sentence gaps, and intentional pauses so generated speech does not run words together. The later screen-caption SRT follows the returned real audio and omits terminal punctuation for a cleaner screen while retaining useful internal punctuation. Never overwrite one with the other or call an untimed TXT the formal production asset. Do not split two-character words, proper names, or one continuous semantic phrase across cues.

## Gate 2 — voice master lock

Probe and record:

- duration, sample rate, channels, and silence intervals
- exact sentence or cue timecodes
- selected take and transcript version
- music path and intended gain
- clean voice or remixable master path

Rules:

- Voiceover determines every scene, subtitle, mark, and transition.
- Music is a low-level secondary track with ducking and fades. Replacing it must not move picture edits.
- Do not impose a default voice speed. The accepted returned voice track is authoritative. Do not batch-close pauses or silently accelerate it.
- Keep a clean or remixable master whenever practical.

Record both subtitle tracks:

- `tts_import_srt`: timed, pause-preserving, natural Chinese punctuation retained, generated before voice production
- `screen_caption_srt`: timed to the returned voice track, visually concise, kept as a separate file

Before accepting the TTS asset, verify that cue numbering is contiguous, timecodes are valid, at least one real punctuation mark remains, and its punctuation-stripped text matches the locked script. Before accepting the screen-caption asset, verify that its timing follows the returned audio rather than the provisional TTS schedule.

## Gate 3 — sentence-to-visual map

For every complete sentence or meaning unit, register:

```text
audio in/out | exact spoken line | one viewer takeaway | theatre
independent objects | entry order | action -> visible consequence
caption | semantic mark target_id | closing state
```

Reject the map when any spoken change has no corresponding visual state, or when the picture cannot communicate the takeaway with sound muted.

For schema 1.2, keep five machine-readable evidence files alongside the episode ledger:

- object registry: stable IDs, parent, source, z-level, source bounds, occlusion rules, and centring evidence
- semantic actions: one `actor_id -> target_id -> action -> visible_result -> closing_state` record per meaning unit
- occlusion allowlist: physical overlaps plus empty undeclared and caption-overlap arrays
- silent review: the subject, action, result, and spoken-line match for every representative state
- motion recipe ledger: chosen motion vocabulary, provenance, and the original implementation decision

`scan`, `inspect`, `crop`, and `screenshot` must target a registered `primary_subject`. A scan also stores trajectory samples and proves that each beam box remains inside the visible target and hard-mask intersection. Machine output declares its producer and output port. Layer decomposition declares at least three child layers, one parent target, and one shared `source_id`.

Pacing rules:

- Keep one full sentence or one complete meaning in one stable theatre.
- Use object entry, page turns, diagram changes, state swaps, and mark draw-ons inside the theatre instead of cutting repeatedly.
- Aim for a meaningful visible change about every 3–7 seconds without turning each phrase into a new camera shot.
- Every 20–30 seconds must introduce a new knowledge state, causal result, or theatre mechanism.
- A long-form episode should normally plan 12–18 countable subject/state assets per finished minute. Recolors, decoration, repeated arrows, and crops from one flattened scene do not count.

## Gate 4 — fixed stage and progressive performance

- Outside an explicit chapter transition, background `x`, `y`, `scale`, and `rotation` remain constant.
- Never use full-frame breathing zoom, slow drift, perpetual pan, or micro-shake as filler.
- Animate semantic objects, not the whole canvas.
- One beat adds at most one semantic group. Complete `enter → interact → visible consequence → settle` before the next group enters.
- Keep earlier groups visible only when they remain causally useful.
- Normally allow no more than two simultaneously moving subject groups.
- A mascot, avatar, or digital person is a role-based actor. It appears only when it performs an explanatory action or reaction and must not remain as a static host in every scene.
- Hold a key conclusion for about one second when readability needs it.
- Use a deliberate page turn, paper curtain, drawer, hard editorial cut, or other declared transition to change theatres.

Useful recurring motions include card slide, page flip, paper tear, wheel turn, counter flash, object swap, arrow draw-on, circle draw-on, and mechanical linkage. Do not use motion that carries no explanatory information.

## Gate 5 — assets, mattes, and layer hierarchy

- Main visual subjects and state changes come from AI-generated or rights-cleared independent assets. Local code may cut, mask, arrange, animate, label, and compose them; it must not replace them with crude placeholder drawings or screenshot fragments.
- One object equals one layer. Objects with different timing cannot share one flattened asset.
- Inspect every matte at original size on near-black, pure-white, and checkerboard backgrounds. Reject leftover paper, black blocks, foreign objects, jagged edges, dirty alpha, accidental halos, or unintended limbs.
- Register source, prompt or provenance, purpose, transparent boundary, z-level, allowed occlusion, forbidden occlusion, and scene assignment.
- Stage borders, caption rails, curtain ties, tape, and safety masks keep explicit top-layer rules.
- Transparent machines, apertures, and insertion slots need geometry-bound hard masks. Z-order alone cannot define their physical boundary.
- Full-frame mirror, reflection, tiling, looping, or stretch padding is forbidden. Keep every transformed viewport inside valid source pixels. If a closer view is required, use a separately generated close-stage composition or move only an independent object.
- Add a canvas-edge gate that inspects all four edge bands for repeated texture, reflected curtains, black seams, half-duplicated subjects, and empty pixels. A hit is a hard rejection.

## Gate 6 — captions and semantic marks

### Caption rail

- Measure the rendered caption rail bounds and centre line.
- For one line, compare the glyph bounding-box centre with the rail centre. For two lines, compare the combined two-line bounding box. Recommended vertical-centre error is no more than 8 px at 1920×1080.
- `vertical centre` means top-to-bottom centring inside the rail, not horizontal centring on the screen.
- Only the current caption may be visible. Old-caption residuals, shadows, overlaps, and duplicate burns must be zero.
- Do not split a continuous Chinese word or phrase. Use at most two lines.
- Important words may use semantic accent colours, but require sufficient contrast plus an edge or outline that survives the paper texture.
- For every visible text, numeral, icon, button, badge, or card child, register the parent container and `center_in_parent`. Check both coordinate geometry and final rendered-pixel optical centring. Either failure blocks release.
- Geometric and optical centring do not prove that text is readable. Register the final rendered glyph bounds plus safety padding as a foreground protection region. Any unrelated prop, character, mask, transition, or platform-safe overlay covering that region is a hard failure. Text may be covered only by its own declared transition while the text is intentionally not yet visible.
- For every isolated transparent asset, measure the non-transparent alpha bounds against all four source edges. A subject touching an undeclared edge is treated as cropped and must be replaced from a complete source; resizing, `object-fit: contain`, or adding canvas padding cannot restore missing pixels.

### Circles, lines, and arrows

- Generate their shape and timing deterministically in post, even when their texture imitates hand-drawn paper ink. Do not rely on image generation for exact geometry.
- Each mark declares the spoken cue, `target_id`, `mark_bbox`, independently measured `target_bbox`, and nearby exclusion targets.
- A circle must contain the intended feature rather than mostly empty space. An arrow endpoint must enter the target or destination bounds.
- A moving target needs a following mark or a mark that exits before the target moves.
- Draw marks on over roughly 0.3–0.8 seconds; do not pop in a complete circle without intent.
- Inspect every mark in the film, not only examples reported by the user.

## Gate 7 — first 40 seconds as proof

The first 40 seconds must use the final voiceover and actual music bed and include:

- at least three distinct theatre expressions
- one one-line caption and one two-line caption
- one measured semantic mark that follows or clearly targets an object
- one three-layer-or-greater occlusion relationship
- one explicit theatre transition
- one complete `enter → interact → consequence → settle` performance

Before showing the sample, require:

- 0.1-second object and collision scan
- canvas-edge scan with no mirror, reflection, tiling, looping, stretch fill, black seam, or duplicated edge subject
- parent-child centre registry plus rendered-pixel optical-centre review for visible text, numerals, icons, buttons, badges, and cards
- old-failure regression that still rejects the known bad version
- original-size frame inspection
- enlarged crops for dense overlaps
- an independent steward verdict
- semantic-action, physical-boundary, and silent-readability gates marked `PASS`

User approval means the style, caption rail, marks, and performance grammar may be reused. It does not approve the remaining duration.

If the first-40 sample fails because the route itself is wrong—for example flattened screenshots, whole-scene drift, reflected padding, or too few independent assets—mark the entire sample `OWNER_REJECTED_DO_NOT_EXTEND` and rebuild from the last approved keyframe/production-contract gate. Do not repair only the one frame the user noticed while keeping the defective route.

## Gate 8 — chapter build and final release

- After the user approves the proof mechanism, complete the entire requested episode. Build the remainder internally in natural 45–60 second chapters, but do not turn those construction units into repeated approval gates unless a new risky mechanism or materially different layout appears.
- Preserve accepted intervals. Rerender only a failed interval unless a global defect is proven.
- Re-run whole-film geometry and semantic checks from zero. Do not inherit the first-40 verdict.
- Re-read all schema 1.2 evidence files. Require semantic action, physical boundary, silent readability, output origin, and same-source layer gates to pass again for the complete film.
- Re-run canvas-edge, all-object collision, z-order, semantic-mark, and container geometry/optical-centre checks from zero. Inspect every semantic mark, not only a sample.
- Inspect at least `max(24, ceil(duration_seconds / 10))` original-size frames and `max(8, ceil(duration_seconds / 30))` enlarged dense-region crops. These are floors, not substitutes for covering every state change, semantic mark, and high-risk overlap.
- Decode the entire output and inspect black frames, frozen intervals, audio peaks, joins, and final-frame holds.
- Only an independent `OWNER_PREVIEW_ALLOWED` verdict permits candidate delivery. Keep this separate from publication and market validation.

## Gate 9 — brand tail and release package

- A user-owned brand sting is optional until supplied. Default target duration is 3.5–4.5 seconds.
- Keep the logo, brand name, and core colours stable. Let each episode change only a short topic-related playful action.
- Prefer a natively designed four-second tail over mechanical speed-up. Check the join, crop, final mark hold, audio level, and black frames.
- Deliver the final video, clean or remixable master when available, timed subtitle file, native 3:4 cover, native 4:3 cover, platform titles/copy/topics, QA report, and hashes.
- Covers are separately AI-generated and composed in each ratio. Verify every Chinese glyph, phone-size subject clarity, title-container geometry and optical centring, safe areas, platform UI overlap, character anatomy, and semantic circles. Never crop one accepted ratio into the other.

## Runtime, asset, focus, and music evidence

- Inspect the current runtime before asset production. Use `builtin_imagegen` only when an image-generation tool is callable. Without it, use user-supplied or licensed local assets and keep provenance visible in `asset-generation.json`.
- Register semantic circles, arrows, spotlights, and magnifier callouts in `semantic-focus.json`. Measure the pointer centre and target centre; the declared tolerance may not exceed 8 pixels.
- Register the actual BGM file, SHA-256, role, render gain, audible review, and speech-masking review in `background-music.json`. A familiar filename is not proof that it is the previous track.
- If the film displays an open-source Skill or GitHub link, store the exact Skill name and full repository URL in the release ledger, then verify text fidelity and foreground protection on the encoded frame.

## Required manifest and validation

Copy `assets/episode-template.json` to the episode folder and maintain it as the production ledger. Schema 1.3 requires the existing five evidence files plus semantic focus, asset generation, background music, and runtime compatibility evidence. Schemas 1.0, 1.1, and 1.2 remain readable for older projects.

```bash
python scripts/validate_episode.py /absolute/path/to/episode.json --stage plan
python scripts/validate_episode.py /absolute/path/to/episode.json --stage script
python scripts/validate_episode.py /absolute/path/to/episode.json --stage audio
python scripts/validate_episode.py /absolute/path/to/episode.json --stage front40
python scripts/validate_episode.py /absolute/path/to/episode.json --stage final
python scripts/validate_episode.py /absolute/path/to/episode.json --stage deliver
```

This validator checks the ledger and required artifacts. It does not inspect visual taste or replace the DAO geometry gate, semantic-mark review, or independent steward.
