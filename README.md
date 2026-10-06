# 基于 Comfy 和 MiniMax H3 的实战教程 —— 以 DeepSeek 鲸鱼娘为例

> 用**一张消费级显卡**跑出 20 秒、双角色、快剪节奏的日漫短剧。
> 全程只跑本地：底模在你自己的显卡上，提示词在你自己的编辑器里。

---

## 🧰 软硬件与链接总清单（本项目用到的一切）

> 下面把**从零跑通本教程**需要的硬件、软件、模型权重、AI 工具链，以及它们的**链接和用途**
> 一次性列清楚。每一项都标明「它是干嘛用的」。详细安装步骤见 §1–§3，模型下载直链见 `references/models.md`。

### 🔧 一、硬件（本地推理跑在什么上）

| 部件 | 本项目用的 / 最低要求 | 它是干嘛用的 |
|---|---|---|
| **GPU（显卡）** | NVIDIA RTX 5060 Ti **16 GB**（实测）；最低 12 GB | **核心算力**：H3 视频扩散模型在显卡上跑，显存决定能开多大分辨率、要不要降画质 |
| **显存类型** | GDDR6 / GDDR6X / GDDR7 均可 | 只是带宽差异，够用即可 |
| **系统内存** | 16 GB（实测）/ 推荐 32 GB | 视频 VAE 解码、参考图编码时吃内存，不够会爆 |
| **硬盘** | 60 GB 空闲（实测）；全量权重 ≈ 57 GB | 存放底模 19.5GB×2 + 文本编码器 14.6GB + VAE/LoRA/放大权重 |
| **CUDA 驱动** | 支持 CUDA 的 N 卡驱动 | 让 PyTorch 能调用显卡；没有它跑不了本地推理 |
| **FFmpeg** | 任意较新版本（系统 PATH 可用） | **后期处理**：把多段视频拼接成全片、裁剪开头杂帧、混音、转码（见 §9、长片实战） |

### 💻 二、软件与运行时（代码跑在什么上）

| 组件 | 版本 / 来源 | 链接 | 它是干嘛用的 |
|---|---|---|---|
| **ComfyUI** | ≥ 0.34.0（节点内置 H3） | <https://github.com/comfyanonymous/ComfyUI> | **生成引擎宿主**：H3 是 ComfyUI 内置节点（`partner/video/MiniMax`），本机在 `http://127.0.0.1:8777` 或 `:8188` 跑图 |
| **PyTorch + CUDA** | 2.12.1+cu130（实测） | 随 ComfyUI 依赖安装 | **深度学习框架**：实际执行模型前向计算，调度显卡 |
| **Python** | 3.11 / 3.13 | <https://www.python.org/> | 跑本仓库所有脚本（`h3_story.py`、`download_hf.py`、`install_nodes.sh` 等） |
| **FFmpeg** | 系统安装 | <https://ffmpeg.org/> | 见上「硬件」条，视频拼接/裁剪/转码命令行工具 |
| **Git** | 任意版本 | <https://git-scm.com/> | 克隆 ComfyUI、节点包，以及本教程仓库本身 |

### 🤖 三、AI / Agent 工具链（谁在编排这条流水线）

| 组件 | 用途 | 链接 |
|---|---|---|
| **WorkBuddy（AI Agent 客户端）** | **总指挥**：读脚本、写提示词、调 ComfyUI、跑拼接、做质检——本教程所有文档/脚本都由它生成并实跑验证 | <https://www.workbuddy.cn/> |
| **本仓库 `scripts/` 脚本** | Agent 落地执行的工具：`h3_story.py`（分镜/批次编排）、`h3_ep_fastcut_duo.py`（双角色快剪）、`download_hf.py`（权重下载）、`install_nodes.sh`（节点包安装） | 见仓库 `scripts/` |
| **llama.cpp（本地大模型）** | **写剧本/聊天**：用 Qwen3.8-27B 一类本地模型生成分镜台词、辅助续写剧情（非生成视频，纯文本） | <https://github.com/ggml-org/llama.cpp> |
| **GPT-SoVITS（可选配音）** | **角色配音**：把剧本文本合成角色音色语音，用于长片对白（H3 原生音频偏糊，对白建议后期配音） | <https://github.com/RVC-Boss/GPT-SoVITS> |

### 🧠 四、模型权重（生成视频的"大脑"，本项目不分发，只给清单）

> 完整清单 + 直链 + 选型理由见 **`references/models.md`**。下面是总览：

| 权重 | 体积 | 它是干嘛用的 | 下载地址 |
|---|---|---|---|
| `minimax_h3_fl2va_pruned_int8_convrot` | 19.5 GB | **首帧/纯文字通道底模**：从一张图或纯提示词生成视频 | <https://huggingface.co/Comfy-Org/MiniMax-H3> |
| `minimax_h3_ref2va_pruned_int8_convrot` | 19.5 GB | **多参考图通道底模**：锁角色外貌（双角色/第三人不串脸用它） | 同上 |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 14.6 GB | **文本编码器**：把提示词+参考图编码成模型能懂的条件 | 同上 |
| `minimax_h3_video_vae` / `audio_vae` | 各 0.3 GB | **视频/音频解码器**：latent↔像素、latent↔声音 | 同上 |
| `minimax_h3_fl2v_turbo_8step` LoRA | 1.8 GB | **加速 LoRA**：把步数从 25 降到 8，出片快 3 倍 | 同上（仓库 `loras/`） |
| `minimax_h3_latent_upscaler_3d` | 0.64 GB | **二采放大**：把 0.4MP 提到 1MP+（路线 B） | <https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler> |
| 融合底模（可选） | ~11.7 GB | 一份权重通吃两条通道，省 19.5 GB | <https://huggingface.co/jfar-z/MiniMax-H3-FL2VA-Ref2VA-Hybrid-NVFP4> |

> 🔴 **本仓库不托管任何模型权重**，全部从上面官方/社区仓库自行下载。

### 🔗 五、相关链接汇总

