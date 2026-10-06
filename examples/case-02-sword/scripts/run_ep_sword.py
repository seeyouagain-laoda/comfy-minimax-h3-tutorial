# -*- coding: utf-8 -*-
"""《深夜剑道 · 深深》 20 秒短剧 = 2 段 × 10s（Motion Context latent 真接续）

【剧情 · 四拍 · 12 镜】
钩子(0-2.5s) 深夜，深深一个人在客厅对着一把木剑摆起中二架势，认真得像要上擂台
升级(2.5-7s) 喊口号、挥剑、脚步乱晃、尾巴自己跟着甩，越打越上头
反转(7-14s) 一记力劈华山，剑风把茶几上的零食袋掀飞，深深整个人呆住，尾巴僵在半空
收尾(14-20s) 主人画外音一句"深深，你在练什么？"→ 深深收剑立正，
              小声"……剑道。" → 尾巴悄悄把零食袋推回桌下（不靠台词的第二笑点）

🔴 接缝选在「剑风掀飞零食袋、深深呆住」这个静止点，两段都在定格式静止，
   Motion Context 钉帧最友好，接缝最自然。
🔴 第 2 段开头必须先复述第 1 段结尾（同人 / 同姿势 / 同光线 / 同道具散落状态），
   变化点落在 1.5s 之后。

用法（必须用 skill 的 venv python）：
  DRY=1 CLIP=1 "<VP>" r0_sword_shen_shen.py    # 只看接线不提交
  CLIP=1 SEED=880601 "<VP>" r0_sword_shen_shen.py
  CLIP=2 SEED=880601 "<VP>" r0_sword_shen_shen.py
  # 拼接
  ffmpeg -f concat -safe 0 -i list.txt -c copy OUT.mp4
"""
import os
import sys

os.environ.setdefault("DURATION", "10")
os.environ.setdefault("OUT_PREFIX", "shenshen_sword")

sys.path.insert(0, r"<AGENT_SKILL_DIR>/scripts")
import h3_motion_context_chain as R

R.OUT_PREFIX = os.environ.get("OUT_PREFIX", "shenshen_sword")

# ---------- 公共段 ----------
# 🔴 公共段只写角色 + 场景框架，**不写具体道具**（道具写进具体 Shot，用到才写），
#    否则模型会把它当展示主体 → 角色中途消失 / 切成道具空镜。
R.BASE_PROMPT = """integrated_multimodal_description:
[reference generation] Image 1 defines the character exactly — reproduce the chibi whale-girl maid from Image 1 with identical face shape and facial features, identical hairstyle and hair colour, identical outfit and accessories, identical body proportions and identical art style. Do NOT redesign, restyle, recolour, reinterpret or "improve" her. Keep her faithful to Image 1 in every shot.
[Subject] The chibi whale-girl maid from Image 1 is the main subject of every shot and must stay on screen for the whole shot: about 2.5 heads tall, long twin-tails of gradient blue hair (deep navy roots to pale blue-white tips), a single curled ahoge, a blue IV-shaped hair clip, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white maid dress with a white frilled apron bearing a small blue whale outline on the chest, a short blue-white gradient whale tail, and small chubby chibi hands. Her face, hair, outfit, accessories and proportions are all fixed by Image 1.
[Setting] The same quiet Japanese-style apartment living room at night in every shot: warm paper-lamp light from frame right, tatami and wooden floor, a low dark-wood table, a sliding shoji screen behind, deep night outside the window. Medium shots and close-ups only, never a full wide shot.
Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel palette — NOT photorealistic, no photograph, no live action, no 3D render.

overall_soundscape:
Quiet late-night room ambience: a faint wall-clock tick, distant traffic hum through the window, soft cloth and footstep rustle on tatami, a light wooden sword whoosh, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack
"""

_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

# ---------- 第 1 段（0 – 10 s）：起手 → 练剑 → 掀飞零食 → 呆住 ----------
SEG1 = (
    "[Shot 1] At 00:00.000, a medium shot at eye level. The maid stands alone in the centre of the "
    "night living room facing the camera, both small hands gripping a plain wooden practice sword "
    "held vertically in front of her chest, feet planted shoulder-width apart, twin-tails and whale "
    "tail hanging still. She takes one deep breath, closes her eyes, and raises the sword straight "
    "above her head in a slow formal salute. Sound inline: 0.00-2.20s a faint clock tick and her "
    "bare feet shifting once on the tatami. Camera static, focus held on her upper body." + _STYLE +
    "[Shot 2] At 00:02.400, cut to a closer medium shot from slightly low angle. She snaps the sword "
    "down to her side, opens her eyes with a fierce determined glint, and declares loudly with clear "
    "lip movement, <d>[Chinese] 深深，开始修行！</d> Her whale tail lifts and wags once behind her "
    "on its own. Sound inline: 2.40-3.20s her bright young female voice in standard Mandarin with a "
    "comedic punch; 2.80s one light wooden swish." + _STYLE +
    "[Shot 3] At 00:03.600, cut to a medium shot, three-quarter view. She steps into a clumsy "
    "sideways shuffle across the tatami, both hands swinging the wooden sword in a big awkward arc, "
    "her whole body wobbling out of balance while her twin-tails lag behind a beat late. She "
    "half-stumbles, catches herself, and puffs her round cheeks in frustration. Sound inline: "
    "3.60-5.20s rhythmic wooden swishes and soft footfalls; 4.60s one small comedy squeak of floor "
    "board creak. Camera pans slightly to keep her centred." + _STYLE +
    "[Shot 4] At 00:05.400, cut to a low medium shot. She plants her feet again, raises the wooden "
    "sword high over her head with both arms trembling, and swings it down in one single heavy "
    "overhead chop. On the impact the camera shakes once and a burst of air lifts a small paper snack "
    "bag off the low table behind her. Sound inline: 5.40-6.20s a fast downward whoosh ending in a "
    "solid thud; 6.20s crinkling paper." + _STYLE +
    "[Shot 5] At 00:06.600, cut to a medium close-up on her face. She freezes in her finishing "
    "pose, wooden sword held down at her side, both eyes wide and round, tiny ahoge standing "
    "straight up in shock, mouth slightly open. Behind her the paper snack bag drifts down onto the "
    "tatami. Sound inline: 6.60-7.60s absolute silence except the clock tick; 7.60s soft paper "
    "landing." + _STYLE +
    "[Shot 6] At 00:07.900, a tighter close-up. Still frozen, she slowly lowers her gaze from the "
    "snack bag on the floor to her own starry whale tail, which is stuck stiffly straight out behind "
    "her like a stiff plank, then gives one tiny guilty wiggle. She blinks twice, swallows, and "
    "tightens her grip on the wooden sword until her knuckles go pale. Sound inline: 7.90-10.00s "
    "room tone only, one faint tail flap; 9.20s a quiet swallow. Camera pushes in very slowly." + _STYLE
)

