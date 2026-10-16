---
name: rebuild-workflow
description: 自有 APK/游戏"源码丢失 → 逆向重建 → 再开发 → 交付工程+试玩包"全流程总控。接手任何"只有安装包没有源码、要重建成可迭代新工程"的项目时首先加载本 skill；它负责阶段划分、输入完整性检查、决策门、出口标准，并把具体阶段分派给其他 rebuild-* skill。触发词：逆向重建、源码丢失、离职未交接、APK 重建、重做一个同款、换皮重建。
version: 1.2.0
owner: ElevenZhou
---

# rebuild-workflow — 逆向重建全流程总控

## 何时用 / 何时不用

- **用**：公司自有产品，只剩 APK/XAPK/EXE，需要重建成可维护新工程，并最终交付「工程源码 + 试玩 APK」。
- **不用**：第三方产品（无权属）——直接拒绝，不开工；只需改一个资源/文案的小修补——用 `rebuild-asset-recovery` 即可。

## 八阶段总流程（严格按序，每阶段有出口标准）

| 阶段 | 内容 | 执行 skill | 出口标准（不达标不进下一阶段） |
|---|---|---|---|
| S0 授权立项 | 输入检查表、scope.md、task_spec.yaml、目录骨架 | 本 skill | 检查表必需项 #1–#7 全部满足（或负责人书面接受风险）；C/S 型产品 #10 已确认；负责人确认 |
| S1 侦察解包 | 哈希基线、引擎识别、解包 | `rebuild-recon` | 引擎类型 machine-verified；资源总量清单（含全部分包）；**源码可恢复性结论** |
| S2 静态分析 | docs/01-09 九篇基线文档 | `rebuild-recon` | 九篇齐全；09 的 P0 项已挂到里程碑（项目既有门禁更严时以严者为准）；负责人看过 01+09 |
| S3 资源回导 | 样品先行 → 批量回导 | `rebuild-asset-recovery` | 样品 100% PASS；批量报告 fail=0 或已登记；版权/再分发审查完成 |
| S4 产品定义 | 产品文档、决策门 D1-D9、品牌、微创新、开发计划 | `rebuild-product-design` | 决策门全部有结论且负责人确认；开发计划含每个 M 的出口标准 |
| S5 工程再开发 | M0-M5 里程碑开发 | `rebuild-dev-milestones` | 每个 M 的进展文档 + 测试全绿 |
| S6 真机采证校准 | 原包对标、数值口径采证、自家包验收（原包不可运行时只做新包验收） | `rebuild-device-evidence` | P0 占位全部关闭、转 AB 或经负责人审定 |
| S7 打包交付 | 签名 APK、工程归档、交付清单 | `rebuild-build-release` | 交付清单逐项打勾 + 真机安装运行通过 + keystore 双人双地备份 |

> S5 与 S6 实际会交替进行（M4 = 真机校准）。阶段图见 `references/stage-map.md`。

## 六条铁律

1. **先授权后动手**：没有 scope.md（权属 + 范围 + 边界）不开工；**只做 scope.md 明确勾选的分析类型**，未勾选 = 未授权（动态、联网/服务端分别单独确认）。
2. **先文档后编码**：docs/01-09 过负责人复核，才写第一行重建代码。
3. **先骨架后血肉**：M0（工具链 + 空骨架 + 资源样品）冒烟通过才进 M1。
4. **出口标准硬卡**：达不到就停，不"差不多先往下走"。
5. **不确定即登记**：所有"看不清 / 先跳过 / 占位"当场写进 `待优化清单.md`，禁止只存在于对话里。
6. **禁止编造**：拿不准的数值标 `P0 占位`，所有结论带置信度（machine-verified / human-reviewed / human-reported）。

## S0 操作步骤

1. 用 `references/input-checklist.md` 逐项向负责人收集输入（必需 7 项 + 后续 3 项），缺项写入 scope.md「开工风险」；先按其中「环境前置」自查一遍。
2. 复制仓库 `templates/project/` 到 `项目X/`，填写 `scope.md`、`task_spec.yaml`。
3. 建目录：`docs/ evidence/ extracted/ assets/ rebuild/ recon/ runs/`。
4. 原包 `sha256sum` 写入 scope.md。
5. 让负责人确认 scope.md → 进入 S1（加载 `rebuild-recon`）。

## S1 源码可恢复性结论（必做，写进 recon/S1-事实基线.md）

不要凭渠道名判断"能找回源码"（如"有 EAS/Unity Cloud 账号就能找回"）。逐项给出 **能拿回 / 拿不回 / 未验证**：
1. 原始源码归档（仓库、网盘、构建机）；2. 未压缩脚本/JS 或 source map（含 `sourcesContent` 才算）；3. 构建云产物（先确认里面到底是安装包、字节码还是源码，例：Expo `updates.ENABLED=false` 时 EAS Update 里没有 JS 包）；4. 包内可反编译程度（字节码/IL2CPP 签名/加密脚本）。
结论决定 D1 路线：拿回源码 → R1；只拿回可读逻辑 → R2；只有契约和资产 → R3。

## 人工决策门（Agent 必须暂停等人确认，不得自行跳过）

- S0 结束：scope.md 确认
- S2 结束：docs/01 + 09 过目
- S1 结束：源码可恢复性结论（决定后续走 R1 还是 R2/R3）
- S4：D1-D9 每一项（见 `rebuild-product-design`）
- 每个里程碑出口
- S7 交付前：品牌/外发许可

## 引擎适配

流程本身与引擎无关；引擎相关的工具链与坑在 `references/engines/`：
- `godot.md` — ✅ 已在项目 D 全程验证
- `react-native-hermes.md` — 🟡 项目 C 实战中（Expo + Hermes v96，S1-S3 + M0 已验证）
- `unity-il2cpp.md` — 🟡 项目 F 实战中（Unity 6 / metadata 31，S1-S3 + M0 部分验证；项目 E 复用）
- `_template.md` — 其他引擎（Cocos / 原生等）尚无真实案例，**遇到时照模板新建，项目结束回写**

## 活文档纪律

- `待优化清单.md` 是唯一登记处，分池：立即池 / M#池 / 归档区（带日期）。每个开发节点过一遍立即池。
- 每日工作日志（如有 .workbuddy/memory）：坑写「根因 + 修法 + 一句经验」。

## 项目收尾（强制，持续进化的来源）

项目交付后执行 `references/retro-checklist.md`：复盘 → 把新坑/新方法写回对应 skill → 提 PR 到 apk-rebuild-skills 仓库。**不回写 = 项目未结项。**

## 卡住时

查 `references/debug-playbook.md`（按症状索引）。

## 相关 skill

`rebuild-recon` · `rebuild-asset-recovery` · `rebuild-product-design` · `rebuild-dev-milestones` · `rebuild-device-evidence` · `rebuild-build-release`

## 变更记录
- 1.2.0（2026-10-16）输入检查表分必需/后续两类（C/S 型 #10 必需）；铁律 1 明确未勾选即未授权；S1 出口加源码可恢复性结论；既有门禁以严者为准；决策门扩到 D9；S3/S6/S7 出口同步（项目 C、F 反馈）。
- 1.1.0（2026-10-16）引擎适配新增 react-native-hermes（项目 C）、unity-il2cpp（项目 F）。
- 1.0.0（2026-10-01）从项目 D（Meowdoku → PawStar，Godot 4.6）全程提炼。
