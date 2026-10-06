# 案例 02 · 《深夜剑道》20 秒两段接续

> 这是本教程的**第二个完整案例**，也是第一个 **20 秒（2 段 × 10s，latent 级真接续）** 的案例。
> 案例 01 证明了「单段 10 秒能出片」，本案例证明的是：**两段能接成一条看不出接缝的 20 秒短剧**。
> 成功的地方和没做到的地方都如实写在这里。

---

## 成片

**20 秒 = 2 段 × 10 秒 / Motion Context latent 接续 / 464 帧 / 861 秒总生成 / 单角色 / Ref2VA**

<https://github.com/seeyouagain-laoda/comfy-minimax-h3-tutorial/raw/main/examples/case-02-sword/01_output_20s.mp4>

### 全片 20 帧验收拼图

![20 帧验收](02_verify_20frames.jpg)

*每 23 帧抽 1 帧。前 9 帧是第 1 段（举剑 → 挥剑 → 掀飞零食袋），后 11 帧是第 2 段（立正 → 画外音 → 藏零食 → 重新举剑）。景别和光线在两段之间没有跳变。*

### 参考图 → 成片

![参考图与成片对比](04_compare_ref_vs_output.jpg)

*左：送进模型的原始参考图。右：成片第 150 帧。呆毛、IV 发牌、围裙小蓝鲸、鲸尾星点全部对上。*

### 接缝 14 帧验收（本案例的核心证据）

![接缝检查](05_seam_check_14frames.jpg)

*成片第 237–250 帧（接缝前后各 7 帧）。14 帧全部连贯：同一姿势、同一光位、同一把木剑、同一袋掉在地上的零食。**没有跳切，没有第三人，没有色偏。** 这是 latent 级接续的视觉证据——如果是"末帧续接"（解码成像素再编码），这里一定会看到一次解码抖动。*

---

## 1. 文件清单

| 文件 | 内容 | 规格 |
|---|---|---|
| `01_output_20s.mp4` | **最终成片**（两段拼接） | 464 帧 / 19.365s / 24fps / 864×480 / aac 双声道 |
| `02_verify_20frames.jpg` | 全片每 23 帧抽 1 帧的验收拼图 | 360×200 每格，6×4 |
| `03_reference_input.png` | 送进模型的**原始参考图** | 2048×2048 |
| `04_compare_ref_vs_output.jpg` | 参考图 vs 成片第 150 帧并排对比 | 左右各 420×420 |
| `05_seam_check_14frames.jpg` | 接缝前后各 7 帧拼图 | 260×146 每格，7×2 |
| `06_clip1_10frames.jpg` | 第 1 段 10 帧验收 | 380×214 每格，5×2 |
| `07_clip2_10frames.jpg` | 第 2 段 10 帧验收 | 360×200 每格，5×2 |
| `08_clip1_10s.mp4` | 第 1 段单独成片 | 243 帧 / 10.125s |
| `09_clip2_10s.mp4` | 第 2 段单独成片（已 Trim） | **221 帧 / 9.208s** |
| `prompts/clip1_full_prompt.txt` | 第 1 段**实际送进模型的完整提示词**（公共段+分镜段拼接后） | 5455 chars |
| `prompts/clip2_full_prompt.txt` | 第 2 段同上 | 5562 chars |
| `scripts/run_ep_sword.py` | 可直接复现的 runner（环境变量驱动，路径已脱敏） | — |

### 帧数是怎么算的（本案例最容易搞错的地方）

```
第 1 段              = 243 帧（10.125s）  ← 完整生成
第 2 段实际交付帧数  = 243 − 22 = 221 帧  ← Motion Context 钉了 22 帧，Trim 剪掉
成片总帧数          = 243 + 221 = 464 帧（19.365s）
```

> 🔴 **如果你算成 486 帧，说明你没开 Trim**——那 22 帧重复画面会留在成片里，
> 观众会看到一段 0.92 秒的"卡住"。日志里确认这两行：
>
> ```
> h3_motion_context: video from latent, video/head, 22 frames -> 7 cond blocks at indices 0..18
> h3_motion_context: tail trimmed 267 samples (8.34ms) so audio matches 221 frames exactly
> ```

