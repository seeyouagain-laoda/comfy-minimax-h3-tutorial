# 在 ComfyUI 里亲手搭图（只用官方内置节点）

> **这是本指南最通用的一条路线**：不需要任何第三方节点包、不需要别人的工作流 JSON。
> 只要 ComfyUI ≥ 0.34.0 就能跑通，底模放进去、改提示词、就能出片。
> 搭好一次之后可以导出成 JSON 复用。

---

## 0. 节点清单

在节点搜索框里搜这些名字（都在 `comfy_extras` 内置，分类 `partner/video/MiniMax`）：

| 搜索名 | 数量 | 作用 |
|---|---|---|
| `UNETLoader` | 1 | 加载底模 |
| `CLIPLoader` | 1 | 加载文本编码器 |
| `VAELoader` | 2 | 视频 VAE + 音频 VAE |
| `LoraLoaderModelOnly` | 1（可选） | 加速 LoRA |
| `EmptyMiniMaxH3LatentAV` | 1 | 画布 / 帧数 / 帧率 |
| `MiniMaxH3ImageToVideo` | 1 | 生成（首尾帧通道） |
| `MiniMaxH3ReferenceToVideo` | 1 | 生成（多参考通道，二选一） |
| `MiniMaxH3SigmaShift` | 1 | 采样调度（官方推荐） |
| `KSamplerSelect` | 1 | 采样器 |
| `BasicScheduler` | 1 | 调度器 + 步数 |
| `RandomNoise` | 1 | 噪声 + 种子 |
| `SamplerCustomAdvanced` | 1 | 采样执行 |
| `VAEDecode` | 1 | 解码音视频 |
| `CreateVideo` | 1 | 合成 mp4 |
| `ComfyMathExpression` | 1（可选） | 帧数自动对齐 |
| `PreviewImage` | 1 | 看首帧用 |

> 🔴 **务必用上面这些内置节点**。某些平台把 `MiniMax*` 节点指向了**云端 API**（按量计费）。
> 确认方法：点开节点，如果 `UNETLoader` 存在且能本地加载 `.safetensors`，
> 就是本地执行；若有 `api_key` 输入框，那是云端通道，别用。

---

## 1. 最小可跑接线（先跑 3 秒试片）

### 1.1 加载层

```
UNETLoader ─┬─ MODEL ──────────────────────┐
            └─ (输出只有 MODEL 一种)        │
                                           │
CLIPLoader(type=minimax) ── CLIP ───────────┤
                                           │
LoraLoaderModelOnly ── MODEL ───────────────┤
   (lora_name = turbo 8step；strength=1.0)  │
                                           ▼
                              MiniMaxH3ImageToVideo
                              (latent_image / conditioning 输入)
```

**接线要点**：

| 节点 | 输入端 | 接谁 |
|---|---|---|
| `LoraLoaderModelOnly` | `model` | `UNETLoader.MODEL` |
| | `lora_name` | turbo LoRA 文件名 |
| | `strength_model` | `1.0` |
| `CLIPLoader` | `type` | 下拉选 `minimax`（**必选，选错加载失败**） |
| `VAELoader` ×2 | 分别选 | `minimax_h3_video_vae_int8_convrot` / `minimax_h3_audio_vae_fp32`（**音频必须 fp32**） |

### 1.2 潜空间与调度

```
EmptyMiniMaxH3LatentAV
  width=864  height=480  length=73  fps=24
  batch_size=1
  → 接到 MiniMaxH3ImageToVideo 的 latent_image

MiniMaxH3SigmaShift
  shift 填 6（宽高比 >1.2 时官方推荐 6；<=1.2 用 3）
  → 接到 BasicScheduler 的 scheduler_input
```

### 1.3 采样

```
KSamplerSelect(sampler_name = res_multistep)  ── SAMPLER ──┐
                                                            ├─ SamplerCustomAdvanced
BasicScheduler(schedule = simple, steps = 8,             │      .sampler
                 denoise = 1.0)                          │      .sigmas
              ← MiniMaxH3SigmaShift ── SCHEDULER ───────┘      .noise ← RandomNoise
RandomNoise(noise_seed = 固定值, control = fixed) ── NOISE       .latent_image
                                                              ← EmptyMiniMaxH3LatentAV
SamplerCustomAdvanced.条件输入 ← MiniMaxH3ImageToVideo 的 conditioning
```

🔴 **`RandomNoise.control` 必须选 `fixed`**。不固定时同一句提示词每次生成的人物姿态、
背景光都不一样 —— 多镜头根本没法连续用。

### 1.4 解码输出

```
MiniMaxH3ImageToVideo.sample ─┐
                              ├─ VAEDecode
VAELoader(video).vae ──────────┤        (samples, audio)
                              │
                              └─ VAEDecode.audio
                                      ↓
                              CreateVideo(fps=24, codec=h264)
```

**关于 `MiniMaxH3SigmaShift`**：官方模板用 `BasicScheduler` 的 `scheduler_input` 接它。
如果你的 ComfyUI 版本上 `BasicScheduler` 没有这个输入端，直接把 `MiniMaxH3SigmaShift`
删掉、用 `BasicScheduler` 默认调度也能跑（画质略差一点）。

