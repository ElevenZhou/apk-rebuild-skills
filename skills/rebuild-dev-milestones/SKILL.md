---
name: rebuild-dev-milestones
description: 逆向重建 S5 工程再开发：按 M0-M5 里程碑（骨架 → 核心玩法 → 商业化 → 留存+微创新 → 真机校准 → 换皮）在新工程上重写产品，附带开发纪律（待优化清单、测试先行、参数外置、降级方案、冒烟规则）和里程碑进展文档格式。单独使用场景：任何"按里程碑重写一个已有游戏/应用"的开发阶段管理。触发词：里程碑开发、M0、M1、重写工程、开发进展、待优化清单、冒烟测试。
version: 1.0.0
owner: ElevenZhou
---

# rebuild-dev-milestones — 里程碑工程再开发

## 何时用 / 何时不用
- **用**：方案与开发计划已锁定（`rebuild-product-design` 出口），开始写代码。
- **不用**：方案没锁 → 先回 S4；只是打包 → `rebuild-build-release`。

## 需要的输入
开发计划.md、产品文档.md、docs/03 接口契约、assets_imported/、引擎工具链（见 `rebuild-workflow/references/engines/`）。

## 里程碑框架（按项目内容填，顺序不变）

| M | 内容 | 典型出口标准 |
|---|---|---|
| M0 骨架 | 工具链表、空工程、单例/插件桥空实现、资源样品接入 | headless 冒烟 0 错误；样品 100% PASS |
| M1 核心玩法 | 规则引擎、关卡/题目生成、对局 UI、存档 | 模拟 100 局无阻断；规则测试全绿 |
| M2 商业化 | 订阅/内购/广告（可先模拟）、埋点、AB 框架 | 购买/广告全链路模拟通过；埋点事件全覆盖 |
| M3 留存 + 微创新 | 每日挑战、打卡、排行、图鉴 + 微创新（AB 开关） | 模块测试全绿；微创新可演示且可关 |
| M4 真机校准 | 用 `rebuild-device-evidence` 对原包采证，关闭 P0 占位 | docs/09 P0 全部关闭或转 AB |
| M5 换皮 + 发布准备 | 品牌替换、图标、启动页、导出配置 | 与原产品可区分度评审通过；签名包可装 |

## 每个里程碑的固定动作
1. 开工：从开发计划拷贝本 M 范围到 `M#-进展.md`（模板 `references/progress-template.md`），过一遍待优化清单的「立即池」和「M# 池」。
2. 开发：遵守下面的纪律。
3. 收尾：全量回归 + 冒烟 → 更新进展文档 → 新问题进待优化清单 → **请负责人确认出口**。

## 开发纪律（防返工的核心）
1. **待优化清单是唯一登记处**（模板在仓库 `templates/project/待优化清单.md`）：分立即池 / M# 池 / 归档区；完成项移入归档并写日期。
2. **测试先行于交接**：每个功能配 headless 可跑的测试；测试 setup 必须彻底重置存档/单例状态（防跨测试污染）。
3. **参数全部外置**：数值放 `cfg/*.yaml|json`，AB 键放 `cfg/ab_keys.json`；代码里只留兜底值，并加注释指向 cfg 键。
4. **契约原样继承**：埋点事件名、AB 键名、插件桥方法名照 docs/03，不擅自改名（后台和运营依赖它们）。
5. **降级方案思维**：依赖重的部分（Spine、原生 SDK）先出降级实现（静态图 + Tween、模拟 SDK），登记升级路径，不阻塞主线。
6. **每个新功能过冒烟**（Godot 示例）：
   ```bash
   godot --headless --path . --quit-after 3 2>&1 | grep -E "SCRIPT ERROR|Parse Error|nonexistent"
   ```
   一定要 grep `nonexistent`：信号连接失败只报这个，headless 不会当错误处理。
7. **日期逻辑**用 ordinal/儒略日计算天数差，测试覆盖跨月、跨年。
8. **不用脚本批量改代码**，除非改完立刻跑冒烟（Python 替换容易把 `\n` 写坏，产生错位的 Parse Error）。
9. **密钥不进代码**：keystore、API Key 放本地文件或环境变量，`.gitignore` 排除。

## 工程目录约定（推荐）
```
rebuild/<工程>/
  autoload/ core/ scenes/ bridges/ cfg/ assets_imported/ tests_dev/ docs/
rebuild/待优化清单.md   rebuild/M#-进展.md   rebuild/tools/
```

## 相关 skill
上游 `rebuild-product-design` → 并行 `rebuild-device-evidence`（M4 及每个 M 真机验收）→ 下游 `rebuild-build-release`。

## 变更记录
- 1.0.0（2026-10-01）项目 D（PawStar，Godot 4.6）M0-M5 提炼。
