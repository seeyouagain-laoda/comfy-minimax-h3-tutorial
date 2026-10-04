#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""HuggingFace 大文件下载器：批量清单 + 断点续传 + 短读重试 + 大小对账 + 改名重试

用法
----
    # 下全套必需权重（按清单自动落到 models/ 下的正确子目录）
    python download_hf.py --all --dest <COMFYUI_ROOT>/models

    # 只下指定几项
    python download_hf.py --dest <COMFYUI_ROOT>/models vae video_vae

    # 手动下单个文件
    python download_hf.py <repo_id> <filename> [目标目录]

清单
----
    ASSETS 里是「逻辑名 -> (仓库, 仓库内路径, 落到 models/ 的哪个子目录)」。
    不同发布方的文件名略有差异，所以按**名字前缀/关键字**匹配而不是死等文件名。
    若某个逻辑名匹配不到，会打印候选提示，你可以把实际路径填进 ASSETS 再跑。

三个踩过的坑（都修在这份脚本里）
--------------------------------
    ① 「循环正常结束」≠「数据完整」—— urllib 的 r.read() 在断连时返回**空 bytes**，
       循环会正常退出，脚本把 0.91GB 的残缺文件当 19.53GB 完成品改名。
       → 按 Content-Length 对账，不符就继续续传。
    ② Range 续传要从**已下载字节数**开始，不是从头。
    ③ Windows 上刚写完的大文件会被杀软/索引临时占用，os.replace 抛 WinError 32
       → 改名重试若干次，仍失败则 copyfile 兜底。

