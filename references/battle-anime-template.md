# 日式魔法动漫打斗场景模板（H3 本机版）

> 2026-10-02 落盘。来源：动画运动规律（Timing & Spacing / Anticipation / Impact Frame / Follow-Through 等通用原理）
>
> - AI 打戏实测方法论（Seedance/Kling 系打戏控场法）+ 本机 H3 实测约束（16GB RAM、12 步、576×1024）。  
>   配套骨架：`references/battle-shot-skeleton.txt`（六段式可直接填）。  
>   **核心一句话：一镜只做一个动作；打击感 = 蓄力保持 → 模糊挥出 → 冲击定帧；背景动糊、主体锐利。**



---

## 0. 适用边界

| 项     | 结论                                                           |
| ----- | ------------------------------------------------------------ |
| 能生成   | 单镜 5–6s 的打斗节拍（一次出拳 / 一次挥刀 / 一次对波 / 一次受击反应）                   |
| 不能    | 三连击 combo、双方持续交互对打（H3 会糊成一团）→ **必须拆成多镜后期剪**                  |
| 本机档位  | 竖版 576×1024 / 横版 768×576；步数 12；单镜 5–6s；同场戏固定 seed            |
| 角色一致性 | 只能靠 Ref2VA 参考图 + 逐字复用的不可变层（本机**没有角色 LoRA**，见 SKILL.md §5-10） |

🔴 **最大误解**：写「激烈打斗 / 光影炸裂 / 热血沸腾」= 废话提示词，只会得到动作脱节 + 人物融化。  
AI 只认**功能型硬指令**（谁 → 做什么 → 打中谁 → 什么结果 → 镜头怎么动）。

---

## 1. AI 打戏五条硬铁律

| # | 铁律            | 反例（会翻车）                            | 正例（写这句）                                                                                |
| - | ------------- | ---------------------------------- | -------------------------------------------------------------------------------------- |
| 1 | **一镜一个动作**    | `punch then kick then dodge`       | `one single punch thrust forward`                                                      |
| 2 | **必须写镜头运动**   | 只写动作 → 模型默认静态大远景，出来像监控画面           | `a fast whip pan following her thrust, motion blur on the swing, settling by 4.0s`     |
| 3 | **蓄力必须保持**    | 直接挥 → 棉花拳                          | `the wind-up held for a full half second, then one explosive release`                  |
| 4 | **背景糊、主体锐**   | 整体 motion blur → 人物脸糊              | `motion blur on background only` ★最有价值的一句                                              |
| 5 | **武器/道具并入主体** | `a samurai with a katana` → 武器时有时无 | `a samurai gripping a katana in both hands` + `swinging the blade in a horizontal arc` |

**附：复杂度降级**（AI 的稳定区很窄）：

| 想要   | 写这个                                            | 别写                                                |
| ---- | ---------------------------------------------- | ------------------------------------------------- |
| 回旋踢  | `a fast roundhouse kick`                       | ❌ `an explosive spinning jumping kick`（morph 重灾区） |
| 快动作  | `slow motion, 60fps rendered at 24fps`（给模型更多帧） | ❌ 直接加速                                            |
| 极端动作 | 拆两镜：先只做蓄力，再只做击发                                | ❌ 一镜塞完                                            |

---

## 2. 动画八条基础原理（翻译成 AI 提示词）

| 原理                                 | 干什么         | 提示词写法                                                                              |
| ---------------------------------- | ----------- | ---------------------------------------------------------------------------------- |
| **Timing & Spacing**               | 快招少帧、重击多帧   | `sharp quick spacing on the swing, tight spacing at impact`                        |
| **Anticipation 蓄力**                | 挥之前先往回拉     | `a held wind-up backwards, shoulders coiled`                                       |
| **Squash & Stretch**               | 速度/冲击的形变夸张  | `her body stretching along the line of action, then squash on landing`             |
| **Staging 舞台调度**                   | 视线永远知道看哪儿   | 关键一击放画面中心 + `silhouette clarity, the attacker rim-lit against a bright window`     |
| **Follow-Through & Overlap 跟随/重叠** | 头发衣服比身体慢半拍  | `her hair and apron hem lagging behind the motion, settling a beat later`          |
| **Exaggeration 夸张**                | 日式的飞出去/光刃拖尾 | `sent flying across the frame, a glowing slash trail arcing behind the blade`      |
| **Impact Frame 冲击帧**               | 单帧高对比定格     | `a one-frame white impact flash at the contact point, black speed lines radiating` |
| **Sound & 反应**                     | 听感卖重量       | `a low-frequency thud, the target recoiling and briefly frozen stiff`              |

---

## 3. 日式魔法打斗词库（直接抄）

### 3.1 视觉（日式赛璐璐 + 光效）

```
cel-shaded anime style, hard-edged flat shading, bold ink outlines,
flat two-tone shadows, limited high-saturation palette, animated on twos,
snappy key poses, no 3D rendering, no photographic texture
white speed lines radiating outward, motion smear on the swing
a one-frame white impact flash at the contact point
glowing FOOL-colo aura crackling around her, volumetric energy sparks and motes
hard rim light from behind, backlight bloom, energy glow against a dark violet night sky
a loose sweat drop, a blush line, a vein-pop anger mark     (情绪符号，少量)
```

### 3.2 打击感（★核心几句）

```
the wind-up held for a full half second
one explosive release with a fast motion smear
motion blur on background only        ← 背景糊、主体/武器保持锐利
a crisp impact, the target's head snapping back
brief stiff freeze on contact, then recoil
debris and sparks scattering past the camera
```

### 3.3 镜头（打戏专属，缺镜头=监控视角）

```
a fast whip pan following her thrust from left to right, settling by 4.0s
a low-angle shot from below, camera slightly tilting up with her
a handheld slight sway, breathing frame
a crash cut to a close-up of the clenched fist on impact
a slow push-in on the held impact frame
```

### 3.4 声音（内联进每个镜头，防时间漂移）

```
a rising hum          (蓄力起势)
one sharp release whoosh    (挥出)
a low-frequency meaty thud + a ringing crackle    (击中)
cloth rip, metal clash, stone grinding   (环境反馈)
silence for one beat, then the sound rushing back    (定格留白)
```

---

## 4. 四型预设（拆子模板，别用一套词打全部）

| 型         | 重点          | 动作词                                                                                                | 光效控制           | 镜数  |
| --------- | ----------- | -------------------------------------------------------------------------------------------------- | -------------- | --- |
| **近身格斗**  | 接触反馈 + 肢体姿势 | `lunge, block, hook punch, recoil`                                                                 | 少，靠汗/衣摆/灰尘     | 4–5 |
| **兵器对抗**  | 武器轨迹 + 重量感  | `gripping the katana in both hands, swinging the blade in a horizontal arc, a glowing slash trail` | 刃口高光 + 火花      | 5–6 |
| **超能力对波** | 光效面积 + 表情   | `planting both palms, a held wind-up, one explosive release of a blue-magenta beam`                | ★光效最猛，最易糊，控制面积 | 4–5 |
| **追逐穿插**  | 镜头移动 + 背景位移 | `sprinting, hair streaming back, background streaking past`                                        | 靠环境光           | 4–6 |

---

## 5. 镜位表（6 镜 / 本机 H3 切法）

| 镜 | 内容                   | 相机         | 时长 | 关键句                                                   |
| - | -------------------- | ---------- | -- | ----------------------------------------------------- |
| 1 | 建立：两人对峙、能量起势         | 广角固定、低机位   | 5s | `a static wide shot, both auras crackling`            |
| 2 | **蓄力保持**             | 低角度仰拍      | 5s | `the wind-up held for a full half second`             |
| 3 | 挥出（whip pan + smear） | 横向摇镜追运动    | 5s | `a fast whip pan, motion blur on background only`     |
| 4 | **冲击定帧**             | 特写锁死 + 速度线 | 5s | `a one-frame white impact flash, head snapping back`  |
| 5 | 反应（踉跄、衣摆乱飞）          | 手提微晃       | 5s | `a handheld slight sway, apron hem lagging`           |
| 6 | 收招站定、能量收回            | 广角缓推       | 6s | `a slow push-in, her tail settling, the aura dimming` |

🔴 **镜 4（冲击帧）结尾别停死**：让速度线还在扩张，才不会在镜 4→5 产生顿挫。

---

## 6. 六段式骨架用法（Ref2VA，顺序不可改）

```
subject_definitions → summary → retention_analysis → detailed_description
                    → overall_soundscape → non_diegetic_music
```

**六条填空规则**：

1. `subject_definitions` 给**每张参考图一个独立段落**，段首字段名重复写（H3 吃这个）；  
   每张图必须写「appearance anchor 职责 + 逐项复刻清单 + is not a frame of the target video」。
2. `summary` 用 `[reference generation]` 开头，一句话点明「本片是几秒的什么戏、三镜各干什么」。
3. `retention_analysis` 逐图逐镜列 `fully_preserved` 清单。
4. `detailed_description` 每镜三段式（画面 → Sound inline → Camera），**声音必须内联进每个镜头**（用户硬规则）。
5. `overall_soundscape` 只放贯穿全片的底噪（风声/魔法余鸣/环境）。
6. `non_diegetic_music` 给时间轴：紧张鼓点 → 蓄力定音 → 击发爆点 → 收尾一响。

**🔴 风格锚点每 2–3 行插一次**（模型约每 10 帧重评风格，不插就漂回写实）：  
把 `cel-shaded, flat shading, bold outlines, no 3D rendering` 这句**在 detailed_description 里至少重写两遍**。

**🔴 负向收尾**：每镜末尾加  
`no speckles, no spots, no bubbles, no blobs, no floating artifacts.`

**🔴 反融合**：参考图段落里写死 `only one girl may be visible in the frame`，防把设定图的多视图排版画进画面。

**完整实例**（《深深·魔法对波》6s，照这个抄）：见下方 §9。

---

## 7. 本机参数配方

| 场景             | 参数                                                                  | 耗时      |
| -------------- | ------------------------------------------------------------------- | ------- |
| 打斗试片（验证动作语言）   | `--duration 3 --steps 8 --w 384 --h 640 --seed 42`                  | ~45s    |
| **单镜正式打斗（推荐）** | `--duration 5 --steps 12 --w 576 --h 1024 --seed 42 --ref-size max` | ~15 min |
| 长镜（收招 / 对峙）    | `--duration 6 --steps 12 --w 576 --h 1024`                          | ~18 min |

- 同场戏**不换 seed**（换场才换）；失败重跑先 +1 seed。
- 打斗戏**别上 8 步**（斑点重灾区）；12 步起步。
- 画布天花板见 SKILL.md §3.8（836K 死档、720×1028 双重不可用）。
- 参考图喂 `_正面.png` 一张就够（三视图拆分见 Step 2.5）。
- 提交后必查 8188 队列真有任务（8777 会播僵尸假进度）。