**本机实测**：第 1 段 **404 秒**，第 2 段 **457 秒**（接续段略慢，因为它要额外处理钉帧条件块），总计 **861 秒 ≈ 14.4 分钟**。

---

## 2. 参数（可直接复制）

| 项 | 值 |
|---|---|
| 时长 | **20s = 2 段 × 10s**（>15s 必须拆段） |
| 接续方式 | **Motion Context latent 钉帧**（`context_length=22` / `audio_context_length=24`） |
| 通道 | **Ref2VA**（挂参考图锁角色） |
| 画布 | **864 × 480**（0.4 MP） |
| 步数 | **8 步** + `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16` LoRA @1.0 |
| 采样器 / 调度 | `er_sde` + `simple` |
| 底模 | `UNETLoader` 加载 **ref2va** 权重（**不是** fl2va，见 §7 第 1 条） |
| 参考图 | 1 张，正面全身，2048×2048，`ref_image_size='max'` |
| seed | **每段不同**（本例 `SEED+1` / `SEED+2`，脚本自动递增） |
| 二采放大 | 未开（本次是 0.4MP 原生） |
| 后期 | **无变速**。原速播放即正常观感 |

> 🔴 **seed 必须每段不同**。两段用同一个 seed 会让模型产生"这大概是同一段"的先验，
> 反而在接缝处出现重复感。脚本里是 `SEED + clip_index`。

---

## 3. 怎么跑（完整命令）

### 3.1 前置

- ComfyUI ≥ 0.34.0，且已装社区节点 **`ComfyUI-H3-Motion-Context`**（提供 `MiniMaxH3MotionContext` / `…SaveLatent` / `…LoadLatent` / `…Trim`）
- 有一份**含 Motion Context + MultiImageLoader 的 ref2v 工作流 JSON**
- 参考图已放进 `<COMFYUI_ROOT>/input/`，文件名**纯英文**（`shenshen_ref.png`）
- 引擎已启动，且 `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8188/system_stats` 返回 **200**

### 3.2 环境变量驱动的 runner

`scripts/run_ep_sword.py` 是一个把"打补丁 → 转 API → 提交 → 等结果"全包了的薄封装，
核心是覆盖底层 runner 的两个变量：

```python
R.BASE_PROMPT = """..."""   # 公共段（角色卡 + 场景框架 + 声音）
SEG1 = "..."                  # 第 1 段分镜
SEG2 = "..."                  # 第 2 段分镜
```

运行：

```bash
# ① 干跑预检（DRY=1 不烧显存，只打印接线）
DRY=1 CLIP=1 "<VP>/python.exe" run_ep_sword.py
DRY=1 CLIP=2 "<VP>/python.exe" run_ep_sword.py

# ② 第 1 段（首段：MotionContext / LoadLatent / Trim 自动 bypass）
CLIP=1 SEED=880601 REF_IMAGE=shenshen_ref.png DURATION=10 "<VP>/python.exe" run_ep_sword.py

# ③ 抽帧自检 → 【人工审核通过再继续】

# ④ 第 2 段（自动 LoadLatent=1 / MotionContext ON / Trim ON / SaveLatent=2）
CLIP=2 SEED=880601 REF_IMAGE=shenshen_ref.png DURATION=10 "<VP>/python.exe" run_ep_sword.py

# ⑤ 拼接（Trim 已把钉子头剪掉，直接首尾相接）
printf "file 'clip1_00001_.mp4'\nfile 'clip2_00001_.mp4'\n" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy 深夜剑道_深深_20s.mp4
```

### 3.3 干跑必须逐行核对这 5 条

```
ref image -> shenshen_ref.png ×2 @2048（并改接线到 slot 1）    ← 参考图真生效的关键
接线修正: 336.slot2 -> 191 改为 slot 1 (image_1)                ← 同上，不改这行参考图是全黑空图
#237 MotionContext bypass(首段) (context=22, audio=24)            ← 首段必须 bypass
#202 LoadLatent clip_index=0 bypass(首段)
#218 SaveLatent clip_index=1                                    ← 首段必须存 latent，否则第2段无从接续
#238 LoRA -> minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16 @1.0 ← 必须是 comfyui 格式
#339 UNETLoader -> ref2va 权重
duration -> 10.0s
resolution -> 16:9 (Widescreen) @ 0.4 MP
```

