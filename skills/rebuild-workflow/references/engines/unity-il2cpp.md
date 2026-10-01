# 引擎：Unity IL2CPP（🟡 项目 F S1 部分验证；S3/S5/S7 待填）

> 项目 E/F 共同维护。起草：项目 F（Card Factory! 1.28.0 XAPK，Unity 6000.0.82f1，metadata 31）。未跑完的 S3/S7 段标「未验证」。

## 识别特征（S1，✅ 项目 F machine-verified）
- base APK： `assets/bin/Data/Managed/Metadata/global-metadata.dat` 头 magic `0xFAB11BAF`，偏移 4 处为 metadata 版本号（项目 F = 31）。
- 同目录 `data.unity3d` 头是 UnityFS 归档，含可读字符串 `5.x.x 6000.0.82f1` → **Unity 版本号直接从这里取**。
- ABI 分包（config.<abi>.apk）内 `lib/<abi>/libil2cpp.so` 与 `libunity.so`。**XAPK 可能只带一个 ABI**（项目 F 仅 armeabi-v7a，无 arm64）——作者笔记里写什么以实际解包为准。
- `assets/bin/Data/ScriptingAssemblies.json` 列全部托管程序集名单（项目 F 共 215 个）。
- 加固判别：detect_engine packers 空 + Il2CppDumper 无 warning 直读成功 = 未见传统壳。注意广告/反欺诈库（穿山甲 pglarmor、AppHarbr 等）不算加固。

## 解包与回导工具

| 资源类型 | 工具 | 命令 / 输入 | 验证状态 |
|---|---|---|---|
| C# 签名（dump.cs / DummyDll） | Il2CppDumper 6.7.46 | `Il2CppDumper.exe libil2cpp.so global-metadata.dat <outdir>`；so 用 ABI 分包里的，metadata 在 base APK | ✅ 项目 F machine-verified（dump.cs 43MB / 120 万行 / stringliteral 2.5 万条） |
| manifest/权限/SDK | apktool 3.0.3 | `java -jar apktool.jar d base.apk -s -f`；**Windows PATH 里若无 java，apktool.bat 会静默卡死，务必显式指向 jdk** | ✅ 项目 F（-s 先拿资源层；dex 用 jadx 另看） |
| Java/Kotlin 层（SDK/桥） | jadx 1.5.6 | `jadx -d <out> <apk>`（18+ dex 大包皮重，后台跑） | ✅ 工具就位，项目 F 结果待 S2 |
| 资产回导（贴图/音频/ScriptableObject） | AssetRipper / AssetStudio；**Python 侧用 UnityPy 1.25+（可逐 bundle 操作，注意多文件同加载易 segfault，单文件单进程更安全）；bundle 里 MonoBehaviour 可用 `obj.read()` + `get_raw_data()` 直接取字节，关卡数据保留完整结构** | ✅ 项目 F：defaultlocalgroup.bundle 内 HitFunnel V2 全量 480 关 MonoBehaviour 可用 |
| Addressables bundle | assets/aa/Android/*.bundle（项目 F：3 场景 + defaultlocalgroup + CJK 字体 + monoscripts + unitybuiltin，77.6MB） | 待 S3 样品验证 | ⬜ |
| 云端关卡（Unity CCD） | CCD endpoint 无鉴权直读：`https://{projectId}.client-api.unity3dusercontent.com/client_api/v1/environments/{env}/buckets/{bucketId}/entry_by_path/content/?path=...`。**projectId 在 PlayerSettings.cloudProjectId；bucketId/env 在 datapack 或 addressables 里的 CloudContentConfiguration MonoBehaviour（raw bytes 扫 GUID+environment 名）；注意 307 重定向要 `curl -L`** | ✅ 项目 F：Live 481 关 + Wip 50 关全量拉下，MD5 抽检一致 |

## 开发（S5）
- 冒烟命令：⬜ 未验证（候选：Unity 编辑器批处理模式 + 真机 ADB）
- 测试运行方式：⬜

## 打包（S7）
- 工具链版本：⬜（项目 F 若沿用 Unity 6 → Unity 6000.0.x LTS + JDK)
- 签名方式：⬜
- 已踩坑：⬜

## 案例
- 项目 F（2026-10，进行中）：Unity 6 IL2CPP XAPK 三层（base + config-abi + UnityDataAssetPack）结构成立；**puzzle 品类的"关卡全在云端"假设被推翻**——本地兜底 funnel 通常就是全量（HitFunnel V2 1–480 都在 defaultlocalgroup bucket），CCD 只承载 AB 批次和 Remote 运营位；CCD 公开桶可无鉴权全量拉。
