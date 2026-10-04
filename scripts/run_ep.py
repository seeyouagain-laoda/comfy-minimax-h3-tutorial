#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MiniMax-H3 短剧生成 runner（通用版 · 跨机器）

在 ComfyUI 的社区工作流（ref2v 接续版）基础上打补丁，实现：
  · 多段接续（Motion Context latent 钉帧，音画零漂移）
  · 单角色 / 双角色（两张参考图）
  · 可选二采放大（1 MP）
  · 干跑预检（不烧显存）

用法
----
    export COMFY_ROOT=/path/to/ComfyUI
    export H3_WORKFLOW=/path/to/ref2v_workflow.json     # 见 README §3
    export H3_SCRIPTS=/path/to/h3-video-guide/scripts

    python run_ep.py --dry                     # 干跑：只转换不提交，逐行核对接线
    python run_ep.py --clip 1                  # 跑第 1 段
    python run_ep.py --clip 2                  # 跑第 2 段（自动接 latent）
    python run_ep.py --clip 1 --upscale 1.0    # 带二采放大到 1 MP

命令行参数
----------
    --clip N        跑第几段（默认 1）
    --seconds S     每段秒数（默认 10）
    --ref A.png     角色 A 参考图（放 ComfyUI 的 models/input/）
    --ref2 B.png    角色 B 参考图（双角色时传）
    --upscale MP    >0 启用二采放大（0.4 → 1.0）
    --seed N        随机种子
    --mp N          画布百万像素（默认 0.4；12GB 显存降到 0.3，不要低于 0.25）
    --dry           只转换不提交
    --out PREFIX    输出前缀（默认 h3_ep）

接线要点（已踩过的坑，改动前先读 README §7）
------------------------------------------------
    ① MultiImageLoader.image_paths 永远写两行 —— 只写 1 行时 slot 2 是 64×64 全黑图，
       参考图从未生效，角色会变成「照文字画的」。
    ② 191(MiniMaxH3ReferenceToVideo).ref_image_0 必须接 336 的 **slot 1**。
    ③ 双角色时再建一条 link 把 336.slot 2 接到 191.ref_images.ref_image_1（target_slot=4）。
    ④ 二采放大必须换**不钉帧的 guider**（钉帧条件是分辨率锁定的）。
