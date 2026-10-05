# -*- coding: utf-8 -*-
"""《深深的家》EP04《最后一碗饭》—— 森森 × 哒哒 抢饭，20s 两段接续

用户定：① 20 秒；② 打闹点 = 抢最后一碗饭；③ 台词只用「自称」——
深深说「深深的！」、哒哒说「哒哒的！」—— 避开复杂中文词，降低 H3 中文咬字负担。

接缝选在 S2（拉碗较劲）中间 —— 两段都在拽同一个碗，动作连续。

用法：
  CLIP=1 REF_IMAGE2=ref_dada.png python run_ep04.py
  CLIP=2 REF_IMAGE2=ref_dada.png python run_ep04.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DURATION", "10")
os.environ.setdefault("REF_IMAGE", "shenshen_ref.png")
os.environ.setdefault("REF_IMAGE2", "ref_dada.png")   # 🔴 双角色：第二张参考图
import run_wf1_chain as R

R.OUT_PREFIX = "shenshen_ep04"

# ---------- 公共段（双角色）----------
# 🔴 三条铁律（都实测踩过）：
#   ① Image 1 / Image 2 分别定义两个角色，并明说"是两个不同角色、不许融合/互换"
#   ② [Props] 类道具描述一律写进 shot，用到才写（否则模型去拍道具空镜、角色消失）
#   ③ 每镜结尾重复画风锚 + 显式否定写实
R.BASE_PROMPT = """integrated_multimodal_description:
[reference generation] Image 1 defines the FIRST character exactly — reproduce the chibi whale-girl maid from Image 1 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign, restyle, recolour or reinterpret her. Image 2 defines the SECOND character exactly — reproduce the chibi whale-girl in the white kimono-style dress from Image 2 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign, restyle, recolour or reinterpret her. These are TWO DIFFERENT girls and must never be merged, swapped or blended into one.
[Subject A] The navy maid girl from Image 1: about 2.5 heads tall, long twin-tails of gradient blue hair (deep navy roots to bright blue tips), a single curled ahoge, a blue IV-shaped hair clip on her forehead, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white frilled maid dress with a white apron bearing a small blue whale outline, a blue-purple whale tail with starry speckles, and small navy shoes.
[Subject B] The silver-haired girl from Image 2: about 2.5 heads tall, long gradient silver-to-lilac-grey hair with a single curled ahoge, large whale-fin ears, calm pale eyes, a white kimono-style dress with a pale-blue gradient hem and a wide blue sash, a tassel ornament at her waist, a long translucent whale tail with a water-and-starlight sheen, and bare feet in thin-strapped sandals.
[Setting] A bright, warm, fully natural-colour dining nook: a low wooden table, two floor cushions on opposite sides of it, warm afternoon light on the wooden floor.
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots and close-ups and partial details, never a full wide shot.

