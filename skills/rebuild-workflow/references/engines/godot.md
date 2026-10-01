# 引擎：Godot 4.x（✅ 项目 D 全程验证，Godot 4.6.3）

## 识别特征（S1）
- APK 内 `lib/*/libgodot_android.so`；assets 下 `.pck` 或 `.godot/imported/`；XAPK 的 assetpack 内也可能有 `.godot/imported/`。
- `.ctex` 头 `GST2`、资源头 `RSRC`/`RSCC`。

## 解包与回导（S3） → 见 `rebuild-asset-recovery`
- 可用 GDRE Tools：`gdre_tools --headless --recover=<pck/apk> --output=<dir>`（参数是 `--output`；参数错了不报错，直接卡住）。D 项目 v2.6.4 CLI 卡死，改用自研 headless 脚本。
- 加密脚本（.gdc/.gde）通常无法还原 → 直接按「纯重做」路线走。

## 开发（S5）
- 冒烟：`godot --headless --path . --quit-after 3 2>&1 | grep -E "SCRIPT ERROR|nonexistent"`。
- 测试：`tests_dev/*.gd` 以 `extends SceneTree` 写，`godot --headless -s tests_dev/xxx.gd` 运行。
- 原包用了 Spine（`.spatlas/.spskel`）→ 需要 spine-godot 运行时；先做静态贴图 + Tween 降级版，不阻塞主线。

## 打包（S7）五坑
1. 导出模板目录名必须等于编辑器版本号（如 `export_templates/4.6.3.stable/`），tpz 解压出来叫 `templates/`，要改名。
2. build-tools：Godot 4.6 模板 target SDK 35+，需 build-tools ≥35；dl.google 新命名无次版本号（`build-tools_r36_windows.zip`），查 `repository2-3.xml` 得到真实文件名。
3. **全 ASCII 路径**：SDK/JDK/Godot/keystore/输出路径都放纯英文目录。
4. keystore 三元组（路径 + user + password）debug/release 各自**要么全填要么全空**，空字符串不等于没填。
5. **ETC2/ASTC**：`project.godot` 的 `[rendering]` 加 `textures/vram_compression/import_etc2_astc=true`。缺了这一项导出会失败，而且错误列表是空的。
- 命令：`Godot_console.exe --headless --path . --export-release "Android" C:/out/app.apk`

## 编辑器设置（editor_settings-4.x.tres）
```
export/android/java_sdk_path = "C:/jdk21/..."
export/android/android_sdk_path = "C:/android-sdk"
export/android/debug_keystore = ".../debug.keystore"
export/android/debug_keystore_user = "androiddebugkey"
export/android/debug_keystore_pass = "android"
```
