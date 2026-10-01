---
name: rebuild-recon
description: 逆向重建 S1 侦察解包 + S2 静态分析。对自有 APK/XAPK/EXE 做哈希基线、引擎/加固识别、解包，并产出 docs/01-09 九篇基线文档（带置信度标注）。单独使用场景：只想摸清一个自家安装包的结构、SDK、接口、存储和资源，不一定要重建。触发词：解包、APK 分析、引擎识别、逆向文档、九篇文档。
version: 1.0.0
owner: ElevenZhou
---

# rebuild-recon — 侦察解包与静态分析

## 何时用 / 何时不用
- **用**：已有 scope.md 授权的自有安装包，需要了解其引擎、结构、SDK、接口、资源。
- **不用**：没有权属确认（先走 `rebuild-workflow` S0）；只想导出资源（直接 `rebuild-asset-recovery`）。

## 需要的输入
- 原包文件（APK/XAPK/AAB/EXE）、scope.md（单独使用时至少有一句权属确认）。
- 工具：`unzip`、`sha256sum`；按引擎：apktool + jadx（原生 / 通用 manifest）、GDRE Tools（Godot）、AssetRipper/Il2CppDumper（Unity）、hermes-dec（React Native + Hermes，见 `engines/react-native-hermes.md`）。

## S1 步骤
1. **哈希基线**：`sha256sum <包>` → 写入 scope.md。XAPK 先解 zip，对内部每个 APK 也做哈希。
2. **引擎识别**：`python scripts/detect_engine.py <包>` → 根据 so/特征文件给出引擎与加固判断（machine-verified）。
3. **解包**：
   - 所有包：`apktool d <apk> -o extracted/apktool`（RN 等业务不在 Java 层的大包可先 unzip，apktool 按需，见引擎专节）（manifest、权限、资源）+ `jadx -d extracted/jadx <apk>`（Java 层 SDK/桥接）。
   - 引擎专用：见 `rebuild-workflow/references/engines/<引擎>.md`。
4. **资源清单**：`python scripts/asset_manifest.py extracted/ > assets/manifest.json`（按扩展名计数 + 体积）。

S1 出口：引擎类型（附日志证据）、加固结论、资源总量清单。

## S2 九篇文档（固定编号与命名）

| 文件 | 内容 | 主要信息源 |
|---|---|---|
| docs/01-概述.md | 产品定位、版本线、包名、商店数据、是否在架 | manifest + 商店页（联网核实） |
| docs/02-功能模块.md | 页面/场景/玩法逐一描述 | 场景文件名、文案 i18n、原包录屏 |
| docs/03-接口文档.md | 单例/插件桥、埋点事件、AB 键、服务端点 | jadx、配置 json、字符串 |
| docs/04-本地存储.md | 存档结构、键名、版本迁移 | 代码/存档样本 |
| docs/05-权限与SDK.md | 权限、第三方 SDK 清单及用途 | manifest、jadx 包名 |
| docs/06-异常与容错.md | 断网/存档损坏/广告失败降级 | 代码、实测 |
| docs/07-安全逻辑.md | 加密、校验、cheat/debug 面（重建时剔除） | 代码 |
| docs/08-资源清单.md | manifest 详表 | manifest.json |
| docs/09-人工复核清单.md | 所有不确定项，每项 P0/P1/P2 | 汇总前 8 篇 |

模板：`references/doc-templates.md`。

### 写作规则
- **每个结论带置信度**：`machine-verified`（工具输出可复现）/ `human-reviewed`（人对过录屏或实机）/ `human-reported`（口述待验证）。
- 拿不准的数值写 `P0 占位`，进 09 篇，**禁止编造**。
- 涉及商业判断（是否在架、竞品）必须联网核实并附链接和日期。
- 密钥/token 类发现只记录"存在 + 位置"，**不把值写进文档**。

S2 出口：九篇齐全；09 篇里每个 P0 都标了计划在哪个里程碑关闭；负责人看过 01 与 09。

## 常见坑
- XAPK = zip 套多个 APK + OBB/assetpack，资源常在 assetpack 里，不要只解 base.apk。
- 加固包（360/梆梆/腾讯乐固等）jadx 只看到壳 → 文档改靠真机动态观察，预期降级写进 09。
- Godot 加密脚本（.gdc 加密）无法还原逻辑 → 只取契约（接口名、配置、埋点），玩法按规则重写。

## 相关 skill
上游 `rebuild-workflow`（S0）→ 下游 `rebuild-asset-recovery`（S3）、`rebuild-product-design`（S4 使用九篇文档）。

## 变更记录
- 1.0.0（2026-10-01）项目 D 提炼。
