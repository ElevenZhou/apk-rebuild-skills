---
name: rebuild-device-evidence
description: 真机采证与验收：通过 ADB 全自动操作安卓真机（启动、截图、像素定位点击、录屏），或对用户自然游玩录屏做场景切变抽帧，再交给视觉模型读取画面状态，用于对标原包数值口径、校准 P0 占位、验收自家新包。单独使用场景：任何手游/应用的真机自动化测试与录屏分析。触发词：真机测试、ADB 截图、采证、录屏分析、抽帧、实机验证、数值校准。
version: 1.1.0
owner: ElevenZhou
---

# rebuild-device-evidence — 真机采证与验收

## 何时用 / 何时不用
- **用**：M4 数值口径对标原包；每个里程碑在真机上验收自家包；S7 交付前冒烟。
- **不用**：纯逻辑问题（先用 headless 测试定位）。

## 先判断：原包能不能跑
- **能跑**：正常对标原包采证（通道一/二）+ 新包验收。
- **不能跑或不能联网**（服务端已下线、强制更新、账号体系失效）：**S6 只做新包验收**，不做原包采证；数值口径在 S4 由负责人自定义/审定，docs/09 的 P0 标"经负责人审定"关闭，并在 `M4-*.md` 写明原因（项目 C）。
- 不要为了让原包跑起来去改包、抓包伪造服务端——超出授权范围（见 scope.md 勾选项）。

## 需要的输入
- 安卓真机，已开 USB 调试，`adb devices` 能看到；原包和/或自家包已安装。
- Python 3 + `pillow numpy opencv-python`。
- 视觉模型（可选）：环境变量 `VISION_API_URL`、`VISION_API_KEY`、`VISION_MODEL`（Gemini 兼容接口）。**Key 不写进脚本、不提交仓库。**

## 通道一：ADB 全接管（短流程、需精确操作）
```bash
adb devices
adb -s <SN> shell monkey -p <包名> -c android.intent.category.LAUNCHER 1   # 启动
adb -s <SN> exec-out screencap -p > shot.png                               # 截图
python scripts/find_color.py shot.png --rgb 240,140,40 --tol 40             # 像素定位按钮中心
adb -s <SN> shell input tap <x> <y>                                         # 点击
python scripts/vision_ask.py shot.png "当前是什么页面？读出关卡号、生命数"   # 视觉读图
```
规则：
- **点击坐标必须像素定位**（找目标色块中心），不允许目测估算。
- 每步截图存 `evidence/playtest/<日期>-<步骤>.png`，结论引用截图文件名。
- 双击/长按等手势：`input swipe x y x y <ms>` 模拟长按；双击两次 tap 间隔要短于游戏的双击判定窗口（D 项目约 250ms）。

## 通道二：用户录屏 + 抽帧（复杂流程：结算、广告、引导）
1. 让用户在真机上自然玩 3-5 分钟并录屏（`adb shell screenrecord` 或手机自带录屏）。
2. `python scripts/extract_keyframes.py video.mp4 out_dir --threshold 28` → 场景切变关键帧 + 时间线。
3. 对关心的切变点 ±1.2s 再细抽（`--start/--end` 参数）。
4. `python scripts/vision_ask.py frame1.png frame2.png … "问题"` 批量读图。

比 ADB 硬点效率高，适合一次性流程。

## 采证清单（通用口径，按需选）
- 开局预置数量 / 难度分档
- 失误惩罚（扣多少、动效、是否留痕）
- 输入语义（单击/双击/长按/划选），双击窗口 ms 级
- 结算文案策略（按玩家行为选文案时，记录**策略**而不只是文案）
- 广告出现时机与无填充时的表现
- HUD/顶栏信息架构逐元素对齐

## 结论落地（两层同时写）
1. 数值写进工程 `cfg/`（校准值，注明来源截图）；
2. 记录写进 `M4-<主题>采证.md` + 待优化清单关闭对应 P0。

## 常见坑
- 视觉模型读数会前后不一致 → 关键数值用像素采样交叉验证；渐变色区域靠截图分类不可靠，改用交互反馈验证。
- OpenCV `imwrite` 中文路径静默失败 → 脚本已改用 `imencode + 二进制写`。
- 截图带状态栏 → 坐标以截图像素为准，和 `input tap` 坐标系一致（不需要换算）。

## 相关 skill
被 `rebuild-dev-milestones`（M4 与每个 M 验收）、`rebuild-build-release`（交付冒烟）调用。

## 变更记录
- 1.1.0（2026-10-16）新增"原包能不能跑"前置判断：原包不可运行/联网时只做新包验收，数值在 S4 审定（项目 C 复盘 C-10）。
- 1.0.0（2026-10-01）项目 D M4 采证 + APK 实机验收提炼；脚本参数化，视觉 Key 改环境变量。
