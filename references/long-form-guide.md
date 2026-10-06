# 长片实战指南（> 2 分钟 · 多段接续）

> 配套 `references/pipeline-checklist.md`（逐段交付清单）与 `scripts/h3_story.py`（通用故事链 runner）。
> 本文是把"单段 10–20 秒"扩展到"2–3 分钟连续剧情"的全部实战经验，
> 全部基于本机 **RTX 5060 Ti 16GB** 实跑验证（12 段 × 15 秒一次跑通，无重跑）。
> 短篇（≤ 40 秒）请回 README §4 主流程；本文只讲短篇覆盖不到的部分。

---

## 0. 什么时候用长片结构

| 成片长度 | 推荐结构 | 单段时长 | 段数 |
|---|---|---|---|
| ≤ 20 秒 | 单段 / 2 段接续 | 10 秒 | 1–2 |
| 30–40 秒 | 3–4 段接续 | 10 秒 | 3–4 |
| **2–3 分钟** | **多段接续** | **15 秒** | **10–12** |

🔴 **单段不要超过 15 秒**。H3 在 >15 秒单段上不稳定（动作漂移、角色变形概率陡增）。
要做长片，**拆成 10–15 秒一段，用 Motion Context 接续**，而不是一次硬出长视频。

---

## 1. 帧数公式（15 秒段）

短篇用的是 10 秒段（243 帧首段 + 221 帧接续）。长片用 15 秒段，帧数不同：

```
首段：     362 帧   (= 15s × 24fps，向上取整到 17 的倍数 + 偏移)
接续段：   340 帧   (= 362 - 22 钉帧，Motion Context 剪掉尾部的 22 帧钉子头)
```

> ⚠️ **接续段的帧数不是 362，是 340**。拼接时总帧数 = `362 + 340 × (N-1)`。
> 抽接缝帧、算跨段帧号都按这个算，别套用 10 秒段的 243/221。

实测（RTX 5060 Ti 16GB，864×480，8 步 turbo，双角色）：

| 段类型 | 帧数 | 生成耗时 |
|---|---|---|
| 15 秒首段（单/双角色） | 362 | 约 13 分钟 |
| 15 秒接续段（单/双角色） | 340 | 约 13–14 分钟 |

12 段连跑约 **2.5–3 小时**，无一失败。

---

## 2. 长片的脚本写法

复用 `scripts/h3_story.py` 的 JSON 故事板格式，把每段分镜写成一条 `segments` 元素：

```json
{
  "title": "湖边的一天",
  "upscale_mp": 0,
  "base_prompt": "（可选，角色卡 + 场景 + 风格锁，见 §3）",
  "segments": [
    "第 1 段分镜提示词（开头先复述上段结尾，见 §4）",
    "第 2 段分镜提示词（开头先复述上段结尾）",
    "... 共 N 段"
  ]
}
```

```bash
# 跑全部 N 段 + 自动拼接
python scripts/h3_story.py story.json 0

# 只跑前 3 段（先验证节奏再继续）
python scripts/h3_story.py story.json 0 --only 3
```

🔴 **每段都要 `--only N` 逐段跑并验收，不要一次全跑完才看**。
长片重跑成本高（13 分钟/段），发现问题越早止损越省。

---

## 3. 第三人（新角色）怎么不"变脸"

短篇只有双角色，长片常要引入第三个路人/配角（例如钓鱼者、店员）。
H3 对"没在参考图里锁定的角色"会**每段随机长相**——这是长片最坑的一点。

### 🔴 解法：在 `base_prompt` 里把第三人钉死外形

把第三人当成"固定 NPC"，用一段固定文字描述他的全部外貌特征，写进公共段，
**每一段都带着这段描述**（不只在登场段写）：

```
[Character C] A middle-aged man with a round face and short trimmed beard, wearing a wide-brim
green fishing hat, a red-and-black plaid shirt and an olive fishing vest, sitting on a folding
stool with a fishing rod and a blue bucket beside him. He is the ONLY adult man in the scene.
```

配套在 `style_lock` 里加一句硬约束：

```
style_lock:
... no other people anywhere — the ONLY human adult male in the entire video is Character C
(as described above); do NOT introduce any other strangers, passengers, staff or bystanders.
```

### 实测结论（12 段长片验证）

- 钓鱼者（圆脸/短须/绿宽檐帽/红黑格衬衫/绿背心/蓝桶/折叠凳）**12 段形象稳定，没有变脸**
- 关键是两个动作都要做：**① 公共段写死外貌 + ② style_lock 禁止出现其他任何人**
- 只做 ① 不做 ② → 模型可能在背景里塞进别的路人，抢戏且串脸
- 只做 ② 不做 ① → 第三人每段长相漂移

> 📌 反过来，如果你**不想要**任何额外角色（比如公交/地铁场景），
> 就把 style_lock 写成"车厢/站台全场只有这两个女孩，没有任何其他乘客、司机、站务、路人"，
> 能彻底杜绝路人抢戏和串脸。

---

## 4. 跨段衔接的铁律（长片命脉）

Motion Context 会把上一段尾部的 22 帧钉进下一段做参考，并 Trim 掉这段钉子头。
但模型**不会自动知道"上一段是怎么结束的"**——它只看到钉进去的尾帧。

### 🔴 每段提示词开头必须复述上一段结尾