| 链接 | 是什么 |
|---|---|
| <https://github.com/seeyouagain-laoda/comfy-minimax-h3-tutorial> | **本教程仓库**（你正在看的这个） |
| <https://github.com/comfyanonymous/ComfyUI> | ComfyUI 生成引擎 |
| <https://huggingface.co/Comfy-Org/MiniMax-H3> | H3 官方权重（底模/编码器/VAE/LoRA） |
| <https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler> | 二采放大权重 |
| <https://huggingface.co/jfar-z/MiniMax-H3-FL2VA-Ref2VA-Hybrid-NVFP4> | 融合底模（可选） |
| <https://github.com/ggml-org/llama.cpp> | 本地大模型（写剧本/聊天） |
| <https://github.com/RVC-Boss/GPT-SoVITS> | 角色配音（可选） |
| <https://www.workbuddy.cn/> | AI Agent 客户端（本教程的编排者） |
| 案例成片（仓库内） | `examples/case-01-pudding/01_output_10s.mp4` |

---

## 🎬 先看成品

下面这段视频是**本机真实跑出来的** —— 不是官方 demo，是按本教程流程从零做出来的第一支成片。

**10 秒单段 / 864×480 / 243 帧 / 417 秒生成 / 提示词全文见 `examples/case-01-pudding/`**

<https://github.com/seeyouagain-laoda/comfy-minimax-h3-tutorial/raw/main/examples/case-01-pudding/01_output_10s.mp4>

<details>
<summary>▶️ 点这里直接播放（无法内嵌视频时的备用入口）</summary>

**成片文件**：`examples/case-01-pudding/01_output_10s.mp4`（1.8 MB，h264 + aac）
**逐帧验收拼图**：

![10 frames](examples/case-01-pudding/02_verify_10frames.jpg)

**参考图 → 成片同帧对比**（左=送进模型的原始参考图，右=成片第 120 帧）：

![compare](examples/case-01-pudding/04_compare_ref_vs_output.jpg)

</details>

### 这支片子验证了什么

| 能力 | 结果 |
|---|---|
| 角色参考图锁保真 | ✅ 发型渐变 / 呆毛 / IV 发牌 / 围裙小蓝鲸 / 鲸尾，10 帧全部对上 |
| 提示词六段式（Ref2VA） | ✅ 没有出现"大概像"的漂移 |
| **快剪 1.5s/镜** | ✅ **原速播放即正常观感，不需要后期加速** |
| 音画联合生成 | ✅ 自带 aac 双声道，台词与环境音同一次扩散生成 |
| 8 步 turbo + 固定 seed | ✅ 10 秒片 417 秒出片 |
| 纯道具镜不写角色 | ❌ **失效** —— 详见案例里的「实测不足」 |

**它同样如实记录了 4 条没做到的地方**（纯道具镜角色消失、姿态不具体、呆毛小动作丢失、8 步语音偏糊），
都在 [`examples/case-01-pudding/README.md`](examples/case-01-pudding/README.md)。

### 全片速览

![hero](docs/hero.png)

**上半**：送进模型的原始参考图（2048×2048）。
**下半**：成片的 4 个抽帧 —— 布丁特写 → 眼神特写 → 腮帮鼓鼓在吃 → 回头。
发色、呆毛、发牌、围裙图案在四帧里都稳定。

---

## ⚠️⚠️ 请先读这一段

### 1. 本教程的文档与代码，全部由 AI 生成

**这不是人手写的教程，是一个 AI 干完一天的实战记录整理成的。**

- 文档、脚本、提示词模板、分镜方法论 —— **全部由 AI（Claude / WorkBuddy 一类的大模型）生成**
- 教程里所有的"经验""坑""最佳实践" —— 都是**这次实战当天真实踩出来**的，
  不是我事先知道的，也不是从教科书抄的
- 每一个参数、每一条命令都**在本机实跑验证过**（教程里标了实测耗时的都是真跑出来的）
- 但**没有人类专家审校过**，所以：
  - 可能存在表述不准确、遗漏边界情况
  - 可能有更优解是我不知道的
  - **欢迎提 issue 纠正**（§0.6）

### 2. 底模与代码不是我写的

- **MiniMax-H3** 模型由 MiniMax 发布，本教程只是**使用者**，不是模型作者
- 本项目**不分发任何模型权重**，只提供下载清单与选择依据
- 文中提到的**示例角色**（Q 版鲸鱼娘）是社区创作者发布的拟人形象，
  版权归其作者，本项目只用于教学演示

### 3. 用 AI 写教程，好在哪、要注意什么

| | |
|---|---|
| ✅ **好** | 记录的是**真实踩过的坑**（含我自己判断错、查错方向、差点换掉好模型的事故）—— 这些是教科书里没有的 |
| ✅ **好** | 参数可以直接复制，因为都验证过 |
| ⚠️ **注意** | AI 可能把"我这次这样做成功了"写成"应该这样做"，**过拟合到我这次的具体情况** |
| ⚠️ **注意** | 不同显卡、不同权重版本可能表现不同，**照做前先做小样验证** |

### 4. 安全与合规提醒

- 只用你自己拥有版权或已获授权的角色素材
- 底模与 LoRA 各自遵循其仓库许可，**部分权重有地区排除条款**
- 商用前务必读原始许可文件（详见 `references/models.md` §4）
- 生成内容的版权归属遵循所用权重的许可条款

### 5. 文档地图