---

## 8. 多镜连起来（末帧续接 + 运动匹配）

按 SKILL.md §「多段连贯性」执行，打戏额外加两条：

1. **末帧别取最后帧**：生成器尾段 10–15% 已把镜头摇停，拿它做种子 → 下镜从静止起步 = 接缝一顿。  
   → 每段多生成 20–30%，回退到「运动还没减速」那一帧当 `--ref`。
2. **运动方向必须写反**：A 镜结尾 `镜头快速右摇` → B 镜开头 `从右摇减速、模糊收敛`。推近配推远。
3. 每 3–4 镜重锚一张新静帧（artifact 会累积下传）。
4. 全链光向/色温逐字不改（`hard rim light from behind` 这种词每段一模一样）。
5. 音频：抽掉分段自带音轨 → 统一 BGM + `acrossfade 0.3–0.4s`；打击音效按节拍裁切对齐。

---

## 9. 完整实例（可直接改）

文件：`<ASSET_DIR>\深深_魔法对波_6s.txt`（生成版英文）+ `_中文版.md`。

```text
subject_definitions:
<Picture 1> is a full-body front-view reference portrait of the chibi anime whale girl named Shen-Shen: two-head-tall chibi proportions, very long wavy hair in a deep-blue to light-blue gradient with one big curled ahoge on top, a white frilled maid headdress, a blue "IV" roman-numeral hair clip on her fringe, a small side ponytail tied with a blue bow and a tiny whale-tail hair ornament, whale fin ears on both sides of her head, large round blue eyes, a navy blue long-sleeved maid dress with gold-trim embroidery and white frilled cuffs, a white frilled apron with a little blue whale print on the pocket, a dark blue neck bow with a blue gemstone brooch, sparkling blue whale tail fins with star speckles at her side, white socks and black mary-jane shoes. <Picture 1> serves [Shot 1] [Shot 2] [Shot 3] as an appearance anchor: her chibi proportions, facial identity, gradient blue hair with ahoge, maid headdress, "IV" hair clip, whale fin ears, navy maid dress, whale-print apron and starry blue whale tail must be reproduced exactly. <Picture 1> is not a frame of the target video; its portrait layout must not appear on screen, and only one girl may be visible in the frame.

summary:
[reference generation] The target video is one continuous 6-second stylized cel-shaded anime magic battle: Shen-Shen plants both palms and holds a dramatic wind-up, then releases one explosive beam with her starry whale tail crackling with blue-magenta energy, and the frame holds on the impact with speed lines radiating as she lets out oneetermined shout. <Picture 1> supplies her appearance only; her identity, hairstyle, outfit and starry whale tail are preserved, while her poses, the environment, the camera work and all sound are newly generated.

retention_analysis:
<Picture 1> ([Shot 1] [Shot 2] [Shot 3] appearance anchor): fully_preserved - chibi two-head-tall proportions, gradient blue long hair with big curled ahoge, white frilled maid headdress, blue "IV" hair clip, whale fin ears, large round blue eyes, navy blue long-sleeved maid dress with gold-trim embroidery, white frilled apron with the little blue whale print, dark blue neck bow with gemstone brooch, and the sparkling starry blue whale tail are all reproduced; only her poses and actions, the camera movement and all audio are newly generated.

detailed_description:
[Shot 1] A dark violet night shrine courtyard, hard rim light from behind, white paper lanterns glowing, cel-shaded anime style, flat two-tone shadows, bold ink outlines. The chibi whale girl from <Picture 1> plants both palms forward, a glowing blue-magenta aura cracking around her whale tail, then holds the wind-up for a full half second with her cheeks puffed and one determined cry on her lips. Sound inline: 0.00-1.400s a rising electric hum climbing in pitch; 1.400-1.900s a held silence with only the hum; 1.900s a soft stone scrape as she braces. Camera: a static low-angle wide shot from below, focus held on her. no speckles, no spots, no bubbles, no blobs, no floating artifacts.

[Shot 2] At 01.900 a quick push-in to medium close while she releases: her palms thrust forward in one explosive release, a fast motion smear across her arms, energy sparks scattering past the camera, white speed lines radiating outward, her hair whipping back and her apron hem flaring. Sound inline: 02.000-03.000s a sharp release whoosh; 02.400-04.600s a ringing energy crackle; 03.400-04.200s her bright determined shout in standard Mandarin. Camera: a fast whip pan following her thrust from left to right, motion blur on background only, settling by 04.800s. no speckles, no spots, no bubbles, no blobs, no floating artifacts.

[Shot 3] At 04.800 the shot holds on the impact frame: a one-frame white flash at her palms, black speed lines still expanding, her whale tail flared wide with star speckles, and a single determined sweat drop on her cheek. Sound inline: 04.800-05.200s one low-frequency thud with a crisp crackle; 05.200-05.700s the expanding speed-line rush; 05.700-06.000s a faint echo through the courtyard. Camera: a slow push-in on the held impact frame, focus locked on her palms. no speckles, no spots, no bubbles, no blobs, no floating artifacts.

overall_soundscape:
A cool night courtyard ambience: wind through shrine trees, distant lantern creaks, faint stone echo; a cute slightly high female voice in standard Mandarin for her lines.

non_diegetic_music:
A tense taiko-and-string cue from 00.000, one held drum hit at 01.900, an explosive hit at 02.000, and one ringing low tail ending at 06.000.
```



---

## 10. 五层排查链（废片按这个顺序，别乱调参）

| 层 | 看什么 | 典型症状 → 修法 |
|---|---|---|
| ① **文本** | 这一镜的动作因果写全了吗？（攻击方 / 目标 / 结果 / 镜头运动） | 动作糊 → 一镜只留一个动作 |
| ② **参考图** | 清晰、无遮挡、风格统一；角色描述逐镜逐字复用 | 换脸/换装 → 锚图缺失或风格常量不一致 |
| ③ **参数** | 步数/分辨率/seed/运动幅度 | 动作僵硬缓慢 → 缺动态词或幅度太低；先拉回常规值 |
| ④ **版本** | 模型/节点版本差异（图生视频类工具尤甚） | 换版本后风格突变 → 先看版本差异再改提示词 |
| ⑤ **后期** | 音效与剪辑 | 画面连贯但不够燃 → **别回去改画面**，问题在音效/剪辑 |

### 崩溃诊断速查

| 症状 | 根因 | 修法 |
|---|---|---|
| 打着打着换张脸 | 角色锚图没逐镜带上 / 风格常量改了 | 每镜 `subject_definitions` 逐字复制 + 风格锚句每 2–3 行插 |
| 多手多脚、肢体扭曲 | 复杂姿态没先出静态关键帧验证 | 先出静帧钥匙 pose，再单独生成 |
| 动作软绵（棉花拳） | 没写蓄力保持 / 没写 `motion blur on background only` | 补 hold + 背景糊 |
| 光效糊住动作 | 「能量/爆炸/光波」词堆太满 | 降光效面积，只留一处主光 |
| 镜头乱晃 / 监控视角 | 没写镜头运动 | 每镜必写一条 camera 指令 |
| 武器时有时无 / 变形 | 武器被当背景细节 | 并入主体：`gripping X in both hands` + 描述它在做什么 |
| 画面空旷像虚空 | 环境没写 | 补环境 + 光锚（`hard rim light from behind`） |
| 中间马赛克 | VAE 换出损坏 / 步数不足 | `--disable-smart-memory` + 12 步（见 SKILL.md §3.10） |

---

## 11. 生成前自检清单

- [ ] 一镜只写了一个动作（没有 `then` 连招）
- [ ] 每镜都有一条 camera 指令（推/摇/跟/固定，不能省）
- [ ] 蓄力写了 `held wind-up` + 保持时长
- [ ] 有 `motion blur on background only`，主体/武器是锐的
- [ ] 有 impact 关键词（white flash / head snapping back / one-frame）
- [ ] 风格锚句在 detailed_description 出现 ≥2 次
- [ ] 环境 + 光向写死且全文一致
- [ ] 武器并入主体描述
- [ ] 声音内联进每个镜头（带秒数）
- [ ] 每镜末尾有 anti-artifact 负向词
- [ ] `<Subject` 全文零命中（只用 `<Picture N>`）
- [ ] **非 ASCII 零命中**（除 `<d>[Chinese] …</d>` 台词）★ 2026-10-02 踩坑：Seg1 写成 `black雾`、Seg3 写成 `black一角`，模型会把中文词当语义吃进去；修 `str.replace` 整串替换 + 扫描复验（Edit 只匹配 old_string 片段、会留 `black mist雾` 这种残句）
- [ ] 参考图只喂 `_正面.png`；参数是 384×640 试片 → 12 步正式档

## 12.1 网络增量（2026-10-02 调研补录，异世界/日式战斗番通用）

> 来源：动画运动规律 + AI 打戏控场法（Seedance/Kling 系）+ 社区 H3 实战 prompt。
> 完整展开见 `桌面\重要AI配置文档\06_视频与图像生成\06_异世界日漫战斗场景_制作要点与提示词库_20261002.md`。

### 帧数表（24fps，控制"重量"的唯一硬指标）

| 动作 | 帧数 | 写法 |
|---|---|---|
| 快拳/快刺 | 6–8 帧（0.25–0.33s） | `a snap thrust, 8 frames of travel` |
| 重砸/大剑劈 | 18–24 帧（0.75–1.0s） | `a heavy overhead slam, tight spacing at impact` |
| 戏剧性停顿 | 12+ 帧静止 | `a held silence, nothing moves for a full beat` |
| Smear 残影 | 1–2 帧扭曲 | `a one-frame smear` |

→ 提示词里**写的时长就是帧数**：想快拳压到 0.3s，想重砸给 1s。

### 日式番剧演出惯例（缺了就像短视频）

| 惯例 | 写法 |
|---|---|
| **Hold + camera-move**（TV 动画主力） | `a static wide shot with a slow drift, her hair swaying` |
| **反应插入 0.5–1s** | 另起一镜：`a half-second insert: one eye widening, a single sweat drop` |
| **3-hit beat** | 蓄力(hold) → smear → impact hold（与本模板 §1 同构） |
| **Pillow shot 空镜**（kire） | `a slow pan across the burning village, embers drifting` |
| **Ma 間 留白** | `silence for one beat, then the sound rushing back` |
| **Impact zoom / slow zoom-out** | 受击瞬间急推脸 `a rapid push-in on her face at the moment of contact`；重击后慢拉远 `a slow zoom-out revealing the crater` |
| **Crash zoom / Dutch angle** | `the camera crash-zooms forward at the instant of impact` / `a tilted Dutch angle, the frame rocking` |

### 社区 prompt 六条硬规则（写多镜必抄）

