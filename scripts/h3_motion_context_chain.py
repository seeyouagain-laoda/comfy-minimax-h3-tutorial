# -*- coding: utf-8 -*-
"""跑 WF1：MiniMax H3 ref2v 长视频接续（Motion Context）+ 多图加载

接续机制（原作者 Note 原文要点）：
  * 首段：把 Motion Context / LoadLatent / Trim 三个节点 bypass，SaveLatent clip_index=1
  * 之后每段：LoadLatent clip_index = 上一段，SaveLatent clip_index = 本段
  * Motion Context 把上一段尾部的 AV latent 直接切出来钉进本段（不重编码）
  * Trim 用 trim_frames 把被钉住的头部（22 帧≈0.92s）从交付里剪掉
  * 🔴 提示词铁律：每段开头必须先描述「上一段是怎么结束的」，让贴合跑过接缝再切到新内容，
    否则模型会把两段内容都渲染（第一段结尾一个人 + 第二段开头两个人 = 画面里三个人）

用法：
  python run_wf1_chain.py 1 "<本段提示词>"          # 第一段
  python run_wf1_chain.py 2 "<本段提示词>"          # 第二段（自动接 clip 1）
"""
import json, os, sys, time

sys.path.insert(0, r"<AGENT_SCRIPTS>")
import comfy_control as cc

WF = os.environ.get(
    "WF1", r"<WF_DIR>\MiniMax H3 ref2v长视频接续+多图加载.json")
OUT_PREFIX = os.environ.get("OUT_PREFIX", "shenshen_chain")

MODEL_MAP = {
    "qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors":
        "qwen3vl_32b_minimax_h3_int8_convrot.safetensors",
    "minimax_h3_fl2va_bf16.safetensors": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "minimax_h3_fl2va_int8_convrot.safetensors": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "minimax_h3_ref2va_bf16.safetensors": "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors",
    "minimax_h3_video_vae_fp16.safetensors": "minimax_h3_video_vae_int8_convrot.safetensors",
    "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors":
        "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
}

# 公共段落：角色/场景/声音定义（对应原工作流 Text Multiline #220 的位置）
BASE_PROMPT = """integrated_multimodal_description:
A bright, warm, fully natural-colour room in an ordinary home — warm wood floor, cream walls, soft afternoon light through a window, and the maid's own colours, especially her deep-navy hair and pale-blue eyes.
A hand-drawn animation in a soft painterly style with visible sketch lines, in full natural colour. The story is told through medium shots and close-ups and partial details that imply the larger room, never a full wide shot.
[Character] A chibi whale-girl maid, about 2.5 heads tall: long twin-tails of gradient blue hair (deep navy roots to pale blue-white tips), a single curled ahoge, a blue IV-shaped hair clip, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white maid dress with a white frilled apron bearing a small blue whale outline on the chest, a short blue-white gradient whale tail, and small chubby chibi hands.
[Setting] A living room: a low wooden table, a sofa with a soft throw, a bookshelf, a potted plant by the window, and warm slanted light on the floor.
[Props] A big white bowl of steamed rice, a pair of chopsticks, a small blue teacup, and a folded blanket on the sofa.

overall_soundscape:
Quiet room ambience, faint clock tick, soft cloth rustle, the light clink of a teacup, no background music.

non_diegetic_music: no music, no background score, completely silent track, no soundtrack
"""


