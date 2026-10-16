# 引擎：React Native（Expo）+ Hermes 字节码

> 首个案例：项目 C（Mochichat 1.3.0，Expo SDK 55，Hermes HBC v96），2026-10-01。
> 标注规则：`已验证（项目C）` = 本项目实测可复现；`未验证` = 资料/推测，未在真实项目跑通。

## 一句话结论
RN+Hermes 包**拿不回原始源码**（TS/JSX、注释、文件结构、局部变量名都已丢失），但能拿回：完整业务逻辑的伪 JS、约 1 万个原始函数名、全部 API 路径、本地 SQLite 建表语句、存储键、全量 i18n 文案。足够做"功能等价重写"，不够"改改就能编译"。

## 识别特征（S1）
| 特征 | 判定 | 验证状态 |
|---|---|---|
| `assets/index.android.bundle` 存在 | RN | 已验证（项目C，`detect_engine.py` 1.3 秒命中） |
| bundle 前 8 字节 `c61fbc03c103191f`（小端魔数 0x1F1903C103BC1FC6），偏移 8 为 uint32 版本号 | Hermes 字节码 + 版本 | 已验证（项目C：v96） |
| bundle 是可读 ASCII JS | 非 Hermes，直接 prettier 格式化即可读 | 未验证 |
| `assets/app.config`（JSON） | Expo 托管工作流；含 owner、slug、sdkVersion、extra.eas.projectId、plugins | 已验证（项目C） |
| Manifest `expo.modules.updates.ENABLED` | **false = 不走 OTA**，EAS Update 里不会有 JS 包 | 已验证（项目C：false） |
| `libjiagu`/`libDexHelper` 等 | 加固；RN 包通常无加固，原生层只是壳 | 已验证（项目C：无） |

## 工具链（S1/S2）
| 用途 | 工具 | 命令 | 耗时（项目C，6.9MB bundle） | 验证状态 |
|---|---|---|---|---|
| 安装 | hermes-dec 0.1.7（pip，支持 v96） | `pip install hermes-dec`（装进隔离 venv） | <1 分钟 | 已验证 |
| 文件头 | hbc-file-parser | `hbc-file-parser index.android.bundle` | 4 秒 | 已验证 |
| 反汇编 | hbc-disassembler | `hbc-disassembler index.android.bundle out.hasm` | 18 秒，82MB | 已验证 |
| 反编译伪 JS | hbc-decompiler | `hbc-decompiler index.android.bundle out.js` | 34 秒，46MB / 112 万行 | 已验证 |
| Java 壳层 | jadx | `jadx -d extracted/jadx base.apk` | 4.5 分钟（旧报告） | human-reported |
| 资源 + manifest | apktool | `apktool d base.apk` | **>30 分钟（89MB 包，旧报告）** | human-reported |

**性能建议**：RN 包的 Java 层几乎没用，**不要对全包跑 apktool**。manifest/assets 用 `unzip` 或 jadx 的 resources 输出即可；只在需要 res/ 解码时才跑 apktool，并加 `--no-src`（未验证提速幅度）。

## 从伪 JS 里提取什么（S2，已验证（项目C））
反编译输出是寄存器式（`r1 = ...`）+ `switch` 跳转，不可编译，但字符串和函数名保留完好：

| 目标 | 做法 | 项目C 产出 |
|---|---|---|
| 原始函数名 | `grep -o 'Original name: \w*'` | 9988 个 |
| API 路径 | 正则提取 `'/api/...'`、`'/chat/...'` 等字符串字面量 | 194 条（旧字符串扫描仅 75） |
| 鉴权方式 | 搜 `'Bearer '` → 回溯 `setTokenGetter` → store 字段 | 证实为自有后端 token（zustand `useAuthStore.token`），非 Firebase ID Token |
| 本地库表结构 | 搜 `CREATE TABLE` | 5 张表完整 DDL |
| 存储键 | 搜 AsyncStorage 前缀（如 `'@xxx/'`） | 35 个 |
| 常量 | 搜数值（2097152=2MB、5242880=5MB）**再看上下文**，同值常出现在第三方库 | 需人工判读 |
| i18n | 文案对象字面量 `{'title': ...}` 整块存在，多语言齐全 | 全量 |
| Metro 模块边界 | `r0.__d` 调用 = 一个模块定义 | 2377 个模块 |

## 坑
1. **伪 JS 中文等非 ASCII 文案在 grep 输出里乱码**（终端编码），用 Python `open(encoding='utf-8')` 读，不要信终端显示。（已验证）
2. **"EAS 云端找回"不等于找回源码**：
   - `updates.ENABLED=false` 时 EAS Update 里没有 JS 包；
   - EAS Build 产物是 APK/AAB（和手上的包同级），对源码无增益；
   - 真正的价值是构建详情页上的 **git commit hash / 构建日志 / 构建者账号** —— 指向原仓库和人。项目档案（上传的源码 tarball）能否从后台下载：**未验证**。
3. **服务端不在包里**：RN 客户端重建后能否跑，取决于原后端是否在线、接口是否仍兼容。S0 必须问清服务端现状。
4. 同一常量（2MB）在 bundle 里多次出现，多数来自第三方库的枚举表，不能按命中次数下结论。

