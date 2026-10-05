# -*- coding: utf-8 -*-
"""步数对「动作观感」的影响 —— 8 / 12 / 16 步对拍

不只测画面变化量（差分），还测 **运动平滑度**：
把逐帧差分序列做 FFT，低频能量占比越高 = 运动越平滑（真实运动）；
高频占比高 = 抖动/伪影（看起来像"原地蠕动"= 用户说的"慢"）。
"""
import os, sys, time
import cv2, numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["DURATION"] = "3"
os.environ["SEED"] = "20261011"
os.environ["UPSCALE_MP"] = "0"
os.environ["CLIP"] = "1"
os.environ.setdefault("REF_IMAGE", "shenshen_ref.png")
os.environ.setdefault("REF_IMAGE2", "ref_dada.png")
import h3_ep_bowl_duo as E

_STYLE = (" Style: hand-drawn 2D anime, flat cel shading, visible sketch lines, warm pastel "
          "palette — NOT photorealistic, no photograph, no live action, no 3D render.")

SEG = ("[Shot 1] At 00:00.000, a medium shot of the low wooden table with ONE big white bowl of "
       "steamed rice in the centre. The navy maid girl (Image 1) on the left and the silver-haired "
       "girl (Image 2) on the right both grab the bowl at the same moment and pull it toward "
       "themselves, rice grains scattering, both faces flushed, both whale tails lifting. They "
       "yank the bowl back and forth across the table. Camera static." + _STYLE)

OUT_ROOT = r"<COMFYUI_ROOT>\ComfyUI\output"
STEPS = [8, 12, 16]


def analyze(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    prev, diffs, n = None, [], 0
    while n < 400:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            diffs.append(float(np.abs(g - prev).mean()))
        prev = g
        n += 1
    cap.release()
    if len(diffs) < 8:
        return None
    d = np.array(diffs)
    sp = np.abs(np.fft.rfft(d - d.mean()))
    freq = np.fft.rfftfreq(len(d))
    tot = sp.sum() + 1e-9
    low = sp[freq <= 0.15].sum() / tot          # 低频 = 真实运动的持续推进
    high = sp[freq >= 0.35].sum() / tot         # 高频 = 抖动/闪烁/伪影
    return fps, n, d.mean(), low, high, d.std() / (d.mean() + 1e-9)


def main():
    rows = []
    for st in STEPS:
        os.environ["STEPS"] = str(st)
        E.R.OUT_PREFIX = "steps_%d" % st
        print("\n===== steps=%d =====" % st, flush=True)
        t0 = time.time()
        ok, info, outs = E.R.run_clip(1, SEG, upscale_mp=0)
        el = time.time() - t0
        if not ok:
            print("  FAIL", flush=True)
            continue
        mp4 = os.path.join(OUT_ROOT, "steps_%d" % st, outs[0])
        r = analyze(mp4)
        if not r:
            print("  分析失败", flush=True)
            continue
        fps, n, fd, low, high, jitter = r
        rows.append((st, el, fd, low, high, jitter, mp4))
        print(">> steps=%d  %.0fs  差分=%.2f  低频%.0f%%  高频%.0f%%  抖动指数=%.2f"
              % (st, el, fd, low * 100, high * 100, jitter), flush=True)

    print("\n===== 汇总 =====")
    print("  %-7s %-8s %-9s %-9s %-9s %-9s" % ("steps", "耗时", "差分", "低频%", "高频%", "抖动指数"))
    for st, el, fd, low, high, jit, _ in rows:
        print("  %-7d %-8.0f %-9.2f %-9.1f %-9.1f %-9.2f"
              % (st, el, fd, low * 100, high * 100, jit))
    print("\n判读：低频占比↑ / 高频占比↓ / 抖动指数↓ = 运动更真实、更不\"蠕动\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
