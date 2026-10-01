#!/usr/bin/env python3
"""把一张或多张图片 + 问题发给视觉模型（Gemini generateContent 兼容接口），打印回答。

用法:
  python vision_ask.py img1.png [img2.png ...] "问题"
环境变量（必填，不要写进脚本）:
  VISION_API_KEY   API Key
  VISION_API_URL   接口根地址，默认 https://generativelanguage.googleapis.com
  VISION_MODEL     模型名，默认 gemini-2.5-flash
"""
import base64
import json
import os
import sys
import urllib.request


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    *images, prompt = sys.argv[1:]
    key = os.environ.get("VISION_API_KEY")
    if not key:
        sys.exit("缺少环境变量 VISION_API_KEY")
    base = os.environ.get("VISION_API_URL", "https://generativelanguage.googleapis.com").rstrip("/")
    model = os.environ.get("VISION_MODEL", "gemini-2.5-flash")
    url = f"{base}/v1beta/models/{model}:generateContent?key={key}"

    parts = [{"text": prompt}]
    for p in images:
        mime = "image/jpeg" if p.lower().endswith((".jpg", ".jpeg")) else "image/png"
        with open(p, "rb") as f:
            parts.append({"text": f"--- {os.path.basename(p)} ---"})
            parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(f.read()).decode()}})

    body = json.dumps({"contents": [{"parts": parts}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read().decode())
    cands = data.get("candidates") or []
    if not cands:
        sys.exit("NO RESPONSE: " + json.dumps(data, ensure_ascii=False)[:500])
    print(cands[0]["content"]["parts"][0]["text"])


if __name__ == "__main__":
    main()
