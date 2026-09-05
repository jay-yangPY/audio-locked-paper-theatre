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