| 章节 | 内容 |
|---|---|
| **🧰 软硬件与链接总清单** | ⭐ **本项目用到的所有硬件/软件/模型/AI 工具 + 链接 + 各自用途**（开头集中说明） |
| **§0.5** | 三条上手路线（选一条开始） |
| **§1 – §3** | 硬件 / 软件 / 安装 |
| **`references/models.md`** | ⭐ **模型清单 · 下载地址 · 选型理由** |
| **`references/build-graph-in-comfyui.md`** | ⭐ 在 ComfyUI 里亲手搭图（只用官方节点） |
| **`references/prompt-spec-ref2va.md`** | ⭐ Ref2VA 六段式提示词完整规范 |
| **`references/workflow-params.md`** | ⭐ 节点级参数手册 |
| **`references/shot-rhythm.md`** | ⭐ 分镜节奏标准（解决"看起来像慢动作"） |
| **`examples/case-01-pudding/`** | ⭐ **完整案例**：成片 + 原始参考图 + 提示词全文 + 验收流程 + 实测不足 |
| **`references/troubleshooting.md`** | 出片不对时查这一页 |
| **`references/agent-playbook-full.md`** | ⭐⭐ **Agent 完整作战手册**（约 1860 行）：12步端到端流程 + 27 条避坑 + 日式异世界战斗提示词库 |
| **`references/battle-anime-template.md`** | ⭐⭐ 日式异世界/魔法打斗**五铁律 + 打击感词库 + 四型预设 + 镜位表** |
| **`references/long-form-guide.md`** | ⭐ **长片实战（>2 分钟）**：15s 段帧数公式、第三人钉死不変脸、室内场景、跨片总合成、杂帧裁剪 |
| **`references/prompt-mastery.md`** | 提示词分层写法（画风需求必须分层，否则出成写实照片） |
| **`references/base-en.txt` / `ref-en.txt`** | 官方提示词格式权威参考（原文） |
| **`references/train-sill-template.md`** | SillyTails/训练类项目的模板写法 |
| **`references/example-*.md` / `*.txt`** | 可直接抄的实战示例（快剪分镜、Ref2VA、喜剧节奏） |

### 6. 这份教程的初心

**它不是为了教人怎么点 ComfyUI。**

写这份教程的初衷只有一个：

> **希望 AI Agent 自己能做短剧 —— 把"手动调参、反复试错、看日志猜问题"这些脏活
> 全部固化成可复用的规范与脚本，交出去就能自己跑通。**

所以本文的组织方式不是"教你操作"，而是"**让 Agent 照着做就对**"：

| 做法 | 目的 |
|---|---|
| 参数写死具体值、给可直接复制的命令 | 不给 Agent 留"自己猜"的空间 |
| 踩过的坑连**根因和为什么错**一起写 | Agent 遇到变体时能自己推导出解法 |
| 验收清单 / 排查决策树写成表 | Agent 可以机械执行，不用重新推理 |
| 记录 AI 自己判断错、查错方向的事故 | 让 Agent 知道**哪些直觉不可信**，避免重复同样的弯路 |
| 每条规范都标注适用边界 | 超出适用范围时，Agent 知道该回到哪一步重推 |

**换句话说：这份教程是写给 Agent 当"操作手册"的，不是写给人当"入门教程"的。**
人照着看也能看懂，但它的组织方式处处在方便机器执行。

### 7. 发现错误请提 issue

本教程由 AI 生成，**非常需要人来纠错**。如果你发现：
- 参数不合理 / 命令跑不通 / 描述与实际不符
- 有更好的解法
- 某个坑这里没写到

请开 issue 或 PR。**指出具体哪一步、实际报什么错，比说"写得不好"有用得多。**

---

## 关于示例角色

教程全程用一个具体角色走完所有环节 —— **Q 版鲸鱼娘**（蓝渐变双马尾、呆毛、
额侧发牌、鲸耳鳍、深蓝女仆装 + 白围裙、鲸尾）。选她有三个原因：

1. **形象特征足够多**（发色渐变 + 呆毛 + 配饰 + 兽耳 + 尾）——
   能暴露「参考图到底有没有接上」这类问题。特征少的角色反而看不出差别。
2. **短剧天然适配**：Q 版小动作（打哈欠、抢碗、抱膝坐着）比写实人物好演得多。
3. **社区有大量现成素材与讨论**，遇到问题搜得到答案。

> 🔴 **版权提示**：DeepSeek 的社区拟人形象「鲸鱼娘」最早由 B 站创作者发布，
> 采用 **CC BY-NC-SA 4.0（非商业 + 相同方式共享）** 协议，并经过官方收编。
> **这不影响你使用本教程**（本教程只发布方法与脚本），但如果你要商用自己的成片，
> 请自行确认所用角色立绘的授权，或**换成你自己拥有版权的角色**。

### 角色对照表

教程正文用**泛化占位符**（这样你换角色时不用改文字），对照关系如下：

| 占位符 | 教程示例里的样子 | 你要做的 |
|---|---|---|
| **女主角 / 角色 A** | Q 版鲸鱼娘（蓝渐变双马尾、呆毛、IV 发牌、鲸耳鳍、深蓝女仆装 + 白围裙小蓝鲸、鲸尾） | 放一张**干净正面像**到 `models/input/`，填进 `ref_image_0` |
| **角色 B** | 第二位角色（不同发色 / 不同服装，用于验证双角色不串脸） | 同上，填进 `ref_image_1` |
| **画风锚** | 手绘 2D 赛璐璐上色 + 可见线稿 | 按你的目标画风改那句 |

**换角色的唯一动作**：换 `models/input/` 里的图片文件。
提示词里的 `<角色A 外貌清单>` 按新角色改写即可，其余照抄。

---

## 0. 这个项目解决什么问题

MiniMax-H3 是目前开源视频模型里**少数能在一张消费级显卡上跑出多段连贯剧情**的模型。
但官方文档只讲"怎么出一段视频"，没人告诉你：

- 为什么你出的片子**角色不像设定图**（90% 的人不知道参考图压根没接上）
- 为什么你的片子**看起来像慢动作**（根因是分镜，不是模型）
- 为什么 20 秒的剧情**要拆成两段**（以及接缝怎么才不跳切）
- 两个角色**怎么同框**而不串脸

这份指南把踩出来的坑全部写进去，附实测成片的数据。

**最终成果形态**：

```
20 秒成片 = 2 段 × 10 秒（latent 接续）
         = 13–26 个 1.2–2.0 秒快剪镜头
         = 1–2 张角色参考图
         = 原速播放（不需要后期变速）

长片（已验证）= 12 段 × 15 秒（latent 接续）
            = 约 3 分钟连续剧情（362 + 340×11 = 4102 帧）
            = 双角色 + 第三人固定 NPC（不変脸）
            = 室外 → 室内 → 多人场景全跑通
            = 单张 16GB 显卡连跑约 2.5–3 小时一次通过
```
详见 [`references/long-form-guide.md`](references/long-form-guide.md)。

