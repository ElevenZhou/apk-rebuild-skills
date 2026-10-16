# Changelog

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