"""

import argparse
import json
import os
import sys
import time

# ---------------------------------------------------------------- 路径（全部环境变量化）
COMFY_ROOT = os.environ.get("COMFY_ROOT", "")
WORKFLOW = os.environ.get("H3_WORKFLOW", "")
COMFY_HELPER = os.environ.get("H3_COMFY_HELPER", "")   # 含 convert_ui_to_api / direct_submit 的模块
LOG_FILE = os.environ.get("H3_LOG", "")

# 模型名（按你本机 models/ 下实际的改）
UNET = os.environ.get("H3_UNET", "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors")
CLIP = os.environ.get("H3_CLIP", "qwen3vl_32b_minimax_h3_int8_convrot.safetensors")
VAE_V = os.environ.get("H3_VAE_VIDEO", "minimax_h3_video_vae_int8_convrot.safetensors")
VAE_A = os.environ.get("H3_VAE_AUDIO", "minimax_h3_audio_vae_fp32.safetensors")
# 🔴 必须是 _comfyui_ 格式那份，diffusers 命名格式会被 ComfyUI 静默丢弃（README §7.2）
LORA = os.environ.get("H3_LORA", "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors")
UPSCALE_W = os.environ.get("H3_UPSCALE_W",
                           "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors")

# 公共段模板：把 BASE_PROMPT / SEGMENT 换成你自己的
BASE_PROMPT = os.environ.get("H3_BASE_PROMPT", "")
SEG = os.environ.get("H3_SEGMENT", "")

REF_SIZE = int(os.environ.get("H3_REF_SIZE", "2048"))


def die(msg):
    print("[ERROR] " + msg, file=sys.stderr)
    sys.exit(1)


def load_helper():
    """载入提供 ComfyUI API 转换/提交能力的模块。"""
    if not COMFY_HELPER:
        die("未设置 H3_COMFY_HELPER（提供 convert_ui_to_api / direct_submit 的 python 模块）")
    sys.path.insert(0, os.path.dirname(os.path.abspath(COMFY_HELPER)))
    mod_name = os.path.splitext(os.path.basename(COMFY_HELPER))[0]
    return __import__(mod_name)


def patch_workflow(wf, clip_index, ref1, ref2, seconds, seed, mp, upscale_mp, out_prefix):
    for n in wf["nodes"]:
        nid = str(n.get("id"))
        t = n.get("type")
        wv = n.get("widgets_values")

        # ---- 参考图：永远两行（①） ----
        if t == "MultiImageLoader":
            wv[0] = "%s\n%s" % (ref1, ref2 or ref1)
            wv[1] = wv[2] = REF_SIZE

        # ---- 公共段 / 分镜提示词 ----
        if t == "Text Multiline":
            n["type"] = "PrimitiveStringMultiline"   # 避免依赖 was-node-suite
        if nid == "220" and wv is not None:
            wv[0] = BASE_PROMPT
        if nid == "277" and wv is not None:
            wv[0] = SEG

        # ---- 时长 / 画布 / 输出前缀 ----
        if nid == "216":
            wv[0] = float(seconds)
        if nid == "217":
            wv[0] = "16:9 (Widescreen)"
            wv[1] = float(mp)
        if nid == "255":
            wv[0] = "%s/clip%d" % (out_prefix, clip_index)
        if nid == "354":
            wv[0] = int(seed) + clip_index

        # ---- 接续三件套：首段 bypass，后续 ON ----
        on = clip_index > 1
        if nid == "237":
            n["mode"] = 0 if on else 4
            wv[0] = "22"          # context_length（≈0.92s）
            wv[1] = "24"          # audio_context_length
        if nid == "202":
            n["mode"] = 0 if on else 4
            wv[0] = "h3_context"
            wv[1] = clip_index - 1
        if nid == "213":
            n["mode"] = 0 if on else 4
        if nid == "218":
            wv[0] = "h3_context/clip"
            wv[1] = clip_index

    # ---- ② 第一个参考图槽接 slot 1 ----
    for l in wf.get("links", []):
        if isinstance(l, (list, tuple)) and len(l) >= 6 and l[1] == 336 and l[3] == 191:
            if l[2] != 1:
                l[2] = 1

    # ---- ③ 双角色：新建 link 把 slot 2 接到 ref_image_1 ----
    if ref2:
        links = wf.setdefault("links", [])
        new_id = max([l[0] for l in links if isinstance(l, (list, tuple)) and l] or [0]) + 1
        for n in wf["nodes"]:
            if str(n.get("id")) == "191":
                for inp in (n.get("inputs") or []):
                    if inp.get("name") == "ref_images.ref_image_1":
                        inp["link"] = new_id
        links.append([new_id, 336, 2, 191, 4, "IMAGE"])
    return wf


def fix_api(api, upscale_mp):
    """底模/LoRA 改配 + 二采放大（④）"""
    if "39" in api:                       # HybridLoader → 单模型（本机 key 前缀不同会报不一致）
        api["39"] = {"class_type": "UNETLoader",
                     "inputs": {"unet_name": UNET, "weight_dtype": "default"}}
    if "339" in api:
        api["339"]["inputs"]["unet_name"] = UNET
    if "238" in api:
        api["238"]["inputs"]["lora_name"] = LORA
        api["238"]["inputs"]["strength_model"] = 1.0

    # 摘掉只有前端实现、没有后端注册的节点（否则校验失败）
    try:
        oi = cc.get_object_info()
    except Exception:
        oi = {}
    for k in list(api.keys()):
        ct = api[k].get("class_type")
        if oi and ct not in oi:
            del api[k]

    if upscale_mp > 0 and "245:210" in api:
        api["U1"] = {"class_type": "LTXVSeparateAVLatent",
                     "inputs": {"av_latent": ["245:210", 0]}}
        api["U2"] = {"class_type": "MinimaxH3LatentUpscaler3D",
                     "inputs": {"latent": ["U1", 0], "model_name": UPSCALE_W,
                                "mode": "megapixels", "mode.megapixels": upscale_mp,
                                "align": 32, "enable_temporal_chunking": True,
                                "force_unload": False, "device": "cuda", "precision": "bf16"}}
        api["U3"] = {"class_type": "LTXVConcatAVLatent",
                     "inputs": {"video_latent": ["U2", 0], "audio_latent": ["U1", 1]}}
        api["U6"] = {"class_type": "ManualSigmas",
                     "inputs": {"sigmas": "0.9231, 0.8780, 0.8000, 0.6316, 0.3158, 0.0000"}}
        # 🔴 ④ 二采必须用「不钉帧」的 guider —— 钉帧条件按一采分辨率写死
        api["U5"] = {"class_type": "BasicGuider",
                     "inputs": {"model": ["308", 0], "conditioning": ["191", 0]}}
        api["U4"] = {"class_type": "SamplerCustomAdvanced",
                     "inputs": {"noise": ["245:206", 0], "guider": ["U5", 0],
                                "sampler": ["245:208", 0], "sigmas": ["U6", 0],
                                "latent_image": ["U3", 0]}}
        for nid in ("245:211", "245:212"):
            if nid in api:
                api[nid]["inputs"]["samples"] = ["U4", 0]
    return api


cc = None


def main():
    global cc
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", type=int, default=1)
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--ref", required=True, help="角色A 参考图文件名（在 models/input/ 下）")
    ap.add_argument("--ref2", default="", help="角色B 参考图文件名（双角色）")
    ap.add_argument("--upscale", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=20260101)
    ap.add_argument("--mp", type=float, default=0.4)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--out", default="h3_ep")
    a = ap.parse_args()

    if not WORKFLOW:
        die("未设置 H3_WORKFLOW（ref2v 社区工作流 json 路径，见 README §3）")
    if not BASE_PROMPT or not SEG:
        die("未设置 H3_BASE_PROMPT / H3_SEGMENT（提示词建议写进 UTF-8 文件后用 "
            "$(cat prompt.txt) 传入，避免命令行转义吃掉换行）")

    cc = load_helper()
    wf = patch_workflow(json.load(open(WORKFLOW, encoding="utf-8")),
                        a.clip, a.ref, a.ref2, a.seconds, a.seed, a.mp, a.upscale, a.out)
    api = cc.convert_ui_to_api(wf)

    print("== 预检（逐行核对，任一行不对就别提交）==")
    for n in wf["nodes"]:
        if n.get("type") == "MultiImageLoader":
            print("  ref images -> %r  @%d" % (n["widgets_values"][0], n["widgets_values"][1]))
        if str(n.get("id")) in ("216", "217", "255", "238", "339", "39"):
            print("  #%s %s -> %s" % (n.get("id"), n.get("type"),
                                     str(n.get("widgets_values"))[:80]))
    print("  节点数 = %d" % len(api))

    if a.dry:
        print("DRY：只转换不提交")
        return 0

    n_before = 0
    if LOG_FILE and os.path.exists(LOG_FILE):
        import io
        n_before = len(io.open(LOG_FILE, encoding="utf-8", errors="replace").read().splitlines())

    t0 = time.time()
    ok, info = cc.direct_submit(api, timeout_s=7200)
    print("生成 %s，耗时 %.0fs" % ("OK" if ok else "FAIL", time.time() - t0))
    if not ok:
        print(json.dumps(info, ensure_ascii=False, indent=1)[:3000])
        return 1

    # 🔴 只统计本次新增的日志行（grep 整个日志会把上一次的告警算进来）
    if LOG_FILE and os.path.exists(LOG_FILE):
        import io
        seg = io.open(LOG_FILE, encoding="utf-8", errors="replace").read().splitlines()[n_before:]
        warn = [x for x in seg if "lora key not loaded" in x]
        print("  LoRA 检查：%s" % ("⚠️ %d 个 key 未加载（格式不兼容，等于没挂）" % len(warn)
                                   if warn else "✅ 已生效"))
        for x in [x for x in seg if "!!! Exception" in x][:3]:
            print("  ERR>", x.strip()[:200])

    for nid, o in (info.get("outputs") or {}).items():
        for k in ("images", "gifs", "video", "videos"):
            for it in (o.get(k) or []):
                if it.get("filename"):
                    print("  OUT:", it["filename"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
