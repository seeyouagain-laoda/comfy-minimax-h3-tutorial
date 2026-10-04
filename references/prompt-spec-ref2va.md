# Ref2VA 提示词完整规范（官方格式）

> 适用于**带参考图/参考视频/参考音频**的生成（Ref2VA 通道）。
> 本文是格式规范，不含任何机器专属内容，可直接照抄。
> 格式错误最可怕的地方在于：**它不报错，会静默丢弃参考**。

---

## 0. 先判断用哪套格式

| 情况 | 用哪种 | 段数 |
|---|---|---|
| 只有文字（无任何参考素材） | 三字段 | `integrated_multimodal_description` + `overall_soundscape` + `non_diegetic_music` |
| **带参考图 / 参考视频 / 参考音频** | 🔴 **六段式** | 见下 |
| 首帧 / 尾帧 / 关键帧锚定 | 六段式，`[Shot 1]` 首帧不写时间戳 | |

> 🔴 **最常见的致命错误**：把三字段模板直接用进 Ref2VA。
> 结果是参考图**在没有任何格式报错的情况下被静默丢弃**，画面完全按文字重画。

---

## 1. 六段式的段名（顺序不可改，段名必须一字不差）

```
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

无内容的段**也要保留段名**，值写 `N/A`。

### 四个最常见的格式错误

**① 给纯角色参考图建独立 `<Picture N>` 行** ← 最高频错误

```
错：  <Picture 1> is a reference image of the girl.
      <Subject 1> is the girl.

对：  <Subject 1> is the girl in <Picture 1>, with ...保留特征...
```
图片**只在 `<Subject N>` 定义里被引用**，且**不在 `retention_analysis` 里单独出现**。
只有「这张图是具体的某一帧」时才需要独立 `<Picture N>` 行。

**② 定义了 `<Subject N>` 却从不在 `detailed_description` 里引用它**

**③ 风格句写在 `[Shot 1]` 之后** —— Ref2VA 要求风格句**单独成行、位于 `[Shot 1]` 之前**

**④ 段名写成 `integrated_multimodal_description`** —— 那是三字段格式的名字，六段式里必须叫 `detailed_description`

---

## 2. 四种标签的职责

| 标签 | 用于 | 何时给它独立行 |
|---|---|---|
| `<Subject N>` | 可复用的**可见内容**（人/动物/物体/场景/服装/道具/风格/动作/姿势） | **永远要有** |
| `<Picture N>` | 图片作为**具体帧锚点**（首帧/关键帧/尾帧/分镜板） | 只有关键帧时才给 |
| `<Video N>` | 整段视频：编辑/续写/提供运镜结构 | 是源视频时 |
| `<Audio N>` | 音频信号被复制或参考 | 音轨真被复制/参考时 |

- 编号**各自独立**：同一个文件可同时是 `<Video 1>` 和 `<Audio 2>`
- 一个 `<Subject N>` 可组合多源：外观来自图 + 动作来自视频
- 🔴 **参考视频自带声音 ≠ 自动产生 `<Audio N>`**（要显式声明才会被当音频参考）

---

## 3. `summary` 段：六种 task type

用 `+` 组合，不要重复。

| task type | 何时用 |
|---|---|
| `keyframe completion` | 图片是具体的帧锚点（首/中/尾帧） |
| `reference generation` | 资产用于引导生成（角色/场景/风格/动作/运镜），但不是帧、也不是被编辑的源 |
| `video editing` | 直接修改已有源视频（**在两个静帧间生成不算**） |
| `video continuation` | 从已有视频续写/扩展/恢复 |
| `audio reuse` | 同一音频信号被完整或部分重用 |
| `audio reference` | 只参考音色/节奏/纹理，不复制信号 |

**编辑任务的固定开头句**：
```
[video editing] The target video is an edited version of <Video 1>.
```

常见组合：`[keyframe completion + reference generation]`、
`[reference generation + video continuation]`、`[video editing + audio reuse]`

> 🎯 **纯角色参考图（无帧锚点）** = `[reference generation]`

---

## 4. `retention_analysis` 段：关系标记

**视觉**（Subject / Picture / Video）：

| 标记 | 含义 |
|---|---|
| `fully_preserved` | 完整保留（脸、发型、服装全不变） |
| `partially_preserved` | 保留但**明确定义的特征**改变 |
| `attribute_transfer` | 把参考特征转移到另一个可识别主体 |
| `weak_reference` | 只保留风格/类别/构图/氛围 |

**音频**（Audio）：`fully_copy` / `partially_copy` / `reference` / `weak_reference`

> 只有 `weak_reference` 同时属于两套体系。
> 🔴 **本段禁止出现 speaker ID（`(S1)`）** —— 官方明文不允许。

**格式**：
```
<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - 保留她的脸型与服装配色
```

---

## 5. `detailed_description` 硬规则

| 规则 | 说明 |
|---|---|
| 风格句 | **单独成行，在 `[Shot 1]` 之前** |
| 字数 | 生成任务约 **350–500 英文词**（指导值，非硬阈值） |
| `[Shot 1]` | **永不带时间戳** |
| 后续镜头 | 严格递增：`At 00:04.500,` / `At 00:07.000,` |
| 标签插入 | 在主体**首次清晰出现**处插入，后续镜头持续使用 |
| 动作写法 | 写**可见动作与状态变化**，不写抽象意图 |
| 单镜动作数 | **一个动作**（复杂肢体动作 → 手部畸形） |
| 多人镜头 | 🔴 **已知短板** —— 一个镜头重点刻画一位角色 |

**「描述动作」vs「抽象意图」**：
```
弱：  <Subject 1> acts confident.
强：  <Subject 1> straightens her shoulders, lifts his chin slightly, and steps forward.
```

---

## 6. 运镜三要素（缺一即「监控视角」）

写成**自然英文句子融进镜头描述**，不能堆在末尾当标签。

| 维度 | 接受写法 |
|---|---|
| 类型 | `Zoom In/Out` · `Push In/Pull Out` · `Pan Left/Right` · `Truck Left/Right` · `Tilt Up/Down` · `Pedestal Up/Down` · `Arc Shot` · `Tracking Shot` · `Static Shot` · `Shake Slightly` · `POV` · `Roll Clockwise` |
| 幅度 | `with small amplitude` / `with large amplitude`（中幅度省略） |
| 速度 | `at slow speed` / `at fast speed`（常速省略） |

> **`Zoom In` vs `Push In`**：前者固定机位变焦距，后者机身**物理前移**。
> 🔴 **同一镜只写一种运镜** —— 矛盾指令会导致空间畸形。切镜只在场景真正变化时用。

---

## 7. 官方运镜 / 灯光词典（直接抄）

| 中文 | 英文提示词 |
|---|---|
| 推进 | `Zoom in` / `Push in` |
| 拉远 | `Zoom out` / `Pull back` |
| 水平平移 | `Pan left` / `Pan right` |
| 垂直俯仰 | `Tilt up` / `Tilt down` |
| 环绕 | `Orbiting shot` / `Arc shot` |
| 低角度 | `Low-angle shot` |
| 高角度 | `High-angle shot` / `Bird's-eye view` |
| 跟拍 | `Tracking shot` / `Follow shot` |
| 希区柯克变焦 | `Dolly Zoom` / `Vertigo effect` |
| 手持 | `Handheld camera` / `Camera shake` |