1. **多段时间轴**：`0-2s / 2-5s / 5-8s` 分段，每段 = 1 镜头 + 1 动作 + 声音 + 运镜。
2. **参考图只借角色，不借构图**：「只取脸/眼形/瞳色/发型/发色/服饰/武器/剪影，**不复制背景、角度、构图、分屏排版**」。
3. **角色数写死**：禁 `face averaging / 换发色 / 换服饰 / 多加一个人 / 克隆`。
4. **武器数量写死**：`the total number of blades in the whole shot is fixed at six`，防 morph。
5. **双角色双色分离**：攻击方用 A 专属色做主光/刃残光，防守方用 B 专属色做补光/反击残光；**两色不许混**。
6. **背景暗一档**：`make the background one step darker than the characters to clarify the face, silhouette and weapon path`；地面加接触锚点（倒影/水珠/尘/火花/魔法粒子）。

### 混音优先级

台词可懂 > 打击音效 > BGM 床；一拳要分层（合成 kick/tom + whoosh + 布料摩擦），别用干闷响。

## 12.2 30 秒长片 · 3 × 10s 三连切（2026-10-02 写）

> 活样本：`<ASSET_DIR>\异世界_绯樱_狐火斩_30s_脚本.md` + `异世界_绯樱_30s_S1/S2/S3_10s.txt`（+ `_中文版.md`）。
> 30 秒不要一次提交（本机 15s 会撞 VAE NaN 坏块），切 **3×10s**；单段打动作用但**打斗段 ≤6s 的实测经验仍然成立**，10s 段的缓解办法见下。

**三段各扛一拍**（把「蓄力 → 保持 → 爆发」摊到 30 秒）：

| 段 | 幕 | 内容 | 镜头 | 风险 |
|---|---|---|---|---|
| S1 | 钩子 | 建立 / 登场 / 对峙（静态为主） | 低机位广角 + 极慢推 | 低 |
| S2 | 对抗 | 一记硬动作 + **held wind-up 1.5–2s** | 侧面贴地跟 → 定机位 | 中 |
| S3 | 冲击 + 余韵 | 命中白闪 + 定帧 + **slow zoom-out 收 4–5s 空镜** | 横向摇镜 → 锁死定帧 → 慢拉远 | 高 |

**四条硬规则（从本活样本抽象）**

1. **段内时间戳一律 0–10s 起写**，不要写全局 20–30s（模型在一条 10s 片里找不到锚点）。文档表里的「10–20s」是**全片位置**，段内就是第 2 段的 0–10s。
2. **跨镜连续物必须列表写死**（取自社区 10–30s 动作模板）：狐火 3 团 / 纸垂 2 片 / 镰刀 1 把 / 灯笼 2 盏，起点 → 变化 → 终点三段连成一行，逐项对。段间掉物件（多一把刀、狐火变 4 团）全靠这张表抓。
3. **硬动作卡在段中，别卡首尾**：S2 的接触放 3.6–7.2s，S3 的命中放 2.6–5.2s，段首段尾给 hold。这样 10s 段尾部永远是慢镜/静止，正好吃「减速尾巴」，下一段起手不顿。
4. **光向词逐段逐字不改**（`hard rim light from behind` + 灯笼暖橙），只改色温描述词（暖橙 → 暖橙+黑雾 → 蓝白 flood）。

**现成 30 秒结构参考（网上查到的）**

| 来源 | 结构 | 可抄 / 别抄 |
|---|---|---|
| wikiprompt《Samurai vs Fire Titan》30s | 0–2 / 2–10 / 10–18 / 18–30 四拍 | ✅ 30s 四拍等分 + 音效逐秒排时间轴 + 尺度对比（渺小 vs 巨物）；❌ 追逃跟拍本机会糊 |
| awesomevideoprompts《Anime Hero Battle》 | 10 帧 × 1.5s | ✅ 双色 aura 分离、紫只在碰撞点；❌ 1.5s 碎切对连续 AR 模型是灾难 |
| awesomevideoprompts《Weekend Action Fight Scene》 | 0–2 钩子 → 2–10 六连招 → 10–15 Boss | ✅ 开场 2s 内给高风险钩子；❌ 一镜六连招违反一镜一动作 |
| 腾讯频道《动作提示词》10–30s 模板 | S01–S08 + 动作/镜头/光影三公式 | ★跨镜连续物、冲击帧全片至多 2 次、场景左右锁死不镜像；八段是 90s 节奏，30s 只取登场/首冲/胜负手三组 |
| animearc 三幕式短剧 | 钩子(≤15s) / 对抗 / 悬念 | ✅ 短视频前三秒必须给事件 |

---

## 12. 纯文生（无参考图）写法

新角色没有锚图时的正确姿势（异世界·绯樱 Seg1 实测）：

| 项 | 写法 |
|---|---|
| subject_definitions | **整段删掉**（带 `<Picture N>` 才需要）；角色外观改写在 summary 首句 + 每镜 shot 开头 |
| retention_analysis | **整段删掉** |
| summary | 首句 `The target video is one continuous N-second cel-shaded anime … set at NIGHT_PLACE:` 后紧跟一段角色外观长描述（发色/服饰/武器/光效），再写动作链 |
| detailed_description | 每镜开头先复述一次外观锚（hair / hakama / blade / flames）+ 画风锚，再写动作 |
| 一致性 | 靠**同 seed + 逐字复用外观块**，靠不住 → Seg2 起立刻切末帧续接（`<Picture 1>` 写作 "the final frame of the previous connected shot"，见 §8） |


---

## 13. 官方三大公式 + 四套模板（本机同款模型的写作规范）

> 本机底模 = `Minimax-h3_Singularity_ref2va_v1.3_int8`，网上《MiniMax_H3_Singularity_Prompt_Writing_Specification_Enhanced》
> 就是它的**官方提示词规范**。出处与全文：`桌面\重要AI配置文档\06_视频与图像生成\08_MinimaxH3打斗提示词模板库_官方规范与本机对照_20261002.md`

### 三条公式（所有打斗提示词的底层逻辑）

| 公式 | 内容 | 反例 |
|---|---|---|
| **动作链** | 初始状态→触发→主动作→位移/惯性→接触/反应→最终状态 | 只写"攻击" |
| **运镜五要素** | 机位/景别 + 运动方式 + 方向 + 速度幅度 + 跟随主体 | "动态镜头""dynamic camera" |
| **特效四要素** | 触发条件 + 视觉形态 + 运动方向 + **与环境的物理交互** | "酷炫特效" |

官方原话：爆炸要有冲击波和碎片轨迹，火花要有来源和衰减，烟雾要有扩散和光影交互。

### 模板 A · 魔法 / 能量特效（法师对决直接套）

```
[Shot 1] <Subject 1> raises one hand and gathers a concentrated energy field around the palm.
The energy intensifies from a small glow into a dense rotating mass, with particles
spiraling inward before being released forward.
The camera pushes toward the hand, then tracks the energy projectile as it travels
through the environment.
At impact, a shockwave expands outward, nearby dust and loose objects are displaced,
and the surrounding surfaces receive a brief burst of colored illumination.
```
中文：抬手聚能 → 小光点长成旋转粒子团 → 推进后跟拍能量弹 → 命中冲击波扩散 + 浮尘位移 + **环境被彩色光短暂照亮**
🔴 最后那句"环境被彩色光照亮"是本机实测最缺的一项（写了魔法阵但整体偏静）。

### 模板 B · 远景持续动作（防空转，对症"复刻态"）

```
[Shot 1] A wide establishing shot shows <Subject 1> and <Subject 2> far in the background.
Both subjects continue walking steadily along the path throughout the entire shot,
maintaining consistent direction and spacing.
The camera performs a slow lateral tracking movement, keeping the distant figures
within the wide composition.
Their clothing and hair move subtly with the surrounding breeze, while the environment
remains visually dominant.
```
官方明确：**远景人物"走两步就定住"是高频坑，解法就是显式写 `continue walking` / `continue moving throughout`。**
本机 2026-10-02 实测：S1"开阵对峙"段三帧几乎一致 = 空转，就是缺这句。

### 模板 C · 武侠短兵器（单镜一动作的教科书）

```
[Shot 1] A medium-wide side angle frames <Subject 1> and <Subject 2> in opposing positions.
<Subject 1> shifts into a lower stance, draws the weapon backward, then launches forward
with accelerating momentum. The camera tracks laterally with the attack, then arcs
around the point of contact. At impact, sparks and dust burst outward, the opponent
recoils, clothing and hair react to the force, and loose debris is displaced across the
ground. The attacker completes the follow-through and settles into a controlled stance.
```

### 模板 D · 爆炸 / 灾难

```
[Shot 1] The camera begins in a stable wide shot as <Subject 1> stands near the center
of the environment. A sudden trigger occurs behind the subject, followed by a rapidly
expanding explosion. The camera pulls backward while panning to keep the subject and blast
inside the frame. Fire, smoke, debris, dust, and fragments expand outward; nearby surfaces
are illuminated by the flash and respond to the pressure wave. The shot ends as the
initial blast subsides into drifting smoke and falling debris.
```

### 官方自检 5 条

1. 每个动作都有 开始/推进/反应/结束 四段
2. 运镜写明 类型+方向+速度+跟随对象
3. 特效绑定 触发点 + 物理后果
4. 音效与可见事件同步
5. 远景需移动时明确写 `continue walking`

**高频错误**：把每张参考图都当首帧 · 一镜塞太多同时动作 · 堆 `cinematic/epic/high quality` 空泛词。
官方另强调：**多角色别一镜同时动** —— 社区最佳实践是 `Each character performs individually before any combat begins`（先各自演一段再交手）。

### 官方词表（直接抄词，18 运镜 / 17 灯光 / 12 调色）

运镜：Dolly zoom · Crane shot · Steadicam · Whip pan · Rack focus · Dutch angle · Push in · Pull out · Tracking · Orbital · Pedestal · Handheld · Locked-off · SnorriCam · Slow creep zoom
灯光：Golden hour · Blue hour · Rembrandt · Split lighting · Rim light · Chiaroscuro · Neon noir · Practical lights · Silhouette · God rays · Lens flare
调色：Teal & Orange · Bleach bypass · Kodak Portra 400 · Fuji Velvia · Cyan shadows + magenta highlights · Monochrome · LUT Blockbuster


---

## 14. 🔴 2026-10-02 夜 9 段实战：抄原文 > 自己写；本机天花板是静帧动画

### 14.1 最重要的一条：直接抄「成片级原文」，不要自己按规范改写
9 段实测（绯樱3+法师6+拳赛1+豪华魔法3）：我按官方三条公式改写 4 版全部偏暗/能量不出现/空转；
**一字不改照抄 minimaxh3.ai 上 @LudovicCreator 的《Dark Fantasy Mage Duel》-> 一次成片**，
平均亮度 57.5（自己写的只有 40 左右）。**差距在提示词质量，不在模型能力。**