第 2 段干跑要变成：

```
#237 MotionContext ON (context=22, audio=24)
#202 LoadLatent clip_index=1 ON
#213 Trim ON
#218 SaveLatent clip_index=2
```

**任何一行不对都不要提交。**

---

## 4. 提示词写法（本案例的核心）

### 4.1 公共段：只写角色 + 场景框架，**不写道具**

```
integrated_multimodal_description:
[reference generation] Image 1 defines the character exactly — reproduce the chibi
whale-girl maid from Image 1 with identical face shape and facial features, identical
hairstyle and hair colour, identical outfit and accessories, identical body proportions
and identical art style. Do NOT redesign, restyle, recolour, reinterpret or "improve"
her. Keep her faithful to Image 1 in every shot.
[Subject] The chibi whale-girl maid from Image 1 is the main subject of every shot and
must stay on screen for the whole shot: about 2.5 heads tall, long twin-tails of
gradient blue hair (deep navy roots to pale blue-white tips), a single curled ahoge,
a blue IV-shaped hair clip, small whale-fin ears, large pale-blue ringed eyes, a
deep-navy and white maid dress with a white frilled apron bearing a small blue whale
outline on the chest, a short blue-white gradient whale tail, and small chubby chibi
hands. Her face, hair, outfit, accessories and proportions are all fixed by Image 1.
[Setting] The same quiet Japanese-style apartment living room at night in every shot:
warm paper-lamp light from frame right, tatami and wooden floor, a low dark-wood
table, a sliding shoji screen behind, deep night outside the window. Medium shots and
close-ups only, never a full wide shot.
Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel palette
— NOT photorealistic, no photograph, no live action, no 3D render.

overall_soundscape:
Quiet late-night room ambience: a faint wall-clock tick, distant traffic hum through the
window, soft cloth and footstep rustle on tatami, a light wooden sword whoosh, no
background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack
```

**逐条说明为什么这么写**：

| 段 | 作用 | 不写会怎样 |
|---|---|---|
| `[reference generation]` + 「reproduce **EXACTLY** … do NOT redesign」 | 🔴 强制照抄参考图而不是按文字重画 | 角色被重画成"大概像" |
| `[Subject] … must stay on screen for **the whole shot**` | 🔴 钉住主体，防中途消失 | 模型跑去拍道具空镜（案例 01 踩过） |
| 外貌清单列**全部可辨特征** | 呆毛 / IV 发牌 / 围裙小蓝鲸 / 鲸尾星点，逐项列 | 缺项 → 角色退化成"普通蓝发女仆" |
| `[Setting]` 只写框架，**不写具体道具** | 🔴 本案例刻意没把"零食袋"写进公共段 | 写太具体 → 模型把它当展示主体，角色被挤出去 |
| `[Setting]` 写死"**every shot** 同一场景同一光位" | 🔴 两段接续的**光向锚** | 接缝处色温跳变（头号接缝元凶） |
| `Style: … NOT photorealistic` | 全局画风兜底 | 无角色镜头漂成照片级写实 |
| `overall_soundscape` | 环境音 | 出现怪叫 |
| `non_diegetic_music: no music…` | 明确无 BGM | 留空可能自己加配乐 |

### 4.2 分镜段（第 1 段，6 镜）

