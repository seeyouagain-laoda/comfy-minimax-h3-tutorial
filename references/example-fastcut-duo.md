# 快剪双角色范例 —— EP05《困意传染》（2026-10-04，用户评"非常不错"）

> **新对话要出「多段 / 双角色 / 快剪」短剧，直接复制本文件改题材。**
> 主流程见 SKILL.md §1.5；运行脚本 `scripts/h3_ep_fastcut_duo.py`。
> 实测：clip1 = 243 帧 / 10.125s / 585s / probe PASS，双角色全程不串脸。

---

## 一、节奏硬指标（不达标就别开跑）

| 项 | 标准 | 本片 |
|---|---|---|
| 20s 片镜头数 | 10–14 个 | **13 个** |
| 单镜时长 | 1.2–2.0 秒 | **1.5 秒**（末镜 2.0） |
| 特写占比 | ≥50% | **6/13**（中景偏多，可再压） |
| 每镜动作数 | 1 个 | ✅ |
| 台词 | 只说自称，每句 ≤6 字 | 2 句 |

---

## 二、分镜表（13 镜）

| 镜 | 时间 | 画面 | 台词 |
|---|---|---|---|
| 1 | 0.0–1.5 | 中景：森森盘腿坐地毯前，摊着书没在看 | — |
| 2 | 1.5–3.0 | **特写**：森森张大嘴打哈欠，眼角泪花 | 哈欠声 |
| 3 | 3.0–4.5 | 中景：哒哒坐旁边抬眼看她 | — |
| 4 | 4.5–6.0 | **特写**：哒哒没忍住也打哈欠 | 哈欠声 |
| 5 | 6.0–7.5 | 中景：森森转头和哒哒对上眼 | — |
| 6 | 7.5–9.0 | **特写**：哒哒打更大的，手举在头侧 | 森森「深深的……困……」 |
| 7 | 9.0–10.5 | 中景：**两人同时**打第三个哈欠 | — |
| 8 | 10.5–12.0 | **特写**：两人眼睛半闭 | 哒哒「……哒哒的……也……」 |
| 9 | 12.0–13.5 | 中景：森森撑不住，头歪靠在书上 | — |
| 10 | 13.5–15.0 | 中景：哒哒也歪过来靠在她肩上 | — |
| 11 | 15.0–16.5 | **特写**：两颗头挨在一起，都闭眼了 | 时钟声 |
| 12 | 16.5–18.0 | 中景：哒哒的半透明鲸尾慢慢盖过来当被子 | — |
| 13 | 18.0–20.0 | 大远景：两人睡着，尾巴盖着，房间只有光尘浮动 | 只剩时钟 |

**分段**：clip 1 = 镜 1–7（0–10s）；clip 2 = 镜 8–13（10–20s），开头复述镜 7 状态。

---

## 三、公共段提示词（双角色，改题材只改 `[Setting]`）

```
integrated_multimodal_description:
[reference generation] Image 1 defines the FIRST character exactly — reproduce the chibi whale-girl maid from Image 1 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign or restyle her. Image 2 defines the SECOND character exactly — reproduce the chibi whale-girl in the white kimono-style dress from Image 2 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign or restyle her. These are TWO DIFFERENT girls and must never be merged, swapped or blended into one.
[Subject A] <角色A 外貌清单>
[Subject B] <角色B 外貌清单>
[Setting] <场景：地板材质 + 关键家具 + 光线>
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots, close-ups and partial details, never a full wide shot.

overall_soundscape:
<贯穿全片的底噪，不要在这里写台词>

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot keeps this hand-drawn 2D anime style.
```

---

## 四、分镜提示词写法

**每镜三段式**：`时间戳 + 景别/主体 + 动作`，末尾固定追加 style 锚。

```
[Shot N] At 00:0X.XXX, <景别>：<主体> <动作>。<台词用 <d>[Chinese] …</d>。Camera static. + _STYLE
```

**固定 style 锚**（每镜都要带）：

```
 Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel palette
 — NOT photorealistic, no photograph, no live action, no 3D render.
```

**切镜写法**：统一用 `cut to a close-up of …` / `cut to a medium shot of …`，
**不要写转场特效**（ dissolve / fade），H3 照做会糊。

**clip 2 开头必须复述 clip 1 结尾**：
`the same two girls, the same carpet and the same warm light as the previous clip ended`。

---

## 五、运行

```bash
cd <skill>/scripts
CLIP=1 python h3_ep_fastcut_duo.py      # 镜 1-7，约 10 分钟
CLIP=2 python h3_ep_fastcut_duo.py      # 镜 8-13，自动接 latent
# 拼接
printf "file 'clip1.mp4'\nfile 'clip2.mp4'\n" > list.txt
ffmpeg -y -f concat -safe 0 -i list.txt -c copy JOINED.mp4
```

参考图：`REF_IMAGE`（角色A）/ `REF_IMAGE2`（角色B），默认 `shenshen_ref.png` + `ref_dada.png`。

---

## 六、这个题材为什么好（换题材时保留这些优点）

| 点 | 说明 |
|---|---|
| **动作可重复** | 哈欠重复反而"越传越困"，越剪越好笑 —— 快剪最怕动作重复会腻，这题材免疫 |
| **特写为主** | 8/13 是特写，靠表情传递，零位移也能有节奏 |
| **收在安静画面** | 一起睡着 + 尾巴当被子，不靠台词的第二笑点，最耐看 |
| **服装同化场景** | 哒哒的和风裙把房间变成和室 —— 意外收获，**可以主动利用**（想统一成和风就放一个和风角色进参考图） |
