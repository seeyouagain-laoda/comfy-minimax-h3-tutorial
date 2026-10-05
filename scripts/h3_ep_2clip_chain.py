# -*- coding: utf-8 -*-
"""《深深的家》EP03《森森不知道哟》—— 10s + 10s 两段接续

剧情（用户给）：主人出门让森森看家 → 森森见主人一走，扑到冰箱抱着白米饭大吃特吃 →
主人回来发现冰箱空了，问「吃的呢？」→ 森森擦掉嘴角的米粒，说「森森不知道哟」。

接缝选在 S3（大吃特吃）中间 —— 两段都在扒饭，动作连续，接缝最自然。
🔴 第 2 段开头必须先复述第 1 段结尾（同人/同姿势/同光线），变化点落在 1.5s 之后。

用法：
  CLIP=1 python run_ep03.py            # 第 1 段（0-10s）
  CLIP=2 python run_ep03.py            # 第 2 段（10-20s，自动接 clip 1）
  CLIP=1 UPSCALE_MP=1.0 python run_ep03.py   # 带二采放大
  DRY=1 CLIP=1 python run_ep03.py      # 只转换不提交
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DURATION", "10")
import run_wf1_chain as R

R.OUT_PREFIX = "shenshen_ep03"

# ---------- 公共段 ----------
# 🔴 2026-10-04 教训：公共段里的 [Props] 写得太具体（"电饭煲装满白饭"），
#    模型会把它当成要展示的内容 → **角色中途消失、切成厨房空镜**（refcheck 快测实测）。
#    修法：公共段只留角色 + 场景框架，道具一律放进 shot 里"用到才写"；
#    并用 [Subject] 明确「每一镜的主体都是这个角色，且必须全镜在画内」。
R.BASE_PROMPT = """integrated_multimodal_description:
[reference generation] Image 1 defines the character exactly — reproduce the chibi whale-girl maid from Image 1 with identical face shape and facial features, identical hairstyle and hair colour, identical outfit and accessories, identical body proportions and identical art style. Do NOT redesign, restyle, recolour, reinterpret or "improve" her. Keep her faithful to Image 1 in every shot.
[Subject] The chibi whale-girl maid from Image 1 is the main subject of every shot and must stay on screen for the whole shot: about 2.5 heads tall, long twin-tails of gradient blue hair (deep navy roots to pale blue-white tips), a single curled ahoge, a blue IV-shaped hair clip, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white maid dress with a white frilled apron bearing a small blue whale outline on the chest, a short blue-white gradient whale tail, and small chubby chibi hands. Her face, hair, outfit, accessories and proportions are all fixed by Image 1.
[Setting] A bright, warm, fully natural-colour home interior: an entryway with a front door, a living room with a sofa and a low wooden table, and an open-plan kitchen with a tall white refrigerator.
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots and close-ups and partial details that imply the larger room, never a full wide shot.

overall_soundscape:
Quiet room ambience, a faint clock tick, soft cloth rustle, slippers tapping on wood, a fridge door opening with a soft suction pop, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot, including prop and environment shots, keeps this hand-drawn 2D anime style.
"""

_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

# ---------- 第 1 段（0 – 10 s）----------
SEG1 = (
    "[Shot 1] At 00:00.000, a medium shot at the entryway. The maid is the main subject: she stands "
    "just inside the front door with both small hands clasped behind her back, looking up and "
    "nodding eagerly with an angelic smile, twin-tails bobbing. A hand picks up a handbag by the "
    "door — only the hand and the bag are visible, the owner is never shown. An off-screen voice, "
    "warm: <d>[Chinese] 森森，看好家哦。</d> The maid answers brightly: <d>[Chinese] 嗯！</d> The "
    "front door clicks shut. Camera static." + _STYLE +
    "[Shot 2] At 00:03.500, cut to the same entryway. The instant the door shuts, the maid's "
    "angelic smile vanishes, her eyes light up with a bright glint, and she spins around and bolts "
    "toward the kitchen, twin-tails and whale tail flying behind her. The camera pans to follow "
    "her." + _STYLE +
    "[Shot 3] At 00:07.000, cut to the open-plan kitchen. The maid sits on the floor hugging a rice "
    "cooker's inner pot in both arms, shovelling white steamed rice into her mouth with a big "
    "spoon, cheeks puffed out like a hamster, a few grains stuck on her cheek, eyes squeezed shut "
    "in bliss, whale tail wagging behind her. The fridge door stands open beside her. The camera "
    "slowly pushes in." + _STYLE
)

# ---------- 第 2 段（10 – 20 s，开头复述上段结尾）----------
SEG2 = (
    "[Shot 1] At 00:00.000, the maid is still sitting on the kitchen floor hugging the rice "
    "cooker's inner pot in both arms, cheeks puffed out and still chewing — the same girl, the same "
    "pot, the same open refrigerator and the same warm light as the previous clip ended. She keeps "
    "eating for a beat. Then the front door clicks open: she freezes mid-bite, rice still in her "
    "mouth, and slowly turns her head. One beat of silence. An off-screen voice, flat and calm: "
    "<d>[Chinese] ……我饭呢？</d>" + _STYLE +
    "[Shot 2] At 00:03.500, cut to an over-the-shoulder shot from behind the maid, looking past her "
    "shoulder and twin-tails into the open refrigerator — completely empty except one lonely bowl "
    "and a single spring onion. Then cut back to her face." + _STYLE +
    "[Shot 3] At 00:06.000, cut to a close-up of her face: the maid quickly wipes the corner of her "
    "mouth with the back of her hand, tucks both hands behind her back, tilts her head and beams, "
    "eyes curving into happy crescents. She says, perfectly innocent: "
    "<d>[Chinese] 森森不知道哟。</d> The camera slowly tilts down — the tip of her whale tail "
    "quietly sweeps the last grain of rice under the sofa. Hold." + _STYLE
)


def main():
    clip = int(os.environ.get("CLIP", "1"))
    seg = SEG1 if clip == 1 else SEG2
    up = float(os.environ.get("UPSCALE_MP", "0") or 0)
    print("=== EP03《森森不知道哟》 clip %d  %.0fs  放大=%s ===" % (
        clip, float(os.environ.get("DURATION", "10")), up or "关"))
    ok, info, outs = R.run_clip(clip, seg, upscale_mp=up, dry=(os.environ.get("DRY") == "1"))
    print("RESULT:", "OK" if ok else "FAIL", outs)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