---

## 2. 加参考图（Ref2VA 通道）

把 `MiniMaxH3ImageToVideo` 换成 `MiniMaxH3ReferenceToVideo`，其余不变。

| 输入端 | 接什么 | 备注 |
|---|---|---|
| `positive` | 条件 | 提示词在这里 |
| `negative` | 条件 | 也可接，H3 无独立负面输入框时留空 |
| `latent_image` | `EmptyMiniMaxH3LatentAV` | |
| `ref_images` | 动态列表 | **重点看这里 ↓** |
| `ref_videos` / `ref_audios` | 动态列表 | 可留空 |

### 2.1 `ref_images` 动态列表怎么填

这个输入是一个**可增删的列表 widget**（形如 `ref_image_0`、`ref_image_1`…），
每项都是 `IMAGE` 类型。

1. 在节点上右键该输入 → `Add input`（或用 `Convert to dynamic inputs` 按钮），
   让它变成列表形式
2. 列表里每一项再挂一个 `LoadImage`

⚠️ 挂 `LoadImage` 时的两个要点：
- `image` 下拉只列 `models/input/` 里的文件 → 参考图放这个目录
- 该节点的 `upload` 参数选 `image`（会复制到 input），选别的类型可能不显示

### 2.2 三个必设参数

| 参数 | 值 | 为什么 |
|---|---|---|
| `ref_image_size` | **`max`** | 决定参考图被缩到多少再送进模型。**默认 `None` 会按输出宽度缩放**（如 864），脸部/发饰/服装细节全丢，模型只能靠文字脑补 → 角色不像 |
| 参考图底色 | **不透明白底** | 参考管线对 alpha 通道支持差，透明底 PNG 效果差 |
| 参考图尺寸 | 长边 2048 左右 | 官方说 1024 以内也够，**别丢 4K 大图**（只白拉显存） |

### 2.3 🔴 最隐蔽的坑：空槽位返回全黑图

某些多图加载节点（或列表里未接线的项）在取不到图时会返回
`torch.zeros(1, 64, 64, 3)` —— **一张 64×64 的纯黑图**。

后果：你以为挂了参考图，实际上模型收到的是一张黑图 →
**角色完全按文字重画**，而且**不报错、不告警、出片看着"正常"**。

**三条排查手法**：
1. **看耗时** —— 参考 token 参与每一步采样，挂对参考图后耗时通常增加 50%+。
   挂黑图和挂对图的耗时差别很明显。
2. **换输入做对照** —— 把参考图换成完全不同的角色，输出角色应随之改变。
   不变 = 参考图没进去。
3. **数一数** —— 你填 1 张，但工作流从第 2 个槽位取图 → 取到的是黑图。
   这种情况下**把同一个文件连到两个槽位**兜底。

---

## 3. 提示词（两套格式）

| 通道 | 格式 | 段名 |
|---|---|---|
| 首帧 / 纯文字 | 三字段 | `integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music` |
| **带参考图/视频/音频** | 🔴 **六段式** | `subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music` |

完整规范与可抄模板见 **`prompt-spec-ref2va.md`**。

**最容易犯的错**：把三字段模板用在 Ref2VA 上 → 参考**被静默丢弃**，画面按文字重画。
判据很简单：**只要你挂了任何参考素材，就必须写六段式。**

---

## 4. 帧数对齐（可选但推荐）

`EmptyMiniMaxH3LatentAV.length` 需要落在特定网格上。挂一个 `ComfyMathExpression`：

```
node_A = EmptyMiniMaxH3LatentAV 的时长（秒）
node_B = 24
node_C = 0
comfymath.expression =
  max(5, round(a*b)) + (5 - (max(5, round(a*b)) % 17)) % 17
```

`a` 接时长、`b` 接帧率。表达式的输出接回 `EmptyMiniMaxH3LatentAV.length`。

**不做的后果**：帧数不在网格上，画面末尾会出现 1–2 帧卡顿或尾部撕裂。

对照：2s→56 · 5s→124 · 10s→243 · 15s→362 · 20s→485

---

## 5. 导出与复用

1. 搭好后点 **Save** 存成 JSON
2. 后续换题材只需改三处：`prompt` 文本框 · `EmptyMiniMaxH3LatentAV` 的宽高与时长 · `RandomNoise` 的 seed
3. 想换角色只改 `LoadImage` 的图片，**其他一律不动**
4. 想做成系列就保留同一份 JSON + 固定 seed，换提示词即可

---

## 6. 第一次跑的建议顺序

| 步骤 | 做什么 | 预期耗时 |
|---|---|---|
| 1 | 3 秒、864×480、8 步、**不挂参考图**、提示词随便写一句话 | 约 2 分钟 |
| 2 | 挂一张参考图，同样 3 秒 | 明显变慢（说明参考进去了） |
| 3 | 换第二张参考图，**只看角色有没有变** | 变了 = 链路通 |
| 4 | 换成六段式提示词，跑 5 秒 | 约 4 分钟 |
| 5 | 固定 seed 跑两次，结果应**几乎一致** | 验证 fixed 生效 |

第 3 步是最关键的一步 —— 它能直接证伪「参考图静默失效」这个最贵的坑。