def patch(wf, clip_index, segment_prompt):
    for n in wf["nodes"]:
        nid = str(n.get("id"))
        t = n.get("type")
        wv = n.get("widgets_values")

        # --- 模型名重映射（按 basename，兼容带目录前缀的写法） ---
        def _remap(v):
            if not isinstance(v, str):
                return v, False
            base = v.replace("/", "\\").split("\\")[-1]
            if base in MODEL_MAP:
                return MODEL_MAP[base], True
            return v, False

        if isinstance(wv, list):
            for i, v in enumerate(wv):
                nv, hit = _remap(v)
                if hit:
                    wv[i] = nv
                    print("  remap %s.%s -> %s" % (nid, t, nv))
        elif isinstance(wv, dict):
            for k, v in list(wv.items()):
                nv, hit = _remap(v)
                if hit:
                    wv[k] = nv
                    print("  remap %s.%s -> %s" % (nid, t, nv))

        # --- Text Multiline（WAS 包未装）→ comfy-core 的 PrimitiveStringMultiline ---
        if t == "Text Multiline":
            n["type"] = "PrimitiveStringMultiline"
            print("  %s: Text Multiline -> PrimitiveStringMultiline" % nid)

        # --- 参考图 ---
        # 🔴🔴 血案（2026-10-04 查明）：工作流里 191 的 `ref_image_0` 接的是 MultiImageLoader 的
        #    **slot 2 = image_2（第 2 张图）**；而 `multi_image_loader.py:196` 对不足的槽位返回
        #    `torch.zeros((1,64,64,3))` —— **一张 64×64 全黑空图**。
        #    只写 1 张图时 image_2 就是全黑 → **参考图完全没生效**，角色全靠提示词画出来
        #    → 这就是用户说的「跟参考人物不怎么像」的根因。
        #    修法：① patch() 末尾把接线改到 slot 1（image_1）；② 这里仍写两行同名图兜底。
        if nid == "336" and t == "MultiImageLoader":
            ref = os.environ.get("REF_IMAGE", "shenshen_ref.png")
            wv[0] = "%s\n%s" % (ref, ref)
            wv[1] = int(os.environ.get("REF_SIZE", "2048"))
            wv[2] = int(os.environ.get("REF_SIZE", "2048"))
            print("  ref image -> %s ×2 @%s（并改接线到 slot 1）" % (ref, wv[1]))

        # --- 提示词：公共段 + 本段分镜 ---
        if nid == "220":
            wv[0] = BASE_PROMPT
            print("  #220 公共段已写入 (%d chars)" % len(BASE_PROMPT))
        if nid == "277":
            wv[0] = segment_prompt
            print("  #277 本段分镜已写入 (%d chars)" % len(segment_prompt))

        # --- 时长（走 17k+5 网格：5s→124帧，10s→243帧，15s→362帧） ---
        if nid == "216":
            wv[0] = float(os.environ.get("DURATION", "5.0"))
            print("  duration -> %ss" % wv[0])

        # --- 分辨率：保持原 16:9，但降到 0.4MP（864x480）以便本机跑得动 ---
        if nid == "217":
            wv[0] = os.environ.get("ASPECT", "16:9 (Widescreen)")
            wv[1] = float(os.environ.get("MEGAPIXELS", "0.4"))
            print("  resolution -> %s @ %s MP" % (wv[0], wv[1]))

        # --- 输出前缀 ---
        if nid == "255":
            wv[0] = "%s/clip%d" % (OUT_PREFIX, clip_index)
            print("  SaveVideo prefix -> %s/clip%d" % (OUT_PREFIX, clip_index))

        # --- 接续三件套 + SaveLatent ---
        if nid == "237":                     # MotionContext
            n["mode"] = 0 if clip_index > 1 else 4
            wv[0] = "22"                     # context_length
            wv[1] = 24                       # audio_context_length
            print("  #237 MotionContext %s (context=22, audio=24)"
                  % ("ON" if clip_index > 1 else "bypass(首段)"))
        if nid == "202":                     # LoadLatent
            n["mode"] = 0 if clip_index > 1 else 4
            wv[0] = "h3_context"
            wv[1] = clip_index - 1
            print("  #202 LoadLatent clip_index=%d %s"
                  % (clip_index - 1, "ON" if clip_index > 1 else "bypass(首段)"))
        if nid == "213":                     # Trim
            n["mode"] = 0 if clip_index > 1 else 4
            wv[0] = 0
            wv[1] = 24
            print("  #213 Trim %s" % ("ON" if clip_index > 1 else "bypass(首段)"))
        if nid == "218":                     # SaveLatent
            wv[0] = "h3_context/clip"
            wv[1] = clip_index
            print("  #218 SaveLatent clip_index=%d" % clip_index)
        if nid == "354":                     # SeedNode
            wv[0] = int(os.environ.get("SEED", "20261004")) + clip_index

    # 🔴 参考图接线修正：191.ref_image_0 原本接 336 的 slot 2（= image_2）。
    #    MultiImageLoader 在只有 1 张图时，image_2 返回 `torch.zeros((1,64,64,3))` 全黑空图，
    #    参考图等于没接 → 角色全靠提示词画。改成接 slot 1（= image_1，第 1 张有效图）。
    for l in wf.get("links", []):
        if isinstance(l, (list, tuple)) and len(l) >= 6 and l[1] == 336 and l[3] == 191:
            if l[2] != 1:
                print("  接线修正: 336.slot%s -> 191 改为 slot 1 (image_1)" % l[2])
                l[2] = 1
    return wf


