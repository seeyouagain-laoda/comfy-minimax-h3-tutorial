#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""三视图 → 参考图（裁正面 + 抠底 + 边缘碎片剥离 + 白底 2048）

用法：
    pip install opencv-python-headless numpy pillow scipy
    python make_ref.py --src three_view.png --out ref_charA
    python make_ref.py --src three_view.png --out ref_charA --lo 0.40 --hi 0.62

参数
----
    --lo / --hi   裁剪窗口（占原图宽度的比例）。⚠️ 不能对称取中间！
                   三视图中间格**不一定是正面**（同一作者不同角色可能中间是侧面），
                   先用 --dry 看裁出来的图再决定。
    --canvas      输出画布边长（默认 2048）
    --fill        角色占画布高度比例（默认 0.86）
    --bg-thresh   背景色差阈值（默认 12）
    --dry         只裁剪不抠底，用来确认裁剪窗口对不对

规格要求
--------
    2048×2048 · 纯白底 · 不透明 · 单人全身正面 · 含耳朵和尾巴

三个坑（都踩过）
--------------
    ① 裁剪窗口不能对称取中间
    ② binary_closing 会填掉碎片与主体之间的间隙 → 碎片必须在 closing **之前**剥离
    ③ 剥离阈值用「角色高度」的倍数，不是平均宽度（用平均宽度会失效）
"""
import argparse
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter


def crop_front(src, dst, lo, hi, dry=False):
    im = Image.open(src).convert("RGB")
    W, H = im.size
    c = im.crop((int(W * lo), 0, int(W * hi), H))
    c.save(dst)
    print("裁剪 %s -> %s  %s  (原图 x %d..%d)" % (src, os.path.basename(dst), c.size,
                                              int(W * lo), int(W * hi)))
    if dry:
        print("DRY：只裁剪。请目视确认中间是**正面**且左右没有邻居碎片，再跑正式抠底。")
    return dst


def cutout(path, out_path, canvas=2048, fill=0.86, bg_thresh=12, stretch=False):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w = a.shape[:2]
    from scipy import ndimage

    corners = np.concatenate([a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3),
                              a[-20:, :20].reshape(-1, 3), a[-20:, -20:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    fg = np.abs(a - bg).max(axis=2) > bg_thresh
    fg = ndimage.binary_opening(fg, np.ones((3, 3)))

    lab, n = ndimage.label(fg)
    if n == 0:
        raise RuntimeError("没找到前景，检查 --bg-thresh")
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    main = (lab == (int(np.argmax(sizes)) + 1))

    # 坑②：碎片剥离必须在 closing 之前（closing 会桥接几像素间隙）
    ys = np.where(main.any(axis=1))[0]
    role_h = int(ys.max() - ys.min() + 1)
    colsum = main.sum(axis=0)
    valid = colsum > 0.35 * role_h
    if valid.sum() > 0:
        segs, s = [], None
        for x, v in enumerate(valid):
            if v and s is None:
                s = x
            elif not v and s is not None:
                segs.append((s, x)); s = None
        if s is not None:
            segs.append((s, len(valid)))
        if len(segs) > 1:
            segs.sort(key=lambda t: t[1] - t[0], reverse=True)
            keep = segs[0]
            main[:, :keep[0]] = False
            main[:, keep[1]:] = False
            print("  边缘碎片剥离：%d 段 → 保留 x[%d,%d)" % (len(segs), keep[0], keep[1]))

    main = ndimage.binary_closing(main, np.ones((7, 7)))
    main = ndimage.binary_fill_holes(main)

    # 清参考线：整行宽度突增、上下都窄
    rw = main.sum(axis=1)
    for y in np.where(rw > 0.55 * w)[0]:
        nb = rw[max(0, y - 4):y].max() if y > 0 else 0
        na = rw[y + 1:y + 5].max() if y < len(rw) - 1 else 0
        if max(nb, na) < 0.5 * w:
            main[y, :] = False
    main = ndimage.binary_fill_holes(main)

    ys, xs = np.where(main)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb = np.asarray(im).astype(np.uint8)
    alpha = np.asarray(Image.fromarray((main * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(0.8)))
    cut = Image.fromarray(np.dstack([rgb, alpha]), "RGBA").crop((x0, y0, x1, y1))

    nh = int(canvas * fill)
    nw = max(1, int(cut.width * (nh / cut.height)))
    cut = cut.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGB", (canvas, canvas), (255, 255, 255))
    out.paste(cut, ((canvas - nw) // 2, (canvas - nh) // 2), cut)
    out.save(out_path)
    print("✅ %s  %dx%d  （放到 ComfyUI 的 models/input/）" % (out_path, canvas, canvas))
    print("   验证：生成耗时若 +50~75%，说明参考图真接上了（见 README §5.3）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True, help="输出文件名（不含扩展名）")
    ap.add_argument("--lo", type=float, default=0.355)
    ap.add_argument("--hi", type=float, default=0.645)
    ap.add_argument("--canvas", type=int, default=2048)
    ap.add_argument("--fill", type=float, default=0.86)
    ap.add_argument("--bg-thresh", type=int, default=12)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    raw = a.out + "_raw.png"
    crop_front(a.src, raw, a.lo, a.hi, a.dry)
    if a.dry:
        return 0
    cutout(raw, a.out + ".png", a.canvas, a.fill, a.bg_thresh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