```
_风格锚 = " Style: hand-drawn 2D anime, flat cel shading, visible sketch lines,
           warm pastel palette — NOT photorealistic, no photograph, no live action,
           no 3D render."     ← 每一镜末尾都要重复

[Shot 1] At 00:00.000, a medium shot at eye level. The maid stands alone in the centre of
the night living room facing the camera, both small hands gripping a plain wooden practice
sword held vertically in front of her chest, feet planted shoulder-width apart, twin-tails
and whale tail hanging still. She takes one deep breath, closes her eyes, and raises the
sword straight above her head in a slow formal salute. Sound inline: 0.00-2.20s a faint
clock tick and her bare feet shifting once on the tatami. Camera static, focus held on her
upper body. +风格锚

[Shot 2] At 00:02.400, cut to a closer medium shot from slightly low angle. She snaps the
sword down to her side, opens her eyes with a fierce determined glint, and declares loudly
with clear lip movement, <d>[Chinese] 深深，开始修行！</d> Her whale tail lifts and wags
once behind her on its own. Sound inline: 2.40-3.20s her bright young female voice in
standard Mandarin with a comedic punch; 2.80s one light wooden swish. +风格锚

[Shot 3] At 00:03.600, cut to a medium shot, three-quarter view. She steps into a clumsy
sideways shuffle across the tatami, both hands swinging the wooden sword in a big awkward
arc, her whole body wobbling out of balance while her twin-tails lag behind a beat late.
She half-stumbles, catches herself, and puffs her round cheeks in frustration. Sound
inline: 3.60-5.20s rhythmic wooden swishes and soft footfalls; 4.60s one small comedy
squeak of floor board creak. Camera pans slightly to keep her centred. +风格锚

[Shot 4] At 00:05.400, cut to a low medium shot. She plants her feet again, raises the wooden
sword high over her head with both arms trembling, and swings it down in one single heavy
overhead chop. On the impact the camera shakes once and a burst of air lifts a small paper
snack bag off the low table behind her. Sound inline: 5.40-6.20s a fast downward whoosh
ending in a solid thud; 6.20s crinkling paper. +风格锚

[Shot 5] At 00:06.600, cut to a medium close-up on her face. She freezes in her finishing
pose, wooden sword held down at her side, both eyes wide and round, tiny ahoge standing
straight up in shock, mouth slightly open. Behind her the paper snack bag drifts down onto
the tatami. Sound inline: 6.60-7.60s absolute silence except the clock tick; 7.60s soft
paper landing. +风格锚

[Shot 6] At 00:07.900, a tighter close-up. Still frozen, she slowly lowers her gaze from the
snack bag on the floor to her own starry whale tail, which is stuck stiffly straight out
behind her like a stiff plank, then gives one tiny guilty wiggle. She blinks twice, swallows,
and tightens her grip on the wooden sword until her knuckles go pale. Sound inline:
7.90-10.00s room tone only, one faint tail flap; 9.20s a quiet swallow. Camera pushes in
very slowly. +风格锚
```

### 4.3 分镜段（第 2 段，6 镜）—— **开头逐字复述上段结尾**

```
[Shot 1] At 00:00.000, the same night living room, the same warm paper-lamp light from frame
right. The maid is in exactly the same position the previous clip ended in — a tight close-up,
she has just lowered her gaze to her own stiff starry whale tail, both small hands white-knuckled
on the wooden practice sword at her side, the crumpled paper snack bag lying on the tatami just
behind her heel. She holds perfectly still for a beat, then at 01.600 snaps her eyes shut, forces
a tiny straight-lipped smile onto her face and straightens her back like a soldier standing
to attention. Sound inline: 0.00-1.60s room tone and clock tick; 1.60s one crisp sword-cloth
swish as she shoulders the blade. +风格锚

[Shot 2] At 00:02.400, cut to a medium shot from slightly low angle. Facing the camera squarely,
she holds the wooden sword vertically before her chest in a crisp formal salute and bows once,
small and stiff, twin-tails bouncing with the motion. An off-screen voice, calm and flat, an
unseen person occupying the camera position and never entering frame:
<d>[Chinese] 深深，你在练什么？</d> Sound inline: 2.40-3.60s the calm adult male voice line. +风格锚

[Shot 3] At 00:04.000, cut to a medium close-up. She keeps her eyes shut, still in the salute,
and mumbles in a tiny guilty voice with clear lip movement, <d>[Chinese] 剑、剑道……</d>
One drop of sweat slides down her temple. Behind her, out of focus but visible, her starry
whale tail slowly swings around and quietly pushes the crumpled paper snack bag further under
the low table. Sound inline: 4.00-5.40s her small hesitant female voice line; 5.00s faint soft
paper scraping on wood. +风格锚

[Shot 4] At 00:05.800, cut to a wider medium shot of the whole corner. She has now slipped the
wooden sword under her arm like a schoolbag, tiptoes silently toward the low table and peeks
underneath it from a crouch, one hand braced on the tabletop, her tail wagging once behind
her. Her face goes bright with a huge delighted grin when she confirms the snack bag is safely
hidden. Sound inline: 5.80-6.60s light tiptoe footfalls; 6.60-7.20s one small satisfied giggle. +风格锚

[Shot 5] At 00:07.400, cut back to a medium close-up. Still crouched by the table, she turns her
head to the camera and gives one tiny, utterly unapologetic thumbs-up while holding the wooden
sword sideways under her arm, eyes curving into smug crescents, twin-tails bouncing. Sound
inline: 7.40-8.20s the soft tail flap behind her. +风格锚

[Shot 6] At 00:08.600, the camera holds the same medium close-up as she stands back up, plants
her feet, lifts the wooden sword high above her head once more for another round of practice,
determined and eager, while her whale tail wags in perfect sync behind her. Hold on her eager
face until 10.000. Sound inline: 8.60-10.00s one light wooden swish, room tone and clock tick,
no dialogue. +风格锚
```

