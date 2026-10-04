# 模型清单 · 下载地址 · 选型理由

> 本教程用到的每一个权重，都在这里列出：**叫什么 / 从哪下 / 多大 / 为什么选它**。
> 本项目**不分发任何权重**，只提供清单与选择依据。

---

## 0. 一张总表

| # | 用途 | 文件 | 体积 | 必需 | 选它的理由（一句话） |
|---|---|---|---|---|---|
| 1 | 首帧/纯文字通道底模 | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 19.5 GB | ✅ | 官方首帧通道底模，配 turbo LoRA 出片最快 |
| 2 | 多参考通道底模 | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 19.5 GB | ✅ | 官方参考通道底模，多图锁角色用它 |
| 3 | 文本编码器 | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 14.6 GB | ✅ | 官方配套的 32B 视觉语言编码器，负责把提示词和参考图编码成条件 |
| 3′ | 文本编码器（备选） | `qwen3vl_32b_minimax_h3_int8_convrot.safetensors` | 25.3 GB | 二选一 | int8 版兼容性更稳；nvfp4 更省显存 |
| 4 | 视频 VAE | `minimax_h3_video_vae_int8_convrot.safetensors` | 0.3 GB | ✅ | 官方视频解码器，负责 latent↔像素 |
| 5 | 音频 VAE | `minimax_h3_audio_vae_fp32.safetensors` | 0.3 GB | ✅ | 官方音频解码器，**必须 fp32**，int8 会让声音坏掉 |
| 6 | 加速 LoRA | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` | 1.8 GB | 建议 | 官方 8 步加速档，步数从 25 降到 8 |
| 7 | 加速 LoRA（更快档） | `minimax_h3_fl2v_turbo_4step_v1.2_768p_comfyui_bf16.safetensors` | 1.8 GB | 可选 | 4 步更快，但只能配 768p 分辨率 |
| 8 | 官方 embedding ×10 | `embeddings/minimaxh3_*.pt` | ~10 MB | 可选 | 官方预计算的运镜/风格张量，一句话触发运镜 |
| 9 | 二采放大权重 | `minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors` | 0.64 GB | 可选 | 在 latent 空间放大再二采，把 0.4MP 提到 1MP+ |

**全量下载 ≈ 57 GB**（含 3′ 备选为 68 GB）。

---

## 1. 下载地址

### 1.1 官方仓库（权重 1–8）

全部在同一个仓库：

```
https://huggingface.co/Comfy-Org/MiniMax-H3
```

仓库内目录结构与直接链接：

| 权重 | 目录 | 直接下载链接 |
|---|---|---|
| 1 · fl2va 底模 | `diffusion_models/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` |
| 2 · ref2va 底模 | `diffusion_models/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
| 3 · 文本编码器 nvfp4 | `text_encoders/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| 3′ · 文本编码器 int8 | `text_encoders/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors` |
| 4 · 视频 VAE | `vae/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_int8_convrot.safetensors` |
| 5 · 音频 VAE | `vae/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors` |
| 6 · 8 步 turbo LoRA | `loras/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` |
| 7 · 4 步 turbo LoRA | `loras/` | `https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_fl2v_turbo_4step_v1.2_768p_comfyui_bf16.safetensors` |
| 8 · embedding | `embeddings/` | 仓库 `embeddings/` 目录，约 10 个 `.pt` 文件 |

> 🔴 **LoRA 有两种文件名，认准带 `comfyui` 的那份**：
> `..._v1.0_comfyui_bf16.safetensors` ✅
> 同一模型若有 `..._v1.0_bf16.safetensors`（diffusers 格式）则 ❌ 全部 key 被丢弃。
> 详见 `troubleshooting.md` §1.2。

### 1.2 二采放大权重（权重 9，社区发布）

```
https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler
```

放在 `models/latent_upscale_models/`（目录不存在就手建）。

### 1.3 批量下载

```bash
python scripts/download_hf.py --all --dest <COMFYUI_ROOT>/models
```

脚本会按关键字匹配文件名、自动落到正确子目录、支持断点续传。
不同发布方命名有差异时，它匹配不到会打印提示而不是静默跳过。

### 1.4 融合底模（可选，省一份 19.5 GB）

社区把两个底模的 AdaLN 段合并成一个文件，一份权重通吃两条通道：

```
https://huggingface.co/jfar-z/MiniMax-H3-FL2VA-Ref2VA-Hybrid-NVFP4
```

- 体积约 11.7 GB（比一份官方底模还小）
- ⚠️ **不同发布方的模型不能混用**。社区微调版可能带 key 前缀、缺少剪枝标记，
  与官方权重不兼容。**用之前先对拍**（见 `troubleshooting.md` §7）。

---

## 2. 为什么选这些 —— 逐个说清

### 2.1 底模：为什么是两个而不是一个

官方发布了两个底模，**键数完全一致（都是 932 个），差异为 0**。
逐张量对比后差异只集中在 **AdaLN 条件注入段**（首尾帧 / 参考图怎么喂进残差流），
主干约 90% 完全共享。

说人话：**「主干怎么算」两家一样，「外部条件怎么喂进去」这一段不同**。

| 底模 | 通道 | 什么时候必须用 |
|---|---|---|
| `fl2va` | 首帧 / 尾帧 / 纯文字 | 你有一张具体画面要让它动起来 |
| `ref2va` | 多图 / 多视频 / 多音频参考 | 你要锁角色、锁场景、锁风格 |

**结论**：两个都要下。日常单段出片用 fl2va 就够；要锁角色一致性用 ref2va。

### 2.2 文本编码器：为什么是 32B 视觉语言模型

| 理由 | 说明 |
|---|---|
| **必须 32B** | 官方就用 32B。换小的（如 8B）质量明显下降 |
| **必须是视觉语言模型** | 它不只编码文字，**还负责编码参考图**。这是「角色不像」问题的源头之一 |
| **nvfp4 还是 int8** | nvfp4 省显存（14.6 vs 25.3 GB）；int8 兼容性更稳。**16 GB 显卡推荐 nvfp4** |

⚠️ `CLIPLoader` 的 `type` 必须选 **`minimax`**，选错会加载失败或输出乱码。

### 2.3 视频 VAE vs 音频 VAE：为什么音频必须 fp32

| VAE | 精度 | 后果 |
|---|---|---|
| 视频 VAE | int8 | 正常 |
| **音频 VAE** | **必须 fp32** | 用 int8 会让声音变成噪音 |

这是**音画联合生成**的一部分 —— H3 出的视频自带声音，不是后期贴的。

### 2.4 turbo LoRA：为什么用它，以及它的代价

H3 默认采样要 **20–28 步**，5 秒片子就要 20 多分钟。
turbo LoRA 是官方蒸馏的加速档：

| 组合 | 耗时（5 秒片） | 说明 |
|---|---|---|
| 不用 turbo，25 步 | 20+ 分钟 | 画质最好，远景/大动作必需 |
| **turbo_8step + 8 步** ⭐ | 约 6 分钟 | **日常推荐** |
| turbo_8step + **4 步** | 约 4 分钟 | 官方 i2v 模板的默认值，最快 |
| turbo_4step_768p + 4 步 | 约 3 分钟 | 只能配 768p |

**两条硬规矩**：
1. 🔴 **turbo LoRA 必须配接近它标称的步数**。给 `turbo_8step` 配 25 步会崩。
2. 🔴 **步数越高画质越好**，官方文档明确：运动幅度与音轨可用性都在 16 步左右拿满，
   8 步时**语音是输出中最弱的部分**。

**所以本教程的默认是 8 步**；拍打斗/奔跑/远景时**关掉 turbo、提到 20+ 步**。

### 2.5 embedding：为什么值得下

这 10 个文件不是关键词，是**文本编码器预先算好的 bf16 张量**（50–140 个 token 位置）。
命中 `embedding:minimaxh3_bullet_time` 时，ComfyUI 把这些位置原样拼回序列。

等于「花 10 MB 白拿官方级别的运镜控制」，比自己在提示词里堆形容词可靠。

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

**三条硬规矩**（违反会静默失效）：
1. 必须**小写** `embedding:`
2. 不能和前后单词粘连
3. **结尾不能跟句点**

⚠️ **不能调权重**（`(embedding:x:0.8)` 无效），要么满强度生效要么没有。
需要 ComfyUI ≥ 0.33.0。

### 2.6 二采放大：为什么需要它

一采 0.4MP（864×480）出片后，**在 latent 空间**放大再二采一次，
能得到显著更高的分辨率，且比后期插值保留更多细节。

```python
# ComfyMathExpression 里的归一化表达式
1.15 / (864/1920) ** 0.5   # ≈ 2.5 倍线性分辨率
```

- 输入 864×480 → 输出约 2160×1200（约 1.15 归一化像素）
- 二采手动 sigmas：`0.9231, 0.8780, 0.8000, 0.6316, 0.3158, 0.0000`（6 步）
- 🔴 **与多段接续互斥**：帧钉定的 conditioning 索引是按分辨率算好的，
  分辨率一变索引就错。放大那一步要用**不带钉帧**的 guider。

### 2.7 为什么不推荐别的底模

| 替代方案 | 为什么不推荐 |
|---|---|
| 社区微调底模（融合 + 深度微调版） | 质量可能更好，但**血统混杂**：key 前缀、剪枝布局与官方不同，无法用官方 hybrid 工具合并。适合追求特定风格的人 |
| pruned 剪枝版的社区重制版 | ⚠️ **实测会崩坏** —— 同参数对拍出来是一团模糊色块、角色消失。小 40%、快 43% 看着很美，但画质全崩 |
| 第三方量化版（w4a8 等） | 显存更省，但速度与质量的平衡需自行验证。**务必先对拍** |
| 官方托管平台 API | 不用显卡，但要付费，且**提示词策略与本地不完全一致**，本教程的参数不能直接照搬 |

> 📌 **通用原则**：任何「体积更小 / 速度更快」的替代方案，
> 都先用 `scripts/steps_ab.py` 跑同 seed 对拍，**人工看画质**再决定。
> 参数好看 ≠ 出片好看。

---

## 3. 第三方节点包清单（路线 B 专用）

| 节点包 | 仓库 | 提供 | 必需性 |
|---|---|---|---|
| ComfyUI-H3-Motion-Context | `NikoDemon80/ComfyUI-H3-Motion-Context` | 多段接续核心 | ⭐ |
| MultiImageLoader | `WhatDreamsCost/WhatDreamsCost-ComfyUI` | 多图参考 | ⭐ |
| Comfyui_Minimax_h3_latent_Upscaler | `LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler` | 二采放大 | 建议 |
| ComfyUI-VideoHelperSuite | `Kosinkadink/ComfyUI-VideoHelperSuite` | 存视频 / 载音频 | 建议 |
| ComfyUI-MiniMax-H3-Hybrid | `ANe5s/ComfyUI-MiniMax-H3-Hybrid` | 融合底模加载器 | 可选 |
| ComfyUI-Impact-Pack | `ltdrdata/ComfyUI-Impact-Pack` | 批量取帧 | 可选 |
| rgthree-comfy | `rgthree/rgthree-comfy` | 节点分组/种子 | 可选 |

一键安装：

```bash
bash scripts/install_nodes.sh <COMFYUI_ROOT>/custom_nodes
```

> ⚠️ **不要装 `was-node-suite-comfyui`** —— 依赖重且易冲突。
> 路线 A 完全不需要以上任何包。

---

## 4. 许可提醒

- 底模、LoRA、VAE、文本编码器遵循各自仓库的许可。
- ⚠️ 部分权重有**地区排除条款**，且该限制**可能延伸到生成结果**。商用前务必读原始许可。
- 教程示例角色（社区拟人形象）为 **CC BY-NC-SA 4.0（非商业）**，
  本项目只发布方法与脚本、**不附带任何立绘或成片素材**。商用请换成自己授权的角色。