成片级原文自带的六件事（自己写时最容易全部漏掉）：

| 要素 | 原文原话 | 漏掉的后果 |
|---|---|---|
| 亮度 | flooded with light / volumetric energy effects / dramatic storm lighting | 全片暗成一团 |
| 尺度 | massive / gigantic / giant eclipsed moons | 人物一小光效跟着看不见 |
| 双色分工 | cosmic blue energy vs crimson fire | 混色、角色发色漂移 |
| **连续事件链** | 蜡烛灭->墙波纹->重力偏移->碎石绕轨->空间裂隙->楼梯折天->蚀月->时间凝固->爆炸（9 事件） | 单一动作 -> 复刻态空转 |
| 不可动词 | ripple / bend / fold / float / twist / distort / destabilize / orbit | 画面不自己动，只有人物动作 |
| 英雄收尾 | both mages float above the collapsing observatory | 没有收尾定格 |

### 14.2 官方提示词长度红线（一直踩线）
官方 45 条示例统计：**中位 130 个中文字符，最长 657-858**。
自己写的六段式 detailed_description 单段 2000+ 字符 -> **关键事件被稀释，模型只执行最稳的那部分（构图）**。
**写提示词要短，宁可少写不要长。**

### 14.3 「一镜一动作」对 Ref2VA 不适用（推翻本模板 §1）
实测：成片级提示词恰恰是 `one uninterrupted cinematic sequence` 的**持续升级事件链**才出效果。
单一动作 + Ref2VA = 复刻态空转。§1 铁律在 Ref2VA 续接段请改用 §14.1 的事件链写法。


### 14.4 本机天花板：静帧动画（9 段全部如此，含 15s 长片与抄的原文）
- 能做到：画面精美（建筑/法阵/火焰/人物一致性都好）
- 做不到：画面动（机位、构图、物体位置基本冻结，只有火焰闪、粒子飘）
- 抽 5 帧（1.2/4.6/8.3/12.1/14.8s）对比几乎一模一样。
- 根因判断：ref2va + 单参考图 + 12 步 下，模型把参考图当「要复刻的画面」，构图锁死。

**唯一已知解法（还没试）：V2V 运动参考**
H3 Ref2VA 官方规格：视频参考 <=3 段、每段 2-15s、总长 <=15s。官方写法：

    Video 1 defines the hand trajectory and movement timing only.
    Do not copy its actor, wardrobe, setting, lighting, or camera movement.
    Image 1 provides the identity lock.

-> **运动只能从视频参考来，文字写不出来。** 运动源可从 huggingface.co/datasets/ostris/minimax_h3_1k 找。

### 14.5 公开宝库（直接抄，别自己编）
| 资源 | 地址 |
|---|---|
| 官方 52 条原始提示词（16 类别，每条配真实预览视频） | github.com/AtlasCloudAI/awesome-minimax-h3-prompts |
| 官方 1000 条 H3 数据集（含视频，V2V 运动源） | huggingface.co/datasets/ostris/minimax_h3_1k |
| 1000 条导航 | github.com/yangzhou-chaofan/minimax-h3-1000-prompts |
| 提示词站（每条标 creator，可追 X 原帖） | minimaxh3.ai/video-prompts 、 awesomevideoprompts.com |

已抄回本机：`<ASSET_DIR>\抄_DarkFantasyMageDuel_原文.txt`（同目录 `_中文版.md` 是逐句对照）。


---

## 15. 🔴🔴 本机 H3 唯一可靠打法：两段式（先出成品构图，再做动态）

> 2026-10-03 上午 5 轮实测（召唤天使段）跑出来的定论。**比 §14 更根本，优先用这一条。**

### 15.1 核心原理
**H3 擅长复刻，不擅长创造。** 参考图里没有的东西，它基本创造不出来；
参考图的构图如果和提示词描述不一致，它会**忽略这张图**。

| H3 ref2va 能力 | 实测结论 |
|---|---|
| 能出 | 法阵、符文、光柱、火焰、烟雾等**自发光几何体**（复刻参考图里已有的） |
| 出不来 | 天使/恶魔/魔物等**具体生物**，除非参考图里已经有它 |

### 15.2 多参考图的真实行为（重要，纠正了我的错误猜测）
传两张 ref（主角 + 天使）时，**H3 不是「第一张优先」，而是「按提示词匹配度选图」**。
- 实测 A：ref1=主角 / ref2=天使 -> 画面主体是主角（主角图构图与提示词一致）
- 实测 B：ref1=天使 / ref2=主角 -> **画面主体还是主角**（顺序换了主体没换！）
- 工作流确认两张都接上了（ref_image_1 / ref_image_2 都有值），但第二张几乎无视觉影响
- -> **别再试图用多张参考图分工控制不同角色**，做不到。

### 15.3 正确流程（两段式）

**第 1 段 · 用生图模型出「成品构图图」**（Qwen-Image-2.1，本机 68-70 秒）
- 提示词里**把整个场景一次写全**：所有角色同框 + 场景 + 构图角度 + 光效
- 关键句式：A colossal angel ... hovers above him inside the golden light column（天使已在画面里）
- 产出即「这一段视频的第一帧」，同时锁死了角色身份与构图

**第 2 段 · H3 只做局部动态**（5s / 12 步 / 576×1024 / 约 7 分钟）
- --ref 只传**这一张成品构图图**（不要传第二张）
- 提示词极简，结构固定（照抄，尖括号内容按段替换）：

```
subject_definitions: <Picture 1> is the first frame of this shot and it controls the
  entire composition... must be reproduced exactly as in <Picture 1> in every frame.
summary: [reference generation] One continuous N-second shot continuing directly from
  <Picture 1>. <一个局部动态>.
detailed_description: [Shot 1] ... The shot begins exactly on the composition of
  <Picture 1>. At 00.000 the scene is as given. At 01.000 <局部动态1>. At 02.000 <局部动态2> ...
```

- 动态只写**非位移类**：翅膀扇动、羽毛飘落、光柱明暗变化、衣摆飘动、粒子、光环旋转
  （位移类在 §14 已证明会退化成复刻态）

### 15.4 成功判据（对照实测数据）
| 指标 | 失败版 | 成功版（两段式） |
|---|---|---|
| 画面亮度 avg | 33–42 | **117.1** |
| 主体是否完整 | 只有主角，天使缺席 | **主角+天使同框，服装全对** |
| 四帧差异 | 几乎完全一致 | 翅膀角度/光柱宽度/裙摆形态**有可见变化** |
| probe | PASS | PASS |

### 15.5 本机生图（Qwen-Image）命令与坑

    set PY=<PYTHON>
    set CC=<AGENT_SCRIPTS>\comfy_control.py
    set WF=F:\模型\文生图  image_qwen_image_2_1_t2i_gguf.json
    "%PY%" "%CC%" run "%WF%" --prompt "<完整场景提示词>" --negative "photorealistic, 3d render, text, watermark, HUD, UI" --seed N

- 跑 H3 前先 POST /free，body 为 {"unload_models":true,"free_memory":true}，卸载 Qwen-Image，
  否则 16GB 显存不够 H3 用（跑完 H3 再想生图时重新加载即可）。

---

## 16. 🔴 六宫格分镜板 → 顺序关键帧视频（多图参考的正确用法）

> 2026-10-03 实测。**修正了 §15.2 的结论**：多图参考不是没用，是**用法错了**——
> 不能用「多张图分工控制不同角色」，要用「**多张图 = 顺序关键帧**」。

### 16.1 两种成熟玩法（网上已验证）
| 玩法 | 出处 | 写法要点 |
|---|---|---|
| **A. 多图 = 顺序关键帧** | fal.ai 官方 44 例 | `Use Images 1-4 as sequential keyframes` + 逐张点名 `In Image 2, let the fabric move...` |
| **B. 一张多宫格图当首帧** | minimaxh3.ai《Nine-Panel Grid Interactive Animation》 | `【图片1】为首帧画面` + 九宫格内人物互动，`第1-3秒 / 第4-7秒 / 第8-12秒` |
| **C. 宫格分镜板** | minimaxh3.ai《Pharaoh Storyboard》 | `A 9-panel storyboard layout, 3 rows x 3 columns` + `Panel 01: ... Panel 02: ...` |

### 16.2 官方容量与用法红线
- 最多 **9 张图 / 2 段视频 / 1 段音频**，共 12 个文件；**视频与音频不占图片编号**。
- 编号 = 上传顺序（格子左上→右下 = 图1→图9）。
- **9 张是上限不是目标，4-6 张最可靠**（oxava 指南：图与图互相矛盾会出糊片）。
- 分配建议：1-3 张身份图 / 1-2 张细节图 / 1-2 张场景或风格图。
- **画面比例由源图决定**（ref 模式无法事后选比例）→ 想出竖版就先用竖版图。
- 官方镜头上限：5 秒片 1-2 镜、10 秒 2-3 镜、**15 秒 3-4 镜**，切太碎人物会跑掉。
- `detailed_description` 建议 350-500 英文字；提示词总上限 7000 字符。

### 16.3 🔴 本机实测结论：多图 ref 全部接上，但**只有第一张起作用**（2026-10-03 15 秒片验证）

工作流确认 5 张图都接进了节点：

    ref_images.ref_image_1..5 = 节点 20 / 21 / 22 / 23 / 24

**但成片只用了 ref_image_1 的构图**：15 秒里 5 个 AT ÃüÁîÒÑÆúÓá£Çë¸ÄÓÃ schtasks.exe¡£

ÎÞЧµÄÃüÁ

AT ÃüÁÅÅÔÚÌض¨ÈÕÆںÍʱ¼äÔËÐÐÃüÁîºͳÌÐ
ҪʹÓÃ AT ÃüÁ¼ƻ®·þÎñ±ØÐëÒÑÔÚÔËÐÐÖС£
                                                           
AT [\computername] [ [id] [/DELETE] | /DELETE [/YES]]                    
AT [\computername] time [/INTERACTIVE]
    [ /EVERY:date[,...] | /NEXT:date[,...]] "command"

\computername       ָ¶¨Զ³̼ÆËã»ú¡£Èç¹ûʡÂÔÕâ¸ö²ÎÊý£¬
                     »á¼ƻ®Ôڱ¾µؼÆËã»úÉÏÔËÐÐÃüÁ
id                   ָ¶¨¸øÒѼƻ®ÃüÁîµÄʶ±ðºš£
/delete              ɾ³ýĳ¸öÒѼƻ®µÄÃüÁÈç¹ûʡÂÔ id£¬
                     ¼ÆËã»úÉÏËùÓÐÒѼƻ®µÄÃüÁ»ᱻɾ³ý¡£
