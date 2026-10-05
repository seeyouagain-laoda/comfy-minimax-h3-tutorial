# 长片逐段交付 · 执行清单（对着打勾）

> 配套 SKILL.md §1.5「🚦 流程总览」。适用 >15s 的多段长片（20 / 30 / 40s）。
> 2026-10-05《等门》30s / 3 段跑通后固化。

```
项目名：__________________   段数：____   每段时长：____s   总时长：____s
角色：□ 单角色(________)  □ 双角色(________ + ________)
脚本：__________________.py     SEED：__________
```

---

## 阶段一 · 准备（不烧显存）

- [ ] **1. 需求对齐** —— 时长 / 题材 / 单双角色 / 有无台词，四项都明确
- [ ] **2. 写剧本** —— 分镜表列出：几段 × 几镜，每镜 **1.2–2.0s**（>2.5s 必警惕）
      - [ ] 每镜只有**一个**动作
      - [ ] 全片动作**不重复**（数一遍有没有"又是跳"）
      - [ ] 情绪/局面**逐段升级**，不是并列堆砌
- [ ] **3. 写脚本** —— 复制模板改两处：`BASE_PROMPT`（角色卡 + 场景 + 风格锁）、`SEG1..N`（分镜）
      - 模板：温馨向 → `run_warm_wait.py`；喜剧/动作向 → `run_ep12_move.py`
      - [ ] 第 1..N-1 段单角色，**最后一段才加 `REF_IMAGE2`**（避免"先独后合"失效）
- [ ] **4. 全段干跑**（每段都跑，别只跑第 1 段）
      ```bat
      cd /d <PROJECT_DIR>
      set PY=<COMFYUI_ROOT>\ComfyUI\.venv\Scripts\python.exe
      for %c in (1 2 3) do (set CLIP=%c & DRY=1 "%PY%" X.py)
      ```
      - [ ] `ref images -> A | A`（单角色两行同名）或 `A | B`（双角色）
      - [ ] `接线修正: 336.slot2 -> 191 改为 slot 1`
      - [ ] `duration -> 10.0s`　`resolution -> 16:9 @ 0.4 MP`
      - [ ] 底模是 `Singularity_ref2va_v1.3_int8`、LoRA 是 `..._comfyui_bf16`
      - 任一行不对 → **别提交，先修**（全黑参考图 = 静默失效）

## 🔴 闸 1 · 脚本发用户审

- [ ] `present_files` 发 `.py` 文件
- [ ] 聊天里给**中文分镜表**（用户不看英文提示词也能审）
- [ ] 说明「针对上一版的哪个问题做了什么改动」
- [ ] **等用户明确通过**（"可以" / "没问题"）→ 才进阶段二
      ⚠️ 用户说「继续剩下的生成完成」= 单次授权，只对当次有效

---

## 阶段二 · 逐段生成（循环，每段都要发审）

对第 N 段（N = 1, 2, 3 …）：

- [ ] **5. 确认引擎与看板**
      ```bat
      curl 127.0.0.1:8188/system_stats        :: 必须 200
      python <AGENT_SCRIPTS>\h3_board_guard.py   :: 后台常驻
      ```
- [ ] **6. 跑第 N 段**（后台 + 等完；10s 段约 7–10 分钟）
      ```bat
      SEED=xxxx CLIP=N "%PY%" X.py
      ```
      - [ ] 日志出现 `clip N 生成 OK` + `✅ LoRA 已生效（无未加载 key）`
- [ ] **7. 抽帧自检三条**
      ```bat
      :: ① 规格（接续段应为 221 帧，不是 243！）
      ffprobe -v error -show_entries format=duration ^
        -show_entries stream=codec_type,width,height,nb_frames -of default=nw=1 IN.mp4
      :: ② 画面（10 帧拼图，逐格对分镜）
      ffmpeg -y -v error -i IN.mp4 -vf "select='not(mod(n\,24))',scale=380:-1,tile=5x2" -frames:v 1 sheet.jpg
      :: ③ 首帧 = 封面帧（单独查，开头常有杂帧）
      ffmpeg -y -v error -i IN.mp4 -vf "select='between(n,0,5)',scale=200:-1,tile=6x1" -frames:v 1 head.jpg
      ```
      - [ ] 帧数对得上（**第 1 段 243 / 接续段 221**）
      - [ ] **有音轨**
      - [ ] 角色一致（发色、服装、双角色不串脸）
      - [ ] 分镜落实（景别切了、每镜动作对）
      - [ ] 首帧角色正确（不对就裁，见下方「裁帧」）
