# 项目目录规范与看板状态源（project.json）

> 适用：`apk-rebuild-skills` v1.4.2 起（v1.4.3 增加自动刷新与机器观测；见 `dashboard-autorefresh.md`） ｜ 定位：**规则层**，不改变 A0 / S0–S7 八阶段、七条铁律、决策门 D1–D9、G-PUBLISH 发布门禁。
> 解决的问题：多个项目并行时，「进度、卡点、下一步」散落在 README 表格和各个 `启动提示词.md` 里，人要靠记忆找；AI 工具换一个会话就不知道该接着干什么。

---

## 1. 三条原则

1. **项目目录是唯一工作区**：一个产品一个项目目录，产物、分析、文档、新工程链接、交付物都在其内或由其登记外链。目录即隔离。
2. **`project.json` 是看板的唯一事实源**：看板不解析 README、不猜进度、不读 `待优化清单.md` 反推状态。人写自然语言进 `README.md`，机器读 `project.json`。
3. **谁推进谁回写**：Agent 每次阶段切换、出现/解除卡点、会话结束前，必须更新 `project.json`；否则看板就是一张过期报表。**这是本规范里唯一带强制性的一条。**

`project.json` 与 `scope.md` / `task_spec.yaml` 不冲突：**前者管状态与卡点，后两者管授权与工单**。

---

## 2. 标准目录树

```
<项目根>/                          例：E:/Dev-2/离职同事未交接源码的项目/项目F/
├── project.json                   ★ 看板状态源（必需，机读）
├── README.md                     ★ 断点简报（必需，人读：30 秒结论 + 怎么继续）
├── scope.md                       权属状态 / 分析范围 / 发布授权（S0 产物）
├── task_spec.yaml                 工单（沿用旧 RescueBench 契约，可选）
├── input/                         A0：原包本体 + artifact-source.json
│                                  （存量项目原包留在根目录，见 §5 迁移）
├── docs/                          01-概述 … 09-人工复核清单（S1/S2 产物）
├── recon/                         S0/S1 侦察、可恢复性评估、引擎指纹
├── extracted/                     解包中间产物（大、可再生成，可 gitignore）
├── semantics/                     字符串表 / 命名词表 / 接口路径地图
├── evidence/                      证据链（_index.json + 截图录屏）
├── assets/                        资源回导 + manifest.json
├── rebuild/                       S5 新工程；工程在别处时登记到 project.json 的 links
├── release/                       S7 交付物：签名 APK、INTERNAL-ONLY.md、交付清单
├── runs/                          会话账本、心跳、工具日志
├── report/                        复核报告、断点简报（长文）
├── blockers/                      卡点详情长文（可选；project.json 用 ref 指过来）
└── notes/                         方案 / 待优化清单 / 启动提示词 / skill-feedback / 决策记录
```

### 目录职责速查

| 目录 | 放什么 | 不放什么 |
|---|---|---|
| `docs/` | 定稿的 01–09 文档套件 | 草稿方案、会议纪要 |
| `notes/` | 过程性文档：重建方案 v1/v2、开发计划、待优化清单、启动提示词、skill-feedback、盘点与差距表 | 交付物 |
| `report/` | 复核报告、断点简报 | 日常进度（写 README / project.json） |
| `blockers/` | 单个卡点的排查长文、日志、截图 | 卡点清单本身（在 project.json） |
| `release/` | 可交付的包与清单 | 开发期中间包 |

**新项目按此建；存量项目渐进迁移，不搬动大体量文件。**

### 命名规则

- 项目目录：`项目<字母>` 或 `项目<字母>-<短名>`（如 `项目G-红彩复刻-实习生`）。已有目录名**不重命名**，避免打断启动提示词和脚本里的绝对路径；显示名放 `project.json` 的 `product`。
- 文件命名：文档套件固定 `01-概述.md` … `09-人工复核清单.md`；方案类用 `重建方案-v1.md` 递增版本号，不用 `最终版/新版`。
- 启动提示词统一叫 `notes/启动提示词.md`（存量 `启动提示词-用skills推进.md` / `新对话启动提示词.md` 保留但不再新增变体）。

---

## 3. `project.json` Schema（v1.0）

