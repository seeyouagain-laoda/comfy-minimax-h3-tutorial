# 工作流参数手册（ComfyUI 原生节点）

> 本文是**节点级**参数说明，照着填即可。全部使用 ComfyUI 内置 H3 节点，
> 不依赖任何第三方封装。
> 需要 ComfyUI **≥ 0.34.0**（embedding 需 ≥ 0.33.0）。

---

## 1. 两条通道怎么选

| 通道 | 节点 | 用在哪 |
|---|---|---|
| **FL2VA**（首尾帧） | `MiniMaxH3ImageToVideo` | 你有一张（或一对）**具体的画面**要让它动起来 |
| **Ref2VA**（多参考） | `MiniMaxH3ReferenceToVideo` | 你有**角色立绘 / 场景图 / 参考视频 / 参考音频** |
| **T2VA**（纯文字） | `MiniMaxH3ImageToVideo`（不接图） | 纯文本生成 |

> 底模选择：FL2VA 用 `fl2va` 权重；Ref2VA 用 `ref2va` 权重。
> **turbo LoRA 必须与通道配对** —— fl2v 版 LoRA 挂到 fl2va 上有效，
> ref2v 版 LoRA 挂到 fl2va 上无效（键名不匹配，且**不报错**）。

---

## 2. 核心节点与参数

### 2.1 加载层（5 个节点）

