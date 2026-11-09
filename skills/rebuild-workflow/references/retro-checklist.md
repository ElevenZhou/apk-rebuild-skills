# 项目收尾复盘清单（S7 之后强制执行）

1. **时间线**：各阶段实际耗时 vs 计划，最大偏差的原因。
2. **新坑**：本项目遇到、但 skill 里没写的问题 → 写进对应 skill 的「常见坑」或 `debug-playbook.md`。
3. **新方法/脚本**：可复用的脚本整理成通用版本（参数化、去硬编码路径、去密钥）→ 放进对应 skill 的 `scripts/`。
4. **流程偏差**：哪一步实际顺序和 SOP 不同？是 SOP 错了还是执行偏了？SOP 错了就改 SKILL.md。
5. **引擎经验**：非 Godot 项目 → 照 `engines/_template.md` 新建 `engines/<引擎>.md`。
6. **案例**：在仓库 `docs/cases/` 新增 `project-<代号>.md`（一页：背景、决策门结论、关键坑、交付物）。
7. **提 PR**：分支 `retro/<项目代号>`，PR 描述附「项目 / 现象 / 验证方式」。
8. 版本号：涉及的 skill 各自 bump（新增内容 = minor，修正 = patch），更新 CHANGELOG。
9. **G-PUBLISH 复核**：确认交付物若对外发布，所有权已逐产品人工确认、发布由人工执行；未确认的是否已打 `仅内部` 标记且未对外分发。
10. **发布同步（B4，必须逐项打勾）**：改完不是结束，要让四处 Agent 真正读到新版：
    - [ ] `git commit` + 打 tag（如 `v1.4.0`），push 到 GitHub 私有仓库 `ElevenZhou/apk-rebuild-skills`
    - [ ] 本机 clone `C:/Users/AprilWu/apk-rebuild-skills` 与 GitHub 一致（`git status` 干净）
    - [ ] `Y:\Skills\apk-rebuild-skills` 共享副本按「clone 到 `.new` → 旧目录改名 `.bak-<日期>` → `.new` 改正式名」替换，**不在 Y 盘就地 git 操作**
    - [ ] 四处安装点（WorkBuddy / Claude Code / Codex / Trae CN；OpenCode 读 Claude 目录）已更新；目录联接模式 `git pull` 即可，复制模式需重跑 `install.ps1`
    - [ ] 新开会话自检：问「流程几阶段、D 门几个、发布前谁确认所有权」，答案与 SKILL.md 一致
    - [ ] 其他工作区副本（如 `E:/Dev-2/.../通用工程/apk-rebuild-skills/`）已同步，避免副本滞后被误当权威源

11. **看板状态回写（v1.4.2）**：确认项目根 `project.json` 已更新到最终状态（`stage / completed / progress / blockers / next_action / updated_at / publish_gate`），卡点已清空或写明等谁处理；重新生成 `dashboard/index.html` 并核对卡片；`build_dashboard.py --check` 无 schema 错误。开启自动刷新后由定时任务重建，无需手动生成；确认 `watch.log` 有本轮记录、`signals.json` 的待核实项已被处理或说明。规则见 `references/project-layout.md` 与 `dashboard-autorefresh.md`。

> 教训（2026-11-09）：通用工程内的开发期副本曾长期停在 v1.0.0，而正式版已是 v1.2.1，导致误判"回写链路断档"。**改之前先确认哪份是权威源，改之后按本清单同步。**