# ---------- 第 2 段（10 – 20 s，开头逐字复述上段结尾）----------
SEG2 = (
    "[Shot 1] At 00:00.000, the same night living room, the same warm paper-lamp light from frame "
    "right. The maid is in exactly the same position the previous clip ended in — a tight close-up, "
    "she has just lowered her gaze to her own stiff starry whale tail, both small hands white-knuckled "
    "on the wooden practice sword at her side, the crumpled paper snack bag lying on the tatami just "
    "behind her heel. She holds perfectly still for a beat, then at 01.600 snaps her eyes shut, forces "
    "a tiny straight-lipped smile onto her face and straightens her back like a soldier standing "
    "to attention. Sound inline: 0.00-1.60s room tone and clock tick; 1.60s one crisp sword-cloth "
    "swish as she shoulders the blade." + _STYLE +
    "[Shot 2] At 00:02.400, cut to a medium shot from slightly low angle. Facing the camera squarely, "
    "she holds the wooden sword vertically before her chest in a crisp formal salute and bows once, "
    "small and stiff, twin-tails bouncing with the motion. An off-screen voice, calm and flat, an "
    "unseen person occupying the camera position and never entering frame: "
    "<d>[Chinese] 深深，你在练什么？</d> Sound inline: 2.40-3.60s the calm adult male voice line." + _STYLE +
    "[Shot 3] At 00:04.000, cut to a medium close-up. She keeps her eyes shut, still in the salute, "
    "and mumbles in a tiny guilty voice with clear lip movement, "
    "<d>[Chinese] 剑、剑道……</d> One drop of sweat slides down her temple. Behind her, out of focus "
    "but visible, her starry whale tail slowly swings around and quietly pushes the crumpled paper "
    "snack bag further under the low table. Sound inline: 4.00-5.40s her small hesitant female voice "
    "line; 5.00s faint soft paper scraping on wood." + _STYLE +
    "[Shot 4] At 00:05.800, cut to a wider medium shot of the whole corner. She has now slipped the "
    "wooden sword under her arm like a schoolbag, tiptoes silently toward the low table and peeks "
    "underneath it from a crouch, one hand braced on the tabletop, her tail wagging once behind her. "
    "Her face goes bright with a huge delighted grin when she confirms the snack bag is safely hidden. "
    "Sound inline: 5.80-6.60s light tiptoe footfalls; 6.60-7.20s one small satisfied giggle." + _STYLE +
    "[Shot 5] At 00:07.400, cut back to a medium close-up. Still crouched by the table, she turns her "
    "head to the camera and gives one tiny, utterly unapologetic thumbs-up while holding the wooden "
    "sword sideways under her arm, eyes curving into smug crescents, twin-tails bouncing. Sound "
    "inline: 7.40-8.20s the soft tail flap behind her." + _STYLE +
    "[Shot 6] At 00:08.600, the camera holds the same medium close-up as she stands back up, plants "
    "her feet, lifts the wooden sword high above her head once more for another round of practice, "
    "determined and eager, while her whale tail wags in perfect sync behind her. Hold on her eager "
    "face until 10.000. Sound inline: 8.60-10.00s one light wooden swish, room tone and clock tick, "
    "no dialogue." + _STYLE
)


def main():
    clip = int(os.environ.get("CLIP", "1"))
    seg = SEG1 if clip == 1 else SEG2
    up = float(os.environ.get("UPSCALE_MP", "0") or 0)
    print("===《深夜剑道 · 深深》 clip %d  %ss  放大=%s ===" % (
        clip, os.environ.get("DURATION", "10"), up or "关"))
    ok, info, outs = R.run_clip(clip, seg, upscale_mp=up, dry=(os.environ.get("DRY") == "1"))
    print("RESULT:", "OK" if ok else "FAIL", outs)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())