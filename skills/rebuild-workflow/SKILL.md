---
name: rebuild-workflow
description: 任意作品（自有 / 第三方 / 权属待确认）的“安装包 → REA 逆向取证 → 重建 → 再开发 → 交付工程+试玩包”全流程总控。接手只有安装包、需要方法级静态分析、真机采证和可维护新工程的任务时使用；负责权属登记、阶段、决策门、出口标准和发布门禁，并调度 rebuild-* 与 REA。正式发布前必须逐产品人工确认所有权，由人工执行发布，Agent 不得自动发布。输入可为本地 APK / 游戏名 / Google Play 链接 / 三方市场链接，A0 负责获取原包；多项目并行时按 project-layout.md 回写各项目 project.json 供看板聚合。
version: 1.4.2
owner: ElevenZhou
---

# rebuild-workflow — 逆向重建全流程总控（REA 联合模式）

> REA 集成规则见 [references/rea-integration.md](references/rea-integration.md)。REA 负责逆向证据，本文负责权属登记、决策、重建、交付和发布门禁。
> 现成成果与工具检索见 [references/prior-art.md](references/prior-art.md)。
> 项目目录规范与看板状态源见 [references/project-layout.md](references/project-layout.md)。

## 合规模型（v1.4.0 起，必读）

**分析放行 / 发布管控**，两件事分开：

| 环节 | 规则 |
|---|---|
| 作品准入（S0） | **允许所有作品**进入分析与重建流程：公司自有、权属待确认、第三方、来源未知均可。权属只做**状态登记**，不再是开工阻断条件 |
| 分析范围（S0） | 仍逐项勾选：静态分析 / 真机动态 / 联网与服务端 / 产物用途。**没勾 = 不做**，这是操作边界，与作品准入无关 |
| 安全红线（全程） | 禁止绕过登录、验证码、风控、证书校验或服务端访问控制；不复用第三方生产服务；不把真实账号/Token/短信写进证据、文档或交付物；不公开发布反编译产物 |
| **正式发布（S7 前，G-PUBLISH）** | **每个产品逐个人工确认所有权**（书面凭证 + 确认人 + 日期），**由人工执行发布**。Agent 不得自行对外发布、上架或外发包 |
| 未确认所有权时 | 只能产出 `仅内部` 的试玩包与工程，交付物打内部标记，不得对外分发；此状态写进 `scope.md` 与交付清单 |

> 判断口诀：**能不能分析 ≠ 能不能发布**。放宽的是前者；后者始终由人把关。
> 分析第三方产品仍受当地法律与服务条款约束，本 skill 不提供法律意见；有疑问时由负责人决定。

## 何时用 / 何时不用

- **用**：任意作品，只剩 APK/XAPK/EXE，需要分析结构、重建成可维护新工程，并最终交付「工程源码 + 试玩 APK」；或只需竞品研究抽象 / 取证。
- **不用**：只需改一个资源/文案的小修补 → 用 `rebuild-asset-recovery`；只需打包 → 用 `rebuild-build-release`。

## 看板与状态回写（多项目并行，v1.4.2 起）

多个项目并行时，进度与卡点**不靠记忆、不靠会话上下文**。每个项目根目录放一份 `project.json` 作为看板唯一状态源，规则见 [references/project-layout.md](references/project-layout.md)，模板 `templates/project/project.json`。

| 时机 | 必须回写 |
|---|---|
| A0 完成 / S0 立项 | `stage`、`completed`、`ownership`、`publish_gate`、`summary` |
| 任一阶段出口通过 | `completed` 追加该阶段、`stage` 前移、`progress` |
| 出现或解除卡点 | `blockers[]`、`status`、`next_action` |
| **每次会话结束前** | 至少 `updated_at`、`next_action`、`blockers[]`，并说明本次改了什么 |

卡点必须写全「卡在哪 / 等谁 / 要做什么」；**卡住就标 `blocked`，不要为了好看写 `active`**。超过 7 天未回写，看板标「数据可能过时」。

```bash
python scripts/build_dashboard.py --root "<项目父目录>" --out "<父目录>/通用工程/dashboard/index.html"
python scripts/build_dashboard.py --root "<项目父目录>" --check
```

看板**只反映状态**：不判定阶段是否达标、不替代出口标准、不自动关闭卡点、不自动发布；G-PUBLISH 仍由人执行。本层不占 S 阶段编号，不改七条铁律、D1–D9 与输入检查表。

## A0 原包获取（流程第一步，不占 S 阶段编号）

