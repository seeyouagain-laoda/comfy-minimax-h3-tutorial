#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A/B 对拍：同 seed / 同提示词 / 同参考图，只改一个变量，用来判断"换模型/换步数值不值"。

为什么需要它
------------
本机实测教训：某社区剪枝版底模体积小 40%、速度快 43%，看着是明显收益，
但同参数对拍出来的画面是**一团模糊色块、角色完全消失**。
如果只看"体积小 + 速度快"就换，会把好模型换掉。
**任何"参数看起来更优"的改动，先对拍再决定。**

用法
----
    # 步数对拍：8 / 12 / 16 步，各跑 3 秒
    python steps_ab.py --steps 8 12 16

    # 底模对拍：两个模型文件各跑一次
    python steps_ab.py --models a.safetensors b.safetensors

    # 起停 ComfyUI 时带上
    python steps_ab.py --steps 8 16 --seconds 3 --width 864 --height 480
    python steps_ab.py --models a.safetensors b.safetensors --prompt "a chibi girl"

依赖
----
    只需 ComfyUI 在 127.0.0.1:8188 运行。不依赖任何第三方节点包、不依赖外部工作流 JSON。
    本脚本直接构造 **API 格式** 的图（不是 GUI 格式），所以换机器不用改任何东西。
"""
import json
import os
import sys
import time
import urllib.request

HOST = os.environ.get("COMFY_HOST", "http://127.0.0.1:8188")
OP = {"NO_PROXY": "*", "no_proxy": "*"}


# ---------- 帧数对齐（与官方公式一致） ----------
def align_frames(sec, fps=24):
    n = max(5, round(sec * fps))
    return n + (5 - n % 17) % 17


# ---------- 最小 API 图：只用官方内置节点 ----------
def build(unet, steps, seconds, width, height, prompt, ref_image=None, seed=1):
    frames = align_frames(seconds)
    n = {}

    n["1"] = {"class_type": "UNETLoader",
              "inputs": {"unet_name": unet, "weight_dtype": "default"}}
    n["2"] = {"class_type": "CLIPLoader",
              "inputs": {"clip_name": os.environ.get(
                  "CLIP_NAME", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
                  "type": "minimax", "device": "default"}}
    n["3"] = {"class_type": "VAELoader",
              "inputs": {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"}}
    n["4"] = {"class_type": "VAELoader",
              "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}}

    n["5"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}}
    n["6"] = {"class_type": "BasicScheduler",
              "inputs": {"schedule": "simple", "steps": steps, "denoise": 1.0}}
    n["7"] = {"class_type": "RandomNoise",
              "inputs": {"noise_seed": seed, "control": "fixed"}}

    latent_in = "8"
    n["8"] = {"class_type": "EmptyMiniMaxH3LatentAV",
              "inputs": {"width": width, "height": height, "length": frames,
                         "batch_size": 1, "fps": 24}}

    gen = "9"
    if ref_image:
        n["10"] = {"class_type": "LoadImage", "inputs": {"image": ref_image, "upload": "image"}}
        n[gen] = {"class_type": "MiniMaxH3ReferenceToVideo",
                  "inputs": {"width": width, "height": height, "length": frames,
                             "prompt": prompt,
                             "ref_images": ["10", 0],
                             "ref_image_size": "max",
                             "ref_videos": [], "ref_audios": []}}
    else:
        n[gen] = {"class_type": "MiniMaxH3ImageToVideo",
                  "inputs": {"width": width, "height": height, "length": frames,
                             "prompt": prompt, "fps": 24}}

    n["11"] = {"class_type": "VAEDecode",
               "inputs": {"samples": [gen, 0], "vae": ["3", 0]}}
    n["12"] = {"class_type": "CreateVideo",
               "inputs": {"frame_rate": 24, "codec": "8", "pix_fmt": "yuv420p",
                          "video": ["11", 0]}}
    n["13"] = {"class_type": "SaveVideo",
               "inputs": {"video": ["11", 0], "filename_prefix": "ab", "format": "mp4"}}

    # SamplerCustomAdvanced：噪声/采样器/sigmas/latent/条件
    n["20"] = {"class_type": "SamplerCustomAdvanced",
               "inputs": {"noise": ["7", 0], "guider": ["21", 0],
                          "sampler": ["5", 0], "sigmas": ["6", 0],
                          "latent_image": [latent_in, 0], "conditioning": [gen, 0]}}
    n["21"] = {"class_type": "BasicGuider", "inputs": {}}
    return n


# ---------- 提交与等待 ----------
def queue(prompt, client_id="abtest"):
    data = json.dumps({"prompt": prompt, "client_id": client_id}).encode()
    req = urllib.request.Request(HOST + "/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=60)
    return json.loads(r.read().decode())


def wait(pid, timeout=3600):
    t0 = time.time()
    seen = 0
    while time.time() - t0 < timeout:
        try:
            h = json.loads(urllib.request.urlopen(HOST + "/history/" + pid,
                                                  timeout=20).read().decode())
        except Exception:
            time.sleep(2); continue
        if pid in h:
            v = h[pid]
            st = v.get("status", {})
            if st.get("status_str") in ("success", "error"):
                return v
        q = json.loads(urllib.request.urlopen(HOST + "/queue", timeout=20).read().decode())
        run = q.get("queue_running") or []
        cur = q.get("queue_pending") or []
        txt = "exec" if any(str(pid) in json.dumps(x) for x in run) else \
              ("wait" if cur else "?")
        if txt != seen:
            print("    [%s] %.0fs" % (txt, time.time() - t0), flush=True)
            seen = txt
        time.sleep(2)
    return None


def log_line_count():
    """读 ComfyUI 控制台日志行数，用于分辨本次运行新增的 warning。"""
    p = os.environ.get("COMFY_LOG")
    if not p or not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return None


def log_new_lines(n0):
    p = os.environ.get("COMFY_LOG")
    if not p or n0 is None or not os.path.exists(p):
        return []
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()[n0:]
    except Exception:
        return []


def outputs_of(hist):
    out = []
    for nid, o in (hist.get("outputs") or {}).items():
        for key in ("video", "videos", "gifs", "images"):
            for it in (o.get(key) or []):
                if isinstance(it, dict) and it.get("filename"):
                    out.append(it.get("filename"))
    return out


def run_one(tag, unet, steps, args):
    print("\n=== %s | steps=%s ===" % (tag, steps), flush=True)
    prompt = build(unet, steps, args["seconds"], args["width"], args["height"],
                   args["prompt"], args["ref"], args["seed"])
    n0 = log_line_count()
    t0 = time.time()
    try:
        res = queue(prompt)
    except Exception as e:
        print("  提交失败:", e)
        return None
    if "error" in res:
        print("  图有错:", json.dumps(res["error"], ensure_ascii=False)[:600])
        return None
    pid = res.get("prompt_id")
    hist = wait(pid)
    if not hist:
        print("  超时")
        return None
    st = hist.get("status", {})
    if st.get("status_str") != "success":
        print("  执行失败:", json.dumps(st.get("messages", [{}])[-1],
                                          ensure_ascii=False)[:600])
        return None
    outs = outputs_of(hist)
    # LoRA/权重静默失效自查：只看本次新增的日志行
    new = log_new_lines(n0)
    lora_bad = [l for l in new if "lora key not loaded" in l]
    if lora_bad:
        print("  ⚠️ 本次 LoRA 有 %d 个 key 未加载（格式不兼容，等于没挂）" % len(lora_bad))
    if n0 is not None:
        print("  本次日志新增 %d 行" % len(new))
    print("  ✅ %.0fs  输出: %s" % (time.time() - t0, outs or "(在 output/ 目录)"))
    return {"tag": tag, "steps": steps, "unet": unet,
            "seconds": round(time.time() - t0), "outputs": outs}


def main():
    args = {"steps": [], "models": [], "seconds": 3.0, "width": 864, "height": 480,
            "seed": 1, "ref": None,
            "prompt": ("integrated_multimodal_description: A close-up of a white bowl of "
                       "steamed rice on a wooden table, steam rising. Hand-drawn 2D anime, "
                       "clean line art, flat cel shading, warm indoor light. "
                       "overall_soundscape: quiet room ambience. non_diegetic_music: N/A")}

    a = sys.argv[1:]
    i = 0
    while i < len(a):
        k = a[i]
        if k == "--steps":
            j = i + 1
            while j < len(a) and not a[j].startswith("--"):
                j += 1
            args["steps"] = [int(x) for x in a[i + 1:j]]; i = j
        elif k == "--models":
            j = i + 1
            while j < len(a) and not a[j].startswith("--"):
                j += 1
            args["models"] = a[i + 1:j]; i = j
        elif k.startswith("--") and k[2:] in args:
            args[k[2:]] = float(a[i + 1]) if k in ("--seconds", "--width",
                                                   "--height") else a[i + 1]
            i += 2
        else:
            i += 1

    if not args["steps"] and not args["models"]:
        print(__doc__)
        return 2
    if args["models"]:
        unets = args["models"]
        steps_list = args["steps"] or [8]
    else:
        unets = [os.environ.get("UNET_NAME",
                                "minimax_h3_fl2va_pruned_int8_convrot.safetensors")]
        steps_list = args["steps"]

    print("待跑 %d 组 | %.0fs/条 | %dx%d | seed=%d | 参考图=%s"
          % (len(unets) * len(steps_list), args["seconds"], args["width"],
             args["height"], args["seed"], args["ref"] or "无"))

    results = []
    for unet in unets:
        for s in steps_list:
            r = run_one(os.path.basename(unet)[:28], unet, s, args)
            if r:
                results.append(r)

    print("\n===== 汇总（人工看画质，秒数只是参考）=====")
    print("%-30s %6s %9s" % ("变量", "步数", "耗时"))
    for r in results:
        print("%-30s %6s %8ds" % (r["tag"], r["steps"], r["seconds"]))
    print("\n产物在 ComfyUI 的 output/ 目录，请逐个打开看画质再决定。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
