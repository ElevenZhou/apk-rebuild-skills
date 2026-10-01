# 项目收尾复盘清单（S7 之后强制执行）

1. **时间线**：各阶段实际耗时 vs 计划，最大偏差的原因。
2. **新坑**：本项目遇到、但 skill 里没写的问题 → 写进对应 skill 的「常见坑」或 `debug-playbook.md`。
3. **新方法/脚本**：可复用的脚本整理成通用版本（参数化、去硬编码路径、去密钥）→ 放进对应 skill 的 `scripts/`。
4. **流程偏差**：哪一步实际顺序和 SOP 不同？是 SOP 错了还是执行偏了？SOP 错了就改 SKILL.md。
5. **引擎经验**：非 Godot 项目 → 照 `engines/_template.md` 新建 `engines/<引擎>.md`。
6. **案例**：在仓库 `docs/cases/` 新增 `project-<代号>.md`（一页：背景、决策门结论、关键坑、交付物）。
7. **提 PR**：分支 `retro/<项目代号>`，PR 描述附「项目 / 现象 / 验证方式」。
8. 版本号：涉及的 skill 各自 bump（新增内容 = minor，修正 = patch），更新 CHANGELOG。