---

## 0.5 三条上手路线（按你的情况选）

| 路线 | 你需要什么 | 适合谁 | 文档 |
|---|---|---|---|
| **A · 纯 ComfyUI 搭图** ⭐ | **只要 ComfyUI ≥ 0.34.0**。零第三方节点、零外部工作流 | 想自己掌控、想学原理、只想用官方节点 | **`references/build-graph-in-comfyui.md`** |
| **B · 社区工作流 + 脚本** | 装 5–9 个第三方节点包 + 一份社区工作流 JSON | 要多段接续、二采放大、想批量出片 | 本文 §2.1 / §3.5 / §9 |
| **C · 商用平台 API** | 只要一个 key，不吃本地显卡 | 没有显卡 / 想先试水 | 官方托管平台（注意计费方式） |

> 🔴 **路线 A 是最通用的**。本模型在 ComfyUI 里是**内置节点**，
> 不装任何第三方东西就能跑通。本指南 80% 的内容（提示词规范、分镜节奏、
> 静默失效排查）三条路线通用。

**先读哪篇**：

| 你要 | 读 |
|---|---|
| **先看模型从哪下、为什么选它** | ⭐ **`references/models.md`**（清单 + 直链 + 逐个选型理由 + 为什么别选别的） |
| 第一次上手 | 本文 §1 硬件 → §2 软件 → §3 安装 → `build-graph-in-comfyui.md` |
| 写提示词 | **`references/prompt-spec-ref2va.md`**（六段式完整规范 + 可抄模板） |
| 填节点参数 | **`references/workflow-params.md`**（节点级参数 + 分辨率对照 + 步数选择） |
| 写出「不慢」的节奏 | **`references/shot-rhythm.md`**（分镜硬指标 + 完整分镜示例） |
| 抄现成模板 | **`references/prompt-templates.md`** |
| **看一个完整案例** | ⭐ **`examples/case-01-pudding/README.md`**（成片 + 原始参考图 + 提示词全文 + 验收流程 + 实测不足） |
| 出片不对 | ⭐ **`references/troubleshooting.md`**（一页速查：静默失效 / 画质 / 声音 / 速度 / 崩溃 / 决策树） |

---

## 1. 硬件要求

### 1.1 最低可跑

| 部件 | 最低 | 推荐 | 说明 |
|---|---|---|---|
| **GPU** | 12 GB 显存 | **16 GB** | 8 步 turbo + 864×480；低于 12GB 需降分辨率 |
| **显存类型** | GDDR6 | GDDR6X / GDDR7 | 无所谓，够用 |
| **内存** | 16 GB | 32 GB | 视频 VAE 解码吃内存 |
| **硬盘** | 60 GB 空闲 | 120 GB SSD | 底模 31.7GB + 文本编码器 25.3GB + LoRA/VAE/放大权重 |
| **其它** | 需支持 CUDA 的驱动；ffmpeg（后期拼接/倍速） | | |

### 1.2 实测数据（本指南成片所用配置）

| 项 | 值 |
|---|---|
| GPU | NVIDIA RTX 5060 Ti **16 GB**（Blackwell, sm_120） |
| PyTorch | 2.12.1+cu130 |
| 内存 | 16 GB |
| 画布 | 864×480（0.4 MP） |
| 步数 | 8 步 + turbo LoRA |

**生成耗时实测**：

| 任务 | 帧数 | 耗时 |
|---|---|---|
| 单角色 10 秒 | 243 帧 | **约 7 分钟** |
| 双角色 10 秒 | 243 帧 | **约 10 分钟** |
| 单角色 3 秒（试片） | 73 帧 | 约 2 分钟 |
| 二采放大到 1 MP | 243 帧 | +约 3 分钟 |

> ⚠️ 参考图开启 `ref_image_size='max'`（2048px 短边）会让参考 token 参与每一步采样，
> 耗时增加约 75% —— 但这是角色保真的必要代价。

### 1.3 关于 12GB 显存

把 `MEGAPIXELS` 从 `0.4` 降到 `0.3`（约 720×404）可省显存，画质略降。
**不要低于 0.25 MP**，H3 在更小画布上容易出现三角形网格伪影。

---

## 2. 软件栈

### 2.1 引擎

| 层 | 组件 | 版本 | 来源 |
|---|---|---|---|
| 生成引擎 | **ComfyUI** | **≥ 0.34.0**（embedding 需 ≥ 0.33.0） | GitHub（comfyanonymous） |

H3 在 ComfyUI 里是**内置节点**（分类 `partner/video/MiniMax`），不需要装插件。

### 2.2 权重清单

🔴 **先看这张表再决定下什么**。全量下载 ≈ **57 GB**。

| 用途 | 权重 | 体积 | 必需 |
|---|---|---|---|
| 底模（首帧/纯文字通道） | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 19.5 GB | ✅ |
| 底模（多参考通道） | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 19.5 GB | ✅ |
| 文本编码器 | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 14.6 GB | ✅ |
| 文本编码器（int8 备选） | `qwen3vl_32b_minimax_h3_int8_convrot.safetensors` | 25.3 GB | 二选一 |
| 视频 VAE | `minimax_h3_video_vae_int8_convrot.safetensors` | 0.3 GB | ✅ |
| 音频 VAE | `minimax_h3_audio_vae_fp32.safetensors` | 0.3 GB | ✅ **必须 fp32** |
| 加速 LoRA | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1.8 GB | 建议 |
| 加速 LoRA（更快档） | `minimax_h3_fl2v_turbo_4step_v1.2_768p_comfyui_bf16.safetensors` | 1.8 GB | 可选 |
| 官方 embedding ×10 | `embeddings/minimaxh3_*.pt` | ~10 MB | 可选 |
| 二采放大权重 | `minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors` | 0.64 GB | 路线 B |

**下载源**：官方发布方在 HuggingFace 上有两个仓库，一个放底模/VAE/编码器/embedding，
一个放 LoRA 与放大权重。搜模型名即可。**具体仓库名见 `scripts/download_hf.py` 里的清单**
（不同发布方文件名略有差异，按名字前缀匹配即可）。

