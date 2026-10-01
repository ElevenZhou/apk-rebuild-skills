---
name: rebuild-asset-recovery
description: 逆向重建 S3 资源回导：从自有安装包解包产物中恢复可编辑的美术/音频/字体/动画/文案资源，遵循"样品先行 → 批量 → 报告 → 原件不动"规则。内置 Godot 4.x 全套无 GDRE 依赖回导脚本（ctex→png、oggvorbisstr→ogg、fontdata→ttf、spatlas/spskel→Spine）；其他引擎给出通用流程与候选工具。由原 godot-asset-recovery 迁入。触发词：资源回导、提取素材、ctex、oggvorbisstr、spine 导出、恢复美术资源。
version: 1.0.0
owner: ElevenZhou
---

# rebuild-asset-recovery — 资源回导

## 何时用 / 何时不用
- **用**：已完成解包（`rebuild-recon` S1），需要把引擎导入格式还原为可编辑源格式，供新工程复用。
- **不用**：资源本来就是明文 png/ogg（原生 apktool res/ 直接可用，只需拷贝 + 登记）。

## 需要的输入
- 解包目录（如 Godot 的 `.godot/imported/`）、输出目录、报告目录。
- 引擎对应的官方编辑器（Godot 用同主版本 headless 即可）。

## 通用规则（与引擎无关）
1. **样品先行**：每类资源先挑 3-5 个样品回导，人工验收（能打开、尺寸/时长正确），填 `references/sample-acceptance.md` 表，全部 PASS 再批量。
2. **原件不动**：解包目录只读；输出到 `rebuild/<工程>/assets_imported/<类型>/`。
3. **批量必出报告**：每行 `OK|FAIL <类型> <源> -> <目标> <规格>`，末行 `SUMMARY`。fail>0 的逐条进待优化清单。
4. **命名还原**：去掉引擎加的 hash 后缀（`name.png-<md5>.ctex` → `name.png`），重名追加短 hash。
5. **回读校验**：能用引擎再加载回来的，做往返对比（音频时长误差 <0.05s）。
6. 全部路径用纯 ASCII 更稳（OpenCV 等库遇中文路径会静默失败）。

## Godot 4.x（✅ 已验证）

| 源格式 | 实质 | 脚本 |
|---|---|---|
| `.ctex`（GST2） | CompressedTexture2D | `scripts/godot/ctex_batch.gd` → png |
| `.fontdata`（RSCC） | FontFile，`data` 即原始 TTF/OTF | 同上 → ttf |
| `.oggvorbisstr`（RSRC） | AudioStreamOggVorbis，内部是**按页分组的 vorbis 包，没有 OggS 页流** | `scripts/godot/ogg_batch.gd` 重封装 → ogg |
| `.spatlas` | 纯 JSON，`atlas_data` 字段是原始 .atlas 文本 | `scripts/godot/spine_batch.py` |
| `.spskel` | 原始 Spine 二进制原样存储 | 同上，改名 .skel |

运行（所有路径以 `--` 之后的用户参数传入）：
```bash
godot --headless -s scripts/godot/ctex_batch.gd -- <imported_dir> <out_dir> <report.txt>
godot --headless -s scripts/godot/ogg_batch.gd  -- <imported_dir> <out_dir>/audio <report.txt>
python scripts/godot/spine_batch.py <imported_dir> <out_dir>/spine <report.txt>
```

### Ogg 重封装的坑（都踩过）
1. Ogg CRC32：多项式 0x04C11DB7、MSB-first、init=0、无 xorout（≠ zlib CRC32）。
2. 查表索引用**移位前**的高字节：`idx=((crc>>24)^b)&0xFF; crc=((crc<<8)&0xFFFFFFFF)^table[idx]`。单字节用例测不出错，必须多字节验证。
3. GDScript `PackedInt32Array` 是有符号的，取出后 `& 0xFFFFFFFF`。
4. 段表：包长是 255 整数倍时必须补一个 0 段，否则解码器把包粘在一起。
5. `granule_positions` 每页一条，与页一一对应。
6. libogg 会**静默丢弃** CRC 错误的页 → 解析失败先查 CRC。

### 其他 Godot 注意
- `.etc2.ctex`（移动端压缩）：✅ 桌面 Godot 4.6 可以 `get_image()` + `decompress()` 正常导出（项目 D 582/582）。文件名多一层 `.etc2` 后缀，脚本按最后一个 `-` 切分去掉 hash。
- `.fontdata` 若引用了其他字体作为 fallback（如 `res://assets/fonts/xxx.ttf`），单独加载会因依赖缺失失败 → 报告里记为 FAIL，从其他导出的字体手工补齐即可（项目 D 13 个里 1 个）。
- `.scn` 二进制场景 → GDRE Tools 是首选（`--recover=… --output=…`），D 项目 v2.6.4 CLI 卡死未用。
- 有 Spine 资源 = 原包用了 spine-godot 定制版，重建需集成运行时或先降级为静态贴图。

## 其他引擎（⚠️ 待真实案例）
按通用规则执行，工具候选见 `rebuild-workflow/references/engines/_template.md`。首个真实项目做完后在此补一节并 PR。

## 出口标准（= M0 资源部分）
- 样品验收表 100% PASS；
- 各类批量报告 SUMMARY fail=0，或失败项已登记且有降级方案。

## 相关 skill
上游 `rebuild-recon` → 下游 `rebuild-dev-milestones`（M0 骨架引用 assets_imported）、`rebuild-product-design`（换皮时决定哪些资源替换）。

## 变更记录
- 1.0.0（2026-10-01）由 godot-asset-recovery 迁入并改名；脚本参数化；增加通用规则。
