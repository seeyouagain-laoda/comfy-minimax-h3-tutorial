#!/usr/bin/env bash
# 批量安装 MiniMax-H3 短剧所需的第三方 ComfyUI 节点包
#
#   bash install_nodes.sh /path/to/ComfyUI/custom_nodes
#
# 装完重启 ComfyUI，再检查节点是否注册：
#   curl -s http://127.0.0.1:8188/object_info | grep -o 'MiniMaxH3MotionContext' | head -1

set -u
CN="${1:?用法: bash install_nodes.sh <ComfyUI>/custom_nodes}"
mkdir -p "$CN"
cd "$CN" || exit 1

clone() {
  local name="${1##*/}"
  if [ -d "$name" ]; then
    echo "  跳过（已存在） $name"
  else
    printf "  克隆 %-42s " "$name"
    if git clone --depth 1 -q "https://github.com/$1.git" "$name" 2>/dev/null; then
      echo "OK"
    else
      echo "FAIL（检查网络）"
    fi
  fi
}

echo "== 核心（缺了就做不了对应功能）=="
clone NikoDemon80/ComfyUI-H3-Motion-Context        # 多段接续核心
clone WhatDreamsCost/WhatDreamsCost-ComfyUI       # MultiImageLoader（多图参考）
clone ANe5s/ComfyUI-MiniMax-H3-Hybrid             # HybridLoader（可选，需官方 ref2va）

echo "== 强烈建议 =="
clone LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler   # 二采放大
clone Kosinkadink/ComfyUI-VideoHelperSuite            # 存视频 / 载音频
clone Kosinkadink/ComfyUI-VideoHelperSuite

echo "== 辅助 =="
clone ltdrdata/ComfyUI-Impact-Pack                   # 批量取帧
clone rgthree/rgthree-comfy                          # Power Lora Loader / Seed
clone pythongosssss/ComfyUI-Custom-Scripts           # 播提示音
clone Windecay/ComfyUI-ReservedVRAM                  # 显存预留

cat <<'TXT'

== 依赖安装（用 ComfyUI 自己的 python）==
    <ComfyUI>/.venv/bin/python -m pip install scikit-image piexif dill
    Windows: <ComfyUI>\.venv\Scripts\python.exe -m pip install scikit-image piexif dill

== 不要装 was-node-suite-comfyui ==
    依赖重、易与其它包冲突。本指南的脚本已把它的 `Text Multiline`
    换成 comfy-core 自带的 `PrimitiveStringMultiline`，不需要它。

== 检查 ==
TXT
echo "完成。重启 ComfyUI 后跑 scripts/run_ep.py --dry 验证接线。"
