---
name: h3-video-guide
description: 基于 Comfy 和 MiniMax H3 的实战教程（以 DeepSeek 鲸鱼娘为例）。当用户要「用本地显卡出视频/做短剧/做 AI 动画/多段剧情/双角色同框」，或要把角色立绘动起来时使用。提供软硬件清单、ComfyUI 官方节点搭图教程、Ref2VA 六段式提示词完整规范、节点级参数手册、快剪分镜硬指标（1.2-2.0s/镜）、双角色双参考图接法、以及「静默失效」排错手册。**出片"看起来慢"的根因是分镜单镜太长，不是模型参数。** 详细教程见 README.md。
---

# 基于 Comfy 和 MiniMax H3 的实战教程（通用版）

> 🎯 **这份教程的初心**：让 **AI Agent 自己做短剧** —— 把"手动调参、反复试错、
> 看日志猜问题"这些脏活固化成可复用规范与脚本，Agent 照着做就能跑通。
> **所以它不是"教你操作"的入门教程，是给 Agent 当操作手册的。**
> 遇到适用范围外的情况，回到 §1.5 流程重推，不要自行发挥。
>
> 示例角色为 Q 版鲸鱼娘（社区拟人形象，CC BY-NC-SA）。
> **换角色只需换 `models/input/` 里的参考图，提示词改外貌清单即可。**
>
> 完整教程见 **`README.md`**。本文件是 AI Agent 的速查卡。

## 0. 先读哪篇

| 场景 | 读 |
|---|---|
| **第一次用 / 换机器** | `README.md` §0.5 三条路线 → §1 硬件 → §2 软件 → §3 安装 → **`references/build-graph-in-comfyui.md`** |
| **写提示词（带参考图）** | 🔴 **`references/prompt-spec-ref2va.md`**（六段式完整规范，格式错会静默丢参考） |
| **填节点参数 / 查分辨率 / 选步数** | **`references/workflow-params.md`** |
| **写出「不慢」的节奏** | **`references/shot-rhythm.md`** |
| **抄现成模板** | **`references/prompt-templates.md`** |
| **出片不对** | ⭐ **`references/troubleshooting.md`**（五步排查 + 静默失效家族 + 决策树） |

## 0.1 上手路线（AI Agent 必读）

| 路线 | 需要 | 适用 |
|---|---|---|
| **A · 纯 ComfyUI 官方节点** ⭐ | ComfyUI ≥ 0.34.0，**零第三方** | 单段出片、角色一致性、通用性最高。`references/build-graph-in-comfyui.md` |
| **B · 社区工作流 + 脚本** | + 5–9 个第三方节点包 | 多段接续、二采放大、批量出片 |

**默认选 A**，只有用户明确要「多段接续」或「二采放大」才升到 B。

## 0.2 环境自检

```bash
# ① ComfyUI 是否在跑
curl -s http://127.0.0.1:8188/system_stats && echo "UP"

# ② 官方 H3 节点是否注册（路线 A 只需这几项）
curl -s http://127.0.0.1:8188/object_info | python -c "
import json,sys
oi=json.load(sys.stdin)
for n in ['MiniMaxH3ImageToVideo','MiniMaxH3ReferenceToVideo',
          'EmptyMiniMaxH3LatentAV','MiniMaxH3SigmaShift','CreateVideo']:
    print(('  OK  ' if n in oi else '  MISSING ')+n)
"

# ③ 路线 B 才需要
curl -s http://127.0.0.1:8188/object_info | python -c "
import json,sys
oi=json.load(sys.stdin)
for n in ['MiniMaxH3MotionContext','MiniMaxH3MotionContextSaveLatent',
          'MinimaxH3LatentUpscaler3D','MultiImageLoader']:
    print(('  OK  ' if n in oi else '  MISSING ')+n)
"
```

**官方节点缺** → ComfyUI 版本太旧，升级到 ≥ 0.34.0。
**`MultiImageLoader` / `MotionContext` 缺** → 只影响路线 B，装包即可。

