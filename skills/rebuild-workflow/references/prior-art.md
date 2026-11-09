# 现成成果与工具检索（P0 / P4 横切检查点）

> 标语借用 `alexgaoth/awesome-reverse-engineered`：**Don't reverse engineer it twice.**
> 本文件定义两个不占阶段编号的检查点，以及允许接入本流程的外部能力清单。

## 为什么要横切，不新增阶段

`stage-map.md`、7 个 `SKILL.md`、产物表、出口标准、复盘清单全部按 S0–S7 编号交叉引用。插入「S0-pre / S3.5」之类阶段会牵一发动全身。P0/P4 只挂在现有阶段的**门口**，编号一个都不改，可单独启停、灰度或摘除。

```
        ┌──────────── P 横切层（不占 S 编号）────────────┐
        │  P0  S0→S1 门口：查外部存量 / 工具候选        │
        │  P4  S2→S4 门口：查同类玩法实现 / 复用比例    │
        └──────────────────────────────────────────────┘
S0 ─► S1 ─► S2 ─► S3 ─► S4 ─► S5 ─► S6 ─► S7
登记   解包   文档   资源   拍板   开发   采证   交付
                                          ▲
                              G-PUBLISH 人工发布门禁
```

---

## P0（S0 scope 确认后、S1 解包前，必做）

**输入**：产品名 / 原包名 / 引擎预判 / 私有格式或协议名 / 关键 SDK 名。

**操作**：

1. 查 `alexgaoth/awesome-reverse-engineered`（三选一，推荐 2 或 3）：
   ```bash
   # 1) 人工检索
   https://awesome.alexgaoth.com/

   # 2) 装成 Agent skill（让 Agent 自己查）
   npx skills add alexgaoth/awesome-reverse-engineered

   # 3) MCP server（三个只读工具，无依赖，uvx 直接跑仓库内 mcp/reverse_engineered_mcp.py）
   #    search_reverse_engineered / get_reverse_engineered_project / list_reverse_engineered_categories
   ```
2. 关键词组合：产品名、包名、`<引擎> + decompilation / reimplementation`、格式或协议名、同类竞品。
3. 再按 `morluto/awesome-reverse-engineering` 的「Language runtimes and packagers」「Game reverse engineering」「AI-assisted analysis」三节，确认 S1/S3 工具选型是否有更合适的现成工具。

**产出**（写入 `scope.md` 的 `prior_art` 段）：

| 字段 | 说明 |
|---|---|
| 检索日期 / 关键词 | 必填；**未命中也要写**，证明检索做过 |
| 命中项 + 链接 | 项目名、仓库地址 |
| License | 能否用于我们目标；GPL/AGPL 类需单独判断 |
| 健康度 | 🟢 Active / 🟡 Slowing / 🔴 Dormant / 🗄️ Archived / ⚪ Unknown |
| 可复用比例与结论 | 用工具 / 用格式解析器 / 用范式参考 / 不复用（写理由） |
| 第三方实现处理 | 是否涉及他人对第三方闭源产品的逆向实现 → 默认**不搬进交付物** |

**影响**：作为 S4 决策门 **D1（R1/R2/R3 路线）** 的前置输入；命中可复用实现时，D1 可能从「纯重做」改判为「复用 + 增量重建」，必须在方案里写清理由。

### 命中率的现实预期

索引里 6,000+ 个游戏反编译项目绝大多数针对**第三方商业游戏**。本流程自 v1.4.0 起允许所有作品进入分析，但查索引的目的仍是：

1. 找**同类引擎 / 同类私有格式**的现成解析器与反编译范式；
2. 找**工具链**（RE Tooling 分类），避免重写通用能力；
3. 参考「厂商关服后社区复活」类项目的路线选择。

不要指望直接命中"自家产品现成逆向版"。**索引命中不替代 S0 权属状态登记，更不替代 S7 的 G-PUBLISH 人工所有权确认。**

---

## P4（S2 九篇完成后、S4 拍板前，建议做）

查 `opengaming/osgameclones`、`radek-sprta/awesome-game-remakes`、`awesome-reverse-engineered` 的 Game Decompilations 分类，产出「同类玩法 / 格式的开源实现参考清单」，喂给：

- **D5 微创新**：看别人做过什么，避免重复造轮子、也避免撞车；
- 产品文档「保留 / 修改 / 新增 / 删除」四列的参考列。

参考实现只作旁证，标注 `external-reference`，**不能当作 machine-verified、不能用来关闭 docs/09 的 P0 占位**。

---

## 外部能力准入清单

### A 级 — 允许接入流程

| 项目 | 定位 | 落到哪里 |
|---|---|---|
| `alexgaoth/awesome-reverse-engineered` | 已逆向成果索引（17,700+，数据 CC0 / 代码 MIT，夜间刷新，带健康度与 License） | P0 / P4 |
| `morluto/awesome-reverse-engineering` | 按任务找工具的方法论地图 | `engines/*.md` 工具选型 |
| `morluto/rea` | 工具本体，Agent 化逆向证据链 | S1/S2，规则见 `rea-integration.md` |
| `CoplayDev/unity-mcp` | Unity 编辑器自动化（**试点**） | S5 / M0 工具链表，项目 F/E；需登记版本与冒烟状态 |

不混用：**rea = 工具本体 / morluto awesome = 方法论 / alexgaoth = 成果索引**。

### B 级 — 只借方法，不引入项目

| 项目 | 借什么 |
|---|---|
| `hellokaton/game-copycat` | 「复刻 → 正确性验证 → 实测」自动闭环，可提炼为 S6 的验收用例自动生成 + 新包同流程 diff |
| `SubmitGame/awesome-ai-game-dev-tools` | S3 特殊格式 / 加固时的工具候选池，逐个核实 License 后再用 |
| `opengaming/osgameclones`、`radek-sprta/awesome-game-remakes` | P4 参考字典 |

### C 级 — 明确不引入

`aviaryan/awesome-ai-games`、`lappemic/awesome-ai-built-games`、`Glitch-Gaming-Platform/Opensource-AI-Gaming-Projects`（AI 生成的可玩成品库，不适合需要完整源码、长期维护、上架商店的正式项目）；`SeeleAI/awesome-game-dev-ai`、`simoninithomas/awesome-ai-tools-for-game-dev`（与 S0–S7 取证重建阶段不对位 / 部分过时）；`IvanMurzak/Unity-MCP`（与 CoplayDev 重叠，避免工具膨胀）；`cronos996/`、`sqwu/ awesome-reverse-engineering`（无分类逻辑的大杂烩 / 疑似镜像）。

> 记录在此是为了**防止后人重复调研**。完整评估见工作区 `outputs/开源项目落地评估与流程演进分析.md`。

---

## 合规与安全边界（不随准入放宽而取消）

1. 索引只收 interoperability / preservation / research 类项目，明确排除 exploit、越狱、证书固定绕过、DRM、外挂、验证码破解、凭据工具 —— **本流程同样不碰这些**，与 `rea-integration.md` 的安全边界一致。
2. 不把他人对第三方闭源产品的逆向实现搬进交付物；引用仅作范式参考，标 `external-reference`。
3. 不因 `prior_art` 命中跳过 S0 权属状态登记，也不跳过 S7 的 G-PUBLISH 人工确认。
4. 不把反编译产物公开发布；真实账号 / Token / 短信 / 生产接口不写进 Evidence、文档或交付物。
5. 不把 `external-reference` 升级为可关闭 P0 的证据等级；置信度三级制 + `inferred` 维持不变。

## 版本
- 1.0（2026-11-09）随 `rebuild-workflow` 1.4.0 引入。
