# -*- coding: utf-8 -*-
"""跑 WF2：minimax_h3_r2v_Latent Upscaler 双采样（换成本机权重 + 深深参考图）

结构（原样保留）：
  一采 4 步（SplitSigmas 取 8 步档的高段）→ LTXVSeparateAVLatent 拆 AV
  → MinimaxH3LatentUpscaler3D 把视频 latent 放大到 N MP
  → LTXVConcatAVLatent 拼回 → 二采 6 步（ManualSigmas 0.9231→0）
  → VAEDecode + VAEDecodeAudio → VHS_VideoCombine
"""
import json, os, sys, copy, time

sys.path.insert(0, r"<AGENT_SCRIPTS>")
import comfy_control as cc

WF = os.environ.get(
    "WF2", r"<WF_DIR>\minimax_h3_r2v_Latent Upscaler 双采样.json")
OUT_PREFIX = os.environ.get("OUT_PREFIX", "shenshen_r2v_upscale")
REF_IMAGE = os.environ.get("REF_IMAGE", "shenshen_ref.png")   # ComfyUI/input/ 下的文件名

# ---------- 模型名重映射（本机实际文件名） ----------
MODEL_MAP = {
    "qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors":
        "qwen3vl_32b_minimax_h3_int8_convrot.safetensors",
    "minimax_h3_fl2va_bf16.safetensors": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "minimax_h3_ref2va_bf16.safetensors": "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors",
    "minimax_h3_ref2va_int8_convrot.safetensors": "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors",
    "minimax_h3_video_vae_fp16.safetensors": "minimax_h3_video_vae_int8_convrot.safetensors",
    "minimax_h3_latent_upscaler_3d_bf16.safetensors":
        "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors",
    "MiniMax h3\\minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors":
        "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
    # basename 自映射：把带目录前缀的写法统一剥成裸文件名
    "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors":
        "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors",
}

# ---------- 深深版提示词（沿用 WF2 的 四段式 结构） ----------
PROMPT = """subject_definitions:
<Subject 1> is the chibi whale-girl maid character shown in the reference image (a full-body standing view). Appearance, hairstyle, costume, eye colour and facial features strictly follow the reference: long twin-tails of gradient blue hair (deep navy roots to pale blue-white tips), a single curled ahoge antenna on top, a blue IV-shaped hair clip on her forehead, small whale-fin ears, large pale-blue ringed eyes, a deep-navy and white maid dress with a white frilled apron bearing a small blue whale outline on the chest, a short blue-white gradient whale tail, small chubby chibi hands and tiny black shoes. About 2.5 heads tall, Q-version proportions.

summary:
[reference generation] A stylized 2D anime performance in which <Subject 1> does a bright, bouncy little dance under warm afternoon room light, captured across four beat-synced shots with professional camera movement.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2], [Shot 3], [Shot 4]): fully_preserved - face, twin-tails, ahoge, IV hair clip, whale-fin ears, maid dress, apron whale print, whale tail, hands and shoes all match the reference; the added lighting, room and choreography are new target-video content, not a fidelity loss.

detailed_description:
Stylized 2D anime rendering with clean cel shading and soft gradients, set in a bright warm living room; a soft warm key light from the front-left, a gentle bounce fill, and a faint warm rim on the hair. Low contrast, airy, the deep-navy and white palette of <Subject 1> reading cleanly against the warm room.

[Shot 1] A full-body low-angle hero shot frames <Subject 1> centred, feet at the lower third. She begins from a still stance, then pops her hips on the beat and swings both arms out in a wide cheerful flourish, twin-tails and whale tail swaying with the follow-through; the ahoge springs. The camera pushes in with small amplitude at slow speed.

[Shot 2] At 00:01.500, the camera cuts to a medium close-up from a three-quarter front angle, her face and hands filling the frame. She rolls her wrists in a clean finger-wave, head tilting on the off-beat, then shapes a small heart with both hands at her cheek, eyes bright. The camera arcs right with small amplitude at slow speed around her hands.

[Shot 3] At 00:03.000, the shot cuts to a wider low angle as she does a light hop and a small spin on the spot, skirt and twin-tails flaring out, landing softly with a knee pop and both arms thrown up. The camera trucks left with medium amplitude at fast speed, tracking the rotation.

[Shot 4] At 00:04.500, the camera cuts to a low-angle hero framing that holds her final pose: both hands raised in a happy pose, weight sunk into one leg, gaze bright and direct into the lens. Only micro-movements remain - the twin-tails and whale tail settling, a slow controlled breath, the ahoge still springing gently. The camera holds a static shot.

overall_soundscape:
Soft room ambience, the light swish of the skirt, small soft footfalls on the floor, a bright little breath at the held pose, and a faint cloth rustle from the twin-tails.

non_diegetic_music:
N/A
"""


