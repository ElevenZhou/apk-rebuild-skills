# Changelog

## v1.4.1 — 2026-11-09

**A0 原包获取：把「第一步」固化下来**（用户要求：从指定来源下载 APK；已提供 APK 就直接进流程；输入可为游戏名 / Google Play 链接 / 三方市场链接）。定位为补丁版：**八阶段 S0–S7、七条铁律、决策门 D1–D9、G-PUBLISH 一律不变**。

- 新增 `skills/rebuild-workflow/scripts/fetch_artifact.py`：四种输入 `--from-file` / `--name`（配 `--pick N`）/ `--play-url` / `--market-url`；参数化输出目录、代理、Chrome；自动校验文件头与大小、算 sha256、写 `input/artifact-source.json`；输出机器可读 JSON 状态（ok / need-confirm / need-input / failed）。由 2026-09 六个 APK 实战脚本改写，去掉硬编码项目名、E 盘路径、Chrome 151 与 7897 代理。
- 新增 `skills/rebuild-workflow/references/artifact-acquisition.md`：A0 决策树、四种输入命令、源优先级（APKCombo downloader → 变体页 → APKPure）与失败降级、校验留痕、人工确认点、合规边界（不绕过付费/登录/区域限制/反爬）、常见坑。
- `rebuild-workflow` **1.4.1**：新增 A0 章节（不占 S 编号）、S0 步骤 0、A0 人工确认点；frontmatter 描述补四种输入。
- `input-checklist.md` #1 改为 A0 产出并新增 A0 前置动作小节；`templates/project/scope.md` 加「原包来源（A0）」字段与检查表结果行；`stage-map.md` 入口图、产物表、门禁一览同步。
- `docs/SOP.md` **v1.4.1**：总流程前加 A0，S0 标题由「授权立项」修正为「立项登记」，输入表与产出物同步；`docs/ARCHITECTURE.md` 分层图、流程图、门禁表、仓库结构对应表加 A0。
- `README.md`：新增「第一步：获取原包（A0）」章节、四种输入命令、前置环境、常用说法、Agent 停顿点；架构总览简图入口加 A0；版本表与架构链接同步。
- **验证状态**：`py_compile` 通过、`--help` 正常、`--from-file` 本地包路径冒烟通过（校验 + sha256 + 留痕）；**网络下载三条路线未在新站点结构下逐一复测**（🟡），选择器失效时按 `artifact-acquisition.md` 降级并回写。

## v1.4.0 — 2026-11-09

**合规模型重构 + 现成成果能力接入 + 基线统一。** 来源：用户决定「允许所有作品进入流程，正式发布由人工逐产品确认所有权并人工操作」，以及 `outputs/开源项目落地评估与流程演进分析.md` 的 B0–B4 方案。

- `rebuild-workflow` 1.4.0：合规模型改为**分析放行 / 发布管控**——允许公司自有 / 待确认 / 第三方 / 来源未知作品进入分析与重建；权属改为状态登记，不再阻断开工；新增 **G-PUBLISH 发布人工门禁**（逐产品人工确认所有权、人工执行发布、Agent 不得自动发布、未确认则 `仅内部`）；铁律扩为七条（先登记后动手、发布归人）；新增 **P0/P4 横切检查点**（不占 S 阶段编号）；S0/S7 出口、决策门、引擎适配同步；外部能力准入清单落地。
- `rebuild-build-release` 1.2.0：新增 G-PUBLISH 门禁章节，区分内测包 / 正式发布包，交付物加 `INTERNAL-ONLY.md`，出口标准加发布授权；`references/delivery-checklist.md` 加「发布授权」小节（人工填写、Agent 不得代填）。
- `rebuild-product-design` 1.3.0：新增 P4 参考实现检索与 `P4-参考实现清单.md`；D1 加 P0 `prior_art` 前置输入；D2/D5 适配新合规模型；补齐此前 1.2.0 未同步的 frontmatter 版本号。
- `rebuild-recon` 1.3.0：作品准入放开；新增 `external-reference` 外部旁证等级（不得升级为 MV、不得关闭 P0）；09 篇加旁证列；补安全红线与工具地图指引；补齐 frontmatter 版本号。
- `rebuild-asset-recovery` 1.3.0：出口标准补注「素材版权审查不替代 G-PUBLISH 人工所有权确认」。
- 新增 `skills/rebuild-workflow/references/prior-art.md`：P0/P4 操作细则、三种检索接入方式、A/B/C 级外部能力准入清单、合规与安全边界。
- `templates/project/scope.md`：权属四选一状态登记、新增 **发布授权（G-PUBLISH）**段与 **`prior_art` P0 检索表**、发布责任人、安全红线。
- `references/input-checklist.md` 1.4.0：#2 由「权属确认、缺失不开工」改为「权属状态登记、不阻断开工」；新增 **#11 P0 现成成果检索**（必需，未命中也留痕）；新增 G-PUBLISH 发布门禁小节（硬门禁，不可放宽）。
- `references/stage-map.md`：加入 P 横切层与 G-PUBLISH、门禁一览；S0 改名「立项登记」，产物表同步。
- `references/rea-integration.md`：入口第 1 条改为所有作品可做分析取证、发布另过 G-PUBLISH；证据等级补 `external-reference`。
- `references/retro-checklist.md`：新增第 9 条 G-PUBLISH 复核、第 10 条**发布同步检查**（GitHub tag → 本机 clone → Y 盘副本 → 四处安装点 → 其他工作区副本 → 新会话自检）。
- `docs/SOP.md` **v1.4.0**：统一为**八阶段 S0–S7**（此前文档为七阶段、与 SKILL.md 不一致）；补合规模型、P 层、G-PUBLISH、检查表 #11 与发布门禁。
- `README.md`：合规声明、架构总览（简版 Mermaid 图）、版本表、现成成果检索章节、使用说明（含第三方作品 / P0 / 发布门禁的常用说法）、Agent 停顿点、维护发布同步要求。
- **新增 `docs/ARCHITECTURE.md`**：v1.4.0 分层架构图、端到端流程与人机边界图、合规两线模型、外部能力接入位置、仓库结构对应；明确 2026-09 RescueBench 的 S0–S9 旧图为历史版本，不作现行依据。
- `skills/rebuild-device-evidence/SKILL.md` frontmatter 版本补齐为 1.2.0（REA 集成时变更记录已写 1.2.0、frontmatter 漏改）。
- 工作区侧：根目录 `README.md`、`outputs/逆向成果检索清单.md`、`outputs/开源项目落地评估与流程演进分析.md` 同步；`通用工程/apk-rebuild-skills/` 开发期副本从 v1.0.0 同步到 v1.4.0（此前滞后，曾导致「回写断档」误判）。