> ⚠️ **剪枝版（pruned）可能画面崩坏**。社区实测有一个剪枝版跑出来是
> 一团模糊色块、角色消失。**换任何新底模之前，先用同 seed / 同提示词 /
> 同参考图跑一个 3 秒对拍**，见 §8。

**不想下两个底模？** 社区有融合底模（把两个底模的 AdaLN 段合并成一个文件），
一份权重通吃两条通道，详见 `references/workflow-params.md` §4.4。

### 2.3 加速 LoRA 的格式陷阱 🔴

同名的 LoRA 有两种格式，**ComfyUI 只认其中一种**：

| 格式 | key 形态 | ComfyUI |
|---|---|---|
| **ComfyUI generic** | `blocks.N.attn.out_proj.lora_A.weight` | ✅ 生效 |
| kohya | `lora_unet_blocks_0_...` | ✅ 生效 |
| diffusers | `transformer_blocks.*` | ❌ **全部 key 被丢弃** |

diffusers 格式那份的表现是：**不报错、不告警、出片看着正常但等于没挂 LoRA。**

**自查**：跑一次，控制台搜 `lora key not loaded` —— 出现就是没生效。
（只搜本次提交之后的日志，别翻整份历史，否则会把上次的告警算进来。）

### 2.4 必装第三方节点包（仅路线 B）

| 节点包 | 提供 | 必需性 |
|---|---|---|
| `ComfyUI-H3-Motion-Context` | MotionContext ×4（**多段接续核心**） | ⭐ 必装 |
| `Comfyui_Minimax_h3_latent_Upscaler` | LatentUpscaler3D（二采放大） | 建议 |
| `WhatDreamsCost-ComfyUI` | MultiImageLoader（多图参考） | ⭐ 必装 |
| `ComfyUI-VideoHelperSuite` | 存视频 / 载音频 | 建议 |
| `ComfyUI-MiniMax-H3-Hybrid` | HybridLoader（融合底模） | 可选 |

仓库地址见 `scripts/install_nodes.sh`（会自动 clone）。

### 2.5 可选节点包

`ComfyUI-Impact-Pack`（批量取帧）、`rgthree-comfy`、`ComfyUI-Custom-Scripts`、`ComfyUI-ReservedVRAM`。

> ⚠️ **不要装 `was-node-suite-comfyui`** —— 依赖重且易冲突。

---


## 3. 安装

> 下文 `<COMFYUI_ROOT>` 指 ComfyUI 主目录，所有路径都相对它。

### 3.1 路线 A · 纯官方节点（推荐，通用）

**第 1 步 · 装 ComfyUI**

```bash
# Desktop 版直接装，或：
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI && pip install -r requirements.txt
python main.py          # 打开 http://127.0.0.1:8188
```

**第 2 步 · 确认 H3 节点已内置**

在节点搜索框搜 `MiniMax`，应能看到 `MiniMaxH3ImageToVideo`、
`MiniMaxH3ReferenceToVideo`、`EmptyMiniMaxH3LatentAV`、`MiniMaxH3SigmaShift`。

搜不到 → ComfyUI 版本太旧，升级到 ≥ 0.34.0。

**第 3 步 · 下权重**

```bash
# 用仓库里的下载器（自带断点续传 + 大小校验）
python scripts/download_hf.py --all --dest <COMFYUI_ROOT>/models
```

或手动按 §2.2 的清单下载。注意目录归属：

| 文件 | 放哪 |
|---|---|
| `minimax_h3_*_pruned_int8_convrot.safetensors`（底模） | `models/diffusion_models/` |
| `qwen3vl_32b_*.safetensors` | `models/text_encoders/` |
| `minimax_h3_video_vae_*` / `minimax_h3_audio_vae_*` | `models/vae/` |
| `minimax_h3_fl2v_turbo_*.safetensors` | `models/loras/` |
| `minimaxh3_*.pt`（embedding） | `models/embeddings/` |
| 参考图 | `models/input/` |

**第 4 步 · 搭图**

打开 `references/build-graph-in-comfyui.md`，照着接。

**第 5 步 · 按 `references/build-graph-in-comfyui.md` §6 的五步验证**

先跑 3 秒试片，确认「参考图换角色 → 画面跟着变」再往下做。

---

### 3.2 路线 B · 加第三方节点（多段接续 / 二采放大）

在路线 A 基础上追加：

```bash
# ① 第三方节点包
bash scripts/install_nodes.sh <COMFYUI_ROOT>/custom_nodes

# ② 放大权重（目录不存在就手建）→ models/latent_upscale_models/
#    minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors

# ③ 依赖（以各包 requirements.txt 为准）
pip install scikit-image piexif dill segment-anything-py

# ④ 重启 ComfyUI，节点搜索框确认能搜到：
#    "MotionContext" / "LatentUpscaler3D" / "MultiImageLoader"

# ⑤ 跑脚本（脚本走 API 提交，先 --dry 只看接线不提交）
python scripts/run_ep.py --dry
python scripts/run_ep.py --clip 1
```

---
---

## 3.5 工作流 JSON 从哪来（`run_ep.py` 的输入）

`scripts/run_ep.py` 的做法是「**读取一份 ComfyUI 工作流 JSON → 打补丁 → 转成 API 格式提交**」。
所以你需要一份**支持 Motion Context 多图参考的 ref2v 工作流**。

### 路线 A · 用现成的社区工作流（推荐，最省事）

在 Civitai / 闲鱼 / B 站 / HuggingFace 搜 `H3 ref2v motion context workflow`，
下作者分享的 JSON。**确认它包含这些节点**：

| 节点 | 用途 | 必需 |
|---|---|---|
| `MiniMaxH3ReferenceToVideo` | 参考生视频（双角色靠它） | ✅ |
| `MultiImageLoader` | 多图参考 | ✅ |
| `MiniMaxH3MotionContext` + `…SaveLatent` + `…LoadLatent` + `…Trim` | 多段接续 | ✅（无则做不了长片） |
| `SaveVideo` / `VHS_VideoCombine` | 存视频 | ✅ |

拿到后：