模板见 `templates/project/project.json`。字段分三组：**标识**、**状态**、**行动**。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `schema_version` | string | ✅ | 固定 `"1.0"` |
| `id` / `name` | string | ✅ | `F` / `项目F` |
| `product` / `package` | string | ✅ | 产品名 / 原包名；未知填 `"unknown"` |
| `engine` | string | ✅ | 引擎与形态，如 `Unity 6 + IL2CPP`；侦察前填 `待定` |
| `track` | enum | ✅ | `rebuild`（走 A0+S0–S7 主线） / `prototype`（复刻原型） / `research`（调研选品） |
| `status` | enum | ✅ | `active` / `blocked` / `waiting-human` / `not-started` / `parked` / `done` |
| `stage` | string | ✅ | 当前阶段：`A0` 或 `S0`…`S7`；非主线项目填自由文本（`阶段0`） |
| `completed` | string[] | ✅ | 已完成阶段列表，用于画九格进度条；顺序无关 |
| `progress` | int 0–100 | ✅ | 总体完成度（人工估，不要求精确） |
| `milestone` | string | ⬜ | 当前里程碑 `M0`…`M5` |
| `owner` / `operator` | string | ✅ | 决策负责人 / 执行人（AI 工具或人） |
| `updated_at` | YYYY-MM-DD | ✅ | **最后回写日期**；看板据此判断数据新鲜度（>7 天标 stale） |
| `ownership` | enum | ✅ | `自有已确认` / `权属待确认` / `第三方` / `来源未知` |
| `publish_gate` | enum | ✅ | `not-applicable` / `pending-human` / `confirmed`；对应 G-PUBLISH |
| `summary` | string | ✅ | 一句话现状 |
| `next_action` | string | ✅ | **下一次会话要做的第一件事**，写成可直接执行的动作 |
| `blockers` | object[] | ✅ | 可为空数组；结构见下 |
| `key_files` | object[] | ⬜ | `{label, path}`，相对项目根，供看板直接打开 |
| `links` | object | ⬜ | 外链：新工程路径、商店页、仓库等 |
| `data_source` | string | ⬜ | 本份状态从哪些资料整理、哪些待人工核对 |

### `blockers[]` 结构

```json
{
  "id": "F-1",
  "title": "Unity 许可证未激活，工程无法编译",
  "severity": "blocking",
  "waiting_for": "Frank（人工）",
  "action": "在 Unity Hub 激活 6000.0.32f1 许可证后告知执行人",
  "since": "2026-10-29",
  "ref": "notes/待优化清单.md"
}
```

| severity | 含义 | 看板表现 |
|---|---|---|
| `blocking` | 卡死，不解决无法继续 | 红色，置顶「需要你处理」 |
| `waiting` | 等人工确认/授权/资源 | 琥珀色，置顶 |
| `risk` | 未阻断但需留意 | 卡片内提示 |
| `info` | 仅记录 | 折叠在详情里 |

**卡点必须带 `waiting_for` 和 `action`** —— 看板要能回答「卡在哪、等谁、要做什么」。只写「有问题」不算登记。

---

## 4. 状态回写规则（强制）

写进 `rebuild-workflow` 的执行纪律，Agent 在以下时机更新 `project.json`：

| 时机 | 更新什么 |
|---|---|
| A0 拿到原包 / S0 立项完成 | `stage`、`completed`、`ownership`、`publish_gate`、`summary` |
| 任一阶段出口通过 | `completed` 追加该阶段、`stage` 前移、`progress` |
| 出现卡点 / 卡点解除 | `blockers[]`、`status`、`next_action` |
| 决策门 D1–D9 / G-PUBLISH 有结论 | `summary`、`next_action`、必要时 `publish_gate` |
| **每次会话结束前** | 至少更新 `updated_at`、`next_action`、`blockers[]`，并说明改了什么 |

回写后跑一次看板生成（见 §6），确认卡片反映最新状态。

**防止看板变成第二份手工表格**：
- 不为了「好看」把 `blocked` 写成 `active`；卡住就标卡住。
- 不在 README 里另写一套进度数字；README 只讲结论和背景，数字以 `project.json` 为准。
- 超过 7 天未回写，看板标 `数据可能过时`，此时先核实再推进，不要直接信卡片。

