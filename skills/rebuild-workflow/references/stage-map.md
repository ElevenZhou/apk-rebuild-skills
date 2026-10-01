# 阶段地图与产物一览

```
S0 授权立项 ─► S1 侦察解包 ─► S2 静态分析 ─► S3 资源回导
                                                   │
        ┌──────────────────────────────────────────┘
        ▼
S4 产品定义（产品文档 / 决策门 / 品牌 / 微创新 / 开发计划）
        │
        ▼
S5 工程再开发  M0 骨架 → M1 核心玩法 → M2 商业化 → M3 留存+微创新 → M4 真机校准 → M5 换皮
        ▲  │
        │  ▼
S6 真机采证（与 M4 交织，也用于每个 M 的自家包验收）
        │
        ▼
S7 打包交付（签名 APK + 工程归档 + 交付清单）─► 复盘回写 skill 仓库
```

## 每阶段产物（文件名统一）

| 阶段 | 产物 | 位置 |
|---|---|---|
| S0 | scope.md、task_spec.yaml | 项目X/ |
| S1 | sha256、解包目录、assets/manifest.json | extracted/、assets/ |
| S2 | docs/01-概述 … 09-人工复核清单 | docs/ |
| S3 | assets_imported/、import_report_*.txt、M0-验收记录.md | rebuild/<工程>/、runs/ |
| S4 | 产品文档.md、重建方案-v#.md（含决策门 §）、开发计划.md、branding/ | 项目X/、rebuild/branding/ |
| S5 | 工程源码、tests_dev/、cfg/、M#-进展.md、待优化清单.md | rebuild/ |
| S6 | evidence/playtest/、M4-*.md、cfg 校准值 | evidence/、rebuild/docs/ |
| S7 | 签名 APK、交付清单.md、工程归档 zip | release/ |

## 项目 D 实际节奏（参考）

S0-S3 约 1 周；S4 三轮方案迭代（v1→v3，每轮对应一次前提修订：源码确认丢失、原包仍在架）；S5 M0-M3 每个 2-3 天（AI 辅助）；M4 真机采证 1-2 天；S7 打包 1 天（大部分时间花在工具链坑上）。
