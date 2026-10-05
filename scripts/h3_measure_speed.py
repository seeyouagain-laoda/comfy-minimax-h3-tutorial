# -*- coding: utf-8 -*-
"""量化「动作速度」：B 站正常速度成片 = 基准，对比我们的成片

运动量/秒 = 平均帧间差分(灰度) × fps
"""
import os, sys
import cv2, numpy as np

TARGETS = [
    ("B站基准A", r"<PROJECT_DIR>\refs\ref_bilibili_sample.mp4"),
    ("B站基准B", r"<PROJECT_DIR>\refs\ref_bilibili_sample.mp4"),
    ("EP04第1段 原速", r"<ASSET_DIR>\ep04_clip1_0-10s.mp4"),
    ("EP04 20s 原速", r"<ASSET_DIR>\ep04_clip1_0-10s.mp4"),
    ("EP04 20s 1.5x", r"<ASSET_DIR>\ep04_20s_1.5x.mp4"),
]


def measure(path, max_frames=600):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    prev, diffs, n = None, [], 0
    while n < max_frames:
        ok, fr = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            diffs.append(float(np.abs(g - prev).mean()))
        prev = g
        n += 1
    cap.release()
    if not diffs:
        return None
    return fps, n, sum(diffs) / len(diffs)


print("运动量/秒 = 平均帧间差分 × fps   （越大 = 动作越快）\n")
print("%-24s %7s %7s %11s %12s" % ("素材", "fps", "帧数", "帧间差分", "运动量/秒"))
print("-" * 66)
rows = []
for name, p in TARGETS:
    if not os.path.exists(p):
        continue
    r = measure(p)
    if not r:
        print("%-24s  读取失败" % name)
        continue
    fps, n, fd = r
    spd = fd * fps
    rows.append((name, fps, n, fd, spd))
    print("%-24s %7.2f %7d %11.2f %12.1f" % (name, fps, n, fd, spd))

if len(rows) >= 2:
    base = rows[0][4]
    print("\n相对 B 站基准（%s = %.1f）：" % (rows[0][0], base))
    for name, fps, n, fd, spd in rows[1:]:
        if spd <= 0:
            continue
        print("  %-24s %.2fx   → 需 %.2f 倍速才等速" % (name, spd / base, base / spd))
