---
name: rebuild-build-release
description: 逆向重建 S7 打包交付：配置 Android 导出工具链（导出模板、JDK、Android build-tools、keystore）、生成签名试玩 APK、真机安装冒烟、整理交付工程文件与交付清单。内含 Godot 4.x 导出五坑（含"导出失败但零错误文案"的 ETC2 问题）。单独使用场景：任何 Godot 项目打 Android 包；任何项目的最终交付归档。触发词：打包 APK、导出安卓、签名、keystore、试玩包、交付工程、release。
version: 1.0.0
owner: ElevenZhou
---

# rebuild-build-release — 打包与交付

## 何时用 / 何时不用
- **用**：需要出试玩 APK（任一里程碑都可以出内测包）；项目最终交付。
- **不用**：开发中的日常运行（headless/编辑器即可）。

## 需要的输入
- 工程源码、包名与品牌（来自 `rebuild-product-design` D3/D6）。
- release keystore（新建或负责人提供）+ 密码，存放在**仓库之外**的本地文件。
- 真机（安装冒烟）。

## 一、工具链准备（全部放纯 ASCII 路径，如 `C:/android-sdk`、`C:/jdk21`、`C:/godot`）
| 组件 | 要求 | 获取 |
|---|---|---|
| 引擎导出模板 | 版本与编辑器**完全一致** | 官方 release 页；大文件后台下载，失败换镜像 |
| JDK | 17 或 21 | Temurin |
| Android build-tools | ≥ 模板的 target SDK（Godot 4.6 → 35+） | `https://dl.google.com/android/repository/repository2-3.xml` 查真实文件名（新版是 `build-tools_r36_windows.zip`，没有次版本号） |
| platform-tools | adb | 同上 |
| SDK 目录结构 | `<sdk>/build-tools/<ver>/apksigner.bat`、`<sdk>/platform-tools/adb.exe` | 手动整理解压结果 |

新建 keystore：
```bash
keytool -genkeypair -v -keystore C:/keystores/<app>-release.keystore -alias <app>_release \
  -keyalg RSA -keysize 2048 -validity 10000
```
密码写进 `CREDENTIALS.local.txt`（gitignore），并交负责人托管。**丢了 keystore 就再也无法更新这个包名**——这正是项目 D 必须换包名的原因。

## 二、Godot 4.x 导出（✅ 已验证）
1. editor_settings 配 `java_sdk_path`、`android_sdk_path`、debug keystore（见 `rebuild-workflow/references/engines/godot.md`）。
2. `project.godot` 的 `[rendering]` 段加 `textures/vram_compression/import_etc2_astc=true`。
3. `export_presets.cfg`：参照 `references/export_presets.android.example.cfg`；keystore 三元组**要么全填要么全空**。
4. 导出：
   ```bash
   Godot_console.exe --headless --path . --export-release "Android" C:/build/<app>.apk
   ```
5. 失败但没有错误文案 → 按顺序查：ETC2 → 三元组 → 中文路径 → build-tools 版本 → 模板目录名。还查不出就用"最小空项目 + 同一个 preset"判断是环境问题还是项目问题，最后读 `platform/android/export/export_plugin.cpp` 找 `valid = false`。

其他引擎：⚠️ 待真实案例，照 `engines/_template.md` 记录。

## 三、安装冒烟（必须做）
```bash
adb -s <SN> install -r C:/build/<app>.apk          # 报"无证书" = 没签上名
adb -s <SN> shell monkey -p <包名> -c android.intent.category.LAUNCHER 1
```
用 `rebuild-device-evidence` 截图：启动页 → 首页 → 进一局 → 退出，确认无黑屏/崩溃/明显错位，截图存 `evidence/playtest/`。

## 四、交付物与交付清单
按 `references/delivery-checklist.md` 逐项打勾，交付目录：
```
release/<app>-v<版本>/
  <app>-v<版本>-release.apk      签名试玩包（附 sha256）
  <app>-src-v<版本>.zip          工程源码（不含 .godot/ 缓存、build/、密钥）
  docs/                          产品文档、开发计划、M#-进展、待优化清单快照
  交付清单.md                    含已知问题与下一步建议
```
keystore 和密码**单独**交给负责人，不放进交付包。

## 出口标准
签名 APK 真机安装、启动、完成一局全部通过；交付清单全绿；已知问题全部列出。

## 相关 skill
上游 `rebuild-dev-milestones` → 调用 `rebuild-device-evidence` → 交付后回 `rebuild-workflow` 执行复盘。

## 变更记录
- 1.0.0（2026-10-01）项目 D PawStar 首个签名 APK（122MB）打通过程提炼。