## 资源回导（S3，已验证（项目C））
脚本：`rebuild-asset-recovery/scripts/rn/rn_asset_restore.py`、`i18n_extract.py`（详见该 skill 的 RN 小节）。

| 资源 | 位置 | 还原方法 | 项目C 结果 |
|---|---|---|---|
| 图片（png/jpg/webp/gif） | `res/drawable-<密度>/<路径拼接小写去符号>.png` | 伪 JS 里 Metro `registerAsset({httpServerLocation,name,type,width,height,scales,fileHashes})` 对象字面量 → 还原原目录 + 原文件名 + `@2x` 后缀 | 220 张，fail 0 |
| svg / pag / lottie json / 字体 | `res/raw/` | 同上，md5 = `fileHashes` 逐字节一致 | 51 个，全部原件 |
| i18n | bundle 内 locale 模块（对象字面量链） | 解释 `rX = {...}` / `rA['k'] = rB` / `a4['exports'] = rX` | 9 语言 × ~1.9k 键 |
| 启动图标 / 启动底色 | `mipmap-*`、`values/colors.xml`（`splashscreen_background`） | 直接拷贝 | OK |

坑：
1. **aapt2 会重压缩 PNG**：md5 对不上的 190/220 张像素尺寸一致 → 按资源名兜底并标 `OK_RECOMP`，不要判 FAIL。
2. **XAPK/APKS 是按设备裁剪的分包**：多倍图在 `config.<密度>.apk`，只拿到一个密度；记 `PARTIAL`。要全密度需 AAB 或从多台设备取。
3. 包里有、JS 里没引用的"孤儿"资源（项目C 42 个，含 emoji gif），可能是服务端下发资源的本地副本 → 单独目录、路径标 inferred。
4. Expo 包常带 Apple **SF Pro** 字体（name 表含 Apple 许可），Android 上不可再分发 → 重建必须替换。
5. 第三方 SDK 资源（AppLovin、Firebase、ExoPlayer、`node_modules_*`）不导入，随依赖安装。

## 开发（S5，部分已验证（项目C M0））
- 推荐：最新 Expo 模板 + 同版本主要依赖（从 app.config plugins 和 bundle 内嵌 github 链接反推依赖清单）。项目C：`create-expo-app --template blank-typescript@sdk-55` 实测可用。
- **先找原包自研 Expo 模块再选型**：伪 JS 中 grep `requireNativeViewManager('`／`requireOptionalNativeModule('`，jadx 中查 `expo/modules/<名>/`。R8 只混淆辅助类，模块类名、Prop 名、Event 名都保留，可以逐行功能等价重写为 `app/modules/<名>`（本地模块会被自动链接）。项目C：`ExpoPagView`（libpag PAGImageView）就是这样复原的。✅
- 本地模块的 `build.gradle` 用 SDK55 写法：`plugins { id 'com.android.library'; id 'expo-module-gradle-plugin' }`。旧模板 `apply from: ExpoModulesCorePlugin.gradle` 会报"没有 compileSdk"。✅
- 冒烟：`npx expo export --platform android` 能打出 bundle 即视为编译通过（产物 hbc 头可校验 Hermes 版本）。✅ 真机：`expo prebuild` → `gradlew assembleDebug -PreactNativeArchitectures=arm64-v8a` → `adb reverse tcp:8081` + Metro。✅
- 坑：
  1. JDK/SDK 放在**纯 ASCII 路径**（JAVA_HOME 含中文时，sdkmanager.bat 会报"未设置 JAVA_HOME"）；sdkmanager 解压 NDK 失败时，直接下载 `android-ndk-<r>-windows.zip` 解压到 `ndk/<Pkg.Revision>`。
  2. RN 0.83 的 `@react-native/gradle-plugin` 钉死 foojay-resolver 0.5.0，配 Gradle 9 报 `JvmVendorSpec ... IBM_SEMERU` → 用 postinstall 补丁把它升到 1.0.0。
  3. adb daemon 一重启，`adb reverse` 就会失效 → App 报"Unable to load script"。每次启动前重新执行 reverse。如果 Agent 的 shell 每条命令结束都会回收 daemon，表现为白屏或图片 `ECONNREFUSED`，此时应在后台常驻 `adb nodaemon server`，再执行 reverse。核对 Metro 时用 `curl --noproxy '*' 127.0.0.1:8081/status`，否则走系统代理会得到 502 假阴性。
  4. 真机锁屏时 screencap 截出来是全黑 → 采证前先确认 `mWakefulness=Awake` 且 `isKeyguardShowing=false`。

## 打包（S7）
- EAS Build 或本地 Gradle；原签名 keystore 若托管在 EAS（credentials），**负责人登录后可以下载**，决定能否原包名覆盖更新。（未验证）

## 案例
- 项目 C（2026-10-01）：Expo SDK 55 / HBC v96；hermes-dec 34 秒出伪 JS；静态即可证实鉴权方式与本地表结构；OTA 关闭，EAS 只剩"追溯线索"价值。
- 项目 C S3（2026-10-02）：271 个 Metro 资源 4 秒还原到原始路径（fail 0），9 语言 i18n 导出；原服务端已下线、EAS/keystore 均不可得 → 必须新后端 + 新签名。
- 项目 C M0（2026-10-02）：Expo55 骨架 + 复原 expo-pag-view，arm64 debug 包在 Android 12 真机启动无崩溃（Fabric）。