```bash
export H3_WORKFLOW=/path/to/your_workflow.json
python scripts/run_ep.py --dry --clip 1 --ref ref_heroine.png
```

`--dry` 会打印预检行（ref images / 接线 / duration / resolution / LoRA）。
**如果你的工作流节点 id 和脚本里写的不一致**（`run_ep.py` 里的 `220`/`277`/`216`/`217`/`255`/
`237`/`202`/`213`/`218`/`336`/`191`），改脚本里 `patch_workflow()` 的对应判断即可。

### 路线 B · 自己搭（可控，但要懂节点）

最小链路（全部是 ComfyUI 官方节点 + §2.1 的第三方包）：

```
UNETLoader ─┐
CLIPLoader ─┤
LoraLoaderModelOnly ─┤
VAELoader(视频) ─┤
VAELoader(音频) ─┤
            ├─→ MiniMaxH3ReferenceToVideo
MultiImageLoader ─┘   ├─ ref_image_0（角色A）
[Prompt → PrimitiveStringMultiline]    ├─ ref_image_1（角色B）
                                     ├─ ref_video_0
                                     ├─ ref_audio_0
                                     ├─ ref_video_audio_0
                                     ├─ positive
                                     └─ latent
latent + RandomNoise + BasicGuider + KSamplerSelect(er_sde) + BasicScheduler(simple, 8)
     → SamplerCustomAdvanced → VAEDecode ─┐
     → VAEDecodeAudio ─────────────────────┴→ CreateVideo(fps=24) → SaveVideo
```

接续相关（每段一份）：

```
clip N-1 的 AV latent → MiniMaxH3MotionContextSaveLatent(clip_index=N)
第 N 段：MiniMaxH3MotionContextLoadLatent(clip_index=N-1)
      → MiniMaxH3MotionContext(context_length=22, audio_context_length=24)
      → MiniMaxH3MotionContextTrim
```

> ⚠️ 官方 ComfyUI 自带 H3 节点，但**不带** Motion Context（那是社区包）。
> 不用社区包就只能做单段。

### 路线 C · 用 MCP 工具通道（单段够用）

如果你只出单段、且客户端挂了 MCP，可以不用工作流 JSON —— 见 `SKILL.md` §18。

---

## 4. 核心工作流（10 步）

这是整份指南最重要的一节。**照做，别跳步。**

```
① 需求对齐 ──▶ ② 角色资产 ──▶ ③ 写剧本 ──▶ ④ 落成脚本 ──▶ ⑤ 干跑预检
                                                          │
        ⑩ 交付归档 ◀── ⑨ 拼接后期 ◀── ⑧ 第2段接续 ◀── ⑦ 验收发审 ◀── ⑥ 生成一段
```

### ① 需求对齐

必须问清四件事，别猜：

| # | 必问 | 默认 |
|---|---|---|
| 1 | **时长** | ≤15 秒单段一次跑完；>15 秒拆两段各 10 秒 |
| 2 | **题材 / 剧情** | 必须问 |
| 3 | **单角色还是双角色** | 单角色 |
| 4 | **要不要台词** | 只说自称（见 §6.2） |

### ② 角色资产

见 §5。**只在新角色时做这一步**。

### ③ 写剧本 —— 🔴 节奏是硬指标

| 项 | 标准 |
|---|---|
| 20 秒片的镜头数 | **10–14 个** |
| 单镜时长 | **1.2–2.0 秒**（>2.5s 就要警惕） |
| 特写占比 | **≥50%** |
| 每镜动作数 | **1 个** |
| 推进方式 | **靠"切"，不靠"演"** |

**为什么这是硬指标**：本指南的作者最初每镜给 4 秒，成片观感慢到需要 **1.5 倍速**才正常。
逐帧测量后发现画面变化量其实比正常短剧还高 65% —— 问题不在模型，在分镜。
换成 1.5 秒一镜后，原速就正常了。

> 📌 **排查"看起来慢"的正确顺序**：① 分镜单镜时长 → ② 后期变速 → ③ 步数 → ④ turbo LoRA。
> 本指南作者先查了 ③④，方向全错。

### ④ 落成脚本

复制 `scripts/run_ep.py`，改 `BASE_PROMPT`（角色卡 + 场景）和 `SEGMENT`（分镜）。

### ⑤ 干跑预检（不烧显存）

```bash
python scripts/run_ep.py --dry
```

**必须逐行核对**：

```
ref images -> ref_heroine.png | ref_heroine.png  @2048   ← 永远是两行（原因见 §7.1）
接线修正: 336.slot2 -> 191 改为 slot 1 (image_1)          ← 参考图生效的关键
duration -> 10.0s
resolution -> 16:9 (Widescreen) @ 0.4 MP
#238 LoRA -> minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16 @1.0   ← 必须是 comfyui 格式
```

任一行不对 → **别提交**。

### ⑥⑦ 生成一段 → 验收发审

```bash
python scripts/run_ep.py --clip 1      # 后台，约 7-10 分钟
```

验收清单：

| # | 检查 | 不合格怎么办 |
|---|---|---|
| 1 | probe PASS（帧数 / **有音轨** / avg > 12） | 查生成日志 |
| 2 | 角色像设定图 | 参考图可能没真接上（§7.1） |
| 3 | 两张脸分得清、没融合 | 加"两个不同角色、不许融合"指令 |
| 4 | 景别按分镜切了 | 缩短单镜时长 |
| 5 | 无照片级写实镜头 | 每镜补画风锚 + 显式否定写实 |
| 6 | 角色没中途消失 | 公共段别写具体道具（§6.3） |

🔴 **每段生成完必须让用户/自己确认后再跑下一段。**

### ⑧ 第 2 段接续

```bash
python scripts/run_ep.py --clip 2
```

Motion Context 会自动从上一段的 AV latent 里切出尾部 22 帧钉进本段，并把钉住的头部 Trim 掉。

🔴 **本段提示词开头必须复述上一段怎么结束的**（同人 / 同姿势 / 同光线），
否则模型会把两段内容都渲染出来（第一段结尾一个人 + 第二段开头两个人 = 画面里三个人）。

### ⑨ 拼接 + 后期