def patch(wf):
    """就地改 GUI 工作流：模型名 / 参考图 / 提示词 / 分辨率 / 时长 / seed / 打开一采输出"""
    for n in wf["nodes"]:
        nid = str(n.get("id"))
        t = n.get("type")
        wv = n.get("widgets_values")

        # 模型名重映射（含 dict 型 widgets；按 basename 匹配，兼容 "MiniMaxH3\xxx" 这类带目录前缀的写法）
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

        if nid == "9":                      # LoadImage 参考图
            wv[0] = REF_IMAGE
            print("  ref image -> shenshen_ref.png")
        if nid == "2":                      # 提示词
            wv[0] = PROMPT
            print("  prompt replaced (%d chars)" % len(PROMPT))
        if nid == "17":                     # 时长（秒）→ 走 ComfyMathExpression 取 17k+5 网格
            wv[0] = 5.0
            print("  duration -> 5.0s")
        if nid == "23":                     # 放大目标百万像素（原工作流 2.0，先 1.0 验证管线）
            wv[0] = float(os.environ.get("UPSCALE_MP", "1.0"))
            print("  upscale target -> %s MP" % wv[0])
        if nid == "20":                     # 分辨率选择器（保持原样：9:16 竖版 0.2MP）
            print("  resolution -> %s" % wv)
        if nid == "43":                     # Seed (rgthree)
            wv[0] = 20261004
            print("  seed -> 20261004")
        if nid == "1":                      # 一采输出（原为 bypass），打开做对比
            n["mode"] = 0
            if isinstance(wv, dict):
                wv["filename_prefix"] = OUT_PREFIX + "_pass1"
            print("  一采输出已打开 (pass1)")
        if nid in ("7", "8"):               # 一采的解码节点也要打开，否则 #1 没有输入
            n["mode"] = 0
            print("  #%s 解码节点已打开（供 pass1 输出）" % nid)
        if nid == "44":
            if isinstance(wv, dict):
                wv["filename_prefix"] = OUT_PREFIX + "_pass2"
            print("  二采输出 prefix -> %s_pass2" % OUT_PREFIX)
    return wf


def main():
    wf = json.load(open(WF, encoding="utf-8"))
    print("== 打补丁 ==")
    patch(wf)

    tmp = r"<PROJECT_DIR>\_wf2_patched.json"
    json.dump(wf, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    print("== 转 API ==")
    api = cc.convert_ui_to_api(wf)
    print("  api 节点数:", len(api))

    # HybridLoader 要求 base/overlay 权重 key 集合一致；本机 ref2va 是社区版
    # （key 带 model.diffusion_model. 前缀）与官方 fl2va 不匹配 → 换 UNETLoader 单模型。
    if "39" in api:
        api["39"] = {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors",
                "weight_dtype": "default",
            },
        }
        print("  已把 #39 HybridLoader 换成 UNETLoader（key 前缀不兼容）")

    # 放大节点是「动态 combo」，GUI 的 widget 顺序与 API 输入名不一致（keep_proportion
    # 在 API 里叫 enable_temporal_chunking），转换器会串位 → 这里按后端 schema 手工钉死。
    if "26" in api:
        api["26"]["inputs"] = {
            "latent": ["35", 0],
            "model_name": "minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors",
            "mode": "megapixels",
            "mode.megapixels": ["23", 0],
            "align": 32,
            "enable_temporal_chunking": True,
            "force_unload": False,
            "device": "cuda",
            "precision": "bf16",
        }
        print("  已修正 #26 MinimaxH3LatentUpscaler3D 输入（动态 combo 串位）")

    json.dump(api, open(r"<PROJECT_DIR>\_wf2_api.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("== 提交 ==")
    t0 = time.time()
    ok, info = cc.direct_submit(api, timeout_s=7200)
    print("ok=%s  %.0fs" % (ok, time.time() - t0))
    if not ok:
        print(json.dumps(info, ensure_ascii=False, indent=1)[:4000])
        return 1
    outs = (info.get("outputs") or {})
    for nid, o in outs.items():
        for k in ("images", "gifs", "video", "videos", "audio"):
            for it in (o.get(k) or []):
                print("  OUT %s: %s" % (nid, it.get("filename")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