### 4.4 第 2 段开头的写法（本案例最关键的一条）

> 🔴 **钉住的帧不是建议 —— 每一步采样都会重新注入，模型在那段区间里画不出别的东西。**

本案例第 2 段的 `[Shot 1]` 花了 **4 行**（占整段提示词的 12%）做三件事：

| 做什么 | 为什么 |
|---|---|
| 写"**the same** night living room, **the same** warm paper-lamp light **from frame right**" | 光向逐字锁定，防色温跳变 |
| 写"**exactly the same position the previous clip ended in**"，然后把姿势/道具/状态逐项列出 | 模型不知道上一段存在，钉帧就是它唯一的"上一段" |
| 把**变化点推到 01.600** | 22 帧钉子 ≈ 0.92s，变化必须落在钉子之后，否则模型会把"钉住的旧画面"和"你想要的新画面"**两个都渲染** → 画面里出现**第三个人** |

**如果第 2 段开头描述和第 1 段结尾不一致，模型不会二选一，而是两个都渲染。**

### 4.5 玩法要点速查

| 要点 | 本案例怎么用 |
|---|---|
| 台词用 `<d>[Chinese] …</d>` 包裹 | 三处台词，最长 7 字 |
| 台词只说自称 / 极短 | 「深深，开始修行！」「剑、剑道……」（8 步时语音是输出最弱环节） |
| 画外音必须写死 | `An off-screen voice… an unseen person occupying the camera position, **never entering frame** and never seen. Voice only — male, calm and flat.` |
| 道具拟人化（本作亮点） | `her starry whale tail slowly swings around and quietly pushes the crumpled paper snack bag further under the low table` —— 尾巴抢戏比台词好使 |
| 收尾靠"不靠台词的第二笑点" | 第 2 段 S4 探头确认零食藏好了 → 纯视觉，不需要听台词也懂 |
| 每镜末尾重复风格锚 | 12 镜全都重复了 |
| 声音内联进每一镜 | `Sound inline: 5.40-6.20s …` 精确到 0.1s |

---

## 5. 验收工作流

### 5.1 机器校验

```bash
ffprobe -v error -show_entries format=duration \
  -show_entries stream=codec_type,width,height,nb_frames -of default=nw=1 IN.mp4
```

| 检查项 | 第 1 段 | 第 2 段 | 成片 |
|---|---|---|---|
| 分辨率 | 864×480 ✅ | 864×480 ✅ | 864×480 ✅ |
| 帧数 | 243 ✅ | **221**（=243−22）✅ | **464**（=243+221）✅ |
| 时长 | 10.125s | 9.208s | 19.365s |
| 音轨 | aac 双声道 ✅ | aac 双声道 ✅ | aac 双声道 ✅ |

### 5.2 抽帧拼图（每段各抽一次）