```bash
printf "file 'clip1.mp4'\nfile 'clip2.mp4'\n" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy JOINED.mp4

# 需要时倍速（视频音频同步）
ffmpeg -i JOINED.mp4 -filter_complex "[0:v]setpts=0.6667*PTS[v];[0:a]atempo=1.5[a]" \
       -map "[v]" -map "[a]" -c:v libx264 -crf 18 -c:a aac OUT.mp4

# 抽接缝前后各 3 帧验证跳切
ffmpeg -y -i JOINED.mp4 -vf "select='between(n,225,255)*not(mod(n-225,6))',scale=290:-1,tile=6x1" \
       -frames:v 1 SEAM.jpg
```

### ⑩ 交付归档

成片 + 抽帧图 → 写文档（分镜 + 完整提示词 + 参数 + 验收数据 + 踩的坑）→ 归档。

---

## 5. 参考图制作（成败关键）

### 5.1 规格

| 项 | 要求 |
|---|---|
| 分辨率 | **2048×2048** |
| 底色 | **纯白、不透明**（参考管线对 alpha 支持差） |
| 内容 | 单人全身、正面、站姿、完整（含耳朵和尾巴） |
| 来源 | 官方立绘 / 三视图裁切 / 自己画的设定图 |

### 5.2 从三视图裁正面

三视图横排（1376×768 之类）**不能直接当参考图** —— 模型会看到"三个人"。

```bash
python scripts/make_ref.py --src three_view.png --out ref_charA
```

三个坑：

1. **裁剪窗口不能对称取中间** —— 同一作者不同角色，中间格可能是正面、也可能是侧面。先目视确认。
2. **形态学闭运算会填掉碎片与主体之间的间隙** → 边缘碎片必须在 `binary_closing` **之前**剥离。
3. 剥离阈值用 `0.35 × 角色高度`（用平均宽度会失效）。

### 5.3 验证参考图真的生效

🔴 **看生成耗时**：`ref_image_size='max'` 会让参考 token 参与每一步采样，
同样 3 秒片会从约 110 秒涨到约 192 秒（+75%）。**没涨 = 参考图没进去。**

---

## 6. 提示词写法

### 6.1 分层结构

```
integrated_multimodal_description:
  [reference generation]  ← 🔴 必须显式点名"照 Image N 画"
  [Subject A] / [Subject B]  ← 角色外貌清单
  [Setting]                  ← 场景框架（不要写具体道具！）
  画风锚句
overall_soundscape:      ← 只放贯穿全片的底噪
non_diegetic_music: no music
style_lock:              ← 全局兜底
```

### 6.2 台词：只用自称

H3 的中文是**原生音画联合生成**，长句和复杂词容易咬字不清。
让角色只说自己的名字（"我的……不知道呀。"）能显著降低出错率，语气词也保持极短。

> 更好的做法：**尽量少台词甚至无台词**，靠表情和事件推进。
> 6 条镜头的快剪片只放 2 句台词是完全可以的。

### 6.3 三条铁律

| # | 铁律 | 违反后果 |
|---|---|---|
| 1 | **公共段不写具体道具** | 模型把道具当"要展示的内容" → 角色中途消失、切空镜 |
| 2 | **每镜结尾重复画风锚 + 显式否定写实** | 无角色入画的镜头漂成照片级写实（真人手、真实冰箱内舱） |
| 3 | **每个镜头都要有角色入画** | 同上 |

### 6.4 风格锚模板

```
 Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel palette
 — NOT photorealistic, no photograph, no live action, no 3D render.
```

完整模板见 `references/prompt-templates.md`。

---

## 7. 排错：静默失效家族

**本机最贵的一类坑：出片"看起来正常"，但某个环节根本没生效。**

### 7.1 参考图「接了但没接上」🔴 最常见

**现象**：角色完全不像设定图，像"照文字画的"。

**根因**：`MultiImageLoader` 对不足的槽位返回 `torch.zeros((1,64,64,3))`（**一张 64×64 全黑图**），
而社区工作流把 `ref_image_0` 接在 **slot 2 = 第 2 张图**上。只喂 1 张图时，
image_2 就是黑图 → 参考图从未生效。

**为什么不报错**：不报错、不告警、出片正常。只能从"像不像"看出来。

**修法**：
1. 接线改到 **slot 1**（image_1）
2. `image_paths` **写两行**（`A.png\nA.png`）兜底
3. 分辨率给 **2048**（工作流默认 1536 会降采样）

### 7.2 LoRA 静默全丢

**现象**：出片正常但就是没挂 LoRA（发丝糊、细节丢失）。

**根因**：下载到的 LoRA 是 `key_format: minimax-h3-diffusers`（`transformer_blocks.*`），
**ComfyUI 对 H3 不认这个命名格式**，几百个 key 全被丢弃。

**怎么发现**：控制台的 `lora key not loaded` warning。

**修法**：换 **ComfyUI generic 格式**的文件（`blocks.N.attn.out_proj.lora_A.weight`）。

### 7.3 通用排查法

1. **看生成耗时** —— 明显变化说明某条件真进去了
2. **看控制台 warning** —— `lora key not loaded` / `layout checks` / `saved AV latent`
3. **看 API 接线** —— `--dry` 打印的 `inputs` 里你设的参数真的在吗
4. **看是否命中缓存** —— 同样参数**秒出**就说明没真正重跑
5. **换输入做对照** —— 换一张完全不同的参考图，输出角色是否跟着变

> ⚠️ 常见误判：`grep` 整个日志会把上一次的 warning 也算进来。
> **正确做法是记录提交前的日志行数，只统计新增行。**

---

## 8. 踩坑复盘