def fix_api(api, upscale_mp=None):
    """转换后的补丁。

    #39 MinimaxH3_HybridLoader 要求 base/overlay 两个权重的 key 集合一致：
    本机 fl2va 是官方 `minimax_h3_fl2va_pruned_int8_convrot`（key 无前缀），
    而 ref2va 是社区版 `Minimax-h3_Singularity_ref2va_v1.3_int8`（key 带
    `model.diffusion_model.` 前缀）→ HybridLoader 直接报 key 不一致。
    这里换成官方 UNETLoader 单模型加载（本机 Director 的 r2v 通道就是这么用的）。
    若之后补齐官方 ref2va pruned int8，可把这段去掉恢复 HybridLoader。
    """
    if os.environ.get("USE_HYBRID") == "1":
        print("  USE_HYBRID=1：保留 HybridLoader 原样")
        return api
    if "39" in api:
        api["39"] = {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors",
                "weight_dtype": "default",
            },
        }
        print("  #39 HybridLoader -> UNETLoader(Singularity ref2va)（key 前缀不兼容）")

    # 原工作流 #339 挂的是 fl2va 底模 + fl2v turbo LoRA，但接的是 ReferenceToVideo（r2v 通道）。
    # r2v 官方配对是 ref2va 底模 + ref2v turbo LoRA —— 用户的核心诉求就是「严格参考设定图」，
    # 所以这里换成正确配对（如需完全照搬，设 KEEP_SHIPPED_MODEL=1）。
    if os.environ.get("KEEP_SHIPPED_MODEL") != "1":
        if "339" in api:
            api["339"]["inputs"]["unet_name"] = "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors"
            print("  #339 UNETLoader -> Singularity ref2va（r2v 正确配对）")
        if "238" in api:
            # 🔴 LoRA 格式坑：本机 `minimax_h3_ref2v_turbo_8step_v1.0_768p_bf16` 是
            # `key_format: minimax-h3-diffusers`（transformer_blocks.*），ComfyUI 不认，
            # 624 个 key **全部静默丢弃**（只在控制台打 warning，不报错）。
            # 必须用 ComfyUI generic 格式（blocks.N.attn.out_proj.lora_A.weight）的那几个。
            api["238"]["inputs"]["lora_name"] = os.environ.get(
                "LORA", "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors")
            api["238"]["inputs"]["strength_model"] = float(os.environ.get("LORA_STR", "1.0"))
            print("  #238 LoRA -> %s @%s" % (api["238"]["inputs"]["lora_name"],
                                             api["238"]["inputs"]["strength_model"]))

    # 前端专用节点（rgthree 的 Fast Groups Bypasser 等）没有后端实现，
    # 留在 prompt 里会让 ComfyUI 校验直接失败 → 摘掉。
    try:
        oi = cc.get_object_info()
    except Exception:
        oi = {}
    for k in list(api.keys()):
        ct = api[k].get("class_type")
        if oi and ct not in oi:
            del api[k]
            print("  摘掉前端节点 %s (%s)" % (k, ct))

    # ---------- 可选：二采放大（插在采样输出与解码之间） ----------
    # 思路：245:210 是采样输出（AV latent，samples 是堆叠 tensor）。
    #   → 拆 AV → 只放大视频 latent → 拼回 → 换 ManualSigmas 二采 → 再解码
    # SaveLatent 仍然接 245:210（**放大前**的低分辨率 latent），
    # 这样下一段接续用的上下文和本段一致，接缝完全不变。
    mp = float(upscale_mp if upscale_mp is not None
               else (os.environ.get("UPSCALE_MP", "0") or 0))
    if mp > 0 and "245:210" in api:
        api["U1"] = {"class_type": "LTXVSeparateAVLatent",
                     "inputs": {"av_latent": ["245:210", 0]}}
        api["U2"] = {"class_type": "MinimaxH3LatentUpscaler3D",
                     "inputs": {"latent": ["U1", 0],
                                "model_name": "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors",
                                "mode": "megapixels", "mode.megapixels": mp,
                                "align": 32, "enable_temporal_chunking": True,
                                "force_unload": False, "device": "cuda", "precision": "bf16"}}
        api["U3"] = {"class_type": "LTXVConcatAVLatent",
                     "inputs": {"video_latent": ["U2", 0], "audio_latent": ["U1", 1]}}
        api["U6"] = {"class_type": "ManualSigmas",
                     "inputs": {"sigmas": os.environ.get(
                         "UP_SIGMAS",
                         "0.9231, 0.8780, 0.8000, 0.6316, 0.3158, 0.0000")}}
        # 🔴 二采必须换一个 **不钉帧** 的 guider：
        #    Motion Context 的钉帧条件是**分辨率锁定**的（按一采画布算好 token 索引，
        #    日志里那行 "22 frames -> 7 cond blocks at indices 0..18, 124 frame clip at 864x480"）。
        #    放大后 latent 的 token 数变了 → 直接复用 245:207 会报
        #    `shape mismatch: value tensor of shape [2839, 96] cannot be broadcast to
        #     indexing result of shape [7228, 96]`。
        #    社区 WF2 也是给二采单独配一个 BasicGuider（只用 ReferenceToVideo 的 positive）。
        #    钉帧内容已经在被放大的 latent 里，二采只是精修，接缝不受影响。
        api["U5"] = {"class_type": "BasicGuider",
                     "inputs": {"model": ["308", 0], "conditioning": ["191", 0]}}
        api["U4"] = {"class_type": "SamplerCustomAdvanced",
                     "inputs": {"noise": ["245:206", 0], "guider": ["U5", 0],
                                "sampler": ["245:208", 0], "sigmas": ["U6", 0],
                                "latent_image": ["U3", 0]}}
        if "245:211" in api:
            api["245:211"]["inputs"]["samples"] = ["U4", 0]      # VAEDecode
        if "245:212" in api:
            api["245:212"]["inputs"]["samples"] = ["U4", 0]      # VAEDecodeAudio
        print("  ✅ 已插入二采放大：目标 %g MP（SaveLatent 仍取放大前 latent，接缝不变）" % mp)
    return api


