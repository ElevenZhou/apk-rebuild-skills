# apk-rebuild-skills

公司内部用的 **AI Agent Skill 包**：把"自有产品源码丢失 → 逆向重建 → 再开发 → 交付工程 + 试玩 APK"整套流程固化下来。目标是让任何同事接手这类项目时都按同一套流程、同一套出口标准走，不依赖个人经验。

适用于 WorkBuddy / CodeBuddy / Claude Code / Codex 等支持 `SKILL.md` 的 Agent 工具。

> ⚠️ 只用于**公司自有、权属明确**的产品。第三方产品一律不做。

## 包含的 skill

| Skill | 阶段 | 一句话 | 可单独使用 |
|---|---|---|---|
| `rebuild-workflow` | 总控 S0–S7 | 阶段、输入检查表、决策门、出口标准、复盘回写 | 入口 |
| `rebuild-recon` | S1–S2 | 解包、引擎识别、docs/01-09 九篇文档 | ✅ 只做分析 |
| `rebuild-asset-recovery` | S3 | 资源回导（Godot 全套脚本） | ✅ 只提资源 |
| `rebuild-product-design` | S4 | 产品文档、决策门 D1-D7、品牌、微创新、开发计划 | ✅ 规划新版本 |
| `rebuild-dev-milestones` | S5 | M0-M5 里程碑开发与纪律 | ✅ 任何重写项目 |
| `rebuild-device-evidence` | S6 | ADB 真机自动化 + 录屏抽帧 + 视觉模型读图 | ✅ 任何真机测试 |
| `rebuild-build-release` | S7 | 打签名 APK、真机冒烟、交付清单 | ✅ 任何 Godot 打包 |

引擎支持：**Godot 4.x 已全流程验证**；Unity / Cocos / 原生只有模板（`skills/rebuild-workflow/references/engines/_template.md`），等第一个真实项目做完再补全。

## 安装（3 步）

```powershell
# 1. 拉取（私有仓库，需要先被加为协作者）
git clone https://github.com/ElevenZhou/apk-rebuild-skills.git D:/apk-rebuild-skills

# 2. 安装：把 skills/* 链接到本机 Agent 的 skills 目录（目录联接，之后 git pull 就是更新）
powershell -ExecutionPolicy Bypass -File D:/apk-rebuild-skills/install/install.ps1
#   可选参数：-Targets workbuddy,claude,codex   默认 workbuddy
#   macOS/Linux：bash install/install.sh

# 3. 重启 Agent 工具，在技能列表里确认出现 rebuild-*
```

更新：`git pull` 即可（安装用的是目录联接，不需要重新安装）。

### 前置环境（按需）
| 用途 | 需要 |
|---|---|
| 解包分析 | Python 3.10+、apktool、jadx |
| Godot 项目 | 与原包同主版本的 Godot（console 版），放纯英文路径 |
| 真机采证 | adb（platform-tools）、`pip install pillow numpy opencv-python` |
| 视觉读图 | 环境变量 `VISION_API_KEY`（可选 `VISION_API_URL`、`VISION_MODEL`） |
| 打包 | JDK 17/21、Android build-tools ≥35、导出模板 |

**所有工具链放纯英文路径**（如 `C:/android-sdk`），中文路径会导致多个工具静默失败。

## 使用示例

**开一个新项目（完整流程）**
> 用 rebuild-workflow 开一个新的重建项目，原包在 D:/work/项目E/xxx.xapk，负责人是张三。

Agent 会先跑输入检查表、生成 scope.md，等你确认后再进入解包。

**只分析一个包**
> 用 rebuild-recon 分析 D:/apk/foo.apk，先识别引擎，再写 docs/01 和 05。

**只打包**
> 用 rebuild-build-release 把 D:/proj/game 打成签名 APK 装到手机上。

**真机验证**
> 用 rebuild-device-evidence 启动 com.foo.game，截首页，找到"开始"按钮点进去，告诉我关卡号。

## 仓库结构

```
skills/<skill>/SKILL.md          技能本体（Agent 读这个）
skills/<skill>/references/       模板、速查表、引擎手册（按需加载）
skills/<skill>/scripts/          参数化脚本，不含路径和密钥
templates/project/               新项目骨架（scope、task_spec、待优化清单）
docs/SOP.md                      给人读的完整 SOP
docs/cases/                      项目案例复盘
install/                         安装脚本
tools/lint_skills.py             格式检查 + 密钥扫描（提交前跑）
```

## 参与维护
见 [CONTRIBUTING.md](CONTRIBUTING.md)。核心一条：**每个项目结束都要提一个复盘 PR**，这是这套 skill 持续进化的唯一来源。

## 版本
见 [CHANGELOG.md](CHANGELOG.md)。