```bash
ffmpeg -y -i clip1_00001_.mp4 -vf "select='not(mod(n\,24))',scale=380:-1,tile=5x2" -frames:v 1 06_clip1_10frames.jpg
ffmpeg -y -i clip2_00001_.mp4 -vf "select='not(mod(n\,22))',scale=360:-1,tile=5x2" -frames:v 1 07_clip2_10frames.jpg
```

**要看的**：景别有没有按分镜切？有没有哪镜是静止的？画风有没有漂？

### 5.3 接缝检查（🔴 多段片必做，案例 01 没有这一步）

```bash
ffmpeg -y -i 01_output_20s.mp4 \
  -vf "select='between(n,237,250)',scale=260:-1,tile=7x2" -frames:v 1 05_seam_check_14frames.jpg
```

帧号算法：`接缝在第 1 段最后一帧 = 243-1 = 242`（成片索引），
所以抽 `242-5 .. 242+8` 覆盖钉子两侧。

**要看的**：
- 有没有**跳切**（姿势突变 / 景别突变）→ 有就重跑第 2 段
- 有没有**第三人** → 第 2 段开头没复述上段结尾
- 有没有**色温跳变** → `[Setting]` 的光向描述没逐字锁定
- 钉住的那 22 帧有没有**卡住不动** → 变化点推得太晚，要往前挪到 1.2–1.5s

### 5.4 LoRA 静默失效检查

```bash
# 只看本次提交之后新增的日志行，不要 grep 整个历史日志
grep "lora key not loaded" <本次新增日志>
```

本案例两段都是：`✅ LoRA 已生效（无未加载 key）`。

### 5.5 人工验收清单（6 条）

| # | 检查 | 本案例结果 |
|---|---|---|
| 1 | 帧数 / 音轨 / 分辨率 | ✅ 第2段 221 帧，成片 464 帧 |
| 2 | **角色一致性**：外貌特征逐项对上参考图 | ✅ 20 帧全部一致 |
| 3 | **景别按分镜切换** | ✅ 6 中景 + 6 特写/近景 |
| 4 | **画风统一**，无照片级写实漂移 | ✅ 全 2D 动画风 |
| 5 | **角色没中途消失** | ✅ 20 帧全程在画内 |
| 6 | 🔴 **接缝无跳切 / 无第三人 / 无色偏** | ✅ 14 帧连贯 |

---

## 6. 逐镜对照（分镜 → 实际）

### 第 1 段

| 镜 | 分镜写的 | 实际 | 达成 |
|---|---|---|---|
| 1 | 闭眼深呼吸 + 举剑正上方行礼 | ✅ 举剑过顶，呆毛随之动 | ✅ |
| 2 | 睁眼凶光 + 喊「深深，开始修行！」+ 尾巴自己摇 | ✅ 口型清楚，尾巴抬起 | ✅ |
| 3 | 侧向踉跄 + 大幅挥剑 + 鼓腮 | ✅ 挥剑木剑、头发滞后甩 | ✅ |
| 4 | 力劈华山 + 镜头一震 + **零食袋被掀飞** | ✅ 剑风把红色零食袋扬起 | ✅ |
| 5 | 定格呆住 + 零食袋飘落 | ✅ 圆眼 + 呆毛立起 | ✅ |
| 6 | 低头看僵住的尾巴 + 心虚扭一下 | ✅ 尾部特写有戏 | ✅ |

### 第 2 段

| 镜 | 分镜写的 | 实际 | 达成 |
|---|---|---|---|
| 1 | 复述上段结尾 + 1.6s 后闭眼假笑立正 | ✅ 接缝 14 帧连贯 | ✅ |
| 2 | 立剑行礼 + 画外音「深深，你在练什么？」 | ✅ 中景立正 | ✅ |
| 3 | 闭眼小声「剑、剑道……」+ 一滴汗 + **尾巴把零食袋推回桌下** | ✅ 尾巴入镜，准（见下方不足 2） | ✅ |
| 4 | 剑夹腋下 + 蹲下探头看桌底 + 咧嘴 | ✅ 探头动作演到 | ✅ |
| 5 | 回头一个得意小拇指 | ✅ 得意表情对上 | ✅ |
| 6 | 重新举剑 + 尾巴同步摇 | ✅ 收尾成立 | ✅ |

