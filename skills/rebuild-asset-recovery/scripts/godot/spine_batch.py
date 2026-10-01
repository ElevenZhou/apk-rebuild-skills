#!/usr/bin/env python3
"""批量回导 Godot spine-godot 资源：.spatlas → .atlas，.spskel → .skel。

用法: python spine_batch.py <imported_dir> <out_dir> <report.txt>
.spatlas 是纯 JSON（atlas_data 字段为原始 atlas 文本）；.spskel 是原始 Spine 二进制原样存储。
"""
import json
import pathlib
import sys


def strip_hash(name: str, ext: str) -> str:
    # "Name.atlas-<md5>.spatlas" -> "Name" + ext
    p = pathlib.Path(name).stem          # 去 .spatlas
    p = pathlib.Path(p).stem             # 去 ".atlas-<md5>" → "Name"
    return p + ext


def unique(dst: str, src: str, used: set) -> str:
    if dst in used:
        h = pathlib.Path(src).stem.split("-")[-1][:6]
        dst = pathlib.Path(dst).stem + "_" + h + pathlib.Path(dst).suffix
    used.add(dst)
    return dst


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    imp, out, report = (pathlib.Path(a) for a in sys.argv[1:4])
    out.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    lines, ok, fail, used = [], 0, 0, set()
    for f in sorted(imp.iterdir()):
        n = f.name
        try:
            if n.endswith(".spatlas"):
                dst = unique(strip_hash(n, ".atlas"), n, used)
                text = json.loads(f.read_text(encoding="utf-8"))["atlas_data"]
                (out / dst).write_text(text, encoding="utf-8")
                lines.append(f"OK\tatlas\t{n}\t-> {dst} {len(text)}B")
                ok += 1
            elif n.endswith(".spskel"):
                dst = unique(strip_hash(n, ".skel"), n, used)
                data = f.read_bytes()
                vlen = data[8]
                ver = data[9:9 + vlen].decode("ascii", errors="replace").rstrip("\x00")
                (out / dst).write_bytes(data)
                lines.append(f"OK\tskel\t{n}\t-> {dst} {len(data)}B spine={ver}")
                ok += 1
        except Exception as e:  # 单文件失败不中断批量，记入报告
            lines.append(f"FAIL\tspine\t{n}\t{e}")
            fail += 1
    lines.append(f"SUMMARY\tspine ok={ok} fail={fail}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"spine ok={ok} fail={fail}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