**有包就进，没包才下。** A0 的产出就是输入检查表 **#1 原包 + sha256**；细则见 [references/artifact-acquisition.md](references/artifact-acquisition.md)，脚本 `scripts/fetch_artifact.py`。

| 用户给的 | 动作 |
|---|---|
| 本地 APK/XAPK/EXE 路径 | **不下载**：校验 + 归档 + 登记来源 → 直接进 S0 |
| 游戏名 | 搜候选包名 → **人工确认**（同名产品多，Agent 不得自选）→ 下载 |
| Google Play 详情页链接 | 提取 `?id=` 包名 → 走公开镜像下载（Play 不提供 APK 直链） |
| 三方市场下载页 / 直链 | 直接下载（APKPure / APKCombo / APKMirror 等） |

```bash
python scripts/fetch_artifact.py --play-url "https://play.google.com/store/apps/details?id=com.foo.game" --out "项目X/input"
# 另有 --from-file / --name（配 --pick N）/ --market-url，见细则
```

A0 出口：文件头合法且 >1MB、`sha256` 写入 scope.md、`input/artifact-source.json` 留痕、商店页链接记入 #6。**付费 / 需登录 / 区域受限应用不自动下载**，由负责人用 `--from-file` 提供已合法取得的包体；不绕过反爬、验证码或会员墙。A0 不改变八阶段编号、铁律、决策门与 G-PUBLISH。

## 八阶段总流程（严格按序，每阶段有出口标准）

| 阶段 | 内容 | 执行 skill | 出口标准（不达标不进下一阶段） |
|---|---|---|---|
| S0 立项登记 | 输入检查表、**权属状态登记**、scope.md、task_spec.yaml、目录骨架、**P0 现成成果检索** | 本 skill | 检查表必需项 #1–#7 满足（或负责人书面接受风险）；C/S 型 #10 已确认；P0 已执行并留痕；负责人确认 |
| S1 侦察解包 | 哈希基线、引擎识别、解包 | `rebuild-recon` | 引擎类型 machine-verified；资源总量清单（含全部分包）；**源码可恢复性结论** |
| S2 静态分析 | docs/01-09 九篇基线文档 | `rebuild-recon` | 九篇齐全；09 的 P0 项已挂到里程碑（项目既有门禁更严时以严者为准）；负责人看过 01+09 |
| S3 资源回导 | 样品先行 → 批量回导 | `rebuild-asset-recovery` | 样品 100% PASS；批量报告 fail=0 或已登记；版权/再分发审查完成 |
| S4 产品定义 | **P4 参考实现检索**、产品文档、决策门 D1-D9、品牌、微创新、开发计划 | `rebuild-product-design` | 决策门全部有结论且负责人确认；开发计划含每个 M 的出口标准 |
| S5 工程再开发 | M0-M5 里程碑开发 | `rebuild-dev-milestones` | 每个 M 的进展文档 + 测试全绿 |
| S6 真机采证校准 | 原包对标、数值口径采证、自家包验收（原包不可运行时只做新包验收） | `rebuild-device-evidence` | P0 占位全部关闭、转 AB 或经负责人审定 |
| S7 打包交付 | **G-PUBLISH 人工发布门禁**、签名 APK、工程归档、交付清单 | `rebuild-build-release` | 交付清单逐项打勾 + 真机安装运行通过 + keystore 双人双地备份 + **发布授权已人工确认（或明确标记仅内部）** |

REA 作为横向证据层贯穿 S1/S2/S3/S6/S7：每个阶段只引用与该阶段出口匹配的 REA Evidence，不把静态完整覆盖当成原始源码恢复或运行时证明。

> S5 与 S6 实际会交替进行（M4 = 真机校准）。阶段图见 `references/stage-map.md`。

## 七条铁律

1. **先登记后动手**：scope.md 必须存在，记录**权属状态**、范围边界与 P0 检索结论；**只做 scope.md 明确勾选的分析类型**，未勾选 = 未授权（动态、联网/服务端分别单独确认）。权属状态未确认**不阻断分析与重建**，但阻断正式发布。
2. **先文档后编码**：docs/01-09 过负责人复核，才写第一行重建代码。
3. **先骨架后血肉**：M0（工具链 + 空骨架 + 资源样品）冒烟通过才进 M1。
4. **出口标准硬卡**：达不到就停，不"差不多先往下走"。
5. **不确定即登记**：所有"看不清 / 先跳过 / 占位"当场写进 `待优化清单.md`，禁止只存在于对话里。
6. **禁止编造**：拿不准的数值标 `P0 占位`，所有结论带置信度（machine-verified / human-reviewed / human-reported；外部旁证另标 external-reference，不可升级为已验证）。
7. **发布归人**：正式发布前逐产品**人工确认所有权**，发布动作由人执行；Agent 不得自动对外发布、上架或分发。未确认 → 仅内部。

