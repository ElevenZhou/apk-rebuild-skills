"""RN(Metro) asset restore: rebuild original source-tree asset layout from Hermes pseudo-JS registerAsset literals.

Matching is by md5 (Metro fileHashes[i] == md5 of each scale file), so it is byte-exact and path-agnostic.

usage: python rn_asset_restore.py <decompiled.js> <out dir> --res <res dir> [--res <split res dir> ...]
                                   [--limit N] [--only png,svg] [--report path]
"""
import argparse, hashlib, json, re, shutil
from pathlib import Path

LIT = re.compile(r"\{'__packager_asset': true, 'httpServerLocation': '([^']*)', (.*?)'name': '([^']*)', 'type': '([^']*)'\}")
ARR = re.compile(r"r\d+ = \[([^\]]*)\];")
IMG = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def parse(js):
    out, lines = [], js.splitlines()
    for i, ln in enumerate(lines):
        m = LIT.search(ln)
        if not m:
            continue
        loc, mid, name, typ = m.groups()
        g = lambda k: (re.search(rf"'{k}': (\d+)", mid) or [None, None])[1]
        scales, hashes = [1], []
        for j in range(i + 1, min(i + 8, len(lines) - 1)):
            a = ARR.search(lines[j])
            if not a:
                continue
            nxt = lines[j + 1]
            if "['scales']" in nxt:
                scales = [float(x) if "." in x else int(x) for x in a.group(1).replace(" ", "").split(",") if x]
            elif "['fileHashes']" in nxt:
                hashes = re.findall(r"'([0-9a-f]{32})'", a.group(1))
                break
        out.append(dict(loc=loc, name=name, type=typ, width=int(g("width")) if g("width") else None,
                        height=int(g("height")) if g("height") else None, scales=scales, hashes=hashes, line=i + 1))
    return out


DENS = {1: "mdpi", 1.5: "hdpi", 2: "xhdpi", 3: "xxhdpi", 4: "xxxhdpi"}


def android_id(loc, name):
    s = (loc[1:] + "/" + name).lower().replace("/", "_")
    return re.sub(r"^assets_", "", re.sub(r"[^a-z0-9_]", "", s))


def by_name(roots, a, scale):
    """Fallback: aapt2 recompresses PNGs, so md5 differs; locate by Metro->Android resource id + density."""
    rid, d = android_id(a["loc"], a["name"]), DENS.get(scale, "mdpi")
    for r in roots:
        for sub in (f"drawable-{d}", f"drawable-{d}-v4", "drawable", "raw"):
            p = Path(r) / sub / f"{rid}.{a['type']}"
            if p.exists():
                return p
    return None


def index(roots):
    idx = {}
    for r in roots:
        for p in Path(r).rglob("*"):
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ttf", ".otf", ".pag", ".json", ".mp3", ".mp4", ".wav", ".lottie"}:
                idx.setdefault(hashlib.md5(p.read_bytes()).hexdigest(), p)
    return idx


def verify(path, a, scale):
    t = a["type"]
    if t in IMG:
        from PIL import Image
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            if a["width"]:
                exp = (round(a["width"] * scale), round(a["height"] * scale))
                if abs(im.size[0] - exp[0]) > 1 or abs(im.size[1] - exp[1]) > 1:
                    return f"size {im.size} != {exp}"
    elif t in ("ttf", "otf"):
        from fontTools.ttLib import TTFont
        TTFont(str(path)).close()
    elif t == "svg":
        if b"<svg" not in path.read_bytes()[:2000].lower():
            return "not svg"
    elif t == "pag":
        if path.read_bytes()[:3] != b"PAG":
            return "bad PAG magic"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("js"); ap.add_argument("out")
    ap.add_argument("--res", action="append", required=True)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--only", default="")
    ap.add_argument("--report", default="")
    ns = ap.parse_args()
    out = Path(ns.out)
    assets = parse(Path(ns.js).read_text(encoding="utf-8", errors="replace"))
    only = set(filter(None, ns.only.split(",")))
    if only:
        assets = [a for a in assets if a["type"] in only]
    if ns.limit:
        assets = assets[: ns.limit]
    idx = index(ns.res)
    rows = []
    for a in assets:
        rel = a["loc"].removeprefix("/assets/")
        got, missing, errs, srcs, recomp = [], [], [], [], []
        for s, h in zip(a["scales"], a["hashes"] or [None] * len(a["scales"])):
            p = idx.get(h) if h else None
            if not p:
                p = by_name(ns.res, a, s)
                if p:
                    recomp.append(s)
            if not p:
                missing.append(s); continue
            sfx = "" if s == 1 else f"@{s}x"
            dst = out / rel / f"{a['name']}{sfx}.{a['type']}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            try:
                e = verify(dst, a, s)
            except Exception as ex:
                e = f"open fail: {ex}"
            if e:
                errs.append(f"@{s}x {e}")
            got.append(s); srcs.append(f"{p.parent.name}/{p.name}")
        if errs or not got:
            st = "FAIL"
        elif missing:
            st = "PARTIAL"   # some density variants absent from this (split) package
        elif recomp:
            st = "OK_RECOMP"  # pixel-equivalent, bytes re-encoded by aapt2 (size verified)
        else:
            st = "OK"
        rows.append(dict(status=st, target=f"{rel}/{a['name']}.{a['type']}", type=a["type"], scales=a["scales"],
                         got=got, missing=missing, recompressed=recomp, src=srcs,
                         err="; ".join(errs + ([f"missing {missing}"] if missing else []))))
    cnt = {k: sum(r["status"] == k for r in rows) for k in ("OK", "OK_RECOMP", "PARTIAL", "FAIL")}
    first = sum(1 for r in rows if r["got"])
    rep = Path(ns.report) if ns.report else out / "_restore_report.json"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text(json.dumps(dict(total=len(rows), **cnt, usable=first, rows=rows), ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        if r["status"] in ("PARTIAL", "FAIL") or ns.limit:
            print(r["status"], r["target"], r["err"])
    by = {}
    for r in rows:
        by.setdefault(r["type"], [0, 0, 0, 0]); by[r["type"]][("OK", "OK_RECOMP", "PARTIAL", "FAIL").index(r["status"])] += 1
    print("BY TYPE ok/recomp/partial/fail:", by)
    print(f"SUMMARY total={len(rows)} ok={cnt['OK']} ok_recomp={cnt['OK_RECOMP']} partial={cnt['PARTIAL']} fail={cnt['FAIL']} usable={first} report={rep}")


if __name__ == "__main__":
    main()