- [ ] **8. 拷贝到交付目录**（简体文件名！改过名会导致卡片打不开）
      ```bat
      copy "<COMFYUI_ROOT>\output\<prefix>\clipN_00001_.mp4" "<ASSET_DIR>\<片名>_第N段_<幕名>_10s.mp4"
      ```

## 🔴 闸 2 · 发段审

- [ ] `present_files` 发 **mp4 + 抽帧图**
- [ ] 汇报：规格数据 / 自检结果 / 发现的问题 / 下一段是什么
- [ ] **等用户通过** → 才跑第 N+1 段
      ⚠️ **不得连跑两段，也不得全跑完才一起发**
      ⚠️ **自己抽帧看过 ≠ 用户审核**

---

## 阶段三 · 拼接与交付

- [ ] **9. 拼接**（无重编码）
      ```bat
      cd <COMFYUI_ROOT>\ComfyUI\output\<prefix>
      :: 用 printf 写 concat 列表（Windows 下比 echo 可靠）
      printf "file 'clip1_00001_.mp4'\nfile 'clip2_00001_.mp4'\nfile 'clip3_00001_.mp4'\n" > _list.txt
      ffmpeg -y -f concat -safe 0 -i _list.txt -c copy OUT.mp4
      ```
- [ ] **10. 接缝检查**（抽接缝前后各 4 帧，有跳切就重跑该段）
      ```bat
      ffmpeg -y -v error -i JOINED.mp4 ^
        -vf "select='between(n,239,246)+between(n,460,467)',scale=240:-1,tile=8x2" -frames:v 1 seam.jpg
      ```
      帧号 = 各段帧数的前缀和（第 1 段 243 → 接缝 1 在 243；第 2 段 221 → 接缝 2 在 464）
- [ ] **11. 首帧杂帧裁剪**（如果首帧角色不对）
      ```bat
      :: 先确认杂帧持续几帧
      ffmpeg -y -v error -i IN.mp4 -vf "select='between(n,0,11)',scale=200:-1,tile=6x2" -frames:v 1 head12.jpg
      :: 假设是 4 帧 → 裁掉 + 同步裁音频（4 帧 = 0.1667s，已超人耳可感阈值）
      ffmpeg -y -i IN.mp4 -vf "trim=start_frame=4,setpts=PTS-STARTPTS" ^
        -af "atrim=start=0.1667,asetpts=PTS-STARTPTS" ^
        -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k OUT.mp4
      ```
      ⚠️ `-ss 0.0417 -c copy` **跳不过去**（会定位到最近关键帧），必须重编码
- [ ] **12. 交付**：`present_files` 发完整片 + 抽帧图
- [ ] **13. 归档**
      - [ ] 文档：`桌面\重要AI配置文档\06_视频与图像生成\NN_<主题>_<日期>.md`
            （分镜表 + 完整提示词 + 参数 + 验收数据 + 踩的坑 + 复用命令）
      - [ ] 当日 memory
      - [ ] **回写本 skill**：新坑 → 避坑清单；新配方 → 对应 Step；新模板 → `references/`

---

## 常见卡点速查

| 症状 | 先查 |
|---|---|
| 出片但角色不像参考图 | 参考图是否两行同名？接线是否改到 slot 1？（避坑 17） |
| 画面"看着正常但不对" | §5.10 静默失效家族（LoRA 全丢 / 全黑参考图） |
| 动作慢 | 单镜时长 >2.5s？（§2.9.1.5） |
| 中景里尾巴/关键特征消失 | 每镜是否重复写了该特征？（§2.9.1.6） |
| 特写里环境丢失 | 特写镜是否单独声明了环境？ |
| 双角色串脸 / 只出现一个 | 两张 ref_image 是否都给？「先独后合」是否失效？（避坑 20） |
| 角色"浮"在某物前 | 参照物是否在画面内？（避坑 24） |
| 首帧是错误角色 | 裁帧（本清单步 11） |
