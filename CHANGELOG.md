# Changelog

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
