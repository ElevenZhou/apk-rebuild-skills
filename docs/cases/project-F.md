# 案例：项目 F（Card Factory! 1.28.0 → 重建中）— 进行中

> 阶段性记录（截至 2026-10-16，M0 骨架进行中）。项目 E（Annoying Punch，同为 Unity + IL2CPP）复用本案例的引擎专节。

| 项 | 内容 |
|---|---|
| 原包 | Card Factory! 1.28.0 XAPK（259MB，puzzle），Unity 6000.0.82f1 + IL2CPP，metadata v31，仅 armeabi-v7a |
| 路线 | R3 纯重做（dump.cs 只有签名没有方法体，逻辑不可还原）；D1–D7 于 2026-10-03 全部确认 |
| 新工程 | Unity 6 工程，放 ASCII 路径（`E:/Dev-2/rebuild-cf/`） |

## 关键经验
1. **Il2CppDumper 原版即可处理 metadata 31**；结尾 `Console.ReadKey` 在输出重定向时会抛异常，但产物已完整，不是失败。
2. **"关卡云端化"是误判**：看到 CloudContent 索引里有 1257 条时，先去 datapack/defaultlocalgroup 里找本地兜底——项目 F 的 480 关全量就在本地 bundle 里，CCD 只承载 AB 切换和远程批次。
3. CCD 拉桶：bucket ID 在 datapack 的 CloudContentConfiguration MonoBehaviour 里（raw bytes 扫 GUID + 环境名），`entry_by_path` 无鉴权，307 需 `-L`，用 FileIndex 的 hash 对 md5 校验（10/10 一致）。
4. **UnityPy 可作 AssetRipper 之外的回导选项**：单文件单进程（多 bundle 同进程加载易 segfault）；MonoBehaviour 用 `get_raw_data()` 保留完整结构。
5. AudioClip 导出用 `clip.samples`，不是 `audio_data`（用错会静默为空，曾误判"零音频"）；FMOD 外置 FSB5 是压缩不是加密，通常有同名 Vorbis 内联副本。
6. Windows 下 PATH 无 java 时 apktool.bat **静默卡死**，要显式指向 JDK 的 java.exe，并加 `-s` 先拿资源层。
7. Unity / OpenCV 遇中文路径静默失败 → 重建工程一律放 ASCII 路径。
8. 品类经验（puzzle）：Funnel 命名即版本实验，重建只取当前线上主线（v1.15），其余是历史对照组。

## 通用建议（✅ 已经负责人批准，全部纳入 v1.2.0）
| # | 建议 | 影响 |
|---|---|---|
| F-2 | 通用流程写明环境前置：java 在 PATH 或显式指定，apktool 先 `-s` | recon 步骤 |
| F-4 | 哈希基线命令统一写法（Bash `sha256sum`），不依赖 PowerShell 回显 | 全部 skill 使用说明 |
| F-7 | 样品验收按资源类分开评：Unity 的 Mesh/Sprite/AnimationClip 一般只能存 raw，不能要求落 FBX/PNG | asset-recovery 规则 |
| F-8 | AudioClip 两种存储（Vorbis 内联 / FMOD 外置）与正确导出属性写进通用规则 | asset-recovery（引擎节已写） |

## 遗留
M0：Zenject 骨架、480 关转 SO、headless 冒烟进行中；S3 的 Mesh/AnimationClip 转换未做；S7 Unity Android 导出未验证。
