#!/usr/bin/env python3
"""识别 APK/XAPK/AAB 的引擎与加固特征。

用法: python detect_engine.py <package.apk|xapk|aab>
输出: JSON（引擎候选、证据文件、加固候选、内嵌 APK 列表）
"""
import json
import sys
import zipfile

ENGINE_MARKERS = {
    "godot": ["libgodot_android.so", ".pck", ".godot/imported/"],
    "unity-il2cpp": ["libil2cpp.so", "global-metadata.dat"],
    "unity-mono": ["libmono.so", "libmonobdwgc-2.0.so", "Assembly-CSharp.dll"],
    "cocos": ["libcocos2djs.so", "libcocos.so", "libcocos2dcpp.so", ".jsc"],
    "unreal": ["libUE4.so", "libUnreal.so"],
    "flutter": ["libflutter.so", "libapp.so"],
    "react-native": ["libreactnativejni.so", "index.android.bundle"],
}
PACKER_MARKERS = {
    "360jiagu": ["libjiagu"],
    "bangcle": ["libsecexe.so", "libDexHelper"],
    "tencent-legu": ["libshell", "libtup.so"],
    "ijiami": ["libexec.so", "libexecmain.so"],
}


def scan_names(names):
    engines, packers = {}, {}
    for n in names:
        for eng, marks in ENGINE_MARKERS.items():
            if any(m in n for m in marks):
                engines.setdefault(eng, []).append(n)
        for p, marks in PACKER_MARKERS.items():
            if any(m in n for m in marks):
                packers.setdefault(p, []).append(n)
    return engines, packers


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    result = {"file": path, "inner_apks": [], "engines": {}, "packers": {}, "dex_count": 0}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        inner = [n for n in names if n.endswith(".apk")]
        result["inner_apks"] = inner
        all_names = list(names)
        for n in inner:  # XAPK：扫描内嵌 APK
            with z.open(n) as f, zipfile.ZipFile(f) as iz:
                all_names += [f"{n}!{x}" for x in iz.namelist()]
    result["dex_count"] = sum(1 for n in all_names if n.endswith(".dex"))
    engines, packers = scan_names(all_names)
    result["engines"] = {k: v[:5] for k, v in engines.items()}
    result["packers"] = {k: v[:5] for k, v in packers.items()}
    if not engines:
        result["note"] = "未命中引擎特征：可能是原生 Android，或需要人工检查 lib/ 与 assets/"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