| # | 现象 | 根因 | 修法 |
|---|---|---|---|
| 1 | 角色不像设定图 | 参考图是全黑空图 | §7.1 |
| 2 | 前几秒是实拍照片风 | 无角色入画的镜头被按"摄影"理解 | 每镜必须有角色 + 画风锚 |
| 3 | 角色中途消失 | 公共段 `[Props]` 太具体 | 道具写进 shot |
| 4 | 没挂 LoRA | LoRA 命名格式不兼容 | 换 generic 格式 |
| 5 | 指令不生效 | 子图节点 id 转换后带前缀（`459:xxx`），代码取不到 | 按前缀匹配 |
| 6 | 362 帧只输出 4 帧 | `concat` 读 PNG 序列有坑 | 改 `-framerate 24 -i f_%05d.png` |
| 7 | **第 2 段带放大必崩** `shape mismatch [2839,96] vs [7228,96]` | Motion Context 钉帧条件**分辨率锁定** | 二采换**不钉帧的 guider** |
| 8 | 下载 19.53GB 只下了 0.91GB 却报 DONE | `r.read()` 断连返回**空 bytes** → 循环正常退出 | Range 续传 + 按 `Content-Length` 对账 |
| 9 | 下完改名报 `WinError 32` | 杀软/索引临时占用大文件 | 重试 + 复制兜底 |
| 10 | 换了轻量底模画面全崩 | 剪枝版与当前 LoRA 组合不稳 | **别换**，先 A/B 对拍 |
| 11 | 误判"动作慢"的原因 | 先怀疑 turbo 压位移、再怀疑步数，**都错了** | 先查分镜单镜时长 |
| 12 | 房间自动变成和室 | 角色服装会**同化整个场景风格** | 想锁场景就重复+否定；反之可主动利用 |

---

## 9. 二采放大（可选）

一采 864×480 → latent 3D 放大 → 二采 6 步重采样 → 1376×768。

⚠️ **接续链上第 2 段带放大会崩**（坑 7），必须换成不钉帧的 guider：

```python
api["U5"] = {"class_type": "BasicGuider",
              "inputs": {"model": ["308", 0], "conditioning": ["191", 0]}}
```

SaveLatent 仍取**放大前**的 latent，所以接缝不受影响。

---

## 10. 文件清单

| 路径 | 用途 |
|---|---|
| **文档** | |
| `SKILL.md` | AI Agent 速查卡（工具调用者读这个） |
| `references/build-graph-in-comfyui.md` | ⭐ **在 ComfyUI 里亲手搭图**（只用官方内置节点，路线 A） |
| `references/prompt-spec-ref2va.md` | ⭐ **Ref2VA 六段式完整规范** + 可抄模板 + 排查决策树 |
| `references/workflow-params.md` | ⭐ **节点级参数手册** + 分辨率对照 + 步数选择 + 底模/LoRA/节点包关系 |
| `references/shot-rhythm.md` | 快剪分镜表模板 + 完整示例 |
| `references/prompt-templates.md` | 提示词模板（单/双角色/战斗/打斗） |
| `references/troubleshooting.md` | ⭐ 排错速查（静默失效 / 画质 / 声音 / 速度 / 崩溃 / 决策树） |
| **脚本** | |
| `scripts/run_ep.py` | 通用短剧 runner（单/双角色、多段、倍速）—— 路线 B |
| `scripts/make_ref.py` | 三视图裁正面 + 抠底 + 白底参考图 |
| `scripts/probe.py` | 产物探针（帧数/时长/音轨/亮度） |
| `scripts/measure_speed.py` | 帧间差分 / 运动量（查"慢不慢"） |
| `scripts/steps_ab.py` | **A/B 对拍**（改步数 / 改底模，只用它一个） |
| `scripts/download_hf.py` | 权重批量下载（断点续传 + 大小校验） |
| `scripts/install_nodes.sh` | 批量装第三方节点包 —— 路线 B |

### 10.1 常用后期命令（ffmpeg）

```bash
# 拼接多段（不重编码，接缝零损失）
ffmpeg -y -f concat -safe 0 -i list.txt -c copy final.mp4

# 倍速（视频音频同步加速）
ffmpeg -y -i in.mp4 \
  -filter_complex "[0:v]setpts=0.667*PTS[v];[0:a]atempo=1.5[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac out.mp4

# 抽帧拼图（验收用）
ffmpeg -y -i in.mp4 -vf "select='not(mod(n\,24))',scale=380:-1,tile=5x2" -frames:v 1 grid.jpg

# 抽接缝前后各 4 帧
ffmpeg -y -i in.mp4 -vf "select='between(n,220,250)*not(mod(n-220,6))',scale=300:-1,tile=6x1" -frames:v 1 seam.jpg

# 检测音频是否非静音
ffmpeg -i in.mp4 -af astats=metadata=1:reset=240,ametadata=print:key=lavfi.astats.Overall.RMS_level -f null -
```

> ⚠️ **优先做快剪，而不是后期加速**。先按 `shot-rhythm.md` 把分镜改碎，
> 再考虑变速。1.5 倍速通常是在掩盖分镜问题（见 §8 复盘第 12 条）。

---

## 10.5 长片（> 2 分钟）的已知局限

- **单段硬上限约 15 秒**：更长要靠多段接续，不是一次硬出。
- **第三人必须钉死**：没在参考图里锁定的新角色，每段会随机长相，必须在 `base_prompt` 写死外貌 + `style_lock` 禁止其他人（见 `references/long-form-guide.md` §3）。
- **跨段衔接要手动复述**：每段开头必须文字复述上段结尾，否则画面会凭空多角色/跳场景（见 long-form-guide.md §4）。
- **15 秒首段头 2–3 帧是灰底杂帧**：拼接前需裁掉（见 long-form-guide.md §6.2）。
- **连跑耗时长**：12 段约 2.5–3 小时，跑之前关掉系统休眠。
- 以上局限均已在 RTX 5060 Ti 16GB 上实跑验证可规避，其他显卡耗时会有出入。

---

## 11. 许可与免责

- 底模与 LoRA 各自遵循其仓库的许可（**注意排除地区限制**，商用前务必读原文）。
- 生成内容的版权归属请遵循所用底模/LoRA 的许可条款。
- 本指南的脚本与文档可自由使用；**使用自己拥有版权的角色立绘作为参考图**。
- 各第三方节点包版权归其作者。

---

## 12. 一句话总结

> **H3 的上限很高，难点不在模型而在工程**：
> 参考图要真的接上、分镜要够碎、每段都要人工确认。
> 把这三件事做对，消费级显卡也能出连续剧情短片。
