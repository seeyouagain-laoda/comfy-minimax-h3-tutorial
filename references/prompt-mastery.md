---
name: h3-prompt-mastery
description: MiniMax H3 提示词写作总手册（官方格式 + 社区方法论融合版）。当需要为 MiniMax H3 / 海螺3.0 / Hailuo 3.0 编写视频生成提示词（T2VA/I2VA/FL2VA/L2VA/Ref2VA）时使用。触发词：H3 提示词、H3 脚本、MiniMax 脚本、海螺视频脚本、video prompt。
---

# H3 提示词写作总手册（融合版 v1.1）

> 官方格式权威参考：`~/.<AGENT_HOME>/skills/h3-prompt-writing/`（base-en.txt / ref-en.txt）。
> 本手册 = 官方格式骨架 + 三轮社区方法论融合，写提示词时两者结合，官方字段名/顺序/时间戳格式严格照办。
> **v1.1 (2026-09-15) 变更：新增第 0 节硬规则 —— 全流程只用 `<Picture N>`，禁用 `<Subject N>`。**

## 0. 【用户硬规则 · 最高优先级】只用 `<Picture N>`，禁用 `<Subject N>`

用户 2026-09-15 明确要求：**任何情况下都不要出现 `<Subject N>`，参考图一律写 `<Picture 1>`、`<Picture 2>`…**
官方 ref-en.txt 里那套 `<Subject 1> is the woman in <Picture 1>.` 写法**弃用**，改为以 Picture 为唯一参考标签。

执行细则：
- **段名不动**：`subject_definitions` 是官方字段名，保留不改（工具认字段名）；但**段内每一行定义的都是 `<Picture N>`**。
- 每张图必须写清三件事：① 它是什么（三视图角色设定表 / 正脸全身照 / 场景照 / 故事板）② 要保留哪些特征（逐项列：发色渐变、耳、尾、发夹、服装、鞋…）③ 它在该镜头承担什么角色（appearance anchor 外观锚点 / composition anchor 构图锚点 / frame anchor 帧锚点）。
- **三视图 / 设定图必加防御句**（否则模型可能把三视图排版当画面，生成"三个小人并排"）：
  `... is not a frame of the target video; its three-view sheet layout must not appear on screen, and only one <主体> may be visible in the frame.`
- 正文引用：首次出现写 `the whale-girl from <Picture 1>`（列出特征），其后继续沿用同一标签，不重新定义。
- `retention_analysis` 行格式：`<Picture 1> ([Shot 1] appearance and composition anchor): fully_preserved - ...`
- **交付前强制自检**：在成稿里搜 `<Subject`，命中一处都不行，必须全部改成 `<Picture>`。
- 若走 I2VA（图片当首帧），Picture 标签天然正确，另加首行指令：
  `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`

## 1. 模式选择（先选对，写错模式是常见翻车原因）

| 模式 | 输入 | 写法要点 |
|---|---|---|
| T2VA | 纯文本 | 完整建立视听场景：主体+环境+动作+运镜+风格+声音 |
| I2VA | 首帧图 | **别重复描述图已展示内容**，词额留给运动/运镜/声音/需保持的细节 |
| FL2VA | 首+末帧 | 只描述两端之间的变化路径，别重复端点 |
| L2VA | 末帧 | 描述镜头如何到达该结尾 |
| Ref2VA | 多参考（≤9图+3视频+3音频，总数≤12） | 六段式；参考标签跨段一致，且**只用 `<Picture N>`**（见第 0 节） |

官方规格：4-15 秒 / 768p 短边 / 24fps / 32kHz 立体声 / 11 种语言对白。**CFG-distilled 权重：不依赖 CFG，采样直接跑**。

## 2. 结构模板

```
【快速公式】主体(具体) + 动作(带参数) + 环境 + 运镜(前置+幅度速度) + 时机 + 风格 + 光线 + 音频
【官方三字段】（T2VA/I2VA/FL2VA/L2VA）：
  integrated_multimodal_description:  主视觉与叙事（镜头描述）
  overall_soundscape:                 环境/物理声（1-4句）
  non_diegetic_music:                 配乐（1-3句，无则 N/A）
【Ref2VA 六段式】：
  subject_definitions → summary → retention_analysis → detailed_description → overall_soundscape → non_diegetic_music
  （段名照官方不动；段内每一行都用 <Picture N> 定义，禁用 <Subject N>，见第 0 节）
```

**镜头/标签语法（官方硬规则）**：
- 首镜头 `[Shot 1]` 无时间戳；后续 `[Shot 2] At 00:03.500`（秒.毫秒三位小数）
- 对白：声音描述在标签外、台词在标签内——`The calm woman (S1) says: <d>[English] Take the morning with you.</d>`（说话者 ID：S1/S2）
- 参考标签：`<Picture i>` / `<Video k>` / `<Audio j>` 内联跟在主体后（**只用 Picture，不用 Subject**）
- 屏幕文字写确切文本：`A red neon sign reading "OPEN LATE" glows above the doorway.`
- I2VA 指令行（有图时第一行）：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- FL2VA/L2VA 用对齐指令：`Picture 1 aligns with the 0.00-second mark; Picture 2 aligns with the S.SS-second mark.`

## 3. 主体描写

- **具体到不可替换**：❌"一个女人" → ✅"穿红裙子的女人，黑长发，红色耳钉"
- **删修饰副词**：❌"优雅地走" → ✅"缓步行走"；❌"快速旋转" → ✅"旋转 30 度"（模型认参数不认形容词）
- **静态/低动态动词优先**：站立/端坐/手持/背对镜头/缓步 稳；奔跑/挥舞/转身 易闪（冲突戏用"快速逼近/抬拳/定格"替代）
- **情绪锚定动作**：❌"释然" → ✅"攥紧纸条后突然松手，纸条飘向水洼"