## v1.3.0 — 2026-10-17（补记，随 v1.4.0 一并发布）

REA 联合模式（此前已在工作区改动但未提交、未写入 CHANGELOG）：
- 新增 `skills/rebuild-workflow/references/rea-integration.md`：REA 与 `rebuild-*` 职责边界、Evidence 等级与归档、R1/R2/R3 路线判断、阶段映射、安全边界。
- `rebuild-workflow` / `rebuild-recon` / `rebuild-product-design` / `rebuild-device-evidence`：接入 REA 静态与真机证据，D1/D2/D8 引用 Evidence，禁止把静态完整覆盖当成源码恢复。

## v1.2.1 — 2026-10-17
- 安装脚本：修复以 `-File` 方式调用并传 `-Targets a,b,c` 时，多个目标被当成一个字符串、提示 unknown target 而什么都没装的问题（README 共享盘安装命令受影响）。

## v1.2.0 — 2026-10-16
- 来源：项目 C / 项目 F 复盘中 18 条通用建议（C-1～C-14、F-2/F-4/F-7/F-8），经负责人批准全部纳入主流程。
- `rebuild-workflow` 1.2.0：输入检查表分必需 #1–#7 / 后续 #8–#10（C/S 型 #10 必需）；"未勾选 = 未授权"写进铁律；新增环境前置与"以更严格者为准"；S1 出口加源码可恢复性结论（决定 R1/R2/R3）；S3 出口加版权审查；决策门 D1-D9；S6 原包不可运行时只验新包；S7 出口加 keystore 双人双地备份。
- `rebuild-recon` 1.1.0：统一 sha256sum；强制解开全部 config 分包/OBB/assetpack；新增步骤 5 源码可恢复性结论；补 apktool 无 java 卡死、RN 大包慢。
- `rebuild-asset-recovery` 1.2.0：报告状态 OK/OK_RECOMP/PARTIAL/FAIL（PARTIAL 不计 PASS）；按类分评；i18n 入样品表；版权/再分发审查进出口；Unity AudioClip/FSB5 规则（`engines/unity-il2cpp.md` 同步）。
- `rebuild-product-design` 1.1.0：新增 D8 服务端方案、D9 MVP 首版范围（模板、SOP 同步）。
- `rebuild-dev-milestones` 1.1.0：M4 增加"负责人数值审定 + 新包真机验收"分支。
- `rebuild-device-evidence` 1.1.0：新增"原包能不能跑"前置判断。
- `rebuild-build-release` 1.1.0：出口与交付清单加入 keystore 双人双地备份 + 交接记录。
- 仓库：`templates/project/scope.md` 改为逐项勾选授权范围；CONTRIBUTING 增加 `case/`、`release/` 分支与"每个项目独立 worktree"；README / install-prompt 写明 NAS 副本不可就地 git 操作及更新方式。

## v1.1.0 — 2026-10-16
- 来源：项目 C（Mochichat，Expo RN + Hermes）、项目 F（Card Factory!，Unity 6 + IL2CPP）实战回写。
- `rebuild-workflow` 1.1.0：新增引擎专节 `engines/react-native-hermes.md`、`engines/unity-il2cpp.md`。
- `rebuild-recon` 1.0.1：`detect_engine.py` 识别 Hermes 字节码版本、Expo 配置、XAPK 分包。
- `rebuild-asset-recovery` 1.1.0：新增 RN/Expo + Hermes 资源回导小节与 `scripts/rn/`（资源还原、i18n 提取）。
- 安装：支持从网络共享盘（`Y:\Skills`）安装——自动切换复制模式，新增 `trae` 目标、`-Dest`、读取 `CODEX_HOME`；新增 `docs/install-prompt.md`。
- 案例：新增 `docs/cases/project-C.md`、`project-F.md`（进行中案例，阶段性记录）。
- 未纳入：两个项目 skill-feedback 中涉及通用流程/铁律/出口标准的建议（约 20 条）仍待负责人审批，见各案例文档。

## v1.0.0 — 2026-10-01
- 首版：7 个 skill（workflow / recon / asset-recovery / product-design / dev-milestones / device-evidence / build-release）。
- 来源：项目 D（Meowdoku 1.18.0 → PawStar，Godot 4.6.3）全流程。
- `rebuild-asset-recovery` 由原 `godot-asset-recovery` 迁入并改名，脚本参数化。
- 视觉模型脚本改为环境变量读 Key。
- 新增项目模板、安装脚本、lint/密钥扫描。