---

## 1. 六条硬性规则（违反必返工）

| # | 规则 | 违反后果 |
|---|---|---|
| **1** | 🔴 **分镜单镜 1.2–2.0 秒**；20 秒片 = 10–14 镜 | 单镜太长 → 观感慢到需要 1.5 倍速才正常 |
| **2** | 🔴 **带参考图必须写六段式**（`subject_definitions` / `summary` / `retention_analysis` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`） | 用三字段 → **参考被静默丢弃**，角色按文字重画 |
| **3** | 🔴 **每镜都要有角色入画** + 风格句单独成行写在 `[Shot 1]` 之前 | 无主体镜头漂成照片级写实；风格句位置错也丢 |
| **4** | 🔴 **参考图接线要用 slot 1（image_1），且写两行兜底** | 只写 1 行时 slot 2 是**全黑图**，参考从未生效 → 角色不像设定图 |
| **5** | 🔴 **多段接续的第 2 段开头必须复述第 1 段结尾** | 模型把两段都渲染（出现 3 个人） |
| **6** | 🔴 **每段生成完先给用户确认**，再跑下一段 | 白跑后面几段 |

**每镜写几个动作** → 一个。**同镜几个角色** → 一个（多角色同镜是已知短板，会崩脸）。

---

## 2. 最小工作流

```bash
# ① 干跑预检（不烧显存）—— 必须逐行核对 ref images / 接线 / duration / resolution / LoRA
python scripts/run_ep.py --dry

# ② 先生成第 1 段（后台）
python scripts/run_ep.py --clip 1

# ③ 验收 + 抽帧 → 发用户确认
python scripts/probe.py <mp4>
ffmpeg -y -i <mp4> -vf "select='not(mod(n\,24))',scale=380:-1,tile=5x2" -frames:v 1 sheet.jpg

# ④ 用户点头后跑第 2 段（自动接 latent，并 Trim 掉钉住的 22 帧）
python scripts/run_ep.py --clip 2

# ⑤ 拼接
printf "file 'clip1.mp4'\nfile 'clip2.mp4'\n" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy JOINED.mp4
```

环境变量：`CLIP` / `DURATION` / `REF_IMAGE` / `REF_IMAGE2` / `SEED` / `UPSCALE_MP` / `MEGAPIXELS`。

---

## 3. 单段 vs 多段

| 时长 | 做法 |
|---|---|
| **≤15 秒** | 单段一次跑完（15s = 362 帧） |
| **>15 秒** | 拆两段各 10 秒，Motion Context latent 接续（243 帧 + 221 帧 ≈ 19.3s） |

帧数公式：`n = round(sec × 24)` → `n += (5 − n % 17) % 17`
（10s → 243、15s → 362）

⚠️ **>15 秒单段会撞 VAE 坏块**，长片必须靠接续。

---

## 4. 双角色接法

`MiniMaxH3ReferenceToVideo` 的 `ref_images` 支持**最多 9 张**，官方语义是每张定义一个主体。

工作流默认只接了 `ref_image_0`。加第二个角色：

| 步骤 | 做法 |
|---|---|
| 1 | `MultiImageLoader.image_paths` 写两行：`A.png` / `B.png` |
| 2 | 第一个槽接 `336.slot 1`（image_1） |
| 3 | 新建一条 link 把 `336.slot 2` 接到 `191.ref_images.ref_image_1`（**target_slot = 4**） |
| 4 | 提示词显式写「两个不同角色，不许融合/互换」 |

提示词模板见 `references/prompt-templates.md`。

⚠️ 多角色同框容易崩脸。规避：特写交替、动作落在道具上、夸张物理事件推进、收尾同框但静止。
崩了退路：把「两人同时伸手」改成**交替特写**（A 的手 → B 的手 → 道具），叙事不受影响。

---

## 5. 排错：静默失效（不报错 ≠ 生效）

| 现象 | 根因 | 怎么发现 | 修法 |
|---|---|---|---|
| 角色不像设定图 | 参考图是 **64×64 全黑图**（`MultiImageLoader` 不足槽位返回零张量，而工作流接在 slot 2） | **生成耗时 +75%** | 接线改 slot 1 + 写两行 + 2048 |
| 没挂 LoRA | LoRA 是 diffusers 格式（`transformer_blocks.*`），ComfyUI 对 H3 不认 | 控制台 `lora key not loaded` | 换 `comfyui` generic 格式那份 |
| 指令不生效 | 子图节点 id 转换后带前缀（`459:xxx`），代码 `api.get("459")` 取不到 | 命中数为 0；或出片**被缓存秒出** | 按前缀匹配节点 id |

**通用排查顺序**：看生成耗时 → 看控制台 warning → 看 API 接线 → 看是否命中缓存 → 换输入做对照。

⚠️ 别 `grep` 整个日志（会把上一次的 warning 算进来）；要记录提交前的行数、只统计新增行。

---

## 6. 关键参数

| 项 | 值 | 说明 |
|---|---|---|
| 画布 | 864×480（`MEGAPIXELS=0.4`） | 12GB 显存降到 0.3；**不低于 0.25** |
| 步数 | **8** + turbo LoRA | 12/16 步是可选（抖动/伪影多时上调），**不是起步要求** |
| LoRA | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16` | 必须是 `comfyui` 格式 |
| 底模 | `Singularity_ref2va`（社区融合微调版，支持四条管线） | 轻量版（Pruned/w4a8）实测崩坏，**别换** |
| `ref_image_size` | `max`（2048px 短边） | 参考 token 骑过每步采样，耗时 +75%，但保真必需 |
| 文本编码器 | `qwen3vl_32b_minimax_h3_int8_convrot` | |
| 采样器 | `er_sde` + `simple`，shift 6/3 | |

