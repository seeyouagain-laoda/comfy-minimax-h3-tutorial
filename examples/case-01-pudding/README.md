# 案例 01 · 《偷吃布丁》10 秒单段

> 这是本教程的**第一个完整案例**，也是所有方法（提示词规范 / 快剪节奏 / 验收流程）
> 实际跑通的一次记录。**成功的地方和没做到的地方都如实写在这里。**

---

## 1. 成片

| 文件 | 内容 | 规格 |
|---|---|---|
| `01_output_10s.mp4` | 最终成片 | 243 帧 / 10.125s / 24fps / 864×480 / aac 双声道 |
| `02_verify_10frames.jpg` | 每 24 帧抽 1 帧（共 10 帧）的验收拼图 | 380×214 每格 |
| `03_reference_input.png` | 送进模型的**原始参考图**（未抠底） | 2048×2048 |
| `04_compare_ref_vs_output.jpg` | 参考图 vs 成片同帧并排对比 | 左右各 400×400 |

**本机实测**：生成耗时 **417 秒**（约 7 分钟），单段 10 秒。

---

## 2. 参数（可直接复制）

| 项 | 值 |
|---|---|
| 时长 | 10s **单段**（≤15s 一次跑完，不需接续） |
| 通道 | **Ref2VA**（挂参考图锁角色） |
| 画布 | **864 × 480**（0.4 MP，官方默认） |
| 步数 | **8 步** + `turbo_8step` LoRA @1.0 |
| 帧率 | 24 |
| 帧数 | 243（`max(5,round(10*24))` → `240`，对齐 17k+5 → `243`） |
| 采样器 / 调度 | `res_multistep` + `simple` / shift 6 |
| 噪声控制 | `control = fixed` |
| seed | 固定（`RandomNoise` 的 control 必须是 fixed，否则多镜头无法连续） |
| 参考图 | 1 张，正面全身，浅色纯背景 |
| 二采放大 | 未开（本次是 0.4MP 原生） |

---

## 3. 原始提示词（全文，未删减）

### 3.1 公共段

```
integrated_multimodal_description:
[reference generation] Image 1 defines the character exactly — reproduce the chibi
whale-girl maid from Image 1 with identical face shape, facial features, hairstyle,
hair colour, outfit, accessories, body proportions and art style; do NOT redesign,
restyle, recolour or reinterpret her. Keep her faithful to Image 1 in every shot.
[Subject] The chibi whale-girl maid from Image 1 is the only subject of this video and
must stay on screen in every single shot: about 2.5 heads tall, long twin-tails of
gradient blue hair (deep navy roots to bright blue tips), a single curled ahoge, a blue
IV-shaped hair clip on her forehead, small whale-fin ears, large pale-blue ringed eyes,
a deep-navy and white frilled maid dress with a white apron bearing a small blue whale
outline on the chest, a blue-purple whale tail with starry speckles, and small navy shoes.
[Setting] A bright, warm, fully natural-colour home kitchen: a tall white refrigerator
with its door open, a low wooden table, warm afternoon light on the floor.
A hand-drawn animation in a soft painterly style with visible sketch lines, in full
natural colour. The story is told through close-ups and medium shots and partial
details, never a full wide shot.

overall_soundscape:
Quiet room ambience, a faint clock tick, a soft refrigerator hum, a small fridge-door
suction, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch
lines, in full natural colour — never photorealistic, never a photograph, never live
action, never a 3D render. Every single shot, including prop and environment shots,
keeps this hand-drawn 2D anime style.
```

**逐条说明每段为什么这么写**：

| 段 | 作用 | 不写会怎样 |
|---|---|---|
| `[reference generation]` + 「reproduce **EXACTLY** … do NOT redesign」 | 🔴 强制照抄参考图而不是按文字重画 | 角色会被重画成"大概像" |
| `[Subject] … must stay on screen in **every single shot**` | 🔴 钉住主体，防止中途消失 | 模型会跑去拍道具空镜 |
| 外貌清单 | 列出**全部可辨特征**（呆毛 / IV 发牌 / 鲸耳鳍 / 围裙小蓝鲸 / 鲸尾星点） | 特征丢失，角色变成"普通蓝发女仆" |
| `[Setting]` | 场景只写框架，**不写具体道具** | 道具写太具体会把角色挤出去 |
| `style_lock` | 全局画风兜底 | 某镜没角色时画风漂成照片级写实 |
| `overall_soundscape` | 环境音 | 不写会出现怪叫 |
| `non_diegetic_music: no music…` | 明确无 BGM | 留空可能自己加配乐 |