依赖：仅标准库（urllib）。装了 requests 会更稳，但不是必需。
"""
import json
import os
import shutil
import sys
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; h3-video-guide/1.0)"}
CHUNK = 4 * 1024 * 1024

# ---- 仓库（按发布方分开；找不到就把正确的 repo 填进来）------------------------
REPO_MAIN = "Comfy-Org/MiniMax-H3"   # 底模 / 文本编码器 / VAE / embedding
REPO_UPSCALER = None                 # 二采放大权重所在仓库（社区发布，按需填）
# 融合底模（一份通吃两条通道，省一份 19.5GB）—— 想省磁盘可选
REPO_HYBRID = None

# ---- 清单：逻辑名 -> (仓库, 匹配关键字, 落到 models/ 的子目录, 是否必需) --------
ASSETS = [
    ("fl2va",    REPO_MAIN, "minimax_h3_fl2va_pruned_int8",     "diffusion_models", True),
    ("ref2va",   REPO_MAIN, "minimax_h3_ref2va_pruned_int8",    "diffusion_models", True),
    ("te_nvfp4", REPO_MAIN, "qwen3vl_32b_minimax_h3_nvfp4",     "text_encoders",    False),
    ("te_int8",  REPO_MAIN, "qwen3vl_32b_minimax_h3_int8",      "text_encoders",    False),
    ("vae_video", REPO_MAIN, "minimax_h3_video_vae",            "vae",              True),
    ("vae_audio", REPO_MAIN, "minimax_h3_audio_vae",            "vae",              True),
    ("lora_8step", REPO_MAIN, "minimax_h3_fl2v_turbo_8step",    "loras",            True),
    ("lora_4step", REPO_MAIN, "minimax_h3_fl2v_turbo_4step",    "loras",            False),
    ("upscaler", REPO_UPSCALER, "minimax_h3_latent_upscaler",   "latent_upscale_models", False),
    ("hybrid",   REPO_HYBRID,   "hybrid",                       "diffusion_models", False),
]


def list_files(repo_id, timeout=40):
    """列出仓库根目录与常见子目录下的文件（部分仓库有 subfolder 需递归几层）。"""
    found = []
    roots = ["", "diffusion_models/", "text_encoders/", "vae/", "loras/",
             "embeddings/", "vae_approx/", "latent_upscale_models/"]
    for r in roots:
        url = "https://huggingface.co/api/models/%s/tree/main/%s" % (repo_id, r)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
        except Exception:
            continue
        for it in data:
            if it.get("type") == "file":
                found.append((r + it["path"], it.get("size", 0)))
    return found


def resolve(repo_id, keyword):
    """在仓库里按关键字找第一个匹配文件。"""
    if not repo_id:
        return None
    for path, _ in list_files(repo_id):
        if keyword.lower() in os.path.basename(path).lower():
            return path
    return None


def total_size(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA),
                               timeout=timeout) as r:
        return int(r.headers.get("Content-Length", 0))


def download(repo_id, filename, dest_dir=".", max_retry=40):
    url = "https://huggingface.co/%s/resolve/main/%s" % (repo_id, filename)
    dst = os.path.join(dest_dir, filename)
    part = dst + ".part"
    os.makedirs(dest_dir, exist_ok=True)
    expect = total_size(url)
    if expect == 0:
        print("  拿不到 Content-Length，跳过")
        return False
    print("  目标 %.2f GB  %s" % (expect / 1024**3, filename))

    if os.path.exists(dst) and os.path.getsize(dst) == expect:
        print("  已完整，跳过")
        return True
    if os.path.exists(dst) and not os.path.exists(part):
        os.replace(dst, part)          # 把残缺的旧文件当续传种子

    t0 = time.time()
    fails = 0
    while True:
        have = os.path.getsize(part) if os.path.exists(part) else 0
        if have >= expect:
            break
        hdr = dict(UA)
        if have:
            hdr["Range"] = "bytes=%d-" % have
            print("    续传 %.2f/%.2f GB (%.0f%%)"
                  % (have / 1024**3, expect / 1024**3, 100.0 * have / expect), flush=True)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr),
                                        timeout=120) as r:
                with open(part, "ab" if have else "wb") as f:
                    while True:
                        chunk = r.read(CHUNK)
                        if not chunk:      # 坑①：空 bytes = 断线，不是结束
                            raise IOError("empty read")
                        f.write(chunk)
                        have += len(chunk)
                        if have % (512 * 1024**2) < CHUNK:
                            el = max(0.1, time.time() - t0)
                            print("      %.0f%%  %.1f MB/s"
                                  % (100.0 * have / expect, have / 1024**2 / el), flush=True)
            fails = 0
        except Exception as e:
            fails += 1
            print("    断线(%s)，第 %d 次重试…" % (type(e).__name__, fails), flush=True)
            time.sleep(min(20, 3 * fails))
            if fails > max_retry:
                print("  重试过多，跳过")
                return False

    got = os.path.getsize(part)
    if got != expect:                        # 坑①的最后一道闸
        print("  ⚠️ 大小不符 %d/%d，继续续传" % (got, expect))
        return download(repo_id, filename, dest_dir, max_retry)

    for i in range(10):                      # 坑③
        try:
            os.replace(part, dst)
            print("  ✅ 完成 %.2f GB  %.0fs" % (got / 1024**3, time.time() - t0))
            return True
        except PermissionError:
            print("  改名被占用(WinError 32)，第 %d 次重试…" % (i + 1), flush=True)
            time.sleep(4)
    print("  改用复制兜底…", flush=True)
    shutil.copyfile(part, dst)
    if os.path.getsize(dst) == expect:
        try:
            os.remove(part)
        except Exception:
            pass
        print("  ✅ 完成（复制兜底）")
        return True
    return False


def main():
    args = sys.argv[1:]
    if args and args[0] not in ("--all", "--dest") and len(args) >= 2 \
            and "/" in args[0] and not args[0].startswith("-"):
        # 手动模式：python download_hf.py <repo_id> <filename> [dest]
        return 0 if download(args[0], args[1], args[2] if len(args) > 2 else ".") else 1

    dest = "."
    i = 0
    only = []
    while i < len(args):
        if args[i] == "--dest":
            dest = args[i + 1]; i += 2
        elif args[i] == "--all":
            only = []; i += 1
        else:
            only.append(args[i]); i += 1
    if not dest or dest == ".":
        dest = os.environ.get("COMFY_MODELS", "./models")
    if only == [] and "--all" not in args:
        only = [n for n, _, _, _, req in ASSETS if req]

    print("目标目录:", os.path.abspath(dest))
    print("计划下载:", only or "全部", "\n")
    ok = True
    for name, repo, kw, sub, req in ASSETS:
        if only and name not in only:
            continue
        print("[%s]%s" % (name, "" if req else "  (可选)"))
        if not repo:
            print("  ⏭  未配置仓库（REPO_* 留空），请自行下载 %s*" % kw)
            continue
        path = resolve(repo, kw)
        if not path:
            print("  ⏭  仓库里没匹配到 %s*，跳过" % kw)
            continue
        ok &= download(repo, path, os.path.join(dest, sub))
    print("\n完成。" if ok else "\n有项目未完成，见上面提示。")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