**通用负面词**（写在同一段文字里，换行写；H3 没有独立负面输入框）：
```
deformed, distorted camera movement, sudden jitter, blurry, bad anatomy,
morphing artifacts, flickering light, low quality, static background
```

---

## 8. 参考图要求（决定成败）

| 要求 | 说明 |
|---|---|
| **干净正面像** | 官方 Tips：*"A plain-background packshot or a clear portrait transfers more reliably than a cluttered photo"* |
| 🔴 **不要三视图** | 三视图属于 cluttered photo；模型会照抄它的静态感 → 画面不动 |
| **正面半身 / 全身** | 干净正面素材 |
| **背景简洁** | 不要复杂杂物 |
| **数量** | 最多 **9 图 / 3 视频 / 3 音频 / 共 12 文件** |
| **宁少勿滥** | 官方 Tips：*"Two well-directed images usually hold better than nine loosely described ones"* |
| **画风会污染** | 换一张参考图可能让整体画风大变 → 全程画风必须统一 |
| **写明是 subject 还是 style** | 明确这张图是给「内容」还是「风格」 |

---

## 9. 官方 embedding（可选增强）

模型仓库自带约 10 个 embedding，效果是「预计算好的运镜/风格张量」：

| 触发词 | 效果 |
|---|---|
| `embedding:minimaxh3_bullet_time` | 子弹时间 |
| `embedding:minimaxh3_spiral_ascent` | 螺旋上升运镜 |
| `embedding:minimaxh3_truman_show` | 楚门式后拉 |
| `embedding:minimaxh3_dark_magic` | 黑暗魔法氛围 |
| `embedding:minimaxh3_fire_breath` | 火焰吐息 |
| `embedding:minimaxh3_storm_magic` | 风暴魔法 |
| `embedding:minimaxh3_blooming_flowers` | 花朵绽放 |
| `embedding:minimaxh3_four_seasons` | 四季变换 |
| `embedding:minimaxh3_art_is_explosion` | 爆炸式构图 |
| `embedding:minimaxh3_kiss_camera` | 接吻镜头运动 |