overall_soundscape:
Quiet room ambience, a faint clock tick, soft cloth rustle, a wooden spoon knocking on a bowl, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot keeps this hand-drawn 2D anime style.
"""

_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

# ---------- 第 1 段（0 – 10 s）----------
# 🔴 2026-10-04 用户纠正：**分镜时长是"动作慢"的真正根因**（不是 turbo / 步数）。
#    旧版 5 镜 × 4s = 电影长镜头 → 观感慢到需要 1.5x 变速才正常。
#    新版快剪：1.5s/镜、特写交替、每镜只做一个动作、靠"切"推进。
#    参照：B站《大肥鱼小日常》81集/858万播放 = 0.5-1.5s 一镜。
SEG1 = (
    "[Shot 1] At 00:00.000, an extreme close-up of one big white bowl of steamed rice on the low "
    "wooden table, steam curling up, a wooden spoon beside it. Camera static." + _STYLE +
    "[Shot 2] At 00:01.500, cut to a close-up of the navy maid girl's face (from Image 1): her eyes "
    "are locked on the bowl, cheeks puffed, she swallows once. Camera static." + _STYLE +
    "[Shot 3] At 00:03.000, cut to a close-up of the silver-haired girl's face (from Image 2): pale "
    "calm eyes staring at the same bowl from the other side, one brow slightly raised. Camera "
    "static." + _STYLE +
    "[Shot 4] At 00:04.500, cut to a top-down shot of the table: TWO small hands — one in a navy "
    "sleeve, one bare with a thin sandal strap — reach in from opposite sides and grab the bowl at "
    "the same instant. Camera static." + _STYLE +
    "[Shot 5] At 00:06.000, cut to a medium shot: both girls pull the bowl toward themselves, the "
    "navy maid girl straining and shouting: <d>[Chinese] 深深的！</d> Camera static." + _STYLE +
    "[Shot 6] At 00:07.500, cut to a close-up of the bowl between them: rice grains scatter across "
    "the wooden table as it wobbles, the silver-haired girl answers loudly: "
    "<d>[Chinese] 哒哒的！</d> Camera static." + _STYLE +
    "[Shot 7] At 00:09.000, cut to a medium shot: both girls strain harder, and their two whale "
    "tails lift and twist tightly around each other in mid-air while the bowl slides to the exact "
    "centre of the table. The navy maid girl: <d>[Chinese] 深深的！</d> The silver-haired girl: "
    "<d>[Chinese] 哒哒哒哒的！</d> Camera static." + _STYLE
)

# ---------- 第 2 段（10 – 20 s）----------
SEG2 = (
    "[Shot 1] At 00:00.000, an extreme close-up of two small hands gripping the bowl rim, white "
    "knuckles, both arms trembling — the same two girls, the same bowl and the same table as the "
    "previous clip ended. Their whale tails are still twisted together." + _STYLE +
    "[Shot 2] At 00:01.000, cut to a medium shot: both girls pull as hard as they can at the same "
    "instant, faces flushed, both shouting together: <d>[Chinese] 嗯——！</d> Camera static." + _STYLE +
    "[Shot 3] At 00:02.500, cut to a close-up: the bowl slips out of their hands and shoots up in "
    "a short arc, spinning, with a few grains of rice flying off. Camera tilts up with the bowl."
    + _STYLE +
    "[Shot 4] At 00:04.000, cut to a medium shot: both girls freeze for a beat with their arms "
    "still outstretched, then both scream and lunge after it: <d>[Chinese] 哇——！</d> Camera static."
    + _STYLE +
    "[Shot 5] At 00:05.500, cut to a low shot: the two girls crash into each other head-on, their "
    "foreheads bump, and they tumble down in a heap, hair and tails tangled together. A dull thud. "
    "Camera static." + _STYLE +
    "[Shot 6] At 00:07.000, cut to a close-up on the floor: the bowl lands upright beside them, "
    "perfectly intact, rice still steaming. The two girls lie side by side in a heap, hair messy, "
    "tails knotted together." + _STYLE +
    "[Shot 7] At 00:08.500, cut to a medium shot: still lying side by side, the navy maid girl "
    "turns her head to glare at the silver-haired girl, who immediately turns her face away with "
    "puffed cheeks. The navy maid girl: <d>[Chinese] 哼。</d> The silver-haired girl: "
    "<d>[Chinese] 哼。</d> Camera static." + _STYLE
)


def main():
    clip = int(os.environ.get("CLIP", "1"))
    seg = SEG1 if clip == 1 else SEG2
    up = float(os.environ.get("UPSCALE_MP", "0") or 0)
    print("=== EP04《最后一碗饭》 clip %d  %.0fs  放大=%s  参考图=%s + %s ===" % (
        clip, float(os.environ.get("DURATION", "10")), up or "关",
        os.environ.get("REF_IMAGE"), os.environ.get("REF_IMAGE2")))
    ok, info, outs = R.run_clip(clip, seg, upscale_mp=up, dry=(os.environ.get("DRY") == "1"))
    print("RESULT:", "OK" if ok else "FAIL", outs)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
