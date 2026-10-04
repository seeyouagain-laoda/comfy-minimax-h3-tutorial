#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测量视频的「动作速度」—— 用来判断"看起来慢"到底是不是真的慢

用法：
    pip install opencv-python-headless numpy
    python measure_speed.py clip.mp4 [more.mp4 ...]
    python measure_speed.py --bench normal_short.mp4 ours.mp4     # 拿正常片当基准算相对倍数

指标
----
    帧间差分     相邻帧灰度绝对差的平均 → 画面变化量（**大 ≠ 快**，抖动也会大）
    运动量/秒    帧间差分 × fps → 每秒累计变化量
    低频占比     对差分序列做 FFT，低频(<0.15Hz)能量占比 → **越高 = 运动越平滑**
                 高频占比高 = 抖动/伪影（观感是"原地蠕动"，用户会说是"慢"）

⚠️ 本工具只能给**参考**。查"慢"的正确顺序是
   ① 分镜单镜时长 → ② 后期变速 → ③ 步数 → ④ LoRA。先查分镜。
"""
import os
import sys

import cv2
import numpy as np

MAX_FRAMES = 600


def measure(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    prev, diffs, n = None, [], 0
    while n < MAX_FRAMES:
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
    d = np.asarray(diffs)
    sp = np.abs(np.fft.rfft(d - d.mean()))
    fr = np.fft.rfftfreq(len(d))
    tot = sp.sum() + 1e-9
    return dict(fps=fps, frames=total, diff=float(d.mean()),
                low=float(sp[fr <= 0.15].sum() / tot),
                high=float(sp[fr >= 0.35].sum() / tot))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    bench = "--bench" in sys.argv
    if not args:
        print(__doc__)
        return 2

    print("%-34s %7s %7s %10s %12s %9s %9s" %
          ("文件", "fps", "帧数", "帧间差分", "运动量/秒", "低频%", "高频%"))
    print("-" * 96)
    rows = []
    for p in args:
        if not os.path.exists(p):
            print("%-34s  (不存在)" % os.path.basename(p))
            continue
        r = measure(p)
        if not r:
            print("%-34s  读取失败" % os.path.basename(p))
            continue
        r["path"] = p
        r["spd"] = r["diff"] * r["fps"]
        rows.append(r)
        print("%-34s %7.2f %7d %10.2f %12.1f %9.0f %9.0f" %
              (os.path.basename(p)[:34], r["fps"], r["frames"], r["diff"], r["spd"],
               r["low"] * 100, r["high"] * 100))

    if bench and len(rows) >= 2:
        b = rows[0]
        print("\n相对基准 %s（运动量/秒 = %.1f，低频占比 = %.0f%%）："
              % (os.path.basename(b["path"]), b["spd"], b["low"] * 100))
        for r in rows[1:]:
            if r["spd"] > 0:
                print("  %-34s 运动量 %.2fx  → 需 %.2f 倍速才等速"
                      % (os.path.basename(r["path"])[:34], r["spd"] / b["spd"],
                         b["spd"] / r["spd"]))
        print("\n判读：差分大但低频占比低 = 抖动为主（观感『原地蠕动』），"
              "先查步数/LoRA 格式；差分小 = 画面真的不动。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
