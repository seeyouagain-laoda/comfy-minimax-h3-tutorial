# MiniMax-H3 提示词模板

> 直接复制改。占位符用 `<>` 标出。
> 配套 `shot-rhythm.md`（分镜表）。

---

## 0. 三条铁律（先看这个）

| # | 规则 | 为什么 |
|---|---|---|
| 1 | **公共段不写具体道具** | 模型会把道具当"要展示的内容" → 角色中途消失、切道具空镜 |
| 2 | **每镜结尾重复画风锚 + 显式否定写实** | 无角色入画的镜头会漂成照片级写实 |
| 3 | **每镜都要有角色入画** | 同上 |

---

## 1. 单角色模板

```
integrated_multimodal_description:
[reference generation] Image 1 defines the character exactly — reproduce the chibi <角色> from Image 1 with identical face shape, facial features, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign, restyle, recolour or reinterpret her. Keep her faithful to Image 1 in every shot.
[Subject] The <角色> from Image 1 is the only subject of this video and must stay on screen in every single shot: <身高/头身比>, <发色与发型细节>, <标志性配饰>, <瞳色>, <服装形制与配色>, <标志性部件：尾/翼/角>, <鞋>.
[Setting] <场景：地板材质 + 关键家具 + 光线>.  ← 🔴 不写具体道具
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through close-ups and medium shots and partial details, never a full wide shot.

overall_soundscape:
<贯穿全片的底噪：房间音、时钟、窗外音>.  ← 🔴 台词不要写在这里

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot, including prop and environment shots, keeps this hand-drawn 2D anime style.
```

---

## 2. 双角色模板

```
integrated_multimodal_description:
[reference generation] Image 1 defines the FIRST character exactly — reproduce the <角色A> from Image 1 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign or restyle her. Image 2 defines the SECOND character exactly — reproduce the <角色B> from Image 2 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign or restyle her. These are TWO DIFFERENT girls and must never be merged, swapped or blended into one.
[Subject A] <角色A 外貌清单>.
[Subject B] <角色B 外貌清单>.
[Setting] <场景>.  ← 🔴 不写具体道具
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots, close-ups and partial details, never a full wide shot.

overall_soundscape:
<底噪>.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot keeps this hand-drawn 2D anime style.
```

### 双角色关键

- 🔴 **必须显式写「两个不同角色，不许融合/互换」** —— 否则两人会长成同一个人
- 🔴 **外貌清单要刻意写「最不像」的���征**（发色 / 服装形制 / 鞋 / 尾巴质感）——
  靠**反差**帮模型区分，而不是靠共同点

---

## 3. 每镜风格锚（每镜都要追加）

```
 Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel palette
 — NOT photorealistic, no photograph, no live action, no 3D render.
```

---

## 4. 镜头写法

**统一句式**：`时间戳 + 景别/主体 + 动作 (+ 台词) + Camera`

```
[Shot 1] At 00:00.000, a close-up of <主体>: <动作>。<台词用 <d>[Chinese] …</d>>。Camera static. + _STYLE
[Shot 2] At 00:01.500, cut to a medium shot of <主体>: <动作>。Camera static. + _STYLE
```

| 规则 | 说明 |
|---|---|
| 切镜统一写 `cut to a …` | 不要写 `dissolve` / `fade`，H3 照做会糊 |
| 景别交替 | 特写 → 特写 → 中景 → 特写… 切换本身就是节奏 |
| 每镜只做一个动作 | 不要"伸手→抓住→拉→喊"塞一镜 |
| 时间戳精确到 0.1s | `At 00:01.500` |
| 台词 `<d>[Chinese] …</d>` | 短、只用自称 |

### 台词规则

H3 的中文是**原生音画联合生成**，长句和复杂词容易咬字不清。

| ✅ 推荐 | ❌ 避免 |
|---|---|
| 「<角色名>的……不知道呀。」 | 「你把我的布丁吃到哪里去了呀？」 |
| 「嗯！」 | 连续多字的长句 |
| 「哼。」 | 复杂人名/地名 |

> 更好的做法：**尽量少台词甚至无台词**，靠表情和事件推进。
> 6 镜的快剪片只放 2 句台词完全可以。

---

## 5. 日式异世界（2020s 动画感）

```
A hand-drawn 2D anime with soft painterly backgrounds, low-saturation muted pastel palette,
neutral soft lighting, very fine linework, cel shading with soft volume shading.
modern 2020s Japanese TV anime art style. — NOT photorealistic, no 3D render.
```

角色动作写进 shot，不要写进公共段（`i2v` 通道忌重述长相）。

---

## 6. 日式打斗（骨架）

```
[Shot 1] At 00:00.000, a medium shot: <起手/蓄力>, <能量聚于手/武器>, 相机缓慢推近.
[Shot 2] At 00:02.000, cut to a low-angle close-up: <眼神特写>, 释放瞬间 <光柱/斩击特效爆发>.
[Shot 3] At 00:04.000, cut to a wide shot: <命中>, 冲击波扩散, 环境物件被掀飞, 一帧白闪定帧.
[Shot 4] At 00:06.000, cut to a medium shot: <收势>, 角色伫立, 光散, 余烬飘落. 相机缓慢拉远.
```

| 规则 | 说明 |
|---|---|
| 拆成 5–8 秒短镜 | 别写十几秒全程混战（会糊成一片） |
| 动作落在**能量/特效物体**上 | 「光柱轰在石环上炸开」✅；「箭擦肩而过」❌（会贯穿身体） |
| 贴身实体交互要改写成事件 | 拳脚接触容易穿模，改成「能量刃横扫 + 击退」 |
| 风格锚每 2–3 行插一次 | `cel-shaded, flat shading, bold outlines, no 3D rendering` |
| 一镜一个难度 | `fast roundhouse kick` ✅ / `explosive spinning jumping kick` ❌ |

---

## 7. 常见错误写法对照

| ❌ 别写 | ✅ 改写 | 原因 |
|---|---|---|
| `a rice cooker whose inner pot is filled with white steamed rice`（在**公共段**） | 把这句写进**具体 shot** | 公共段写道具 → 模型去拍道具空镜，角色消失 |
| `[Props] 一台冰箱、沙发、绿植…` | 删掉 `[Props]` 段 | 同上 |
| `[Character] 长蓝发、呆毛、蓝眼…`（纯文字） | `[reference generation] Image 1 defines the character exactly — …` | 纯文字 = 让模型自己重画，参考图失效 |
| 镜头里没有角色（纯道具特写） | 加人物过肩/侧影入画 | 无主体镜头 → 漂成照片级写实 |
| `dissolve to` / `fade to` | `cut to` | H3 照做会糊 |
| 20 秒片给 5 个镜头（每镜 4s） | 20 秒给 13 个镜头（每镜 1.5s） | 单镜太长 → 观感慢 |
| 第 2 段开头直接写新内容 | 开头先复述上段结尾 | 模型会把两段都渲染（出现 3 个人） |
