"""Extract i18n locale objects from Hermes pseudo-JS (hermes-dec) module bodies.

Locale modules in Metro bundles are flat sequences of:
    rN = {...literal...} | [...] | 'str' | number | true/false/null | rM | rM.x
    rA['key'] = rB ;  rA.key = rB
    a?['exports'] = rX   (module.exports)
We interpret just these statements; anything else is reported as unsupported.

usage: python i18n_extract.py <decompiled.js> <out_dir> <lang>:<start>-<end> [...]
"""
import ast, json, re, sys
from pathlib import Path

ASSIGN = re.compile(r"^\s*(r\d+) = (.+);\s*$")
SETP = re.compile(r"^\s*(r\d+)\[(.+?)\] = (r\d+);\s*$")
SETD = re.compile(r"^\s*(r\d+)\.(\w+) = (r\d+);\s*$")


def lit(src):
    s = src.strip()
    s = re.sub(r"\btrue\b", "True", s); s = re.sub(r"\bfalse\b", "False", s)
    s = re.sub(r"\bnull\b", "None", s); s = re.sub(r"\bundefined\b", "None", s)
    if s.startswith("new Array("):
        return [None] * int(s[10:-1])
    return ast.literal_eval(s)


def run(lines):
    regs, exports, unsupported = {}, None, 0
    for ln in lines:
        if "['exports'] = " in ln:
            exports = regs.get(ln.split("= ")[-1].strip(" ;"))
            continue
        m = SETP.match(ln)
        if m:
            tgt, key, val = m.groups()
            k = lit(key) if not key.startswith("r") else regs.get(key)
            if tgt in regs and isinstance(regs[tgt], (dict, list)):
                if isinstance(regs[tgt], list) and isinstance(k, int):
                    regs[tgt][k] = regs.get(val)
                else:
                    regs[tgt][k] = regs.get(val)
            continue
        m = SETD.match(ln)
        if m:
            tgt, key, val = m.groups()
            if tgt in regs and isinstance(regs[tgt], dict):
                regs[tgt][key] = regs.get(val)
            continue
        m = ASSIGN.match(ln)
        if m:
            r, rhs = m.groups()
            if re.fullmatch(r"r\d+", rhs):
                regs[r] = regs.get(rhs)
            else:
                try:
                    regs[r] = lit(rhs)
                except Exception:
                    regs[r] = None; unsupported += 1
    return exports, unsupported


def flat(d, p=""):
    for k, v in d.items():
        kk = f"{p}.{k}" if p else str(k)
        if isinstance(v, dict):
            yield from flat(v, kk)
        else:
            yield kk, v


def main():
    js, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    lines = Path(js).read_text(encoding="utf-8", errors="replace").splitlines()
    summary = {}
    for spec in sys.argv[3:]:
        lang, rng = spec.split(":"); a, b = map(int, rng.split("-"))
        exp, uns = run(lines[a - 1:b])
        if not isinstance(exp, dict):
            print("FAIL", lang, "no exports"); summary[lang] = None; continue
        (out / f"{lang}.json").write_text(json.dumps(exp, ensure_ascii=False, indent=2), encoding="utf-8")
        kv = dict(flat(exp)); nulls = sum(v is None for v in kv.values())
        summary[lang] = dict(keys=len(kv), null_values=nulls, unsupported_stmts=uns)
        print("OK" if nulls == 0 else "WARN", lang, summary[lang])
    base = set(dict(flat(json.loads((out / "en.json").read_text(encoding="utf-8"))))) if (out / "en.json").exists() else set()
    for lang in summary:
        if summary[lang] and lang != "en":
            ks = set(dict(flat(json.loads((out / f"{lang}.json").read_text(encoding="utf-8")))))
            summary[lang]["missing_vs_en"] = len(base - ks); summary[lang]["extra_vs_en"] = len(ks - base)
    (out / "_i18n_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