## P 横切检查点（不占阶段编号）

不新增 S 阶段，避免 `stage-map.md`、各 SKILL.md、产物表与复盘清单的编号全部失配。P 层可单独启停、灰度或摘除。操作细则见 [references/prior-art.md](references/prior-art.md)。

| 检查点 | 触发 | 产出 | 影响 |
|---|---|---|---|
| **P0** | S0 scope 确认后、S1 解包前 | `scope.md` 的 `prior_art` 表：命中项、License、健康度、可复用比例、检索日期与关键词 | 作为 **D1 路线（R1/R2/R3）** 前置输入；未命中也必须留痕 |
| **P4** | S2 九篇完成后、S4 拍板前 | 同类玩法 / 格式的开源实现参考清单 | 喂给 **D5 微创新** 与产品文档「保留/修改/新增/删除」四列 |

P 层用到的外部能力（按 `prior-art.md` 的准入清单）：

| 能力 | 定位 | 接入 |
|---|---|---|
| `alexgaoth/awesome-reverse-engineered` | **已逆向成果索引**（17,700+，夜间刷新，带健康度） | 网站 https://awesome.alexgaoth.com/ ；`npx skills add alexgaoth/awesome-reverse-engineered` ；或其 MCP 只读工具 `search_reverse_engineered` / `get_reverse_engineered_project` / `list_reverse_engineered_categories` |
| `morluto/awesome-reverse-engineering` | **按任务找工具的方法论地图** | 供 `engines/*.md` 补工具选型：Language runtimes and packagers / Game reverse engineering / AI-assisted analysis 三节 |
| `morluto/rea` | **工具本体**，S1/S2 证据链，已在 `rea-integration.md` 落地 | MCP 见 `outputs/REA-搭建指令.md`、 WorkBuddy `mcp.json` |
| `CoplayDev/unity-mcp` | Unity 项目 S5 编辑器自动化（编译、场景检查、SmokeTest），**试点** | 项目 F / E 的 M0 工具链表登记版本后启用；不解决 Unity 许可证激活问题 |

> 三者定位不混用：**rea = 工具本体 / morluto awesome = 方法论 / alexgaoth = 成果索引**。
> 索引命中不替代 S0 权属登记，更不替代 G-PUBLISH 人工确认；不把他人对第三方闭源产品的逆向实现搬进交付物。

## S0 操作步骤

0. **先执行 A0 原包获取**（`artifact-acquisition.md`）：本地已提供 APK → 跳过下载直接进本步；否则按游戏名 / Play 链接 / 三方市场链接下载并校验，产出 `input/artifact-source.json`。
1. 用 `references/input-checklist.md` 逐项收集输入（必需 7 项 + 后续 4 项），缺项写入 scope.md「开工风险」；先按其中「环境前置」自查一遍。
2. **登记权属状态**（自有已确认 / 自有待确认 / 第三方 / 未知），不因"第三方"或"待确认"拒绝开工。
3. 复制仓库 `templates/project/` 到 `项目X/`，填写 `scope.md`、`task_spec.yaml`（含 `prior_art` 与「发布授权」段）。
4. 建目录：`docs/ evidence/ extracted/ assets/ rebuild/ recon/ runs/`。
5. 原包 `sha256sum` 写入 scope.md。
6. **执行 P0 现成成果检索**（`prior-art.md`），结论写 `prior_art`；未命中也记录检索日期与关键词。
7. 让负责人确认 scope.md → 进入 S1（加载 `rebuild-recon`）。

### REA 联合入口

当输入是 APK/XAPK/APKS 且需要理解类、方法、接口、存储或调用链时，S1/S2 必须读取 `references/rea-integration.md`，并在 scope.md 记录：REA provider、JADX/APKTool 版本、是否启用 ADB、是否允许联网和真实账号。REA 失败或 coverage partial 时，降级为 R2/R3 并把阻塞写入 docs/09，不得跳过门禁。

## S1 源码可恢复性结论（必做，写进 recon/S1-事实基线.md）

不要凭渠道名判断"能找回源码"（如"有 EAS/Unity Cloud 账号就能找回"）。逐项给出 **能拿回 / 拿不回 / 未验证**：
1. 原始源码归档（仓库、网盘、构建机）；2. 未压缩脚本/JS 或 source map（含 `sourcesContent` 才算）；3. 构建云产物（先确认里面到底是安装包、字节码还是源码，例：Expo `updates.ENABLED=false` 时 EAS Update 里没有 JS 包）；4. 包内可反编译程度（字节码/IL2CPP 签名/加密脚本）。
结论决定 D1 路线：拿回源码 → R1；只拿回可读逻辑 → R2；只有契约和资产 → R3。**P0 命中现成实现时，也要一并纳入 D1 判断。**

