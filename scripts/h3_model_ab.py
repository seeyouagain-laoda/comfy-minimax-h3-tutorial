# -*- coding: utf-8 -*-
"""底模 A/B 对拍：现有完整版 31.67GB vs 新下的 Pruned 19.53GB

同提示词、同 seed、同参考图、3 秒单镜，比耗时 + 画质。
用法：python run_model_ab.py
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["DURATION"] = "3"
os.environ["SEED"] = "20261010"
os.environ["UPSCALE_MP"] = "0"
import run_ep03 as E          # 复用公共段（含参考图指令 + style_lock）

_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

SEG = ("[Shot 1] At 00:00.000, a medium shot in the living room: the chibi whale-girl maid stands "
       "facing the camera holding a big white bowl of steamed rice in both hands, smiling happily, "
       "twin-tails and whale tail swaying. Warm afternoon light. Camera static." + _STYLE)

MODELS = [
    ("A_full", "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors"),
    ("B_pruned", "Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors"),
]


def main():
    results = []
    for tag, model in MODELS:
        os.environ["UNET"] = model
        E.R.OUT_PREFIX = "ab_" + tag
        print("\n===== %s : %s =====" % (tag, model), flush=True)
        t0 = time.time()
        ok, info, outs = E.R.run_clip(1, SEG, upscale_mp=0)
        el = time.time() - t0
        results.append((tag, model, ok, el, outs))
        print(">> %s  %s  %.0fs  %s" % (tag, "OK" if ok else "FAIL", el, outs), flush=True)
    print("\n===== 汇总 =====")
    for tag, model, ok, el, outs in results:
        print("  %-10s %-6s %6.0fs  %s" % (tag, "OK" if ok else "FAIL", el, outs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