/yes                 ²»ÐèҪ½øһ²½ȷÈÏʱ£¬¸úɾ³ýËùÓÐ×÷ҵ
                     µÄÃüÁîһÆðʹÓá£
time                 ָ¶¨ÔËÐÐÃüÁîµÄʱ¼䡣
/interactive         ÔÊÐí×÷ҵÔÚÔËÐÐʱ£¬Ó뵱ʱµÇ¼µÄÓû§
                     ×ÀÃæ½øÐн»»¥¡£
/every:date[,...]    ָ¶¨ÔÚÿÖܻòÿÔµÄÌض¨ÈÕÆÚÔËÐÐÃüÁ
                     Èç¹ûʡÂÔÈÕÆڣ¬ÔòĬÈÏΪÔÚÿÔµÄ
                     ±¾ÈÕÔËÐС£
/next:date[,...]     ָ¶¨ÔÚÏÂһ¸öָ¶¨ÈÕÆÚ(È磬ÏÂÖÜËÄ)ÔË
                     ÐÐÃüÁÈç¹ûʡÂÔÈÕÆڣ¬ÔòĬÈÏΪÔÚÿ
                     Ôµı¾ÈÕÔËÐС£
"command"            ׼±¸ÔËÐеÄ Windows NT ÃüÁî»òÅú´¦Àí
                     ³ÌÐ 切镜**一个都没执行**，
五帧抽检几乎完全相同（城镇远景 + 走向公会门的少女，只有轻微推进）。
亮度 avg 77.9，画面精美，probe PASS——但**这是一条单镜头片，不是五镜序列**。

**结论（推翻 fal.ai 官网示例在本机的可复现性）**
| 项 | 结论 |
|---|---|
| 多图 ref 接线 | ✅ 正常（ref_image_1..5 都有值） |
| 多图 = 顺序关键帧 | ❌ **本机不执行**——后 4 张被忽略，连硬切都不发生 |
| 原因判断 | 「Images 1-4 as sequential keyframes」是**云端 H3（fal / 海螺平台）**的能力；本机 ComfyUI 的 ref2va 节点走的是「多主体参考」语义，不含时序关键帧 |

**本机实现「六宫格 → 视频」的唯一可行路线：分段 + 拼接**
1. 六宫格切单格（同 §16.4 步骤 1-2）。
2. 选 3 格（对应 5 秒 × 3 段 = 15 秒），每段用**该格作为唯一 ref** 跑 5 秒。
3. 每段提示词写「从 <Picture 1> 出发做局部动态」（即 §15.3 两段式的第 2 段写法）。
4.  零重编码拼接。

### 16.3.1 附：工作流确认 5 张 ref 都接上了（接线本身没问题）
工作流实测（`last_h3_workflow.json`）：

    "ref_images.ref_image_1": ["20", 0]
    "ref_images.ref_image_2": ["21", 0]
    "ref_images.ref_image_3": ["22", 0]
    "ref_images.ref_image_4": ["23", 0]
    "ref_images.ref_image_5": ["24", 0]

→ §15.2 里「第二张几乎无影响」的现象，根因是**当时两张图承担的是不同角色**（互相竞争），
改成**不同镜头**后多图就能各司其职。**所以多图要先想清楚每张图的「任务」。**

### 16.3.2 🔴🔴 2026-10-04 修正：多图 ref **能做「多主体参考」**，只是不能做「时序关键帧」

**实测（5s / 124帧 / 8步 / 195 秒出片）**：r2v 传 **2 张图**（角色设定图 + 场景照片）→ **完全生效**。
- 角色外观来自 **Image 1**（蓝发 / 鲸耳鳍 / 女仆裙 / 白围裙小蓝鲸 / 鲸尾）
- 场景来自 **Image 2**（真实高铁车厢 + 窗外飞驰田野）
- 结果：角色被自然地放进真实场景里（**坐在高铁窗沿上看窗外、转头挥手**），
  动漫角色 + 照片级背景**同框共存**，这才是"虚实结合"最省事的做法。

**结论修正**：§16.3 的「只有第一张起作用」**只对"多张图当顺序关键帧"成立**（那确实不支持）。
官方 Ref2VA 指南写明：**最多 9 张图，每张图给一个明确职责**：
```
Image 1 defines the character: <外貌清单>. Keep her appearance consistent with Image 1.
Image 2 defines the location: <场景清单>. Keep the location exactly as in Image 2.
[Shot 1] <角色> in <场景> does <动作>...
```
社区经验：**提示词顺序 = 先人物动作 → 再服装环境 → 最后镜头**；
把环境写在前面，模型会为了环境效果忽略人物长相参考图。

🔴 **参数坑（必踩）**：走 `/api/h3d/run` 时 **r2v 的提示词必须写在 `global_prompt`**。
写进 `segments[].prompt` 会被忽略 → Director 报
`Director Group (Reference to Video): provide a prompt and/or at least one reference image`
并返回 **HTTP 500**。源码依据 `h3_director.py:491-495`（r2v 组只读 `global_prompt`）。
参考图仍走 `global_refs`（会被自动 upload）。

**路线选择**：
| 目标 | 用哪条 |
|---|---|
| 要「角色在真实场景」且**能接受角色被轻微重绘** | ✅ **r2v 一步到位**（一条命令，5s 片 3 分钟） |
| 角色必须**100% 保真**（像素级不重绘） | 分层合成（见 skill `anime-real-composite`）：绿幕动作 + 逐帧抠像 |

### 16.4 落地流程（本机）
1. **出分镜板**：Qwen-Image 出 2 行 x 3 列六宫格，提示词里逐格写 `Panel 1: ... Panel 6: ...`，
   并强调 `the same character appears in every panel with a consistent face and costume`。
2. **切格**：Python + PIL 按 2x3 网格切（留 1.2% gutter 裁切），编号即上传顺序。
3. **写提示词**（六段式，结构固定）：
   - `subject_definitions`：先用 `<Subject 1>` 锁定角色（贯穿全片），再逐张写
     `<Picture N> is the ... framing: ... <Picture N> controls the framing of [Shot N] only.`
   - `retention_analysis`：每张图一条 `fully_preserved`。
   - `detailed_description`：`[Shot 1]` 不带时间戳；后续镜头用 `At MM:SS.mmm,` 递增；
     每镜写 `exactly the framing of <Picture N>`。
4. **提交**：`--ref` 依次传 5 张（顺序=编号），`--duration 15 --steps 12 --w 576 --h 1024`。
5. **验收**：抽 6 帧（每镜 1 帧）拼对比图，看 5 个构图是否都出现。

### 16.5 现成素材
- 分镜板：`<ASSET_DIR>\六宫格分镜板.png`（2x3，无职转生风格六镜）
- 切好的单格：`<ASSET_DIR>\分镜格\01..06_*.png`
- 分段提示词：`<ASSET_DIR>\宫格段2_起阵_5s.txt`、`宫格段3_爆发_5s.txt`
- 成片：`<ASSET_DIR>\无职转生_六宫格_15秒成片.mp4`
- 切格脚本：先用 PIL 按比例算 `(W - gut*4)//3` x `(H - gut*3)//2`，逐格裁切保存即可。

### 16.6 拼接与验收的两个工具坑（2026-10-03 实测，浪费了 4 次尝试）

**坑 1 · concat 列表文件的路径必须全用正斜杠**
用 Python 拼路径时若混用反斜杠，ffmpeg 的 concat demuxer 会把反斜杠当**转义符**吃掉，
文件读不到且**不报错**，表现是「拼出来 15 秒但内容全是第一段重复三遍」。
修法：用 **Write 工具**写列表文件，整行纯正斜杠，例如：

    file '<ASSET_DIR>/seg1.mp4'
    file '<ASSET_DIR>/seg2.mp4'
    file '<ASSET_DIR>/seg3.mp4'

列表文件编码用 **utf-8**（路径含中文时 ascii 会直接抛 UnicodeEncodeError）。

**坑 2 · 抽多帧不能用 select + -frames:v N**
本机 ffmpeg 9.0.2 下，`select='eq(n,60)+eq(n,185)+eq(n,310)' -frames:v 3`
只会输出**第一张匹配帧**并重复三次 → 误判成「拼接失败 / 三段内容相同」。
修法：**逐帧单独抽**（一条命令一个帧号），再拼图。
验收正确姿势：先抽一个「疑似异常点」的单帧（如 n=200）确认，再抽三段各一帧拼图。

### 16.7 成功案例数据
| 项 | 值 |
|---|---|
| 分镜板 | 2 行 x 3 列，Qwen-Image 出图 70s |
| 切格 | 2x3 网格，留 1.2% gutter（1024px 图 → 每格约 325x494） |
| 段落 | 3 段 x 5s（576x1024 / 12 步 / 各约 6.5 分钟） |
| 拼接 | concat -c copy，零重编码，370 帧 / 15.413s / probe PASS |
| 三段内容 | 城镇远景 → 举杖起阵 → 金色光柱爆发，角色全程一致 |

素材：<ASSET_DIR>\六宫格分镜板.png、分镜格\01..06_*.png、
提示词 宫格段2_起阵_5s.txt 与 宫格段3_爆发_5s.txt、成片 无职转生_六宫格_15秒成片.mp4
- Qwen-Image 的**动漫风格不弱**（赛璐璐平涂、轻小说饱和度都对），日式异世界题材可直接用。
- 负面词对动漫场景有效：photorealistic / 3d render / text / watermark / HUD / UI / extra people。
- 现成素材：<ASSET_DIR>\异世界_召唤天使_同框构图.png（主角+天使同框，可作负面对照基准）。



### 15.6 两段式的两个残留问题（2026-10-03 魔法师施法段实测）
| 问题 | 现象 | 修法 |
|---|---|---|
| **地面法阵被简化** | 构图图里是清晰的三重符文法阵，成片只剩发光裂纹、符文环消失 | 构图图里把法阵做得更大更亮、符文更粗；或把法阵放到**人物身后/头顶**（人物身后的元素保留率更高） |
| **动态仍接近静帧** | 四帧（0.3/2.3/4.2/5.0s）几乎一致，只有火焰边缘轻微变化 | 本机天花板，见 §14.4。想加大动态只能：① 提高 steps（12→20）② 换 seed 多试 ③ 走 V2V 运动参考 |

**结论**：两段式能保「画面精美度 + 主体完整」，但**保不住细密图案与运动幅度**。
适合做「一张华丽海报动起来」，不适合做「动作片」。

---

## 17. 🔴🔴🔴 最高优先：改用 MiniMaxH3Director 导演台（2026-10-03 已装已验证）

