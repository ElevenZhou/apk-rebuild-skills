# 看板自动刷新与机器观测（dashboard autorefresh）

> 适用：`apk-rebuild-skills` v1.4.3 起 ｜ 定位：**工作台层的横切能力**，不改变 A0 / S0–S7 八阶段、七条铁律、决策门 D1–D9、G-PUBLISH 发布门禁、输入检查表。
> 要解决的问题：v1.4.2 看板是「AI 沟通一次 → 回写 `project.json` → 手动跑脚本重画」的静态快照。多人/多项目并行时，没人对话就没有新状态，页面也不会自己变。

---

## 1. 先分清两层，别把「定时重画」当成「状态自动更新」

| 层 | 做什么 | 由谁驱动 | 产出 |
|---|---|---|---|
| **① 状态层 · 机器观测** | 扫描项目目录的文件活动、阶段产物、卡点登记后的变动，发现「登记状态 vs 目录实际」不一致 | 每次构建自动执行，无需人触发 | `dashboard/signals.json` + 看板「🛰 机器观测 · 待核实」 |
| **② 呈现层 · 定时重建** | 重新读 `project.json` + 观测数据，原子写 HTML | 计划任务 / `--watch` 每 15 分钟 | `dashboard/index.html`、`dashboard/watch.log` |
| **③ 页面自刷新** | 浏览器每 15 分钟重新加载 HTML | 页面内 `<meta refresh>` | 打开着的看板一直显示最新数据 |

**只有第 ① 层能让「状态」在没有 AI 对话时也变化**；②③ 只是把变化呈现出来。三者缺一，都会退回「人不动、板不动」。

### 一条不能破的边界

`project.json` 仍是**唯一权威状态源**。机器观测只报客观事实，**不自动改写 `project.json`、不判定阶段出口是否达标、不自动关闭卡点、不自动发布**。

「目录里出现 `rebuild/`」只说明有产物，不等于 S5 出口通过。看板把差异列出来，一键复制「核实提示词」交给人或 Agent，由对方**带依据地**回写。这条与 `project-layout.md` §7「看板只反映状态、不做决策」一致。

---

## 2. 机器观测：扫什么、报什么

`build_dashboard.py` 每轮构建调用 `collect_signals()`，对 `<root>/项目*/` 做**限时、限量**扫描（全轮预算 6 秒，单项目最多 4000 个文件；跳过 `.git` / `node_modules` / `extracted` / `Library` 等大目录，以及 `project.json` / `signals.json` / `index.html` / `watch.log` 这些看板自身文件，避免把自我更新算成项目活动）。

| 观测项 | 含义 |
|---|---|
| `last_activity_at` / `activity_days` | 目录内最近文件修改时间 / 距今天数 |
| `changed_since_update` | `updated_at` 之后有多少文件变动 |
| `artifacts` / `observed_stage` | 按 `ARTIFACT_RULES` 观测到哪些阶段产物、最高到哪阶段（**旁证**） |
| `stage_gap` | 观测阶段比登记 `stage` 靠后 |
| `evidence_files` / `release_files` | 证据与交付物文件数 |
| `files_scanned` / `truncated` | 本轮扫描量、是否因预算截断 |

### 触发「待核实」的规则

| level | 条件 | 看板表现 |
|---|---|---|
| `alert` | `stage_gap`：目录出现更靠后的产物 | 红色置顶 |
| `warn` | 标「进行中」但 >7 天未回写 / 目录 >7 天无活动 | 琥珀置顶 |
| `warn` | 有阻塞卡点、但登记后目录仍有文件变动（疑似已解除） | 琥珀置顶 |
| `warn` | `blocking` / `waiting` 卡点挂了 >14 天 | 琥珀，提醒升级处理 |
| `info` | 距上次回写后有文件变动 | 只在详情里，不占用置顶区 |

统计条新增「**状态待核实**」= 有 `warn`/`alert` 的项目数；卡片加「⚠ 待核实」徽标与「🛰 最近活动」时间。

---

## 3. 三种运行方式

```bash
# A. 单次生成（原有用法，仍可用）
python skills/rebuild-workflow/scripts/build_dashboard.py \
  --root "<项目父目录>" --out "<父目录>/通用工程/dashboard/index.html"

# B. 常驻循环 —— 不开计划任务时用它（需保持终端运行）
python skills/rebuild-workflow/scripts/build_dashboard.py \
  --root "<项目父目录>" --out "<...>/index.html" --watch --interval 900

# C. 单次静默 —— 供计划任务 / CI 调用
python skills/rebuild-workflow/scripts/build_dashboard.py --once --root "<...>" --out "<...>"
```