> 第一段结尾：两人趴在岩石上往湖湾看，蝴蝶在前面飞。
> 第二段开头第一句必须写：
> *"The two girls are lying on the rock looking toward the lake bay, a butterfly hovering in front
> of them — the same girls, the same rock, the same light as the previous clip ended."*

不写这句的后果（实测踩过）：模型会把"第一段结尾的一个人"和"第二段开头的两个人"都渲染出来，
画面里凭空多出一个角色，或直接跳场景。

### 脚本层面的衔接

`scripts/h3_story.py` 已经封装好了：第 2 段起自动 `LoadLatent(N-1)` + MotionContext + Trim。
你只需保证**提示词文本**上也复述了上段结尾。

---

## 5. 室内场景（第一次出现要注意）

长片常从室外进室内（木屋、车厢、房间）。H3 对"没在提示词里明确的环境"会按默认理解，
容易跑偏（例如房间自动变成和室，见 README §8 复盘第 12 条）。

### 写法

- **每段都重复声明场景**（不要只在登场段写一次）
- 室内要写具体元素：*wooden table, a stove with a pot, warm interior light, steam rising*
- 如果场景要锁死某种风格（例如不是和室），用"重复 + 否定"：
  *"a plain wooden cabin interior — NOT a Japanese tatami room, NOT a traditional house"*

### 实测：空镜 vs 有角色

- 室内"屋里没人"的空镜（锅冒热气、米袋）**能正常出**，不会漂成写实照片——因为有 `style_lock` 兜底
- 但**关键情节镜头必须有角色入画**（README §6.3 铁律 3），空镜只适合转场过渡，不适合承载剧情

---

## 6. 总合成：把多部短片连成一部

用户要"从离家出走到进屋吃饭"一条龙，本质是**三部独立短片首尾相接**。
拼接要点：

### 6.1 跨片拼接用 concat（重编码）

三部各自的成片已经是 mp4，直接用 ffmpeg concat：

```bash
ffmpeg -y -i part1.mp4 -i part2.mp4 -i part3.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k FULL.mp4
```

### 6.2 开头杂帧裁剪（15 秒段特有）

🔴 **15 秒首段的头 2–3 帧是灰底"预热帧"**（模型把公共段里的元素堆成一张杂烩图），
从第 4 帧起才正常。**拼接前先裁掉这 2–3 帧**，否则成片开头会闪一下错误画面。

```bash
# 假设杂帧持续 3 帧（先抽 0-11 帧拼图肉眼确认边界）
ffmpeg -y -i clip1.mp4 -vf "select='between(n,0,11)',scale=200:-1,tile=6x2" -frames:v 1 head12.jpg

# 裁掉前 3 帧 + 同步裁音频（视频用 setpts，音频必须用 asetpts！）
ffmpeg -y -i clip1.mp4 \
  -vf "trim=start_frame=3,setpts=PTS-STARTPTS" \
  -af "atrim=start=0.125,asetpts=PTS-STARTPTS" \
  -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k clip1_trim.mp4
```

> 🔴 **踩坑**：音频分支必须用 `asetpts`，不是 `setpts`。
> 误用 `setpts` 处理音频会让 ffmpeg 报 "Filter setpts has an unconnected output" 链接错误。
> 视频 `setpts`、音频 `asetpts`，两者配对写。

> ⚠️ 不要用 `-ss 0.125 -c copy` 跳帧——会定位到最近关键帧，裁不干净。
> 必须像上面这样重编码 trim。

### 6.3 跨部接缝验证

总片拼接后，抽两处接缝帧确认不跳切：

```bash
# 帧号 = 各段帧数前缀和（例：part1=685帧 → 接缝1在 n=685；part1+part2=1370 → 接缝2在 n=1370）
ffmpeg -y -i FULL.mp4 -vf "select='eq(n,685)+eq(n,1370)',scale=240:-1,tile=2x1" -frames:v 1 full_seams.jpg
```

实测：上部结尾"奔跑"正好接下部开头"跑到湖边停下"，动作连贯不跳。

---

## 7. 长片质检清单（额外于短篇）

| # | 检查 | 不合格 |
|---|---|---|
| 1 | 每段帧数 = 362（首）/ 340（接续） | 段数算错或没接续 |
| 2 | 第三人每段外貌一致（钉死 + 禁其他人） | 变脸 → 回 §3 重写 base_prompt |
| 3 | 每段开头复述上段结尾 | 凭空多角色/跳场景 → 回 §4 |
| 4 | 室内场景每段重复声明 | 房间风格漂移 → 回 §5 |
| 5 | 首段头 2–3 帧杂帧已裁 | 开头闪错误画面 → 回 §6.2 |
| 6 | 总片跨部接缝不跳 | 重跑接缝段或微调衔接提示词 |
| 7 | 音频分支用 asetpts | ffmpeg 链接报错 → 回 §6.2 |

---

## 8. 长片节奏建议

- 把长片当"几个短篇幕"来写：每 3–4 段一个情绪单元（出发 → 玩耍 → 冲突 → 收尾）
- 段与段之间用"钩子"连接：上一段结尾留一个动作/视线，下一段开头接上
- 双角色段比单角色段慢约 50%（10 秒段 7 分钟 vs 10 分钟；15 秒段约 13–14 分钟），排期时算进去
- **不要让机器休眠**：长片连跑 2–3 小时，中途休眠会断掉。跑之前确认系统休眠已关闭
  （Windows：`powercfg /change standby-timeout-ac 0`）