> **本节优先于 §14 与 §15。** §14/§15 是在「本机后端只有最窄一条路径」前提下的绕路方案；
> 装了 Director 后，§14.4 判定的「本机天花板 = 静帧动画」**已被推翻**。
> 全文归档：`桌面\重要AI配置文档\06_视频与图像生成\11_MiniMaxH3Director导演台_解决静帧动画的正解_20261003.md`

### 17.1 之前 11 段全部"静帧"的机械原因（不是提示词也不是模型）

本机 `comfy_studio.py` 的 `h3_build_workflow()` 只接**一条**路径：
`--ref` 传了就走 `MiniMaxH3ReferenceToVideo`（参考图当身份锁），没传就走
`MiniMaxH3ImageToVideo` 但**只传 clip/vae/prompt/width/height/length，
`first_frame` 与 `last_frame` 两个可选输入留空 = 退化成纯 T2VA**。


官方工作流 `1-Aiden-minimax文-图-首尾帧生视频` 里这两个位是 `link=64` / `link=70` **都接上的**。

| 真正能让画面动起来的三个能力 | 本机此前 |
|---|---|
| `ImageToVideo.first_frame` + `.last_frame`（FL2VA 插值） | 留空 |
| `ReferenceToVideo.ref_videos.ref_video_N`（V2V 运动参考，≤3 段 2–15s） | 只接 `ref_images` |
| `MiniMaxH3AddGuide(frame_idx=N, image=BATCH)`（多帧时序锚定） | 完全没接 |

结论：**"静帧动画"是我后端的接线缺陷，不是模型能力上限。** 别再往提示词上找原因。

### 17.2 安装位置与验证（本机已装）

- 路径：`<COMFYUI_ROOT>\ComfyUI\custom_nodes\ComfyUI_MiniMaxH3_Director`
- 依赖：`pip install -r requirements.txt`（ultralytics / scenedetect / opencv-python-headless / imageio-ffmpeg 等 19 包）
- 重启：`taskkill /PID <pid> /F /T` 后重拉（`/api/shutdown` 返 **405**，不可用）
- 验证：`GET /api/object_info` 应有 **11 个 Director 节点**（装完总节点 977）

节点清单：`MiniMaxH3Director` / `ComfyMiniMaxH3Director` / `MiniMaxH3DirectorConditioning` /
`MiniMaxH3DirectorPlannerConditioning` / `MiniMaxH3DirectorGroupImageToVideo` /
`MiniMaxH3DirectorGroupReferenceToVideo` / `MiniMaxH3DirectorGroupsCombine` /
`MiniMaxH3DirectorRefine` / `MiniMaxH3DirectorSelfLift` / `MiniMaxH3DirectorSemanticBridge` /
`MiniMaxH3DirectorFaceRefine`

### 17.3 七种 task_type 与 UNET 型号对应（选错就废）

| task_type | UNET |
|---|---|
| `t2v — 文生视频(Text to Video)` | **fl2va** |
| `i2v — 图生视频(Image to Video)` | **fl2va** |
| `fl2v — 首尾帧生视频(First-Last Frame)` | **fl2va** |
| `r2v — 参考主体生视频(Reference to Video)` | **ref2va** |
| `v2v — 视频转视频(Video to Video)` | **ref2va** |
| `rv2v — 参考素材改视频(Reference Video Edit)` | **ref2va** |
| `mixed — 混合模式(Mixed Segments)` | 按段 |

`task_type` 传参必须是**下拉框里的完整中英混排字符串**（含全角括号空格），
如 `r2v — 参考主体生视频(Reference to Video)`，**不能简写 `r2v`**。

本机只有 `Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors`
→ **只能用 r2v / v2v / rv2v**；t2v / i2v / fl2v 需补 `minimax_h3_fl2va_pruned_int8_convrot.safetensors`。

### 17.4 四个关键机制（解决我此前所有绕路）

**① 段间引导（Motion Context）— 治接缝生硬**
`timeline_data.output.continuityEnabled = true` + `continuityOverlapFrames = 22`（可选 5/22/39/56）。
把上一段生成结果的**末尾 22 帧运动 + 音频**钉进下一段采样再裁掉前缀。
对比：§15 的"抽末帧当 ref"给的是一张死图，这个给的是 22 帧真实运动。

**② fl2v「添加一组」= 官方六宫格**
每组可只写提示词（文生）或上传首帧/尾帧，**空组自动用上一段末尾 N 帧衔接**。
→ 这才是"六宫格转视频"的正解。§16 用 `ref_images` 传 5 张图**是错的**——那不是时序通道。

**③ r2v 素材组 + 公共参数**
`global.refs` + `global.prompt`（可写 `subject_definitions` 角色锁定）→ 所有段共享；
每段 `refs` 可挂自己独有的图1-9/视1-3/音1-3；提示词用 `<Picture N>` / `<Video K>` / `<Audio J>` 或 `@`。
**同槽位覆盖公共素材。**

**④ 导演包 `*.mmxpack.zip`**
时间轴 JSON + 素材一起打包/导入导出，ASCII 路径 → "分镜板 + 提示词"可复用。

**画质三件套**：`Refine` 二采/放大（`images` 终稿 + `images_pre_refine` 一采两路）、
`SelfLift` 渐进一采（低清前缀→3D lift→高清收尾）、
`Semantic Bridge`（原版偏构图/空间/计数，**BUNNY 偏动作归属/复杂多人**）。
`FaceRefine` 做人脸 track+crop+stitch（需 `models/ultralytics/bbox/face_yolov8m.pt`）。

### 17.5 本机 API 通道（绕开 GUI，已写好）

`<AGENT_SCRIPTS>\director_submit.py`

```bat
set PY=<PYTHON>
rem 单段快速验证（5s / 25 步 ≈ 8 分钟）
"%PY%" <AGENT_SCRIPTS>\director_submit.py --seg 1
rem 三段 + 段间引导 22 帧（≈ 25-30 分钟）
"%PY%" <AGENT_SCRIPTS>\director_submit.py --steps 25 --overlap 22
```

| 参数 | 作用 |
|---|---|
| `--seg N` | 只跑指定段（0 起） |
| `--steps N` | 默认 25 |
| `--overlap N` | 段间引导上下文帧数，默认 22 |
| `--no-continuity` | 关段间引导（做对照实验） |
| `--seed N` | 固定种子 |

产物落 `ComfyUI/output/ComfyStudio_H3Director_*.mp4`（**注意不在** `F:\ComfyStudio\output`）。

### 17.6 API 通道三个坑（各浪费一次尝试）

| 坑 | 症状 | 修法 |
|---|---|---|
| 上传端点 | 用 JSON `{name, data:base64}` 提交 → **HTTP 405** | ComfyUI 原生只收 **multipart**，端点 `/api/upload/image`。（8777 的 `/api/upload` 才是 JSON 封装） |
| 上传成功判定 | 明明成功却报失败 | 新版成功返回**只有** `{name, subfolder, type}`，**没有 `ok` 字段**；判据用 `d.get("name")` |
| Python 默认值 | `def f(segs, total=124*len(segs))` → NameError | 默认设 `None`，函数体内算 |

### 17.7 官方默认采样参数（与我的一贯设置不同，按官方走）

| 项 | 官方 | 我之前 |
|---|---|---|
| 画布 | 0.4MP 16:9 **864×480** | 576×1024 |
| 时长/帧 | 5s / **124 帧** @24fps | 同 |
| **steps** | **25** | 12 |
| **sampler** | **res_multistep** | euler |
| scheduler | simple | simple |
| CFG / shift | 1.0 / 12+3 | 同 |

`length` step = **17**（17k+5 网格），tooltip 明确 **124 帧≈5s，训练范围 124–362**。
→ **10s=244 帧是安全中间值**；15s=362 在边界（我那条崩过）。

### 17.8 实测结果（2026-10-03 15:39，单段 5s / 25 步 / res_multistep / 864×480）

- 耗时 **8 分 11 秒**，probe PASS，avg 亮度 **71.9**
- 四帧抽检（0.6/2.3/4.0/5.0s）**四帧完全不同**：
  镜头仰角**升起环绕**、地面三重符文法阵**在旋转**、角色有位移、裙摆随能量上扬
- **本机 H3 第一次产出真正的运动画面**（对照此前 11 段"四帧几乎完全一致"）

### 17.9 官方提示词规范（`桌面\H3工作流套件\` 七份，此前完全没用上）

| 文件 | 内容 |
|---|---|
| `VIDEO_PROMPT_WRITING_GUIDE_base_en(1).md` | T2VA / **I2VA / FL2VA / L2VA** + 运镜三要素 + 说话人 ID + 屏幕文字 |
| `VIDEO_PROMPT_WRITING_GUIDE_ref_en(1).md` | `<Subject N>` / `<Picture N>` / `<Video N>` / `<Audio N>` + `retention_analysis` 四标记 |
| `MiniMax-H3-全能视频提示词母模板.md` | 母模板 |
| `H3 视频创作助手(1).md` | 官方 Agent 人设：能力边界 + 场景适配 + 输出规范 |
| `1-Aiden-minimax文-图-首尾帧生视频，自动切换_已适配V1.2_去LLM.json` | **官方首尾帧工作流（帧位都接上）** |
| `MiniMax H3全能参考工作流.json` | 全能参考（含 `ref_videos`/`ref_audios`） |
| `1-Aiden-minimax-多参考图.json` | 多参考图 |

