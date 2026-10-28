# REA × apk-rebuild-skills 集成规则

本参考文件定义 REA 与 `rebuild-*` 技能的职责边界。REA 是逆向取证提供者；`rebuild-*` 是授权、产品决策、工程重写、真机验收和交付流程。REA 证据不能单独替代源码、原始工程、服务端权限或产品授权。

## 入口与选择

1. 先检查 `scope.md`：权属、分析范围、动态分析、联网/服务端、真机操作分别单独授权。第三方 APK 未取得重建授权时，只做竞品研究或授权范围内取证，不进入工程重建。
2. APK/SPLIT/APKS 先用 `rebuild-recon` 做哈希、分包、引擎和加固基线。
3. 需要 Android 方法、类、调用引用、Retrofit 注解或本地存储证据时，启用 REA Android/JADX provider：
   - `inspect_android_package`
   - `search_android_classes`
   - `inspect_android_class`
   - `inspect_android_method`
   - `trace_android_references`
4. 需要受控设备证据时，启用 REA ADB 工具或 `rebuild-device-evidence`：
   - `list_adb_devices`
   - `inspect_adb_device`
   - `capture_adb_screen`
   - `read_adb_logcat`
   - `start_adb_app` / `stop_adb_app`
   REA 不安装、启动或操作目标 APK，除非对应工具和 `scope.md` 明确授权；真机安装、点击、登录、短信和联网都必须单独记录。

## 证据等级与交付

- `machine-verified`：REA/Apktool/JADX/脚本可复现结果，保留 Evidence ID、APK SHA-256、工具版本和路径。
- `human-reviewed`：负责人或研究员核对截图、录屏、真机状态。
- `human-reported`：口述或未复核线索，不能作为实现依据。
- `inferred`：由命名、共现或结构推断，必须进入 `docs/09`，不能写成已验证调用链。

每条 REA 证据必须保存：原始 JSON、Evidence ID、artifact SHA-256、工具/provider、分析范围、coverage/limitations。反编译源码是观察材料，不得称为原始源码。把 Evidence ID 链接到 `docs/03`、`docs/04`、`docs/07` 或 `docs/09`。

## R 路线决策

- **R1 原位恢复**：只有原始工程、构建链、签名和服务端/资源权属均可验证时使用。
- **R2 契约 + 重写**：REA 已恢复可读逻辑、接口契约和存储/交互边界，但原始工程不可得时使用。
- **R3 纯重做**：只有产品行为、页面、资产和契约可观察时使用；重建工程必须使用新包名、品牌和实现。

REA 的“完整静态覆盖”不等于 R1。动态加载、反射、服务端策略、远程配置、运行时 Token、第三方 SDK 回调和未覆盖分包保持 unknown，直到补充证据。

## 阶段映射

| 阶段 | REA 工作 | rebuild 工作 | 出口 |
|---|---|---|---|
| S0 | 检查目标是否适合分析 | 权属、scope、风险、负责人确认 | scope.md 已确认 |
| S1 | APK inventory、Manifest、类/资源/引擎、JADX/Apktool | 哈希、分包、S1 事实基线 | 引擎、加固、源码可恢复性结论 |
| S2 | 方法级调用、接口、存储、权限和 SDK 证据 | docs/01-09、P0 清单 | 01/09 负责人复核 |
| S3 | 资源/字符串/布局定位，必要时做证据关联 | 样品回导、版权边界 | 资源报告可复现 |
| S4 | 提供行为和契约证据，不替代产品取舍 | D1-D9、PRD、品牌、开发计划 | 路线锁定 |
| S5 | 对新工程做结构/行为对照，不能将对照当原包等价证明 | M0-M5 重写与测试 | 各里程碑出口 |
| S6 | ADB 截图、日志、状态和受控流程证据 | 原包对标/新包验收、关闭 P0 | 采证包和验收记录 |
| S7 | 可做 APK/Manifest/安装状态检查 | 签名、安装、冒烟、交付归档 | 交付清单全绿 |

## 安全边界

禁止把 REA 用于绕过登录、验证码、风控、证书校验或服务端访问控制。真实账号、密码、Token、短信和生产接口不得写入 Evidence、技能、记忆或交付文档。登录流程复刻默认使用本地 mock；真实测试必须有明确授权、隔离设备、最小范围和可审计记录。