| 参数 | 默认 | 说明 |
|---|---|---|
| `--interval` | 900 | `--watch` 重建间隔（秒），最小 30 |
| `--refresh-sec` | 900 | 页面自动重载间隔；`0` = 关闭页面自刷新 |
| `--once` | — | 静默单次，日志写 `watch.log` |
| `--no-signals` | — | 跳过机器观测，只按 `project.json` 重画 |
| `--quiet` | — | 不打印完整扫描报告 |
| `--check` / `--strict` | — | 只做 schema / 目录规范检查 |

**原子写**：HTML 与 `signals.json` 都先写 `.tmp` 再 `os.replace`，避免浏览器正好在重写时读到半个文件。`watch.log` 保留最近 512 KB，每行含时间、项目数、阻塞/待人工数、待核实数与耗时。

### Windows 计划任务（推荐，无人值守）

在有权限的 **PowerShell** 里执行一次即可（修改路径后）：

```powershell
powershell -ExecutionPolicy Bypass -File ^
  "C:\Users\<用户>\apk-rebuild-skills\skills\rebuild-workflow\scripts\install_dashboard_task.ps1" ^
  -Root "E:\Dev-2\离职同事未交接源码的项目" ^
  -Out "E:\Dev-2\离职同事未交接源码的项目\通用工程\dashboard\index.html" ^
  -IntervalMinutes 15
```

脚本会：写 `dashboard-task-config.json`（UTF-8，非 ASCII 路径都放这里，保证 Windows PowerShell 5.1 不乱码）→ 注册每 15 分钟的 `RebuildDashboard-AutoRefresh` 任务 → 立即生成一次。

```powershell
# 查询 / 手动触发 / 卸载
powershell -ExecutionPolicy Bypass -File "<同一路径>\install_dashboard_task.ps1" -Status
powershell -ExecutionPolicy Bypass -File "<同一路径>\install_dashboard_task.ps1" -RunOnce
powershell -ExecutionPolicy Bypass -File "<同一路径>\install_dashboard_task.ps1" -Uninstall
```

> 任务默认「用户登录时运行」、`/RL LIMITED`（无需管理员）。若创建被安全策略拦截，退回方式 B（`--watch` 常驻），或由运维在服务器/CI 上定时调 `--once`。
> 页面本身不依赖计划任务：它每 15 分钟会自动重载；**超过 2 个刷新周期没有新数据，右上角标红「自动刷新可能已停止」**，正是用来发现定时任务挂了。

---

## 4. 服务器 / 多人场景

上一轮 `outputs/多人协作使用方案分析.md` 的阶段 1 建议「状态源集中 + CI 重建 + 静态只读看板」，本层直接复用：

- 服务器端把各项目 `project.json` 收进小仓库，提交触发 `build_dashboard.py --once --out <站点目录>/index.html`
- 或用 `--watch --interval 900` 常驻服务（无需 Web 框架，只写静态 HTML）
- 同事浏览器访问同一个 HTTP 地址，页面自刷新；`signals.json` 可一并发布供其他系统消费

**注意**：机器观测需要能读到**项目目录的真实文件**。若服务器只有 `project.json` 而没有项目工作数据，`collect_signals()` 扫不到东西，应加 `--no-signals`，只保留定时重建与页面自刷新；观测仍由各自本机生成。

---

## 5. 排查清单

| 现象 | 先查 |
|---|---|
| 页面右上角标红「自动刷新可能已停止」 | `dashboard/watch.log` 最后一行时间；`-Status` 看计划任务；或 `--watch` 终端是否还开着 |
| 数据一直不变 | 是否真的有人/AI 改了 `project.json`；定时任务是否指向正确的 `--root` / `--out` |
| 「状态待核实」一直不消失 | 那是**等人确认**，不是 bug。复制「核实提示词」交给 Agent 回写 `project.json`，下一轮自动消失 |
| 观测结果明显不准 | 看 `signals.json` 的 `truncated` 与 `files_scanned`；大项目可能触及 6 秒 / 4000 文件预算，调 `SIGNAL_BUDGET_SEC` / `SIGNAL_MAX_FILES` |
| 大量无意义「文件变动」 | 确认 `SIGNAL_SKIP_FILES` 是否排除了看板自身文件与临时文件 |
| 中文路径乱码 / 任务跑不起来 | 配置是否写在 `dashboard-task-config.json`（UTF-8）；ps1 本体保持 ASCII |

---

## 6. 与流程的关系

| 项 | 是否改变 |
|---|---|
| A0 + 八阶段 S0–S7、七条铁律、D1–D9、G-PUBLISH、输入检查表 | ❌ 不变 |
| `project.json` 唯一状态源、状态回写时机、卡点三要素 | ❌ 不变 |
| 新增：定时重建、页面自刷新、机器观测旁证、待核实提示与核实提示词 | ✅ 工作台层新增 |

---

## 变更记录

- 1.0（2026-11-09）v1.4.3 新增：两层自动更新模型、机器观测字段与提示规则、三种运行方式、Windows 计划任务脚本、服务器场景与排查清单。
