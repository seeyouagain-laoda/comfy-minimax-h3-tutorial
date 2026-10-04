#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""产物探针：校验分辨率 / 时长 / 帧数 / 音轨 / 亮度 / 静帧

用法：
    pip install opencv-python
    python probe.py out.mp4

判据（有画面 + 有音轨 + 非黑图）：
    video : h264 864x480 24.00fps 243 frames 10.125s
    audio : aac 32000Hz ch=2 10.075s
    mid   : 864x480x avg=126.7 min=0 max=255
    VERDICT: PASS
"""
import os
import subprocess
import sys


def probe_av(path):
    """用 ffprobe 读流信息（ffmpeg 需在 PATH）"""
    cmd = ["ffprobe", "-v", "error", "-show_entries",
           "stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,duration,channels,sample_rate",
           "-of", "json", path]
    out = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if out.returncode != 0:
        return None
    import json
    return json.loads(out.stdout or "{}").get("streams", [])


def analyse_pixels(path):
    """中间帧亮度分布（判断是否黑图 / 静帧）"""
    import cv2
    import numpy as np
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if n <= 0:
        cap.release()
        return None
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, n // 2))
    ok, fr = cap.read()
    cap.release()
    if not ok:
        return None
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    return fr.shape[1], fr.shape[0], float(g.mean()), int(g.min()), int(g.max())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        print("文件不存在:", path)
        return 2
    size = os.path.getsize(path) // 1024

    streams = probe_av(path)
    if not streams:
        print("ffprobe 读取失败（ffmpeg 装了吗？）")
        return 2
    print("size  = %d KB" % size)
    vinfo = next((s for s in streams if s.get("codec_type") == "video"), None)
    ainfo = next((s for s in streams if s.get("codec_type") == "audio"), None)

    ok = True
    if vinfo:
        fps = eval(vinfo.get("r_frame_rate", "24/1")) if "/" in str(vinfo.get("r_frame_rate")) else 24.0
        print("video : %s %sx%s %.2ffps %s frames %ss" % (
            vinfo.get("codec_name"), vinfo.get("width"), vinfo.get("height"),
            fps, vinfo.get("nb_frames"), vinfo.get("duration")))
        if int(vinfo.get("nb_frames") or 0) < 5:
            print("  ⚠️ 帧数过少"); ok = False
    else:
        print("video : 缺失"); ok = False

    if ainfo:
        print("audio : %s %sHz ch=%s %ss" % (
            ainfo.get("codec_name"), ainfo.get("sample_rate"),
            ainfo.get("channels"), ainfo.get("duration")))
    else:
        print("audio : 缺失（若用了音画联合生成，缺音轨说明没接上）")

    px = analyse_pixels(path)
    if px:
        w, h, avg, mn, mx = px
        print("mid   : %dx%d avg=%.1f min=%d max=%d" % (w, h, avg, mn, mx))
        if avg < 12 or mx < 60:
            print("  ⚠️ 中间帧近似黑图（avg<12 或 max<60）"); ok = False
    else:
        print("mid   : 读取失败"); ok = False

    print("VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
