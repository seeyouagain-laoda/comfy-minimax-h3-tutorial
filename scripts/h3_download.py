# -*- coding: utf-8 -*-
"""带断点续传 + 自动重试的下载器（HF 单文件）。

上一版踩的坑：`r.read()` 在连接被中断时返回空 bytes，循环直接退出，
脚本却把残缺文件当成完成品改名 —— 于是 19.53GB 只下了 0.91GB 却报 DONE。
本版：① 用 Range 续传；② 短读即重试；③ 末尾按 Content-Length 校验大小，不符就继续续。
"""
import os, sys, time, urllib.request, urllib.error

os.environ["NO_PROXY"] = "127.0.0.1,localhost"
os.environ["HTTP_PROXY"] = "http://<LOCAL_PROXY>"
os.environ["HTTPS_PROXY"] = "http://<LOCAL_PROXY>"

DST_DIR = r"<COMFYUI_ROOT>\ComfyUI\models\diffusion_models"
REPO = "WarmBloodAban/Minimax-h3_Singularity"
FILES = [
    "Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors",
    "Minimax-h3_Singularity_ref2va_v1.3_Pruned_w4a8.safetensors",
]
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def total_size(url):
    r = urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA), timeout=60)
    return int(r.headers.get("Content-Length", 0))


def download(url, dst):
    part = dst + ".part"
    expect = total_size(url)
    if os.path.exists(dst) and os.path.getsize(dst) == expect:
        print("  已完整，跳过 %.2f GB" % (expect / 1024**3), flush=True)
        return True
    # 把上一版的残缺文件当续传种子
    if os.path.exists(dst) and not os.path.exists(part):
        os.replace(dst, part)
    t0 = time.time()
    fails = 0
    while True:
        have = os.path.getsize(part) if os.path.exists(part) else 0
        if have >= expect:
            break
        if have:
            hdr = dict(UA)
            hdr["Range"] = "bytes=%d-" % have
            print("  续传 %.2f/%.2f GB (%.0f%%)"
                  % (have / 1024**3, expect / 1024**3, 100.0 * have / expect), flush=True)
        else:
            hdr = dict(UA)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=120) as r:
                with open(part, "ab" if have else "wb") as f:
                    while True:
                        chunk = r.read(1024 * 1024 * 4)
                        if not chunk:
                            break
                        f.write(chunk)
                        have += len(chunk)
                        if have % (512 * 1024 * 1024) < 4 * 1024 * 1024:
                            el = max(0.1, time.time() - t0)
                            print("    %.0f%%  %.2f/%.2f GB  %.1f MB/s"
                                  % (100.0 * have / expect, have / 1024**3, expect / 1024**3,
                                     have / 1024**2 / el), flush=True)
            fails = 0
        except Exception as e:
            fails += 1
            print("  断线(%s)，第 %d 次重试…" % (type(e).__name__, fails), flush=True)
            time.sleep(min(20, 3 * fails))
            if fails > 40:
                print("  重试过多，放弃", flush=True)
                return False
    got = os.path.getsize(part)
    if got != expect:
        print("  ⚠️ 大小不符 %.2f/%.2f GB" % (got / 1024**3, expect / 1024**3), flush=True)
        return False
    # 🔴 Windows 上刚写完的大文件常被杀软/索引服务临时占用，
    #    os.replace 会抛 WinError 32（另一个程序正在使用此文件）——
    #    这里重试若干次，仍失败则用「复制 + 删源」兜底。
    for attempt in range(10):
        try:
            os.replace(part, dst)
            print("  ✅ DONE %.2f GB  %.0fs" % (got / 1024**3, time.time() - t0), flush=True)
            return True
        except PermissionError:
            print("  改名被占用(WinError 32)，第 %d 次重试…" % (attempt + 1), flush=True)
            time.sleep(4)
    import shutil
    print("  改用复制兜底…", flush=True)
    shutil.copyfile(part, dst)
    if os.path.getsize(dst) == expect:
        try:
            os.remove(part)
        except Exception:
            pass
        print("  ✅ DONE（复制兜底）%.2f GB" % (expect / 1024**3), flush=True)
        return True
    print("  ❌ 复制后大小不符", flush=True)
    return False


ok_all = True
for name in FILES:
    url = "https://huggingface.co/%s/resolve/main/%s" % (REPO, name)
    dst = os.path.join(DST_DIR, name)
    print("== %s" % name, flush=True)
    if not download(url, dst):
        ok_all = False
print("ALL DONE ok=%s" % ok_all, flush=True)
