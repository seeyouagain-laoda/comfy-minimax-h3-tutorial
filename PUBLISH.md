# 发布清单（上传 GitHub 前照这个走）

## 1. 仓库信息

| 项 | 值 |
|---|---|
| **仓库名** | `comfy-minimax-h3-tutorial` |
| **显示名 / 标题** | 基于 Comfy 和 MiniMax H3 的实战教程 —— 以 DeepSeek 鲸鱼娘为例 |
| **一句话简介** | 用一张消费级显卡跑出 20 秒双角色快剪日漫短剧：ComfyUI 官方节点接线、Ref2VA 六段式提示词规范、分镜节奏标准、静默失效排查 |
| **Topics** | `comfyui` `minimax-h3` `ai-video` `text-to-video` `image-to-video` `short-drama` `anime` `workflow` `tutorial` |
| **License** | MIT（见 `LICENSE`，内含权重与示例角色的免责说明） |

> ⚠️ **GitHub 仓库名不能用空格和中文标点**，所以：
> 标题写「基于 Comfy 和 MiniMax H3 的实战教程 —— 以 DeepSeek 鲸鱼娘为例」，
> 仓库名用 ASCII 的 `comfy-minimax-h3-tutorial`。
> 标题会显示在 README 首行和仓库首页 About 里。

## 2. 上传前检查（全部已通过）

| # | 检查项 | 状态 |
|---|---|---|
| 1 | Python 脚本 `py_compile` 通过 | ✅ |
| 2 | `bash -n` 检查 `install_nodes.sh` | ✅ |
| 3 | 文档内交叉引用（12 条）全部指向存在的文件 | ✅ |
| 4 | 脱敏：15 类敏感串全部 0 命中 | ✅ |
| 5 | 无绝对本机路径（`C:\` / `F:\` / 内网 IP） | ✅ |
| 6 | 无本机角色私有名（示例角色的对外称呼已泛化） | ✅ |
| 7 | 无通知 / 消息推送等无关工具痕迹 | ✅ |
| 8 | `.gitignore` 已排除 `out/` `*.mp4` `*.part` `__pycache__` | ✅ |
| 9 | README 首行是中文完整标题 | ✅ |
| 10 | LICENSE 写明权重与示例角色的授权边界 | ✅ |
| 11 | 文档内交叉引用全部指向存在的文件 | ✅ |

## 3. 建议的推送步骤

```bash
# ① 进目录
cd h3-video-guide

# ② 初始化（若已存在 .git 就跳过）
git init

# ③ 确认将要提交的文件（应只有源码与文档）
git add -A
git status --short          # 确认没有 mp4 / part / __pycache__

# ④ 提交
git commit -m "docs: 基于 Comfy 和 MiniMax H3 的实战教程（以 DeepSeek 鲸鱼娘为例）"

# ⑤ 建远端（在 GitHub 上先建空仓库，勾选 README/License/.gitignore 全部不勾）
git remote add origin https://github.com/<你的账号>/comfy-minimax-h3-tutorial.git
git branch -M main
git push -u origin main
```

## 4. GitHub 仓库设置建议

| 设置 | 建议值 | 原因 |
|---|---|---|
| Description | 见 §1 一句话简介 | 搜索结果里会显示 |
| Topics | 见 §1 | 让别人搜得到 |
| License | MIT | 与 `LICENSE` 文件一致 |
| 默认分支 | `main` | |
| Discussions | **开启** | 适合放"卡住了求帮忙"的帖子，能提权重复现率 |

## 5. 可选增强（做完后教程更好用）

| # | 增强项 | 说明 |
|---|---|---|
| 1 | **英文版 README** | 面向国际读者（国内这类教程几乎没有英文版） |
| 2 | `examples/` 目录 | 放 2–3 份**自己搭的**工作流 JSON（不含任何版权素材） |
| 3 | `CONTRIBUTING.md` | 说明实测数据来自什么机器，方便读者判断是否适用 |
| 4 | 录一段 30 秒的成片 demo | 放仓库顶部，说服力最强 |
| 5 | 录一段 30 秒的成片 demo | 放仓库顶部 GIF/视频，说服力最强 |

## 6. 诚实说明（建议写进 README）

这几点如实写出来，别人踩坑时才知道是教程的局限还是模型的问题：

- **无法原生输出 1080P** —— 最高约 0.9MP（1280×736），更高要后期超分。
- **>15 秒的单段视频不稳** —— 长片必须拆段接续。
- **不做精准口型同步** —— 原生音频适合环境音，对白要后期配音。
- **多人同镜是已知短板** —— 一个镜头重点刻画一位角色。
- **参考图质量决定一切** —— 特征少、背景杂的参考图会让角色直接画错。
- 实测数据来自单张 16GB 显卡（见 README §1.2），**其他显卡耗时会有出入**。
