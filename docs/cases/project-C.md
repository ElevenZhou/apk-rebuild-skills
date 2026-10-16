# 案例：项目 C（Mochichat 1.3.0 → 重建中）— 进行中

> 阶段性记录（截至 2026-10-16，M0 骨架进行中）。项目结束时补全"交付 / 遗留"并按 retro-checklist 复盘。

| 项 | 内容 |
|---|---|
| 原包 | Mochichat 1.3.0 XAPK（AI 陪伴聊天 App），Expo SDK 55 / RN + Hermes HBC v96 |
| 状况 | 源码不可恢复（只有 Hermes 伪 JS）；原服务端已下线；EAS 账号与 keystore 不可得；原版已下架 |
| 路线 | R3 纯重做。伪 JS 只作契约来源（接口、SQLite DDL、存储键、store 名）+ 资产来源（资源、i18n）+ 交互对标 |
| 新工程 | Expo SDK 55 / RN 0.83 / Hermes 客户端 + Fastify 5 + Drizzle + Postgres 服务端 |

## 关键经验
1. **RN+Hermes 拿不回源码，但能拿回约 1 万个原始函数名、全部 API 路径、SQLite 建表、存储键、全量 i18n**，足够做功能等价重写。hermes-dec 34 秒出伪 JS，apktool 对 89MB RN 包 >30 分钟，应按需跳过。
2. **EAS / OTA 不是捷径**：Manifest `expo.modules.updates.ENABLED=false` 时 EAS Update 里没有 JS 包；判断"能找回什么"要先验证内容，不能凭渠道名。
3. 原包里的**自研 Expo 模块虽经 R8 混淆，包名和属性名都保留**，jadx 可见完整实现，可以逐行功能等价复原（expo-pag-view 已真机播放通过）。
4. RN 资源难点不是去 hash，而是**还原 Metro 原路径**，还原后新工程可以沿用原 require 写法（`scripts/rn/rn_asset_restore.py`）。
5. 原包带 **Apple SF Pro 字体**（不可再分发），M0 即替换为 OFL 字体——回导后需做版权扫描。
6. 环境坑：JAVA_HOME 含中文导致 sdkmanager 失败；RN 0.83 gradle-plugin 钉死 foojay 0.5.0 与 Gradle 9 冲突；adb 常驻和 Metro 代理会造成假阴性。详见 `engines/react-native-hermes.md`。
7. 多项目共用一个仓库工作区来回切分支，提交会落错分支 → **每个项目开独立 `git worktree`**。

## 待负责人审批的通用建议（未纳入 v1.1.0）
| # | 建议 | 影响 |
|---|---|---|
| C-1 | 输入检查表"7 项 / 10 项"口径统一，区分必需与后续输入 | rebuild-workflow S0 出口 |
| C-2 | 缺授权时只在明确授权内执行，动态/联网分别确认 | 铁律 / input-checklist |
| C-3 | 既有项目门禁更严格时（如 P0 清零）以严格者为准，写明决策点 | S2 出口 |
| C-4 | S1 出口增加"源码可恢复性结论"（能拿回什么 / 拿不回什么），EAS/OTA/source map 先验内容 | S1 出口 |
| C-5 | 客户端-服务端型产品：输入清单 #10 服务端现状提为必填 | S0 |
| C-6 | 资源报告状态扩为 OK / OK_RECOMP / PARTIAL / FAIL | asset-recovery 规则 |
| C-7 | 回导后增加版权/再分发审查（字体 name 表、图片元数据） | asset-recovery 出口 |
| C-8 | 样品表加"文案 / i18n"行 | asset-recovery 模板 |
| C-9 | recon 解包要列出并解开所有 `config.*.apk` 分包 | recon 步骤 |
| C-10 | 原服务端下线 → S6 只做新包验收，原包数值在 S4 自定义 | device-evidence |
| C-11 | 决策门新增 D8 服务端方案、D9 MVP 范围 | product-design |
| C-12 | M4 改为"原包可采证则采证，否则数值审定 + 新包验收" | dev-milestones |
| C-13 | S7 出口加"keystore 双人双地备份 + 交接记录" | build-release |
| C-14 | README / CONTRIBUTING 写明每个项目用独立 worktree | 仓库协作 |

## 遗留
M0：CI 与 Postgres 联调未完成（本机无 docker）。
