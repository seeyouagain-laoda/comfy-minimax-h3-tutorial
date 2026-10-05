# -*- coding: utf-8 -*-
"""《深深の家》EP05《困意传染》—— 20s 两段接续，13 镜 × 1.5s 快剪

剧情：森森打哈欠 → 哒哒传染 → 两人越打越困 → 一起睡着，哒哒的鲸尾当被子。

节奏标准（2026-10-04 用户确认）：1.2-2.0s/镜，靠"切"推进不靠"演"。
台词规则：只用自称（深深的 / 哒哒的），中文咬字压力最小。

用法：
  CLIP=1 python run_ep05.py     # 镜 1-7（0-10s）
  CLIP=2 python run_ep05.py     # 镜 8-13（10-20s，自动接 clip 1）
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DURATION", "10")
os.environ.setdefault("REF_IMAGE", "shenshen_ref.png")
os.environ.setdefault("REF_IMAGE2", "ref_dada.png")
import run_wf1_chain as R

R.OUT_PREFIX = "shenshen_ep05"

# ---------- 公共段（双角色，客厅场景）----------
R.BASE_PROMPT = """integrated_multimodal_description:
[reference generation] Image 1 defines the FIRST character exactly — reproduce the chibi whale-girl maid from Image 1 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign or restyle her. Image 2 defines the SECOND character exactly — reproduce the chibi whale-girl in the white kimono-style dress from Image 2 with identical face shape, hairstyle, hair colour, outfit, accessories, body proportions and art style; do NOT redesign or restyle her. These are TWO DIFFERENT girls and must never be merged, swapped or blended into one.
[Subject A] The navy maid girl from Image 1: about 2.5 heads tall, long twin-tails of gradient blue hair (deep navy roots to bright blue tips), a single curled ahoge, a blue IV-shaped hair clip on her forehead, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white frilled maid dress with a white apron bearing a small blue whale outline, a blue-purple whale tail with starry speckles, and small navy shoes.
[Subject B] The silver-haired girl from Image 2: about 2.5 heads tall, long gradient silver-to-lilac-grey hair with a single curled ahoge, large whale-fin ears, calm pale eyes, a white kimono-style dress with a pale-blue gradient hem and a wide blue sash, a tassel ornament at her waist, a long translucent whale tail with a water-and-starlight sheen, and bare feet in thin-strapped sandals.
[Setting] A bright, warm, fully natural-colour living room: a soft beige carpet on the wooden floor, a low wooden table, a sofa with a throw blanket, warm late-afternoon light.
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots, close-ups and partial details, never a full wide shot.

overall_soundscape:
Quiet room ambience, a faint clock tick, soft cloth rustle, occasional yawns, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot keeps this hand-drawn 2D anime style.
"""

_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

# ---------- 第 1 段（0 – 10 s，镜 1-7）----------
SEG1 = (
    "[Shot 1] At 00:00.000, a medium shot: the navy maid girl (Image 1) sits cross-legged on the "
    "beige carpet in front of the low table, a few open books spread in front of her that she is not "
    "really reading. Warm late-afternoon light. Camera static." + _STYLE +
    "[Shot 2] At 00:01.500, cut to a close-up of her face: she opens her mouth wide and yawns hugely, "
    "eyes squeezed shut, a tiny tear at the corner of one eye, her ahoge bouncing. Camera static."
    + _STYLE +
    "[Shot 3] At 00:03.000, cut to a medium shot: the silver-haired girl (Image 2) sits on the "
    "carpet beside her, and lifts her eyes to look at the yawning maid girl. Camera static." + _STYLE +
    "[Shot 4] At 00:04.500, cut to a close-up of the silver-haired girl's face: she cannot hold it "
    "and yawns hugely too, mouth wide, eyes squeezed shut. Camera static." + _STYLE +
    "[Shot 5] At 00:06.000, cut to a medium shot: the navy maid girl turns her head and meets the "
    "silver-haired girl's eyes. Camera static." + _STYLE +
    "[Shot 6] At 00:07.500, cut to a close-up of the silver-haired girl yawning even wider, both "
    "hands raised beside her head. The navy maid girl, already half asleep, mumbles: "
    "<d>[Chinese] 深深的……困……</d> Camera static." + _STYLE +
    "[Shot 7] At 00:09.000, cut to a medium shot of both girls: they yawn a third time at the same "
    "moment, mouths wide open in perfect sync, bodies swaying. Camera static." + _STYLE
)

# ---------- 第 2 段（10 – 20 s，镜 8-13）----------
SEG2 = (
    "[Shot 1] At 00:00.000, a close-up of the two girls' faces side by side, both eyes half closed "
    "and mouths open — the same two girls, the same carpet and the same warm light as the previous "
    "clip ended. They are still mid-yawn. The silver-haired girl mumbles: "
    "<d>[Chinese] ……哒哒的……也……</d> Camera static." + _STYLE +
    "[Shot 2] At 00:02.000, cut to a medium shot: the navy maid girl can no longer hold herself up "
    "and her head tilts sideways, resting on the open book. Camera static." + _STYLE +
    "[Shot 3] At 00:03.500, cut to a medium shot: the silver-haired girl also tilts sideways and "
    "leans her head onto the navy maid girl's shoulder. Camera static." + _STYLE +
    "[Shot 4] At 00:05.000, cut to a close-up: the two girls' heads rest against each other, both "
    "eyes now closed, breathing slowly. Camera static." + _STYLE +
    "[Shot 5] At 00:06.500, cut to a medium shot: the silver-haired girl's long translucent whale "
    "tail slowly slides over and drapes across both girls like a blanket. Camera static." + _STYLE +
    "[Shot 6] At 00:08.000, cut to a close-up of the two girls asleep, heads touching, the glowing "
    "translucent tail covering them, their hair fanned out on the carpet. Camera static." + _STYLE +
    "[Shot 7] At 00:09.500, cut to a wide shot of the quiet living room: both girls asleep on the "
    "carpet under the whale-tail blanket, books scattered, warm light, nothing moves except the "
    "faint dust in the air. Hold." + _STYLE
)


def main():
    clip = int(os.environ.get("CLIP", "1"))
    seg = SEG1 if clip == 1 else SEG2
    up = float(os.environ.get("UPSCALE_MP", "0") or 0)
    print("=== EP05《困意传染》 clip %d  %.0fs  放大=%s ===" % (
        clip, float(os.environ.get("DURATION", "10")), up or "关"))
    ok, info, outs = R.run_clip(clip, seg, upscale_mp=up, dry=(os.environ.get("DRY") == "1"))
    print("RESULT:", "OK" if ok else "FAIL", outs)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
