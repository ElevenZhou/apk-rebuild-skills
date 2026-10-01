#!/usr/bin/env python3
"""录屏场景切变抽帧：按帧差找页面切换点，导出关键帧与时间线。

用法:
  python extract_keyframes.py video.mp4 out_dir [--threshold 28] [--sample-fps 2] [--min-gap 1.0] [--start S] [--end S]
细抽某段：--start 61.0 --end 63.5 --threshold 0 --sample-fps 10
"""
import argparse
import os
import sys

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out_dir")
    ap.add_argument("--threshold", type=float, default=28.0, help="灰度缩略图平均帧差阈值")
    ap.add_argument("--sample-fps", type=float, default=2.0)
    ap.add_argument("--min-gap", type=float, default=1.0, help="两张关键帧最小间隔秒")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=1e9)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    cap = cv2.VideoCapture(a.video)
    if not cap.isOpened():
        sys.exit("无法打开视频（路径含中文时先复制到英文路径）")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"视频: {total} 帧 @ {fps:.1f}fps = {total / fps:.0f}s")
    step = max(1, int(round(fps / a.sample_fps)))
    cap.set(cv2.CAP_PROP_POS_MSEC, a.start * 1000)

    prev, last_t, idx, saved = None, -1e9, int(a.start * fps), 0
    timeline = []
    while True:
        ok = cap.grab()
        if not ok:
            break
        idx += 1
        t = idx / fps
        if t > a.end:
            break
        if idx % step:
            continue
        ok, frame = cap.retrieve()
        if not ok:
            break
        small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (90, 200)).astype(np.int16)
        diff = 999.0 if prev is None else float(np.mean(np.abs(small - prev)))
        prev = small
        if diff >= a.threshold and t - last_t >= a.min_gap:
            name = f"key-t{t:07.1f}.png"
            ok_w, buf = cv2.imencode(".png", frame)  # 中文路径下 imwrite 会静默失败
            if ok_w:
                with open(os.path.join(a.out_dir, name), "wb") as fp:
                    fp.write(buf.tobytes())
            timeline.append(f"t={t:7.1f}s diff={diff:5.1f} {name}{'' if ok_w else ' [写失败]'}")
            last_t, saved = t, saved + 1
    cap.release()
    with open(os.path.join(a.out_dir, "timeline.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(timeline) + "\n")
    print(f"关键帧 {saved} 张 → {a.out_dir}/timeline.txt")


if __name__ == "__main__":
    main()