**三条硬规矩**：
1. 🔴 **必须小写 `embedding:`** —— 大写 `Embedding:` 会被静默丢弃
2. 🔴 **不能和前后单词粘连**，要空格隔开
3. 🔴 **结尾不能跟句点**

**机制**：这些不是关键词，是文本编码器算好的 bf16 张量，命中时 ComfyUI 把这些
token 位置原样拼回序列。因此**不能调权重**（`(embedding:x:0.8)` 无效），
要么满强度生效，要么没有。需要 ComfyUI ≥ 0.33.0。

---

## 10. 完整模板（照抄改内容即可）

```
subject_definitions:
<Subject 1> is the girl in <Picture 1>, a young woman with long wavy dark hair and a
red coat, keeping her face, hairstyle, outfit colours and proportions exactly as
shown in <Picture 1>.

summary:
[reference generation] A 20-second hand-drawn 2D anime short: <Subject 1> struggles over
the last bowl of rice with a second girl, <Subject 2>, in a warm home living room.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2], [Shot 3]): fully_preserved - keep her face,
hair, outfit and the red colour scheme
<Subject 2> (appears in [Shot 2], [Shot 3]): fully_preserved - keep her silver hair and
white kimono

detailed_description:
Hand-drawn 2D anime with clean line art, flat cel shading, full natural colour, warm
afternoon light. Never photorealistic, never a live-action photograph.

[Shot 1] A close-up of a single steaming white bowl of rice on a low wooden table.
[Shot 2] At 00:03.000, a medium shot: <Subject 1> sits on the left cushion staring at the
bowl, and <Subject 2> sits on the right cushion staring at the same bowl; both swallow.
[Shot 3] At 00:07.000, two pairs of hands grab the bowl at once and pull it in opposite
directions; rice grains scatter across the table.

overall_soundscape:
Quiet room ambience, faint clock tick, soft cloth rustle, the scrape of a bowl on wood.

non_diegetic_music:
N/A
```

---

## 11. 排查决策树

```
画面崩了
├─ 角色没对上
│  ├─ 参考图是三视图 / 杂物多 → 换干净单张正面像（§8）
│  ├─ 提示词没用六段式 → 改（§1）
│  ├─ 给参考图建了独立 <Picture N> 行 → 删掉，引用进 <Subject N>（§1①）
│  ├─ 挂了画风 LoRA → 撤掉（§12）
│  └─ 同镜两个角色 → 拆镜，一个镜头重点刻画一位
├─ 画风不对
│  ├─ 提示词没写画风 → 补风格句，且必须在 [Shot 1] 之前单独成行
│  ├─ 参考图画风污染 → 换风格一致的图
│  └─ 用了三字段而非六段式 → 改
├─ 画面静止
│  ├─ 参考图是静态三视图 → 换图或改用单张 + 提示词写明动作
│  └─ 动作写太少 → detailed_description 写「可见动作」
└─ 五官糊
   ├─ 步数过少 → 提高步数
   ├─ 开了 turbo LoRA → 关掉
   └─ 分辨率太低 → 提高（见官方分辨率对照表）
```

---

## 12. 其他已知约束

| 编号 | 问题 | 解法 |
|---|---|---|
| 7 | 剪枝（pruned）模型画面发灰 / 色彩断层 | 正式成片用完整 int8/bf16，避开 pruned |
| 16 | 中远景五官糊 | 提高步数；远景不用 turbo 低步数 |
| 18 | 随意改服饰发色 | 参考图背景简洁；提示词不写冲突服饰；**不叠加过多风格 LoRA** |
| 20 | 手部畸形 | 单镜不写复杂肢体动作 |
| 21 | 同镜多人物，其一崩坏 | **拆镜**，一个镜头重点刻画一位 |
| 23 | turbo 大动作拖影 | 成片不用最低步数档；打斗/奔跑关 turbo |
| 25 | SageAttention 与某加速同开报错 | 同一时间只用一种 |
| 27 | 加速后闪烁 / 颜色跳 | 关加速重跑对比；pruned 不搭配加速 |
| 30 | 物体畸形 / 透视怪 | 同镜只写一种运镜 |
| 32 | 要 1080P | 🔴 **模型无法原生 1080P** —— 后期用 SeedVR2 / FlashVSR / Topaz 超分 |
| 33 | 音画不同步 | 原生音频只适合环境音，**不做精准对口型**；后期配音 |
| 34 | 提示词写清楚但画面不体现 | 模型文字服从度有限，**人物特征优先交给参考图**；不要堆砌指令 |

---

## 参考源

- 模型仓库自带的两份提示词指南
- ComfyUI 官方 H3 文档（含 Tips 与 Quality Checklist）
- Tensor.Art 官方工作流提示词页
- RunComfy / Runware 官方 API 文档
- 国内社区 34 条实操踩坑汇总
