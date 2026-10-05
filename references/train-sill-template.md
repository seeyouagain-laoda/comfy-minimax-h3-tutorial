# 模板 · 固定机位 + 局部运动 + 角色站在某物上

> 来源：2026-10-05 高铁窗沿蹦跳（3 版迭代跑通）
> 脚本：`<PROJECT_DIR>\run_train_sill.py`
> 文档：`重要AI配置文档\06_视频与图像生成\48_高铁窗沿蹦跳_车窗静止窗外移动_20261005.md`
> 避坑：SKILL.md §5 第 24、25 条

## 适用场景

「**背景局部静止、局部运动**」+「**角色与某物发生接触**」的组合题材：

- 运动中的高铁/地铁/汽车：车窗不动、窗外景物掠过
- 站在窗沿 / 桌沿 / 台阶 / 栏杆上做动作
- 传送带、电梯、扶梯上站着
- 摩天轮舱内、缆车里

## 三条核心写法（缺一不可）

### ① 先保证参照物入画（构图层）

🔴 **最容易翻车的一条**。想让角色「站在窗沿上」，镜头里**必须先有窗沿** ——
只写 `she stands ON the sill` 而镜头正对窗户（窗台在画面外），模型只会把她画成
「浮在窗户前面的贴纸」。

```
[Framing] Every shot is framed close on the character: she fills at least half of the frame
height. The solid flat window sill — the ledge running along the bottom edge of the window —
is kept inside the frame as a clear horizontal line across the lower part of the picture, and
she stands directly on top of it: her two small navy shoes rest flat on the sill surface and
the sill is plainly visible as a solid horizontal ledge right beneath her feet.
Never pull back to a wide shot of the whole carriage, and never let her float in mid-air with
nothing under her feet.
```

机位句（写进 shot）：`taken from a slightly low angle that keeps the sill in frame`

→ **通用原则：先让参照物可见，再声明相对关系。**

### ② 固定机位 + 局部运动：三句齐全

只写 `camera static` 不够。三句都要写，且每镜末尾用 style 锚重复：

```
The camera NEVER moves in any shot — no pan, no zoom, no shake, no handheld drift, no camera
movement of any kind.                                       ← ① 镜头不动
The window frame, the window sill and the whole carriage interior stay perfectly still and
locked in place for the entire video.                       ← ② 场景不动
ONLY the scenery outside the glass moves: the countryside is smeared into long horizontal
streaks of blurred green and grey, individual trees and power poles sweep past from one side
to the other, and the whole outside view slides sideways continuously.
                                                            ← ③ 只有指定部分动 + 可辨识参照物
Never let the window, the sill or the interior drift, slide or move with the scenery.
                                                            ← ④ 显式否定「跟着动」
```

**必须有可辨识参照物掠过**（trees / power poles sweep past）—— 只有一团糊绿，观者看不出在动。

### ③ 排除人物泛白

```
in full vivid natural colour with strong contrast — never washed out, never pale,
never faded, never desaturated, never hazy, at all times
```

## 分镜骨架（5s / 4 拍 × 1.25s）

| 拍 | 时间 | 内容 |
|---|---|---|
| 1 | 0.000s | 站在窗沿上小幅弹跳（建立「脚踩在窗沿上」的空间关系） |
| 2 | 1.250s | 用力向上跳起 —— **脚离开窗沿，空窗沿仍可见**（反证她原本站在上面） |
| 3 | 2.500s | 落回窗沿膝盖弯曲，立刻再弹 |
| 4 | 3.750s | 跳到最高点欢呼（中景，**保留车厢环境 + 窗沿**） |

**每拍都要重申窗沿位置**（`shoes rest flat on the sill surface` / `the sill visible again
under her feet` / `the empty flat sill still clearly visible below her`）。

## 特写镜的额外约束

特写一放大，环境就容易消失只剩背景。特写镜必须**单独声明环境**：

```
directly behind her the still window frame, the black rubber seal and the carriage wall are
all in frame
```

或干脆把该镜从 `close-up` 放宽为 `medium shot`。

## 参数（本机）

| 项 | 值 |
|---|---|
| 通道 | Ref2VA |
| 底模 | `Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors` |
| LoRA | `minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` @1.0 |
| 步数/调度/采样器 | 8 / simple / er_sde |
| 分辨率 | 16:9 @ 0.4 MP（864×480） |
| 5s | 124 帧；单段约 4.5 分钟 |

## 验收命令

```bat
:: 全片抽帧
ffmpeg -y -v error -i IN.mp4 -vf "select='not(mod(n\,16))',scale=380:-1,tile=4x2" -frames:v 1 sheet.jpg
:: 查「窗外是否真在动」——裁窗户区域看连续帧位移
ffmpeg -y -v error -i IN.mp4 -vf "select='between(n,20,44)*not(mod(n,4))',crop=380:270:0:0,scale=380:-1,tile=4x2" -frames:v 1 motion.jpg
:: 规格
ffprobe -v error -show_entries stream=codec_type,width,height,nb_frames -of default=nw=1 IN.mp4
```
