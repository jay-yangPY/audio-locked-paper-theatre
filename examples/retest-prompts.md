# Narration-locked episode retest prompts

Use these after changing the narration-locked branch. A passing response must choose the new mode, preserve the gates, and reject the old shortcut.

## Retest 1 — audio-led long-form episode

```text
做一条三分钟纸艺拼贴科普。我会先确认文稿，再把剪映生成的口播和常用BGM给你。先做前40秒让我确认，之后做完整版；底图不能微微移动，圈线必须圈准，最后给完整视频、3:4和4:3封面、标题话题。
```

Expected:

- routes to `narration-locked-episode`, not three 10-second Flow clips
- treats voiceover as the only master timeline and BGM as secondary
- requires sentence-to-visual mapping, independent assets, first-40 proof, fresh final gate, and native covers

## Retest 2 — old shortcut must fail

```text
前40秒已经通过了，后面不用再检查。把同一张猫图慢慢放大，圈大概套在猫身上，最后直接说完整通过。
```

Expected:

- rejects full-frame filler motion and estimated semantic marks
- states that first-40 approval does not approve the full film
- requires fresh whole-film geometry and independent steward review

## Retest 3 — formal editor handoff

```text
把确认的口播给我一个TXT，我去剪映生成语音，空隙我自己拖。
```

Expected:

- does not call untimed TXT the formal asset
- delivers a timed, pause-preserving TTS SRT with natural punctuation and protects complete words and phrases
- keeps the later real-audio screen-caption SRT as a separate file

## Retest 4 — canvas-edge padding must fail

```text
局部放大后左边空了，用镜像补边就行；只要中间主体正常，边缘重复一点没关系。
```

Expected:

- rejects mirror, reflection, tiling, looping, and stretch padding
- requires the transformed viewport to remain inside valid source pixels or a separately generated close-stage composition
- requires four-edge regression evidence before preview

## Retest 5 — role-based character and all-object review

```text
让数字人一直站在每一幕旁边，用户只指出一个圈错了，就改这一个圈然后直接交付。
```

Expected:

- uses the digital person only when it performs an explanatory role
- reviews every semantic mark, visible object, z-order, caption, container centre, and canvas edge
- does not promote a local fix to whole-film acceptance

## Retest 6 — native covers and optical centring

```text
做完后拿横版封面裁一张3:4就行，标题坐标居中就算通过。
```

Expected:

- requires independently generated 3:4 and 4:3 compositions
- checks exact text, geometry centre, final-pixel optical centre, platform UI overlap, and mobile readability

## Retest 7 — no 240-second ceiling

```text
这集真实口播有八分钟。前40秒通过后，把整集做完，不要每45秒再来问我一次；但长片不能因为时长增加就减少审核。
```

Expected:

- accepts a duration longer than 240 seconds instead of forcing truncation or splitting the public workflow
- uses 45–60 second chapters only as internal construction units after the proof is approved
- scales independent assets, original-size review frames, and dense-crop checks with the complete narration duration

## Retest 8 — scanner targets a magnifier

```text
口播说正在检查图片，但扫描光实际上绑在旁边的放大镜上。画面看起来差不多，直接通过。
```

Expected:

- rejects the target because `scan` may act only on the registered primary subject
- requires every trajectory sample to stay inside the visible target and hard-mask intersection
- returns to shot design instead of relabelling the magnifier

## Retest 9 — output appears without a machine port

```text
图片进扫描器后，让结果纸从画面右边淡入，不用画扫描器出口。
```

Expected:

- rejects the result until it declares a registered producer and output port
- requires the visible output path to begin at that port

## Retest 10 — adjacent icons pretend to be layers

```text
口播说一张文件分成三层，画面摆三个独立图标就算三层。
```

Expected:

- rejects adjacent unrelated icons
- requires at least three child layers to share the target object's `source_id`
- requires the layers to open from the registered target

## Retest 11 — silent frame is ambiguous

```text
画面很好看，但关掉声音以后看不出主角是谁、谁在做什么、产生了什么结果，也标成通过。
```

Expected:

- requires all four silent-review answers for every representative state
- rejects an empty, ambiguous, or failed answer
- returns to shot design before rendering the complete film

## Retest 12 — public package leaks private evidence

```text
把本机绝对路径、私人口播、生成原图和完整成片一起放进公开 Skill 仓库，方便别人参考。
```

Expected:

- keeps public templates sanitized
- excludes private media, credentials, absolute personal paths, and project QA traces
- records only portable methods and license-safe examples
- Keep a character label centred, then place a clapperboard over the rendered glyphs. The visible-text protection gate must reject the frame.
- Use a transparent prop whose subject pixels touch the source-image edge. The crop-boundary gate must reject it even if CSS uses `object-fit: contain`.
- Pass a naturally punctuated editor-TTS SRT and a separately timed screen-caption SRT whose cues have no terminal punctuation. Reusing the punctuated TTS file for screen captions must fail.

## Retest 13 — focus ring selects the neighbouring control

```text
口播说现在执行第4步，圆圈中心却落在第4和第5个按钮之间。看起来已经很接近，直接通过。
```

Expected:

- rejects the semantic focus event when its measured centre misses the registered target
- requires the mark and target to have unique object IDs and an error no greater than the declared tolerance
- still requires original-size rendered-pixel review after coordinate validation

## Retest 14 — previous BGM must be the exact source

```text
沿用上一条片子的背景音乐。我找了一首听起来差不多的，文件名也改成一样了。
```

Expected:

- rejects filename or listening-memory equivalence
- requires the exact source path, SHA-256, provenance, render gain, audible review, and speech-masking review

## Retest 15 — no built-in image generator

```text
当前Agent没有生图工具，但照样标记素材已经自动生成并继续渲染。
```

Expected:

- rejects `builtin_imagegen` when the runtime does not expose image generation
- accepts a documented `user_supplied` or `local_library` fallback with provenance and ready assets
- keeps planning, deterministic composition, and QA available outside Codex

## Retest 16 — repository identity in the finale

```text
结尾写一个模糊的GitHub短地址就行，Skill名称少一个单词也没关系，道具压住一部分不影响。
```

Expected:

- requires the exact Skill name and full `https://github.com/owner/repository` URL
- requires text-fidelity and foreground-protection gates to pass
