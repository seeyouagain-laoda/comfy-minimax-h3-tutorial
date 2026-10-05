# -*- coding: utf-8 -*-
"""把三视图裁出的正面 → 抠底 → 合成纯白底 2048×2048 参考图

背景是浅灰渐变 + 参考线 + 水印文字；用四角估背景色 + 阈值 + 连通域取最大块（=角色），
水印/文字/参考线都是独立小块，会被自动排除。
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

D = r"<ASSET_DIR>"
OUT_DIR = r"<COMFYUI_ROOT>\ComfyUI\input"
CANVAS = 2048
FILL = 0.86          # 角色占画布高度比例


def process(name, src):
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w = a.shape[:2]
    # 四角估背景色
    corners = np.concatenate([a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3),
                              a[-20:, :20].reshape(-1, 3), a[-20:, -20:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    diff = np.abs(a - bg).max(axis=2)
    fg = diff > 12
    fg = ndimage.binary_opening(fg, np.ones((3, 3)))
    lab, n = ndimage.label(fg)
    if n == 0:
        raise RuntimeError("no foreground")
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    main = (lab == (int(np.argmax(sizes)) + 1))
    print("  components=%d  main=%.1f%%" % (n, 100.0 * main.sum() / (h * w)), flush=True)
    # 🩹 边缘碎片剥离 —— 必须在 closing **之前**！closing 会把碎片与主体之间的
    #    几像素间隙填掉，之后就再也分不开了（本次踩过：7×7 闭运算把邻接视角的头发粘上了）。
    ch = main.sum()
    colsum = main.sum(axis=0)
    _ys = np.where(main.any(axis=1))[0]
    role_h = int(_ys.max() - _ys.min() + 1) if _ys.size else h
    valid = colsum > 0.35 * role_h          # 碎片又窄又矮，主体（含大鲸鳍耳）是连续的
    if valid.sum() > 0:
        segs, s = [], None
        for x, v in enumerate(valid):
            if v and s is None:
                s = x
            elif not v and s is not None:
                segs.append((s, x))
                s = None
        if s is not None:
            segs.append((s, len(valid)))
        if len(segs) > 1:
            segs.sort(key=lambda t: t[1] - t[0], reverse=True)
            keep = segs[0]
            before = int(main.sum())
            main[:, :keep[0]] = False
            main[:, keep[1]:] = False
            print("  边缘碎片剥离：%d 段 → 保留 x[%d,%d)，去掉 %d px"
                  % (len(segs), keep[0], keep[1], before - int(main.sum())), flush=True)

    main = ndimage.binary_closing(main, np.ones((7, 7)))
    main = ndimage.binary_fill_holes(main)
    # 清参考线：整行宽度突增且上下都窄
    rw = main.sum(axis=1)
    killed = 0
    for y in np.where(rw > 0.55 * w)[0]:
        nb = rw[max(0, y - 4):y].max() if y > 0 else 0
        na = rw[y + 1:y + 5].max() if y < len(rw) - 1 else 0
        if max(nb, na) < 0.5 * w:
            main[y, :] = False
            killed += 1
    if killed:
        main = ndimage.binary_fill_holes(main)
    print("  参考线清除 %d 行" % killed, flush=True)

    ys, xs = np.where(main)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb = np.asarray(im).astype(np.float32)
    alpha = (main * 255).astype(np.uint8)
    # 边缘羽化 1px，避免锯齿
    alpha = np.asarray(Image.fromarray(alpha).filter(
        __import__("PIL.ImageFilter", fromlist=["ImageFilter"]).GaussianBlur(0.8)))
    cut = Image.fromarray(np.dstack([rgb.astype(np.uint8), alpha]), "RGBA").crop((x0, y0, x1, y1))
    # 放到白底画布
    scale = (CANVAS * FILL) / cut.height
    nw, nh = max(1, int(cut.width * scale)), int(CANVAS * FILL)
    cut = cut.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (CANVAS, CANVAS), (255, 255, 255))
    canvas.paste(cut, ((CANVAS - nw) // 2, (CANVAS - nh) // 2), cut)
    dst = os.path.join(OUT_DIR, "ref_%s.png" % name)
    canvas.save(dst)
    print("  ✅ %s  bbox=(%d,%d,%d,%d)  ->  %s  (%dx%d)" % (
        name, x0, y0, x1, y1, dst, CANVAS, CANVAS), flush=True)


if __name__ == "__main__":
    for nm in ["深深", "哒哒"]:
        print("== %s" % nm, flush=True)
        process(nm, os.path.join(D, "%s_正面_raw.png" % nm))