---

## 7. 实测不足（如实记录）

**这一节比成功记录更有价值。**

| # | 问题 | 根因 | 下次怎么改 |
|---|---|---|---|
| 1 | **底模通道容易配错** | 社区工作流 `HybridLoader` 挂的是 **fl2va** 底模 + fl2v turbo LoRA，但接的是 **ReferenceToVideo** 节点。r2v 的正确配对是 **ref2va 底模** | runner 里改用 `UNETLoader` 单模型加载 ref2va 权重。⚠️ 本机 `HybridLoader` 还有第二个坑：base 与 overlay 两个权重的 **key 集合必须一致**——官方权重 key 无前缀，社区 ref2va 权重 key 带 `model.diffusion_model.` 前缀，混用直接 `RuntimeError` |
| 2 | **零食袋在第 2 段偏小、位置飘** | 写的是「out of focus but visible」的背景道具，模型给了很小的面积 | 零食袋这种**第二笑点载体**要升级成显式动作镜（给它一整个 `[Shot]`），或者干脆提前 0.5s 让它进画 |
| 3 | **木剑剪影偏细长**，不像正经练习剑 | 提示词只写 `plain wooden practice sword`，没给形状约束 | 写 `a short blunt wooden practice sword (shinai), thicker than a chopstick` —— 用**比较句**给形状锚 |
| 4 | **台词中文咬字略糊** | 8 步 turbo 是语音输出的最弱环节（与案例 01 同一瓶颈） | 想要清晰台词 → 提到 12/16 步；或继续压短台词（本例最长 7 字，明显好于案例 01 的长句） |
| 5 | **第 2 段整体比第 1 段"更稳"了一点** | 接续段 22 帧钉帧 = 复刻倾向，第 2 段的画面自由度天然低于第 1 段 | 想让第 2 段更"活"：把变化点从 1.6s 提前到 1.2–1.5s，并给保持段安排**非动作变化**（光效窜动 / 呼吸 / 发丝摆动） |

---

## 8. 这个案例新增验证了哪些方法

| 方法 | 案例 01 | 案例 02（本案例） |
|---|---|---|
| 角色参考图锁保真 | ✅ | ✅ 20 帧全部一致 |
| 快剪节奏（1.5–3s/镜） | ✅ | ✅ 12 镜 / 20s，原速可播 |
| 每镜重复风格锚 + 全局兜底 | ✅ | ✅ |
| 8 步 turbo + LoRA key 检查 | ✅ | ✅ 两段 0 丢 key |
| **Motion Context latent 接续** | — | ✅ **接缝 14 帧连贯，无跳切/无第三人/无色偏** |
| **Trim 帧数核算（243−22）** | — | ✅ 成片 464 帧，与预期完全一致 |
| **第 2 段开头逐字复述上段结尾** | — | ✅ 这是本案例接缝成功的直接原因 |
| **接缝落在静止点** | — | ✅ 「掀飞零食袋 → 呆住」两段都在定格 |
| **道具不进公共段** | ⚠️ 案例 01 踩坑 | ✅ 零食袋只在具体镜写，角色全程在画内 |
| 纯道具镜 | ❌ 失效 | —（本案例无纯道具镜） |
| 台词只说自称 | ⚠️ | ⚠️ 改善但仍偏糊，8 步是瓶颈 |

---

## 9. 如果你照着做

1. **先只做 10 秒单段**（照案例 01），确认角色锁得住再上两段
2. 直接复制 §2 的参数
3. 直接复制 `prompts/` 里两段提示词全文（把外貌清单换成你角色的）
4. 参考图要求：**干净正面全身、纯色浅背景、2048px**
5. **第 2 段的开头必须复述第 1 段结尾**，变化点推到 1.2s 之后 —— 这是本案例最重要的一条
6. **接缝选在"两段都静止"的时刻**（不要选在剧烈运动中）
7. 跑完按 §5 验收，**特别是 5.3 接缝检查**
8. 记住帧数是 `243 + 221 = 464`，不是 486