### 3.2 分镜段（7 镜 × 1.5 秒）

```
_风格锚 = " Style: hand-drawn 2D anime, flat cel shading, visible sketch lines,
           warm pastel palette — NOT photorealistic, no photograph, no live action,
           no 3D render."

[Shot 1] At 00:00.000, a close-up inside a white refrigerator: a single glass cup of pale
yellow pudding sits alone on the middle shelf, lit by the fridge light. Camera static. +风格锚

[Shot 2] At 00:01.500, cut to an extreme close-up of the maid girl's eyes: her pale-blue
eyes lock onto the pudding, pupils dilating, a tiny excited gleam. Camera static. +风格锚

[Shot 3] At 00:03.000, cut to a close-up of her small hand reaching in and lifting the
pudding cup off the shelf. Camera static. +风格锚

[Shot 4] At 00:04.500, cut to a close-up of her face: cheeks puffed out as she chews, eyes
squeezed shut in bliss, a tiny smear of pudding at the corner of her mouth.
Camera static. +风格锚

[Shot 5] At 00:06.000, cut to a medium shot: the fridge door swings shut and the maid girl
stands leaning back against it, hands behind her back, wearing an innocent angelic smile.
Camera static. +风格锚

[Shot 6] At 00:07.500, cut to a close-up of her face: she turns her head sharply toward the
camera, her ahoge standing straight up, a brief startled pause. An off-screen voice asks:
<d>[Chinese] 布丁呢？</d> Camera static. +风格锚

[Shot 7] At 00:09.000, cut to a close-up of her face: she quickly wipes the corner of her
mouth with the back of her hand, then beams up with a sweet innocent smile and answers:
<d>[Chinese] 深深的……不知道呀。</d> Camera static. Hold. +风格锚
```

**写法要点**：

| 要点 | 说明 |
|---|---|
| `[Shot 1]` **不带时间戳**，后续镜递增 | 官方硬规则 |
| 每镜**末尾都重复风格锚** | 单镜不写就可能被漂走 |
| 每镜只写 `Camera static` **一种**运镜 | 同镜写两种运镜会空间畸形 |
| 台词用 `<d>[Chinese] …</d>` 包裹 | H3 的中文标记语法 |
| 台词极短、只说自称 | 8 步时语音是输出最弱环节，长句咬字不清 |
| 7 镜 × 1.5 秒 = 10.5 秒 | **靠"切"推进，不靠"演"**（见 `shot-rhythm.md`） |

---

## 4. 验收工作流（这部分最值得学）

出片**不等于**做完了。下面是本案例实际走的验收流程。

### 4.1 机器校验（客观）

```bash
python scripts/probe.py 01_output_10s.mp4
```

| 检查项 | 本案例结果 |
|---|---|
| 可解码 | ✅ |
| 帧数 / 时长 | 243 帧 / 10.125s（与预期一致） |
| 音轨存在 | ✅ aac 双声道（**H3 自带声音**，不是后期贴的） |
| 音频非静音 | ✅ RMS 正常 |
| 中间帧非黑图 | ✅ avg 126.7 |

### 4.2 抽帧拼图（看节奏）

```bash
ffmpeg -y -i 01_output_10s.mp4 \
  -vf "select='not(mod(n\,24))',scale=380:-1,tile=5x2" \
  -frames:v 1 02_verify_10frames.jpg
```

**要看的**：景别有没有按分镜切？有没有哪镜是静止的？画风有没有漂？

### 4.3 参考图对比（看角色保真）

把参考图和成片同一时刻并排：

```bash
ffmpeg -i 03_reference_input.png -vf \
  "scale=400:400:force_original_aspect_ratio=decrease,pad=400:400:(ow-iw)/2:(oh-ih)/2:color=white" -frames:v 1 /tmp/r.png
ffmpeg -i 01_output_10s.mp4 -vf \
  "select='eq(n\,120)',scale=400:400:force_original_aspect_ratio=decrease,pad=400:400:(ow-iw)/2:(oh-ih)/2:color=black" -frames:v 1 /tmp/o.png
ffmpeg -i /tmp/r.png -i /tmp/o.png -filter_complex "[0][1]hstack" -frames:v 1 04_compare_ref_vs_output.jpg
```