**"看起来慢"排查顺序**：分镜单镜时长 → 后期变速 → 步数 → turbo。
先查分镜，别先怀疑模型参数。

---

## 7. 参考图制作

规格：**2048×2048** / **纯白底不透明** / 单人全身正面 / 含耳朵与尾巴。

三视图不能直接用（模型会看到三个人）。裁剪时注意：窗口不能对称取中间、形态学闭运算要在碎片剥离**之后**。

```bash
python scripts/make_ref.py --src three_view.png --out ref_charA
```

**验证生效**：`ref_image_size='max'` 下，同样 3 秒片耗时会 +75%。没涨就是没进去。

---

## 8. 文件

| 路径 | 用途 |
|---|---|
| `README.md` | **完整教程**：硬件、软件栈、安装、10 步流程、提示词、排错 |
| `scripts/run_ep.py` | 通用短剧 runner（单/双角色、多段、倍速） |
| `scripts/make_ref.py` | 三视图 → 白色参考图 |
| `scripts/probe.py` | 产物探针 |
| `scripts/measure_speed.py` | 帧间差分 / 运动量 |
| `scripts/steps_ab.py` | A/B 对拍（改步数 / 改底模，只用它一个） |
| `scripts/download_hf.py` | 权重批量下载（断点续传 + 大小校验） |
| `scripts/install_nodes.sh` | 批量装节点包 |
| `references/build-graph-in-comfyui.md` | ⭐ 纯官方节点搭图（路线 A，通用性最高） |
| `references/prompt-spec-ref2va.md` | ⭐ Ref2VA 六段式完整规范 + 可抄模板 + 排查决策树 |
| `references/workflow-params.md` | ⭐ 节点级参数 + 分辨率对照 + 步数选择 + 底模/LoRA/节点包关系 |
| `references/prompt-templates.md` | 提示词模板（单/双角色/日式/打斗） |
| `references/shot-rhythm.md` | 快剪分镜表模板 + 完整示例 |

---

## 9. 免责

底模与 LoRA 遵循各自许可（**注意排除地区限制**，商用前读原文）。
生成内容版权归属遵循所用权重许可。参考图请使用自己拥有版权的立绘。