## 人工决策门（Agent 必须暂停等人确认，不得自行跳过）

- **A0**：游戏名搜出多个候选包名、包名/版本与描述不符、来源可疑时，等人确认，不得自选
- S0 结束：scope.md 确认（含权属状态、P0 结论）
- S2 结束：docs/01 + 09 过目
- S1 结束：源码可恢复性结论（决定后续走 R1 还是 R2/R3）
- S4：D1-D9 每一项（见 `rebuild-product-design`）
- 每个里程碑出口
- **S7 交付前：G-PUBLISH —— 逐产品人工确认所有权 + 品牌/外发许可；由人工执行发布**

## 引擎适配

流程本身与引擎无关；引擎相关的工具链与坑在 `references/engines/`：
- `godot.md` — ✅ 已在项目 D 全程验证
- `react-native-hermes.md` — 🟡 项目 C 实战中（Expo + Hermes v96，S1-S3 + M0 已验证）
- `unity-il2cpp.md` — 🟡 项目 F 实战中（Unity 6 / metadata 31，S1-S3 + M0 部分验证；项目 E 复用）
- `_template.md` — 其他引擎（Cocos / 原生等）尚无真实案例，**遇到时照模板新建，项目结束回写**

新引擎起步时按 `prior-art.md` 查 `morluto/awesome-reverse-engineering` 的「Language runtimes and packagers」选解包工具，并在 `engines/<引擎>.md` 的「已知候选工具」里标 `未验证`。Unity 项目可在 S5 试点 `CoplayDev/unity-mcp`，须在 M0 工具链表登记版本与冒烟状态。

## 活文档纪律

- `待优化清单.md` 是唯一登记处，分池：立即池 / M#池 / 归档区（带日期）。每个开发节点过一遍立即池。
- 每日工作日志（如有 .workbuddy/memory）：坑写「根因 + 修法 + 一句经验」。

## 项目收尾（强制，持续进化的来源）

项目交付后执行 `references/retro-checklist.md`：复盘 → 把新坑/新方法写回对应 skill → 提 PR 到 apk-rebuild-skills 仓库 → **按发布检查同步到本机 clone / Y 盘共享副本 / 各 Agent 安装点**。**不回写、不同步 = 项目未结项。**

## 卡住时

查 `references/debug-playbook.md`（按症状索引）。

## 相关 skill

`rebuild-recon` · `rebuild-asset-recovery` · `rebuild-product-design` · `rebuild-dev-milestones` · `rebuild-device-evidence` · `rebuild-build-release`

## 变更记录
- 1.4.2（2026-11-09）新增**看板与状态回写**：项目目录规范 `project-layout.md`、`project.json` 模板、离线看板生成器 `build_dashboard.py`；新增状态回写时机与卡点登记要求（横切层，不改阶段编号与门禁）。
- 1.4.1（2026-11-09）新增 **A0 原包获取**：本地包直接进 S0；游戏名 / Google Play 链接 / 三方市场链接由 `fetch_artifact.py` 下载并留痕；新增 `artifact-acquisition.md`；不改八阶段编号、铁律、门禁。
- 1.4.0（2026-11-09）合规模型改为「分析放行 / 发布管控」：允许所有作品进入流程，权属改为状态登记；新增 **G-PUBLISH 发布人工门禁**（逐产品人工确认所有权、人工发布）；新增 P0/P4 横切检查点与 `prior-art.md` 外部能力清单；铁律扩为七条；置信度体系加 external-reference 旁证；S0/S7 出口同步。
- 1.3.0（2026-10-17）新增 REA 联合模式：统一逆向证据、Evidence 归档、ADB 真机证据、R1/R2/R3 决策和第三方 APK 权属边界；详见 `references/rea-integration.md`。
- 1.2.0（2026-10-16）输入检查表分必需/后续两类（C/S 型 #10 必需）；铁律 1 明确未勾选即未授权；S1 出口加源码可恢复性结论；既有门禁以严者为准；决策门扩到 D9；S3/S6/S7 出口同步（项目 C、F 反馈）。
- 1.1.0（2026-10-16）引擎适配新增 react-native-hermes（项目 C）、unity-il2cpp（项目 F）。
- 1.0.0（2026-10-01）从项目 D（Meowdoku → PawStar，Godot 4.6）全程提炼。
