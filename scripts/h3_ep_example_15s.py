# -*- coding: utf-8 -*-
"""《深深的家》EP02《看守》—— 15 秒单段

剧情（用户给）：主人让深深看守仓库（家），自己出去旅游；回来发现冰箱被清空、
尤其是大米饭全没了，深深狡辩。

四拍结构（网上那套 15s 短剧公式）：
  0-3s   钩子：主人回家，深深双手背后、笑容过度灿烂
  3-7s   升级：冰箱门打开 —— 里面只剩一个空碗
  7-11s  狡辩：摊手耸肩「它自己走的，走我肚子里了」
  11-15s 爆点：打饱嗝 + 一粒米掉出来 + 鲸尾扫走，定格

用法：
  python run_ep_voyage.py                 # 15s 一采（864x480）
  UPSCALE_MP=1.0 python run_ep_voyage.py  # 15s + 二采放大到 1MP
  DRY=1 python run_ep_voyage.py           # 只转换不提交
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DURATION", "15")
import run_wf1_chain as R

R.OUT_PREFIX = "shenshen_voyage"

# ---------- 本集专用公共段（角色不变，场景换成「玄关 + 开放式厨房冰箱」） ----------
R.BASE_PROMPT = """integrated_multimodal_description:
A bright, warm, fully natural-colour home interior — warm wood floor, cream walls, soft afternoon light through a window, and the maid's own colours, especially her deep-navy hair and pale-blue eyes.
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots and close-ups and partial details that imply the larger room, never a full wide shot.
[Character] A chibi whale-girl maid, about 2.5 heads tall: long twin-tails of gradient blue hair (deep navy roots to pale blue-white tips), a single curled ahoge, a blue IV-shaped hair clip, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white maid dress with a white frilled apron bearing a small blue whale outline on the chest, a short blue-white gradient whale tail, and small chubby chibi hands.
[Setting] A small home seen in fragments: a doorway with a suitcase just set down, a sofa with a soft throw, a low wooden table, and an open-plan kitchen with a tall white refrigerator whose door stands open.
[Props] A tall white refrigerator with an almost empty interior, one lonely empty bowl and a single spring onion left on its shelf, a rice cooker with its lid open and its inner pot scraped completely clean, a pair of chopsticks, and a folded blanket on the sofa.

overall_soundscape:
Quiet room ambience, a faint clock tick, soft cloth rustle, the soft thud of a suitcase being set down, the click and suction of a fridge door opening, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack

style_lock:
The entire video is 2D hand-drawn animation with flat cel shading and visible sketch lines, in full natural colour — never photorealistic, never a photograph, never live action, never a 3D render. Every single shot, including prop and environment shots, keeps this hand-drawn 2D anime style.
"""

# ---------- 本集分镜 ----------
# 🔴 铁律（本次实测踩到）：**纯道具/环境镜头会把画风漂回照片级写实**。
#    所以 ① 每一镜都必须有角色入画；② 每一镜结尾都重复一遍画风锚 + 显式否定写实。
_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

SEG = (
    "[Shot 1] At 00:00.000, a medium shot inside the small home: the chibi whale-girl maid stands "
    "in the living room right beside a suitcase that has just been set down by the doorway, both "
    "small hands clasped behind her back, grinning far too brightly straight at the camera, "
    "twin-tails swinging. An off-screen voice, warm and cheerful, greets her: "
    "<d>[Chinese] 深深，我回来啦！</d> The camera slowly pushes in on her over-bright smile."
    + _STYLE +
    "[Shot 2] At 00:03.000, cut to a medium shot of the open-plan kitchen: the maid stands right "
    "beside the tall white refrigerator with its door wide open and lit from inside, leaning in and "
    "peering at the empty shelves with a carefully innocent face. Inside there is almost nothing — "
    "one lonely empty bowl and a single spring onion. The off-screen voice, now flat and "
    "suspicious: <d>[Chinese] ……我冰箱呢？</d> The camera slowly pushes past her toward the empty "
    "shelf."
    + _STYLE +
    "[Shot 3] At 00:07.000, cut back to a medium shot of the maid in the living room: she spreads "
    "both small hands wide and shrugs, chin lifted, perfectly matter-of-fact, whale tail swaying "
    "once. She says, completely unbothered: <d>[Chinese] 它自己走的，走我肚子里了。</d> The camera "
    "holds steady on her."
    + _STYLE +
    "[Shot 4] At 00:11.000, cut to a close-up of her face: the off-screen voice asks: "
    "<d>[Chinese] ……锅呢？</d> The maid freezes for a beat, then lets out one small satisfied burp "
    "and a single grain of rice drops from the corner of her mouth. Her whale tail flicks out and "
    "sweeps the grain under the sofa. Hold on her face, still grinning."
    + _STYLE
)


def main():
    up = float(os.environ.get("UPSCALE_MP", "0") or 0)
    print("=== 《深深的家》EP02《看守》 %.0fs  放大=%s MP ===" % (
        float(os.environ.get("DURATION", "15")), up or "关"))
    ok, info, outs = R.run_clip(1, SEG, upscale_mp=up, dry=(os.environ.get("DRY") == "1"))
    print("RESULT:", "OK" if ok else "FAIL", outs)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