**要看的**：发型渐变、呆毛、发牌、围裙图案、尾——**逐项对照**，缺一项就是参考图或提示词有问题。

### 4.4 人工验收清单（6 条）

| # | 检查 | 本案例结果 |
|---|---|---|
| 1 | probe 通过（帧数/音轨/亮度） | ✅ |
| 2 | **角色一致性**：外貌特征逐项对上参考图 | ✅ 10 帧全部一致 |
| 3 | **景别按分镜切换** | ✅ 6 个特写 + 1 个中景 |
| 4 | **画风统一**，无照片级写实漂移 | ✅ 全 2D 动画风 |
| 5 | **角色没中途消失** | ⚠️ 见下方「实测不足」第 1 条 |
| 6 | 道具按分镜出现/消失 | ✅ 布丁只在镜 1–4 出现 |

---

## 5. 逐镜对照（分镜 → 实际）

| 镜 | 分镜写的 | 实际 | 达成 |
|---|---|---|---|
| 1 | 冰箱里一布丁杯 | ✅ 一模一样 | ✅ |
| 2 | 眼睛特写、瞳孔放大 | ✅ | ✅ |
| 3 | 手伸进去拿走布丁 | ✅ | ✅ |
| 4 | 腮帮鼓鼓在吃、嘴角有布丁 | ✅ **最萌的一帧** | ✅ |
| 5 | 背靠冰箱、双手背后、无辜笑 | ⚠️ 成了"站在厨房中景" | ⚠️ |
| 6 | 转头 + 呆毛弹起 | ⚠️ 转了，呆毛不明显 | ⚠️ |
| 7 | 手背擦嘴 + 闭眼笑 | ✅ | ✅ |

---

## 6. 实测不足（如实记录）

**这一节比成功记录更有价值。**

| # | 问题 | 根因 | 下次怎么改 |
|---|---|---|---|
| 1 | **镜 1 前后 3 秒只有布丁，角色完全没入画** | 该镜是纯道具镜头，模型按"摄影"理解，把 `style_lock` 也一起忽略了 | 公共段那句"must stay on screen in every single shot" 力度不够 → **纯道具镜改成"角色侧脸入画 + 视线看向道具"** |
| 2 | 镜 5 没演到"背靠冰箱" | 姿态描述不够具体，模型自由发挥 | 写"her back flat against the fridge door"，并把姿态放进 `[Subject]` 句尾 |
| 3 | 镜 6 的"呆毛弹起"幅度小 | 呆毛这种小形变在 8 步 + 单帧渲染下容易丢 | 呆毛这类细节动作**单独给一镜**（1.5s）而不是附在转头后面 |
| 4 | 台词中文咬字略糊 | 8 步时语音是输出最弱环节 | 想要清晰台词 → 提到 12 步；或让角色只说自称（本例已如此，仍偏糊） |

> 📌 **这四条不是"失败"，是"下一代改进项"**。
> 教程最有价值的部分不是"这样就完美了"，而是**这样之后还能怎么改**。

---

## 7. 这个案例验证了哪些方法

| 方法 | 验证结果 |
|---|---|
| 角色参考图锁保真 | ✅ 10 帧全部对上参考图特征 |
| `reproduce EXACTLY / do NOT redesign` 指令 | ✅ 没有出现"大概像"的漂移 |
| 快剪 1.5s/镜 | ✅ 原速播放即正常观感，**不需要后期加速** |
| 每镜重复风格锚 + `style_lock` 兜底 | ✅ 无照片级写实漂移 |
| 8 步 turbo + 固定 seed | ✅ 417 秒出片，探针全过 |
| 台词只说自称 | ⚠️ 有改善但仍偏糊，8 步是瓶颈 |
| 纯道具镜不写角色 | ❌ **失效**，这是本次唯一的方法性缺陷 |

---

## 8. 如果你照着做

1. 直接复制 §2 的参数
2. 直接复制 §3 的提示词（把外貌清单换成你角色的）
3. 参考图要求：**干净正面全身、纯色浅背景、2048px**（本例的 `03_reference_input.png` 就是这样）
4. 跑完按 §4 验收
5. 特别注意 **§6 第 1 条**：纯道具镜也要让角色入画
