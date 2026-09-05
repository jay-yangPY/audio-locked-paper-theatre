# Audio-Locked Paper Theatre

一套面向 60–240 秒口播科普视频的 Codex Skill 与可执行门禁：先锁定真实口播，再用固定纸艺剧场、独立 AI 素材和确定性后期，让画面逐件登台并与每一句解释严格对齐。

它解决的不是“如何给一张拼贴图加慢速推拉”，而是长篇不露脸科普最容易失败的几个地方：

- 口播、字幕和画面时间线错位
- 一张整景撑太久，或者一句话乱切很多镜头
- 画面素材不够，后半段明显偷懒
- 圈线圈错对象，标签和图层互相遮挡
- 放大后使用镜像/反射补边，边缘出现重复幕布或半截主体
- 转语音 SRT 丢失中文标点，生成语音连续朗读
- 前 40 秒通过后，完整版没有重新审核
- 3:4 与 4:3 封面由同一张图机械裁切

## 核心流程

```text
初稿
→ 第二模型做事实、结构、小白表达和口语优化
→ 人工锁稿
→ 带标点、带时间码的 TTS SRT
→ 返回真实口播
→ 单独生成与真实口播同步的屏幕字幕 SRT
→ 逐句画面映射＋独立素材清单＋图层合同
→ 前40秒高风险证明样片
→ 几何、边缘、容器居中、旧错回归与独立复核
→ 按45–60秒自然章节完成余片
→ 全片从0秒重新审核
→ 独立生成3:4与4:3封面
→ 完整视频＋字幕＋封面＋发布包＋QA＋哈希
```

## 这套方法的关键观点

1. **真实口播是唯一主时间轴。** 不能在制作端擅自变速、收紧停顿或让 BGM 决定剪辑点。
2. **固定舞台，移动语义对象。** 禁止用整画面慢推、呼吸缩放和微漂移冒充丰富动画。
3. **一幕讲清一个完整意思。** 让对象按“进入 → 互动 → 可见后果 → 停稳”表演。
4. **主要对象必须独立。** 截图裁块、一个扁平整景和简单换色不计入素材密度。
5. **精确元素由确定性后期负责。** 中文、字幕、圈线、箭头、遮罩、图层和运动轨迹不交给生成模型碰运气。
6. **前40秒只证明机制。** 完整版必须重新执行全部门禁。
7. **候选、发布和市场验证是三种状态。** 本地通过不等于已经发布，更不等于有市场效果。

## 仓库内容

```text
SKILL.md                         Codex Skill 入口
references/workflow.md           完整长片工作流
assets/episode-template.json     生产账本模板
scripts/validate_episode.py      分阶段结构验证器
examples/retest-prompts.md       正向与反向行为测试
tests/test_validator.py          验证器回归测试
```

## 安装为 Codex Skill

将仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/jay-yangPY/audio-locked-paper-theatre.git ~/.codex/skills/audio-locked-paper-theatre
```

Windows PowerShell 示例：

```powershell
git clone https://github.com/jay-yangPY/audio-locked-paper-theatre.git "$env:USERPROFILE\.codex\skills\audio-locked-paper-theatre"
```

也可以只使用模板和验证器，不安装为 Skill。

## 快速开始

复制生产账本：

```bash
cp assets/episode-template.json /path/to/project/episode.json
```

按阶段验证：

```bash
python scripts/validate_episode.py /path/to/project/episode.json --stage plan
python scripts/validate_episode.py /path/to/project/episode.json --stage script
python scripts/validate_episode.py /path/to/project/episode.json --stage audio
python scripts/validate_episode.py /path/to/project/episode.json --stage front40
python scripts/validate_episode.py /path/to/project/episode.json --stage final
python scripts/validate_episode.py /path/to/project/episode.json --stage deliver
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 门禁边界

验证器负责检查生产账本、SRT、文件存在性、阶段状态、封面比例和关键审核回执。它不会判断画面是否好看，也不会自动证明圈线真的圈准、光学居中真的舒服或人物手指没有穿帮。

因此正式交付仍需要：

- 每 0.1 秒的全对象几何扫描
- 全部语义圈线逐项核对
- 四边画布回归检查
- 原尺寸帧与高密区放大检查
- 容器几何居中与最终像素光学居中检查
- 完整视频解码
- 与制作端分离的独立复核

## 不包含什么

- 不包含任何私人口播、BGM、品牌 Logo、商业视频或生成素材
- 不自动登录、付费、提交视频生成任务或发布到平台
- 不复制 Vox 的 Logo、字体、具体画面或商业包装；这里只保留通用的编辑部纸艺解释语法
- 不保证播放量、完播率或商业结果

## License

MIT