| 节点 | 参数 | 值 |
|---|---|---|
| `UNETLoader` | `unet_name` | `minimax_h3_fl2va_pruned_int8_convrot.safetensors`（FL2VA）<br>`minimax_h3_ref2va_pruned_int8_convrot.safetensors`（Ref2VA） |
| | `weight_dtype` | `default` |
| `CLIPLoader` | `clip_name` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| | `type` | **`minimax`**（选错会加载失败） |
| | `device` | `default` |
| `VAELoader` | `vae_name` | `minimax_h3_video_vae_int8_convrot.safetensors` |
| `VAELoader` | `vae_name` | `minimax_h3_audio_vae_fp32.safetensors`（**必须是 fp32**，int8 音频会坏） |
| `LoraLoaderModelOnly` | `lora_name` | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` |

> 🔴 **LoRA 格式陷阱**：`transformer_blocks.*`（diffusers 格式）的 LoRA 在 ComfyUI 上
> **全部 key 被丢弃、不报错、出片看着正常但等于没挂**。认准
> `blocks.N.attn.out_proj.lora_A.weight` 这类 **ComfyUI generic 格式**。
> 自查：控制台搜 `lora key not loaded`，出现就是没生效。

### 2.2 空潜空间

`EmptyMiniMaxH3LatentAV`：

| 参数 | 值 |
|---|---|
| `width` / `height` | 见下方分辨率对照表 |
| `length` | 帧数，对齐规则见 §3 |
| `batch_size` | 1 |

### 2.3 生成节点

**`MiniMaxH3ImageToVideo`**（FL2VA）：

| 参数 | 值 |
|---|---|
| `width` / `height` / `length` | 同上 |
| `prompt` | 提示词（**负面词在同一框里换行写**，无独立负面输入） |
| `first_frame` / `last_frame` | 可选，只接 `first_frame` 即普通 i2v |

**`MiniMaxH3ReferenceToVideo`**（Ref2VA）：

| 参数 | 值 |
|---|---|
| `prompt` | 🔴 **必须是六段式**（见 `prompt-spec-ref2va.md`） |
| `ref_images` | 动态列表 `ref_image_0` … `ref_image_8`（**最多 9 张**） |
| `ref_image_size` | **`max`**（= 2048px 短边）。调小会让参考图细节全丢，模型只能靠文字脑补 |
| `ref_videos` | 最多 3 个 |
| `ref_audios` | 最多 3 个 |

> 🔴 **多图接线的静默失效**：某些多图加载节点对未填充的槽位返回
> `torch.zeros(1,64,64,3)`（一张全黑图）。如果你的工作流从**第 2 个槽位**取图，
> 而你只填了 1 张 → 参考图**静默失效**，角色纯靠文字画出来。
> **自查**：填 1 张 vs 填 2 张，生成耗时应有明显差异（参考 token 参与每步采样）；
> 或把参考图换成完全不同的角色，输出角色应随之改变。

### 2.4 采样层

| 节点 | 参数 | 值 |
|---|---|---|
| `KSamplerSelect` | `sampler_name` | `res_multistep` |
| `BasicScheduler` | `schedule` | `simple` |
| | `steps` | 见 §3 |
| | `denoise` | `1` |
| `RandomNoise` | `noise_seed` | 固定值 |
| | `control` | 🔴 **`fixed`** |

> 🔴 **`control` 必须 `fixed`**。不固定时同一句提示词每次生成的人物姿态、背景光
> 都不一样，**多镜头根本没法连续用**。这是短剧连贯的第一前提。

### 2.5 输出层

`CreateVideo`：`fps = 24` · `codec = h264`（值为 `8`）

---

## 3. 帧数与分辨率

### 3.1 帧数对齐规则

模型要求帧数落在特定网格上。用一个 `ComfyMathExpression` 节点即可自动对齐：

```
max(5, round(duration_sec * 24)) + (5 - (max(5, round(duration_sec * 24)) % 17)) % 17
```

实测对齐结果：

| 时长 | 原始 | 对齐后 |
|---|---|---|
| 2s | 48 | **56** |
| 5s | 120 | **124** |
| 10s | 240 | **243** |
| 15s | 360 | **362** |
| 20s | 480 | **485**（单段）|

### 3.2 分辨率对照表（官方）

| 百万像素 | 16:9 输出 | 适用 |
|---|---|---|
| 0.2 | 608 × 352 | 极速试片 |
| 0.3 | 736 × 416 | 试片 |
| **0.4** | **864 × 480** | ⭐ **官方默认，日常出片用这个** |
| 0.5 | 960 × 544 | |
| 0.6 | 1056 × 608 | |
| 0.7 | 1152 × 640 | |
| 0.8 | 1216 × 672 | |
| 0.9 | 1280 × 736 | |

> 🔴 **不要直接填 1080P** —— 模型无法原生输出 1080P，需要后期超分
> （SeedVR2 / FlashVSR / Topaz）。

### 3.3 步数怎么选

| 组合 | 说明 |
|---|---|
| **`fl2v_turbo_8step` + steps = 4** | 官方默认，最快 |
| **`fl2v_turbo_8step` + steps = 8** | 平衡，**日常推荐** |
| 不用 turbo，20–28 步 | 画质最好，耗时翻数倍；远景 / 大动作必需 |
| **打斗 / 奔跑** | 🔴 关掉 turbo，步数提到 20+（低步数 + 大动作 = 拖影） |

> turbo LoRA 必须配接近它标称的步数，**步数给高反而崩**。
> 步数还能改善「运动幅度」和「音轨可用性」：8 步时语音是输出中最弱的部分，
> 12 步以上音轨才可用。远景/大动作的收益在 **16 步左右**拿满。

---

## 4. 底模 / LoRA / 节点包 三者关系

新手最容易混淆的地方，说清楚能省很多时间。

| | 底模 | LoRA | 节点包 |
|---|---|---|---|
| 本质 | 主权重 | **低秩权重补丁** | **Python 代码**（算子/调度/UI） |
| 操作对象 | — | 底模里某个**具体参数张量** | ComfyUI 抽象类型（MODEL/LATENT/…） |
| 换底模要改吗 | — | **经常要换** | **不用** |
| 通用性 | 单一任务族 | 绑定架构 + 命名格式 + 剪枝布局 + 任务族 | 通用，只耦合 ComfyUI 版本 |

**结论：节点包通用，LoRA 不通用。**

### 4.1 两个官方底模的差异

| | 键数 | 说明 |
|---|---|---|
| `fl2va_pruned_int8` | 932 | 骨架与 ref2va **完全一致（零差异）** |
| `ref2va_pruned_int8` | 932 | 同上 |

差异**只在 AdaLN 条件注入段**（首尾帧 / 参考图怎么喂进残差流），主干约 90% 共享。
所以：fl2v 训的动作 LoRA 挂到 ref2va 上通常能跑（共享主干），但参考注入段没被优化。

### 4.2 「合并底模」

社区有把两个底模的 AdaLN 段融合成一个文件的方案（覆盖 block 30-49 / 45-49 等），
省一份权重、可同时吃首帧与参考图。**前提是两个权重必须同血统**（同一发布方、同一剪枝布局）。

⚠️ **不同发布方的同名模型不能混**。社区微调版可能带 key 前缀
（`model.diffusion_model.`）且没有 `adaln_t_table` 标记，与官方权重不兼容。
**判断方法**：读权重文件头（safetensors 前 8 字节是 header 长度，之后是 JSON），
数一下键数、看前缀、看有没有 `adaln_t_table`。

### 4.3 剪枝版（pruned）⚠️

剪枝版体积小（省 40%），但**实测可能画面崩坏**（一團模糊色块，角色消失）。
**换任何新底模之前，先用同 seed / 同提示词 / 同参考图跑一个 3 秒对拍。**

---

## 5. 可选增强：latent 放大（二采）

一采 0.4MP 出片后，可以在 latent 空间放大再二采一次，得到更高分辨率。
参考社区工作流的做法：

```
一采(0.4MP) → Latent 3D Upscale → 二采(6 步 ManualSigmas) → 解码
```

典型 sigmas：`0.9231, 0.8780, 0.8000, 0.6316, 0.3158, 0.0000`

🔴 **两个坑**：
1. 放大权重需要额外下载（小型，约 0.6 GB）
2. **带「帧钉定」的接续 conditioning 与放大互斥** —— 钉帧索引是按分辨率算好的，
   分辨率一变索引就错。二采要另配一个**不带钉帧**的 guider。
   症状：`shape mismatch [2839,96] vs [7228,96]`，且 `2839 × 2.55 ≈ 7228`
   （2.55 正是放大倍率²）。

---

## 6. 可选增强：帧接续（Motion Context）

把上一段视频尾部 latent **直接钉进下一段**（不解码成像素、也不重新编码），
实现音画零漂移的多段长视频。

```
clip1: 采样 → 存档 latent(1) → 解码
clip2: 载入 latent(1) → 钉住尾部 N 帧 → 采样 → Trim 掉 N 帧 → 存档 latent(2) → 解码
```

🔴 **接续铁律（原作者原话）**：

> 钉住的帧不是建议 —— 每一步采样都会重新注入，模型在那段区间里画不出别的东西。
> 如果第 2 段提示词开头描述的和第 1 段结尾不一样，模型**不会二选一，而是两个都渲染**
> （第 1 段结尾特写一个人、第 2 段开头要两个人同框 → 出来三个人）。
>
> ✅ **修法**：每段提示词开头先**复述上段结尾**（同人、同衣、同构图、同动作），
> 让这段"贴合"跑过接缝，再切到真正想要的内容。变化点落在 **1.5–2 秒之后**。

- 钉子长度：常用 **22 帧**（≈0.92s）
- Trim 必须精确剪掉这 22 帧，否则接缝处会有 22 帧的重复停顿
- **参考图没有时间概念**，整段生效

---

## 7. 自检清单（提交前 60 秒过一遍）

| # | 检查 | 怎么看 |
|---|---|---|
| 1 | `RandomNoise.control` = `fixed` | 节点参数 |
| 2 | LoRA 是 **ComfyUI generic 格式** | 控制台搜 `lora key not loaded`，应为 0 |
| 3 | 参考图**真的接上了** | 生成耗时比空参考明显长（参考 token 参与每步采样） |
| 4 | `ref_image_size` = `max` | 节点参数 |
| 5 | 帧数已对齐网格 | 用 §3.1 公式 |
| 6 | 分辨率不是 1080P | 查对照表 |
| 7 | 打斗段没开低步数 turbo | 步数 ≥ 20 |
| 8 | 种子已固定 | 记下这次的 seed，方便复现 |