**四种模式的对齐句是硬性格式（此前我一条都没写）**：
```text
I2VA   For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
FL2VA  How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.
L2VA   How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

**FL2VA 正文写法**：不复述两张图静态描述，**只写怎么从第一帧走到最后一帧**；
结构 `首帧状态 → 可观察的中间变化 → 差异逐步收窄 → 尾帧状态`；**优先单镜**；
ref 模式 `detailed_description` 350–500 英文词。

**运镜三要素**（缺一不完整）：类型（`Push In`/`Arc Shot`/`Tracking Shot`/`Pedestal Up` 等）
+ 幅度（`with small|large amplitude`）+ 速度（`at slow|fast speed`），**融进句子**：
`The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.`

**官方给的 H3 优势场景**：生动情绪表现（写清情绪转换序列）/ 真实人体动态（直接写具体动作）/
电影级爆破特效（冲击波+火光+碎片+浓烟+低角度+震动）/ 概念组合（泛化强）。
**单段镜头运动时长控制在 5–6 秒内**。

### 17.10 修正对本模板前文的结论

| 前文结论 | 修正 |
|---|---|
| §14.4「本机天花板 = 静帧动画，唯一解法是 V2V（还没试）」 | **已推翻**。真因是后端没接 `first_frame`/`last_frame`/`ref_videos`；装 Director 后单段即得真实运动画面 |
| §16.3「多图 ref 只有第一张起作用，顺序关键帧本机不执行」 | 结论对但原因错。本机 ref2va 确实无时序关键帧；正解是 Director 的 `timeline_data.segments` + 段间引导，**不是** `ref_images` 塞多张 |
| §15「两段式：生图出构图 → H3 做局部动态」 | 仍有效但**已被 Director 覆盖**（Director 直接吃多组首尾帧，省掉手工切片与 ffmpeg 拼接） |
| §1「一镜一个动作」 | 依然成立（§14.3 已说明 Ref2VA 用事件链） |

**今后默认打法**：多段/长片 → Director `timeline_data` + 段间引导；
单段快速出图 → `h3_video_agent.py`（它只接 reference 一条路，作为轻量通道保留）。


## 19. 🔴🔴 LoRA 栈 + 配方表（2026-10-03 18:10-18:30 上线，本机 6 个 LoRA 就位）

### 为什么装
用户要求「装画风 LoRA + 加速 LoRA，以后我自己决定用哪几个」。
→ 维护成**配方表**（场景 -> LoRA 组合+权重），不是每次现猜。

### 本机已装 LoRA（`models/loras/`，ComfyUI 全部识别）
| 文件 | 大小 | 类别 | 来源 |
|---|---|---|---|
| `studio1939-strong.safetensors` | 250MB | 画风：全赛璐璐，触发词 `gulliv3r,` | ModelScope `lovis93/studio-1939-old-animation-lora-minimax-h3` |
| `minimax_h3_ref2v_turbo_8step_v1.0_768p_bf16.safetensors` | 1.32GB | **加速：ref2v 8 步（默认）** | ModelScope `lightx2v/Minimax-h3-Turbo` |
| `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 1.86GB | 加速：ref2v 4 步（脸糊，备用） | 同上 |
| `MiniMax-H3-Ref2VA-Acc-8Step.safetensors` | 1.31GB | 加速：PDD 官方（⚠️ 未接，见下） | ModelScope `PAI/MiniMax-H3-Acc-LoRAs` |
| `h3-realism-people-t2v-i2v-r2v.safetensors` | 125MB | 写实人物（**做动画绝不能挂**） | 原有 |
| `H3_MysticXXX_MMH3-V2.safetensors` | 164MB | 解除审查 | 原有 |

### 🔴 本机只有 ref2va UNET，所以只能用 ref2v 系 LoRA
`Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors` 是唯一 H3 权重。
→ `lightx2v` 的 **fl2v** 系（`minimax_h3_fl2v_turbo_*`）本机用不了。
下载时必须看清文件名里有 **ref2v**。

### 配方表（`h3_director.py` 的 `LORA_RECIPES`）
```python
"doraemon_fight"      : studio1939 0.7 + turbo_8step 1.0     # 默认，5秒 104秒出片
"doraemon_fight_fast" : studio1939 0.85 + turbo_4step 1.0    # 极端赶时间，脸会糊
"anime_cel"           : studio1939 0.8 + turbo_8step
"isekai_thin_paint"   : studio1939 0.6 + turbo_8step
"turbo_only"          : turbo_8step
"realistic"           : h3-realism-people 0.8               # 唯一允许 realism 的场景
```

### 接线（`h3_director.py` 的 `build_workflow`）
```
UNETLoader(1) -> LoraLoaderModelOnly(20) -> LoraLoaderModelOnly(21) -> MiniMaxH3Director.model
```
- 挂 turbo 时**自动强制** `cfg=1.0` + `sampler="euler"`（蒸馏是 guidance-free，抬 CFG 会打架）
- 节点号从 20 起递增，不与既有 1-5/10-12 冲突
- `TURBO_STEPS` 记录每个 turbo 的训练步数（4/8），超了无收益、8 步以上反而过锐

### 加速实测（本机 5060Ti 16GB，124帧/5秒）
| 档 | 步数 | 耗时 | 画面 |
|---|---|---|---|
| 原版 25 步 | 25 | 8 分钟 | 基准 |
| turbo_4step | 4 | **88 秒** | ❌ 脸糊成褐色团块，五官不清 |
| turbo_8step | 8 | **104 秒** | ✅ 眼睛/嘴/眼镜清楚，描边干净 |
→ **提速 4.6×，8 步档是甜点**（官方作者实测 6-8 步最好，4 步是广告下限）。

### 🔴 PDD 官方 Acc LoRA 装了但**暂不可用**
`MiniMax-H3-Ref2VA-Acc-8Step.safetensors` 带 32 份 head bank，
**普通 LoraLoader 会静默丢弃** -> 加速完全无效。
必须配节点包 `ComfyUI-MiniMax-H3-PDD-Acc`（`MiniMaxH3PDDAccApply` 节点）。
本机未装该节点包，所以走 lightx2v 的 turbo（标准格式，可直接用）。

---

## 19.5 🔴🔴 画风提示词：分层写背景与角色（2026-10-03 血泪教训）

### 事故：出成真人（10 秒版，17:53）
我写的 `global_prompt` 里有：
```
Japanese hand-drawn cel-animation fight scene, gritty shonen battle anime,
dramatic high-contrast lighting, warm afternoon sunlight through dust, film grain
```
结果出的是**照片级写实**（皮肤纹理、景深、真实光影）。

**根因**：`gritty shonen battle anime` + `hard shadow terminators` + `film grain`
这三个词在 H3 训练数据里对应**成人向写实番剧**，不是 TV 动画截图。
参考图是平涂+粗描边（平的），文字却要"硬阴影质感"（立体的）——**信号互相打架，模型服从了文字**。

### ✅ 正确写法：背景与角色**分层描述**
```text
BACKGROUND: hand-painted watercolor background art, soft air perspective,
layered atmospheric depth, painted foliage and stone textures,
diffuse even daylight, delicate paper grain
CHARACTERS: 2D cel-shaded characters, refined clean line art,
flat opaque color base with soft painted shading, simple round anime eyes
with small dot pupils, thick uniform black outlines
ABSOLUTELY NOT photorealistic, NOT live-action, NOT 3D render, NOT CGI,
NOT real skin texture, NOT depth of field bokeh, NOT film grain
```

### 必须删的词（会把画面拽向写实）
`gritty` · `shonen`（不带 anime）· `dramatic high-contrast lighting` ·
`hard shadow terminators` · `film grain` · `rim light` · `volumetric` ·
`cinematic realism` · `photoreal`

### 三代画风分水岭（判断用）
| 世代 | 代表作 | 特征 |
|---|---|---|
| 老赛璐璐（00年代） | 无职转生 | 纯平色块 + 粗黑描边 + 高饱和 |
| 伪厚涂（10年代） | 盾之勇者 | 平涂角色 + 开始加厚涂光影 |
| **当代主流（20年代）** | **葬送的芙莉莲** | **背景手绘厚涂水彩 + 角色精致平涂（2.5D）** |

📌 **背景是关键分水岭**。不写"背景厚涂"，模型默认给纯平色块或写实背景。

## 19.6 🔴🔴🔴 画风定位：当代主流 ≠ 厚涂水彩（我连错三次的教训）

### 四次尝试的完整记录
| 时间 | 我写的画风线索 | 实际结果 |
|---|---|---|
| 17:53 (10s) | `gritty shonen battle anime` + `hard shadow terminators` + `film grain` | 照片级写实 |
| 18:21 (5s) | LoRA `studio1939-strong` 0.7 | 1939 古早水粉 |
| 19:06 (2s) | `hand-painted watercolor background` + `vivid palette` | 2000 年代初 TV 动画 |
| **19:15 (2s)** | **`muted low-saturation palette` + `soft multi-step gradients` + 三个动作 LoRA** | ✅ **芙莉莲级，成了** |


### 根因不是措辞，是我**对"现代主流画风"的理解本身有偏差**
我一直以为「现代 = 厚涂水彩」——那是 **2000 年代末～2010 年代初**（京阿尼/轻音系）。
**2020s 主流恰恰相反**（查证芙莉莲官方制作资料）：

| 特征 | 芙莉莲真实做法 | 我之前写错的 |
|---|---|---|
| 配色 | **低饱和、淡雅、彩度偏低** | `vivid palette` ❌ |
| 光影 | **柔和**，多阶渐变 | `hard shadow` / `dramatic contrast` ❌ |
| 魔法特效 | **柔和色彩 + 流动线条**，刻意避开夸张刺眼光效 | — |
| 背景 | **纯 2D 手绘 + 干净平滑渐变**，无 3D 渲染感 | `thick painterly brushwork` ❌ |
| 线条 | 优美流畅，每根发丝动态清晰 | — |

**关键认知**：厚涂水彩是**上一代**的当代表达。数字作画时代的"现代感"来自
**精致赛璐璐 + 柔和渐变 + 低饱和 + 干净背景**，不是来自笔触。

### ✅ 芙莉莲画风可用模板（19:15 实测通过）
```text
Contemporary Japanese TV anime, Madhouse-style modern cel animation
as in Frieren Beyond Journey's End.
CHARACTER RENDERING: refined elegant cel animation, clean beautiful linework,
soft cel shading with delicate multi-step gradients, subtle rim light,
every strand of hair crisply drawn and clearly readable,
natural relaxed facial features, gentle expressive eyes with a soft light reflection.
COLOR: muted low-saturation palette, pale soft colours, gentle contrast,
an airy calm atmosphere, warm diffused daylight.
BACKGROUND: pure 2D hand-drawn background art with clean smooth gradients,
soft depth from layered painted planes, no 3D rendering look,
delicate and precise rather than thick painterly brushwork.
EFFECTS: soft flowing light with graceful lines, never harsh glaring bloom.
```
必加否定词：`NOT thick painterly watercolour` / `NOT oversaturated high-contrast colours`
/ `NOT 3D render` / `NOT photorealistic` / `NOT film grain`

### 🔴 LoRA 选型教训
- `studio1939-strong` = 1939 黄金时代手绘水粉 → **不是现代风**，已从默认配方撤出
- `minimax_h3_looping_sketch_anime` = 手绘**草图**风（名字里就有 sketch / rough textured outlines）
  → **也不是现代主流**。19:15 成功版本**没有挂任何画风 LoRA**，画风纯靠提示词。
- → **H3 生态里没有"现代主流画风"LoRA**，别指望 LoRA，用提示词。
- ✅ 动作类 LoRA（wushu / spatial / camera）不干预画风，可放心叠加。

### ✅ 19:15 成功版配方（角色也对了）
```
frames=39 (2秒) / steps=25 / 544x320 / 25步不挂turbo
lora = [camera_motion 0.7, wushu_spatial_physics 0.35, wushu_action 0.6]
prompt = 芙莉莲模板 + <Subject 1>=Nobita / <Subject 2>=Gian 外形逐项写死
```
**关键**：LoRA 全部只管动作不碰画风 → 提示词的画风控制**不被稀释**。
这解释了为什么之前挂 `looping_sketch_anime` 时"cartoon boy"被拉成成年女性：
**画风 LoRA 的风格权重压过了身份词**。

