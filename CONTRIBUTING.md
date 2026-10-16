# 协作约定

## 1. 分支
- `main`：受保护，只能通过 PR 合并，必须保持随时可用。
- 工作分支命名：
  - `skill/<skill名>-<主题>`：改进某个 skill（例 `skill/rebuild-build-release-unity`）
  - `fix/<主题>`：修正错误
  - `retro/<项目代号>`：项目复盘回写
  - `engine/<引擎>`：新增引擎手册
  - `case/project-<代号>`：项目进行中的引擎专节、项目特例（可直接提交，阶段性合入）
  - `release/v<版本>`：维护人汇总发版
- **每个项目用独立 worktree**，不要在同一个工作区来回切分支（提交会落错分支，项目 C 踩过）：
  ```bash
  git worktree add ../apk-rebuild-skills-e -b case/project-e main
  ```
- 改动分级：引擎专节、项目特例 → 直接进 case 分支；通用流程、铁律、决策门、出口标准 → 先写进 `docs/cases/project-X.md` 的"待审批建议"，负责人确认后再改。

## 2. 提交信息
```
<类型>(<范围>): <一句话>
```
- 类型：`feat` 新增内容 / `fix` 修正 / `docs` 纯文字 / `refactor` 重组 / `chore` 杂项
- 范围：skill 名、`repo`、`install`、`templates`
- 例：`feat(rebuild-build-release): 补充 ETC2 导出失败无文案的排查`

## 3. 修改审核
- 每个 skill 有一名 **owner**（写在 SKILL.md 头部 `owner:`），负责审核该 skill 的 PR。
- 合并条件：
  1. 至少 1 人 approve（改动涉及 skill 的 owner 优先）；
  2. `python tools/lint_skills.py` 通过（格式 + 密钥扫描）；
  3. PR 描述写清 **项目 / 现象 / 验证方式**。**没有实证的经验不收**，推测性内容必须标 `未验证`。
- 结构性改动（新增/合并/拆分 skill、改阶段编号）需要所有 owner 同意。

## 4. 写 skill 的规范
- 每个 SKILL.md 必须有 frontmatter：`name`、`description`（含触发词）、`version`、`owner`。
- 正文固定顺序：何时用/何时不用 → 需要的输入 → 步骤 → 出口标准 → 常见坑 → 相关 skill → 变更记录。
- 每个 skill **单独可读**：别的 skill 的内容用"见 `xxx`"引用，不要假设读者已经读过别的 skill。
- SKILL.md 控制在 200 行以内，长内容放 `references/`。
- 脚本：参数化（不写死路径）、不含密钥（用环境变量）、开头 docstring 写用法。
- 禁止提交：keystore、密码、API Key、原包文件、解包产物、客户数据。

## 5. 版本管理
- 每个 skill 独立语义化版本（SKILL.md 头部 `version`）：新增内容 minor+1，修正 patch+1，流程不兼容变化 major+1。
- 仓库整体打 tag：`v1.0.0`、`v1.1.0`……，每次合并一批 PR 后由维护人发 Release。
- `CHANGELOG.md` 每次 PR 都追加一行。

## 6. 更新通知
- 发 Release 时在团队群发一条：版本号 + 3 行以内的变化 + 是否需要重启 Agent。
- 同事日常 `git pull` 即可（安装是目录联接，拉取即生效，重启 Agent 后加载新版）。
- 团队共享盘副本（`Y:\Skills\apk-rebuild-skills`）由维护人更新：NAS 上文件写入几分钟后即被锁定，**禁止在 Y 盘就地 git pull/merge/checkout**；用"clone 到 `.new` → 旧目录改名 `.bak-<日期>` → `.new` 改名替换"。从 Y 盘安装的同事更新后重跑 install.ps1。
- 建议在 GitHub 仓库点 Watch → Releases only，自动收到邮件。

## 7. 复盘回写（强制）
项目交付后按 `skills/rebuild-workflow/references/retro-checklist.md` 执行，提交 `retro/<项目代号>` PR。不回写 = 项目未结项。
