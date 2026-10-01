#!/usr/bin/env python3
"""在截图中按颜色找目标区域中心，输出可直接用于 adb input tap 的坐标。

用法:
  python find_color.py shot.png --rgb 240,140,40 [--tol 40] [--min-pixels 100] [--region x0,y0,x1,y1]
输出: center=(x, y) bbox=(x0,y0,x1,y1) pixels=N
"""
import argparse
import sys

import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--rgb", required=True, help="目标颜色 r,g,b（可先用取色工具或 PIL 读像素）")
    ap.add_argument("--tol", type=int, default=40, help="每通道容差")
    ap.add_argument("--min-pixels", type=int, default=100)
    ap.add_argument("--region", help="限定搜索区域 x0,y0,x1,y1")
    a = ap.parse_args()

    arr = np.array(Image.open(a.image).convert("RGB")).astype(np.int16)
    ox = oy = 0
    if a.region:
        x0, y0, x1, y1 = map(int, a.region.split(","))
        arr = arr[y0:y1, x0:x1]
        ox, oy = x0, y0
    target = np.array(list(map(int, a.rgb.split(","))), dtype=np.int16)
    mask = np.all(np.abs(arr - target) <= a.tol, axis=2)
    ys, xs = np.where(mask)
    if len(ys) < a.min_pixels:
        sys.exit(f"NOT FOUND (pixels={len(ys)})")
    cx, cy = int(xs.mean()) + ox, int(ys.mean()) + oy
    print(f"center=({cx}, {cy}) bbox=({xs.min()+ox},{ys.min()+oy},{xs.max()+ox},{ys.max()+oy}) pixels={len(ys)}")


if __name__ == "__main__":
    main()
