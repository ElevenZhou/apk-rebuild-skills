#!/usr/bin/env python3
"""统计解包目录的资源类型清单（扩展名 × 数量 × 体积）。

用法: python asset_manifest.py <extracted_dir> > assets/manifest.json
"""
import json
import pathlib
import sys
from collections import defaultdict


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = pathlib.Path(sys.argv[1])
    stats = defaultdict(lambda: {"count": 0, "bytes": 0})
    for p in root.rglob("*"):
        if p.is_file():
            ext = p.suffix.lower() or "(none)"
            stats[ext]["count"] += 1
            stats[ext]["bytes"] += p.stat().st_size
    ordered = dict(sorted(stats.items(), key=lambda kv: -kv[1]["count"]))
    total = {"files": sum(v["count"] for v in ordered.values()),
             "bytes": sum(v["bytes"] for v in ordered.values())}
    print(json.dumps({"root": str(root), "total": total, "by_ext": ordered},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