## 4. 动作与节奏

- **5-15 秒只放 2-3 个动作节拍**（一个主事件 + 一个反应 + 1-2 个镜头决策），贪多必仓促
- 分镜短句：每镜头 12-28 字/句，换行分隔
- 控制颗粒度：明确景别分配（"第 3 镜特写，最后 1 镜黑场"）→ 视觉重心清晰

## 5. 运镜

- **前置 + 绑定焦点**：`电影感慢推镜头→穿红裙的女人→焦点始终在她脸上`（防跑焦人物消失）
- **一条路径 + 幅度速度**：`The camera pushes in with small amplitude at slow speed toward her hands`（写进动作句）
- **每镜头一个主镜头想法**；术语别堆砌；单镜头片段不需要时间戳

## 6. 声音

- **环境声 vs 音乐必须分离**；只想要环境声写 `non_diegetic_music: N/A`（未定义≠静音，会乱配乐）
- 音乐写**时间轴**：何时起/何时加强/何时收——`swelling once as the taxi appears`
- 对白台词短到装得进时长（5 秒镜头容不下长对白）

## 7. 参考图（一图一职责，**全部以 `<Picture N>` 承载**）

- 每张参考一个明确工作（身份/服装/产品/场景/故事板），写清职责：`fully_preserved`（完全保留）/ `attribute_transfer`（只转移运动/节奏/音色）
- 角色参考包：身份图（正脸）+ 全身图 + 细节图，光线清晰无遮挡
- 故事板当参考图：分配镜头号（`<Picture 4> is a storyboard reference for [Shot 1] and [Shot 2], defining their viewpoint, subject placement, and shot order.`）
- ✅ 标准写法：`<Picture 1> is the woman's appearance anchor: preserve her facial identity, copper curls, and green jacket.`
- ❌ 禁用写法：`<Subject 1> is the woman shown in <Picture 1>. ...`（本手册第 0 节明令禁止）
- **三视图 / 设定图专用防御句**（必写）：
  `<Picture 1> is a three-view character sheet (front, side, back views on a plain background). It is not a frame of the target video; its three-view sheet layout must not appear on screen, and only one <主体> may be visible in the frame.`

## 8. 硬约束（中文社区技巧）

- **光线必写**：日景/夜景/暖光/冷光（不写可能黄昏配冷白顶灯）
- 破折号绑硬约束：`——日景|老式公寓厨房|手持微晃|无对白`
- 括号塞感官细节：`(铁锈味空气，远处断续汽笛)` 渗透进每帧
- 负面指令具体化：列出不能变的特征（脸型/发型/服装/比例），不写"不要出错"

## 9. 分步测试（重要工作法）

```
Pass 1 角色+场景（1图/1动作/静态/无对白）→ Pass 2 加运动 → Pass 3 加声音对白
→ Pass 4 加剪辑/第二角色/故事板 → Pass 5 最终版
接近理想后一次只改一个变量
```

## 10. 最终检查清单

模式选对？**全文搜 `<Subject` 零命中（只用 `<Picture N>`）**？三视图设定图有防御句？参考图有职责？动作密度现实？运镜前置绑焦点？日景/夜景写清？声音分层+音乐时间轴？对白短+有 ID？结尾姿势/构图明确？负面指令具体？— 全 ✅ 再生成。

## 11. 交付格式（用户偏好）

- **聊天直发，不写文件**；固定三项：英文版（工具粘贴用）+ 中文备注版（每镜头标精确时间段）+ 建议参数
- 每镜头标注：`[Shot N] X.XX–Y.YY 秒：干什么`
- **声音必须内联进每个镜头**（用户硬性要求，2026-08-08）：每个镜头描述 = 画面 + **该时段的精确声音**（标注秒数，如 "2.0s 叉子碰瓷一声叮；2.0–4.5s 衣料摩擦声"）。`overall_soundscape` 只放**贯穿全片的底噪层**（房间氛围等持续声），关键声音事件一律写进对应镜头，防止声音时间漂移（用户实测声音会提前/延后出现）
- 参数默认：576×1024（竖屏）/ 1344×768（横屏）/ step 20 / fps 20 / seed **42**（正数，勿填 -1，H3 后端 RandomNoise 最小 0）/ SageAttention 自动
- 有参考图 → I2VA（1 张）或 Ref2VA（多张），无图 → T2VA（去掉指令行）
- **参考标签自检**：成稿里 `<Subject` 必须零命中，一律 `<Picture N>`（见第 0 节）
- **通知时序（用户硬性要求，2026-09-15）**：微信通知必须在**回复结束的瞬间**触达，不能早于回复、也不要用固定延时糊。机制 = 已注册的 Agent 客户端的 `Stop` hook（`~/.<AGENT_HOME>/settings.json`），它在回复完成时自动拉起 `notify_done_send.py`。我只需在回复前最后一次工具调用跑 `notify_done.sh "任务名" --arm`（清锁 + 写任务名 + 排 60 秒兜底）；**不要再手动调用延时/立即推送**，每轮只 arm 一次，禁止过程中反复推送。
  - 可靠调用姿势（本机 PATH 被 shim 破坏时）：
    `"<BASH>" -lc 'export PATH=/usr/bin:/bin:$PATH; bash ~/.<AGENT_HOME>/scripts/notify_done.sh "任务名"'`
