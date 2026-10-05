# -*- coding: utf-8 -*-
"""H3 故事链统一 runner：一次跑完整条片（多段接续 + 可选二采放大 + 自动拼接 + 质检）。

用法：
  # 内置 2 段示例（深深·白饭保卫战）
  python h3_story.py

  # 从 JSON 故事板跑（推荐）
  python h3_story.py story.json 1.0
    story.json 形如：
    { "title": "深深的家 EP01",
      "upscale_mp": 1.0,
      "base_prompt": "(可选，覆盖公共段)",
      "segments": [ "第1段分镜提示词", "第2段提示词（开头先复述上段结尾）", "..." ] }

  # 只跑前 N 段 / 跳过拼接
  python h3_story.py story.json 1.0 --only 2
  python h3_story.py story.json 0   --no-concat      # 0 = 不放大

要点（已封在流程里）：
  * 每段生成完立刻落盘 latent（h3_context/clip_0000N.safetensors）+ 提示词存档
  * 第 2 段起自动 LoadLatent(N-1) + MotionContext + Trim（Trim 剪掉 22 帧钉子头）
  * 输出直接首尾相接即可（钉子头已剪掉），无需再对齐
  * UPSCALE_MP > 0 时每段都走「一采 → latent 放大 → 二采」，SaveLatent 仍取放大前 latent，接缝不变
  * 每段结束自动查 LoRA 是否静默失效
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import h3_motion_context_chain as CH          # noqa: E402

FF = r"D:\APP\ffmpeg\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
PROBE = r"<AGENT_SCRIPTS>\h3_video_probe.py"
VP = r"<COMFYUI_ROOT>\ComfyUI\.venv\Scripts\python.exe"
OUTDIR = r"<COMFYUI_ROOT>\ComfyUI\output\shenshen_chain"
DESK = r"<ASSET_DIR>"

DEMO = {
    "title": "深深的家 EP01 白饭保卫战",
    "upscale_mp": 1.0,
    "segments": [
        "[Shot 1] A bright room in an ordinary home, seen in a medium shot. The chibi whale-girl "
        "maid stands beside a low wooden table with a big bowl of steamed rice in front of her, "
        "gazing at it with wide, delighted eyes. She lifts the bowl with both hands and breathes in "
        "the steam, twin-tails swaying, tail wagging. She sits down on the floor cushion and starts "
        "eating happily, cheeks puffing out with each bite. Warm afternoon light falls across the "
        "wooden floor. The camera slowly pushes in and settles on her face.",

        "[Shot 1] The chibi whale-girl maid sits on the floor cushion in the warm living room, both "
        "hands holding the big white bowl of steamed rice up to her mouth, eyes closed and cheeks "
        "puffed, still chewing — the same girl, the same bowl, the same cushion and the same warm "
        "afternoon light as the previous clip ended. She holds that beat, swallows, and lets out a "
        "small satisfied sigh, twin-tails settling and the whale tail curling. "
        "[Shot 2] At 00:02.000, she opens her eyes, sets the bowl down on the low wooden table and "
        "stands up, then walks to the window and looks out, one small hand resting on the sill, tail "
        "wagging slowly. Warm light falls across the wooden floor. The camera pulls back and slightly "
        "up to include the sofa and the window.",
    ],
}


def load_story(path):
    if not path:
        return DEMO
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def concat(files, out):
    lst = os.path.join(OUTDIR, "_concat_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in files:
            f.write("file '%s'\n" % p.replace("\\", "/"))
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out],
                   check=True, capture_output=True)
    return out


def probe(path):
    r = subprocess.run([VP, PROBE, path], capture_output=True, text=True, errors="replace")
    return r.stdout.strip()


def sheet(path, out, cols=4, rows=2, step=None):
    n = 226
    try:
        r = subprocess.run([FF, "-i", path], capture_output=True, text=True, errors="replace")
        for line in r.stderr.splitlines():
            if "Duration" in line:
                import re
                m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", line)
                if m:
                    sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
                    n = max(1, int(sec * 24))
                break
    except Exception:
        pass
    st = step or max(1, n // (cols * rows))
    subprocess.run([FF, "-y", "-i", path, "-vf",
                    "select='not(mod(n\\,%d))',scale=340:-1,tile=%dx%d" % (st, cols, rows),
                    "-frames:v", "1", out], capture_output=True)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    story = load_story(args[0] if args else None)
    mp = float(args[1]) if len(args) > 1 else float(story.get("upscale_mp", 0) or 0)
    only = None
    if "--only" in flags:
        only = int(flags[flags.index("--only") + 1]) if len(flags) > flags.index("--only") + 1 else 1
    no_concat = "--no-concat" in flags

    segs = story["segments"][:only] if only else story["segments"]
    title = story.get("title", "H3 故事链")
    if story.get("base_prompt"):
        CH.BASE_PROMPT = story["base_prompt"]

    print("=" * 88)
    print("## %s" % title)
    print("   段数 %d | 二采放大 %s | 画布 %sx%s | 每段 %d 帧"
          % (len(segs), ("%g MP" % mp) if mp > 0 else "关",
             os.environ.get("W", "864"), os.environ.get("H", "480"), 124))
    print("=" * 88)

    outs, t_all = [], time.time()
    for i, seg in enumerate(segs, 1):
        print("\n--- clip %d/%d ---" % (i, len(segs)))
        t0 = time.time()
        ok, info, files = CH.run_clip(i, seg, upscale_mp=mp, quiet=True)
        print("   耗时 %.0fs" % (time.time() - t0))
        if not ok:
            print("❌ clip %d 失败，中止" % i)
            return 1
        # 取本段最新产物（同名会自增编号）
        cands = [f for f in files if f.endswith(".mp4")]
        if not cands:
            print("❌ clip %d 没拿到 mp4" % i)
            return 1
        outs.append(cands[0])

    if no_concat or len(outs) < 2:
        print("\n== 完成（未拼接）==")
        for o in outs:
            print("  ", o)
        return 0

    print("\n== 拼接 ==")
    final = concat(outs, os.path.join(OUTDIR, "STORY_final.mp4"))
    print("   ", final)
    print("\n== 质检 ==")
    print(probe(final))

    base = title.replace(" ", "_").replace("/", "_")
    dst = os.path.join(DESK, "%s_%ds.mp4" % (base, 0))
    try:
        import shutil
        shutil.copy(final, os.path.join(DESK, "%s_成片.mp4" % base))
        shutil.copy(outs[0], os.path.join(DESK, "%s_第1段.mp4" % base))
        sheet(final, os.path.join(DESK, "%s_全程8帧.jpg" % base))
        print("   已拷到桌面：%s_成片.mp4 / _第1段.mp4 / _全程8帧.jpg" % base)
    except Exception as e:
        print("   (拷桌面失败:", e, ")")
    print("\n总耗时 %.0f 分钟" % ((time.time() - t_all) / 60))
    return 0


if __name__ == "__main__":
    sys.exit(main())