### 角色识别的真正解法（不靠 ref2va）
ref2va 锁不住身份（四次全失败），但**纯文字描述能出对**：
- 每个角色写全：体型差异（SHORTER/TALLER/WIDER）+ 发型 + 眼镜 + 上衣颜色 + 裤子 + 袜鞋
- 明确否定错误类别：`schoolboys, NOT adults, NOT women, NOT real people`
- 两人并排时**再强调一次差异**（"Nobita is small and thin on the left, Gian is fat and tall on the right"）

## 20. ✅✅ 成功配方：六段式 + 干净参考图（2026-10-03 20:05 首次全对）

### 成果
`<ASSET_DIR>\★六段式_2秒_角色完全正确.mp4`
- 1.623s / 39 帧 / **864×480** / 25 步 / 280 秒出片 / avg_lum 121.1
- **两个角色特征全部复刻正确**（大雄圆眼镜黄毛衣蓝短裤白袜浅蓝鞋；
  胖虎锯齿发橙上衣+浅黄横条纹深棕裤蓝白鞋，体型明显更大）
- 三帧可见：云在飘、树叶摇动、人物姿态稳定
- 画风 = 70-80 年代日式儿童 TV 动画（平涂 + 粗描边 + 明亮主色）

### 🔴 为什么这一版成了（前 6 版全败的两个改动）
| 改动 | 之前 | 之后 |
|---|---|---|
| **参考图** | 整张三视图（正面+侧面+背面挤一张） | **切成单张正面立绘**（`角色素材\大雄_正面立绘.png` 712×2272 / `胖虎_正面立绘.png` 1024×1713） |
| **提示词** | 自然语言描述角色 | **官方六段式**，`[reference generation]` + `fully_preserved` |

### 切图方法（可复用）
```python
# 1) 逐列统计与背景色的差异，找出空白带 -> 三段边界
# 2) 取第 1 段（正面）
# 3) 抠白底：与 bg 差异 < 34 的像素设 alpha=0
# 4) alpha getbbox() 紧凑裁边 + 8px padding
# 5) 短边不足 1024 则 LANCZOS 放大（最多 2.2x）
# 6) 存两份：白底 RGB（H3 更稳）+ 透明 RGBA
```
实测大雄三段 x 范围 `44..459 / 459..868 / 868..1281`；
胖虎 `9..542 / 542..857 / 857..1362`。**第 1 段都是正面。**

### ✅ 六段式实例（可直接改用，254 词）
```
subject_definitions:
<Subject 1> is the small boy in <Picture 1>, a 9-year-old cartoon character with a
perfectly round head, short neat black bowl-cut hair with one small cowlick, very large
round white glasses with a thin black rim and completely transparent lenses, a tiny round
nose, small dot eyes, a mustard yellow long-sleeve sweater over a white pointed-collar
shirt, dark navy blue shorts, white ankle socks and light blue slip-on shoes.
<Subject 2> is the large boy in <Picture 2>, a 9-year-old cartoon character with a heavy
round build, short spiky black hair with a jagged fringe, thick black eyebrows slanting
inward, a small round nose, small dot eyes, a bright orange long-sleeve shirt with one wide
pale-yellow horizontal stripe running across the chest, dark brown trousers, and
blue-and-white shoes.

summary:
[reference generation] <Subject 1> and <Subject 2> stand side by side on an empty sunlit
grassy field, facing the camera, holding still and looking forward. Both characters appear
together in a single continuous shot, keeping the exact faces, hair, glasses, clothing and
body proportions defined in their reference pictures.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - his round head, black bowl-cut hair,
large round white glasses, mustard yellow sweater, white collar, navy shorts, white socks
and light blue shoes stay exactly as shown in <Picture 1>, with no change of garment,
colour or proportion.
<Subject 2> (appears in [Shot 1]): fully_preserved - his heavy round build, spiky black hair,
thick inward-slanting eyebrows, orange shirt with the wide pale-yellow chest stripe, dark
brown trousers and blue-and-white shoes stay exactly as shown in <Picture 2>, with no change
of garment, colour or proportion.

detailed_description:
The target video is in a classic 1970s-80s Japanese children's TV anime style, in clean 2D
hand-drawn cel animation: bold even black outlines around every shape, flat opaque colour
fills with only one soft shadow tone, very simple round cartoon faces with small dot eyes,
bright and cheerful primary colours, and a calm sunny daytime atmosphere.
[Shot 1] A static full shot shows a wide open grassy field under a clear blue sky, with a
single large leafy green tree in the background on the right and soft flat green grass
covering the ground. <Subject 1> stands on the left side of the frame, noticeably shorter and
thinner than the other boy, feet planted close together, both arms hanging loosely at his
sides, hands open, his head turned slightly toward the camera so that the round white lenses
of his glasses catch a single small white glint. <Subject 2> stands on the right side of the
frame, clearly taller and much wider, with his heavy shoulders squared, both thick arms
hanging down, a broad stern look on his round face directed straight ahead. The two boys are
separated by a clear gap and do not touch. A few small white clouds drift slowly across the
blue sky, the leaves of the big tree sway gently from side to side, and small blades of
grass in the foreground shift slightly in a light breeze. Neither boy moves from his
position. The camera holds a completely static shot with no movement for the whole clip.

overall_soundscape:
A quiet open-air ambience with soft wind moving through grass and leaves, faint distant
birdsong, and the light rustle of the tree canopy above.

non_diegetic_music:
None.
```

### 本版参数（本机可用组合）
```python
frames=39  steps=25  seed=20261009  width=864  height=480   # 864x480 不 OOM！
lora = [camera_motion 0.7, wushu_spatial_physics 0.35, wushu_action 0.6]  # 只挂动作
```
**864×480 在 16GB 上跑 25 步不 OOM**（峰值约 15.4GB）——之前 544×320 是为规避 OOM 才降的，
其实可以直接上 864×480。

### 画风 LoRA 最终结论（H3 生态实况）
| LoRA | 判定 |
|---|---|
| `studio1939-strong` | ❌ 1939 水粉风 |
| `looping_sketch_anime` | ❌ 草图风 |
| `h3-realism-people` | ❌ 写实 |
| `Anime2Real _Alpha` | ❌ 动漫转**真人**（Qwen-Image 2 专用，不能挂 H3） |
| **wushu_action / spatial_physics / camera_motion** | ✅ **唯一有用的三个**（只管动作） |

→ **H3 没有"现代/哆啦A梦画风"LoRA。画风 100% 靠 detailed_description 开头的风格句。**

---

## 21. ✅✅ i2v 打斗串联实跑配方（2026-10-04 跑通，可直接复用）

> 成片：**864×480 / 11.663s / 280 帧 / 有音轨 / probe PASS**，5 段 × 56 帧串联。
> 这是目前本机**最省事、最稳**的"有剧情打斗片"打法：不碰 Director 多段（i2v 通道只认单段），
> 用「上段末帧 → 下段首帧」串联 + `ffmpeg -f concat -c copy` 拼接。

### 21.1 参数（照抄）

| 项 | 值 |
|---|---|
| task_type | `i2v`（`/api/h3d/run`，`global_refs=[首帧png]`，`segments` 只放 1 段） |
| frames / steps | **56 / 8**（每段 ≈2.33s；8 步在本机已够，斑点风险可接受） |
| 画布 / seed | **864×480 / 7** |
| 单段耗时 | **90 s**（5 段 = 7m32s） |
| 验收 | 返回值 `verify.still.is_still` 必须 False；再抽帧拼图肉眼确认 |

### 21.2 五拍分镜骨架（打斗专用，比文戏的 4C 更燃）

| 段 | 节拍 | 写法要点 | 实测 avg_diff |
|---|---|---|---|
| S1 | 蓄力 | 法阵/能量从地面涌起绕身盘旋，头发衣摆被吹起，镜头缓推 | 31.56 |
| S2 | 出招 | 双手前推 + 粗光柱射向画外 + 速度线 + 地面物件被掀飞 | 47.29 |
| S3 | 碰撞 | 光柱撞上屏障/敌人 → 白蓝爆闪 + **环形冲击波**掀飞碎石 | 48.44 |
| S4 | 反扑/格挡 | 敌人只写**巨大黑色剪影**（不给脸）+ 能量刃 → 多层护盾展开挡下，炸火花 | 31.17 |
| S5 | 终结 | 数十把光剑成形 → 齐射 → 白光吞没 → 光散后角色伫立，镜头拉远 | 37.72 |

对比文戏 4 段（5.51/23.57/19.30/10.66）：**打斗类镜头 avg_diff 普遍高 2–3 倍，说明动作真演出来了**。

### 21.3 三条新验证的硬结论

1. **能量事件 = 本机最稳的打斗表达**：全程零"贴身实体交互"（不写擦过/抓住/穿过），
   全部用光柱、冲击波、护盾、齐射承载动作 → 零穿模。
2. **敌人只写剪影可规避双角色漂移**：`colossal dark silhouette` 只给轮廓，
   主锚角色外观全程稳定，不会被第二角色分走算力。
3. **5 段比 4 段更抗"没剧情"**：蓄力→出招→碰撞→反扑→终结 有完整因果，观众读得懂。

### 21.4 打斗首帧配方（别用文戏底图）

| 件 | 做法 |
|---|---|
| 战场底图 | Qwen-Image `t_txt2img`（16:9 / 1.0MP / 25 步），prompt 必含 `no characters, no people`；内容=破碎石广场 + 暗天 + 地裂冷蓝光 + 浮石余烬 |
| 角色 | 官方立绘（RGBA）合成，高占 78%，x≈38% |
| 战斗感（PIL 三层） | 地面法阵椭圆环 ×3（冷蓝，GaussianBlur 1.6）+ 手前径向魔力光晕（140,200,255）+ 暗角 vignette |
| 参考实现 | `run_battle_scene.py` + `compose_battle_frame.py`（本机 <PROJECT_DIR> 工作区） |

### 21.5 环境坑（必踩）

- 🔴 **managed python（3.13.12）没有 `cv2`** → 抽末帧脚本必用
  `<COMFYUI_ROOT>\ComfyUI\.venv\Scripts\python.exe`。
- 🔴 **看板要一开始就起**：`h3_board_guard.py`（8789）+ `os.startfile('http://127.0.0.1:8789')`，
  别等跑完再补——用户会问"为什么没开监控台"。
- 引擎：`comfy_stack.py`（8188/8777 每 15s 巡检），本次冷启后 5 段全程零掉线。

### 21.6 抽帧拼图一条命令（替代 probe_battle.py）

```bat
ffmpeg -y -i 成片.mp4 -vf "select='not(mod(n\,35))',scale=432:-1,tile=4x2" -frames:v 1 全程8帧.jpg
```