---

## 5. 存量项目迁移映射（渐进，不强制搬文件）

2026-11-09 时 A–G 七个项目已存在，目录结构各不相同。**只新增 `project.json`（和缺失的 README），不移动 812MB 级文件**，避免打断绝对路径引用。之后新建文件按 §2 落位。

| 现状（根目录散落） | 规范位置 | 处置 |
|---|---|---|
| `重建方案-v1/v2/v3.md`、`开发计划.md`、`产品文档.md` | `notes/` | 保留原位；新版本写进 `notes/` |
| `待优化清单.md`、`skill-feedback.md`、`现状盘点与差距表.md` | `notes/` | 保留原位 |
| `启动提示词-用skills推进.md`、`新对话启动提示词.md` | `notes/启动提示词.md` | 保留，不再新增新变体 |
| `M0-进展.md` | `notes/` 或 `report/` | 保留；进度数字以 `project.json` 为准 |
| `*.xapk` 原包 | `input/` | 保留原位（A0 已获取，不搬）；新项目放 `input/` |
| `il2cpp-dump/`、`bins/`、早期 `work/` | `extracted/` 或 `recon/` | 保留，登记到 `key_files` |
| `blockers/`（项目D 已有） | 同名保留 | 与 `project.json` 的 `blockers[]` 并用：清单在前，长文在后 |

---

## 6. 看板生成与检查

```bash
# 生成看板（数据内嵌，双击 HTML 即可离线打开）
python skills/rebuild-workflow/scripts/build_dashboard.py \
  --root "E:/Dev-2/离职同事未交接源码的项目" \
  --out  "E:/Dev-2/离职同事未交接源码的项目/通用工程/dashboard/index.html"

# 只检查目录规范与 schema，不生成文件
python skills/rebuild-workflow/scripts/build_dashboard.py --root "<父目录>" --check
```

- 扫描根目录下所有 `项目*` 文件夹，读各自的 `project.json`；缺文件的项目在看板顶部列为「未建档」。
- `--check` 输出：schema 缺失/非法字段、标准目录缺项、数据过期天数、卡点缺 `waiting_for`/`action`。**只报告，不改文件。**
- 生成器零第三方依赖（仅 Python 标准库），HTML 内嵌数据，不需要起服务、不需要联网。

---

## 8. 机器观测层（v1.4.3，横切）

看板每轮构建会额外扫描项目目录，产出 `dashboard/signals.json`：**最近文件活动**、**距上次回写后的文件变动数**、**观测到的阶段产物**、**卡点是否挂太久**。发现「登记状态与目录实际不一致」时，看板列出「🛰 机器观测 · 待核实」并给出一键复制的「核实提示词」。

| 铁律 | 说明 |
|---|---|
| `project.json` 仍是唯一权威状态源 | 观测绝不自动改写它 |
| 产物出现 != 阶段出口达标 | 机器只报事实，阶段前移由阶段 skill 的出口标准决定 |
| 卡点不自动关闭 | 解除需人工/Agent 带依据确认 |
| 不自动发布 | G-PUBLISH 仍由人逐产品执行 |

扫描限时 6 秒 / 单项目 4000 文件，跳过 `.git` / `node_modules` / `extracted` 等大目录与看板自身文件；`truncated` 会标出触及预算的项目。定时重建与页面自刷新见 `dashboard-autorefresh.md`。

## 7. 与流程的关系

| 项 | 是否改变 |
|---|---|
| A0 + 八阶段 S0–S7、七条铁律、D1–D9、G-PUBLISH | ❌ 不变 |
| 各阶段出口标准、模板、检查表 | ❌ 不变 |
| 新增：状态回写时机、卡点登记格式、目录落位、看板入口 | ✅ 规则层新增 |

**看板只反映状态，不做决策**：它不判定阶段是否达标、不替代出口标准、不自动发布、不自动关闭卡点。所有结论仍由阶段 skill 和人工门禁给出。

---

## 变更记录

- 1.1（2026-11-09）v1.4.3 新增 §8 机器观测层与「旁证不改权威状态」铁律。
- 1.0（2026-11-09）v1.4.2 新增：项目目录规范、`project.json` schema、状态回写强制规则、存量迁移映射、看板生成与检查。