def run_clip(clip_index, seg, upscale_mp=None, dry=False, quiet=False):
    """跑一段。返回 (ok, info, out_files)。供 CLI 与 h3_story.py 共用。"""
    wf = json.load(open(WF, encoding="utf-8"))
    if not quiet:
        print("== 打补丁 (clip %d) ==" % clip_index)
    patch(wf, clip_index, seg)

    # 把本段实际用的完整提示词存下来，供后续复刻同一份 conditioning
    try:
        out_ctx = r"<COMFYUI_ROOT>\ComfyUI\output\h3_context"
        os.makedirs(out_ctx, exist_ok=True)
        with open(os.path.join(out_ctx, "clip_%05d.prompt.txt" % clip_index), "w",
                  encoding="utf-8") as fh:
            fh.write(BASE_PROMPT + seg)
        if not quiet:
            print("  提示词已存档 clip_%05d.prompt.txt" % clip_index)
    except Exception as e:
        print("  (提示词存档失败:", e, ")")

    tmp = r"<PROJECT_DIR>\_wf1_clip%d.json" % clip_index
    json.dump(wf, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    api = cc.convert_ui_to_api(wf)
    api = fix_api(api, upscale_mp)
    if not quiet:
        print("== 转 API == 节点数 %d" % len(api))
        for k in sorted(api, key=lambda x: (len(x), x)):
            v = api[k]
            print("  %-6s %-38s %s" % (k, v.get("class_type"),
                                       {kk: (str(vv)[:46]) for kk, vv in v.get("inputs", {}).items()}))
    if dry:
        print("DRY=1 只转换不提交")
        return True, {}, []

    LOG = r"<AGENT_SCRIPTS>\data\comfy_ui.log"
    n_before = 0
    try:
        import io
        n_before = len(io.open(LOG, encoding="utf-8", errors="replace").read().splitlines())
    except Exception:
        pass

    t0 = time.time()
    ok, info = cc.direct_submit(api, timeout_s=7200)
    print("  clip %d 生成 %s  %.0fs" % (clip_index, "OK" if ok else "FAIL", time.time() - t0))

    # 🔴 LoRA 静默失效检查：ComfyUI 只打 warning，不报错，出片看着也正常。
    # 只统计「本次提交之后新增」的日志行，否则会把上一次的告警也算进来。
    try:
        import io
        seg_lines = io.open(LOG, encoding="utf-8", errors="replace").read().splitlines()[n_before:]
        warn = [l for l in seg_lines if "lora key not loaded" in l]
        if warn:
            print("  ⚠️ LoRA 有 %d 个 key 未加载（格式不兼容，等于没挂）" % len(warn))
        else:
            print("  ✅ LoRA 已生效（无未加载 key）")
        err = [l for l in seg_lines if "!!! Exception" in l]
        for e in err[:2]:
            print("  ERR>", e.strip()[:200])
    except Exception:
        pass

    outs = []
    if ok:
        for nid, o in (info.get("outputs") or {}).items():
            for k in ("images", "gifs", "video", "videos", "audio"):
                for it in (o.get(k) or []):
                    if it.get("filename"):
                        outs.append(it["filename"])
        print("  产物:", ", ".join(outs) or "(无)")
    else:
        print(json.dumps(info, ensure_ascii=False, indent=1)[:2500])
    return ok, info, outs


DEFAULT_SEG1 = (
    "[Shot 1] A bright room in an ordinary home, seen in a medium shot. The chibi whale-girl "
    "maid stands beside a low wooden table with a big bowl of steamed rice in front of her, "
    "gazing at it with wide, delighted eyes. She lifts the bowl with both hands and breathes in "
    "the steam, twin-tails swaying, tail wagging. She sits down on the floor cushion and starts "
    "eating happily, cheeks puffing out with each bite. Warm afternoon light falls across the "
    "wooden floor. The camera slowly pushes in and settles on her face."
)


def main():
    clip_index = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    seg = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SEG1
    ok, _, _ = run_clip(clip_index, seg, dry=(os.environ.get("DRY") == "1"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
