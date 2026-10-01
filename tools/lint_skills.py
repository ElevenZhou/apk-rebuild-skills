#!/usr/bin/env python3
"""Skill 仓库检查：frontmatter 必填字段、章节齐全、行数上限、密钥扫描。

用法: python tools/lint_skills.py   （在仓库根目录运行；非 0 退出码 = 不通过）
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REQUIRED_FM = ["name", "description", "version", "owner"]
REQUIRED_SECTIONS = ["何时用", "相关 skill", "变更记录"]
MAX_LINES = 200
SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|secret|password|passwd|token)\s*[=:]\s*[\"'][A-Za-z0-9_\-]{16,}[\"']"), "疑似明文密钥"),
    (re.compile(r"\b[0-9a-f]{64}\b"), "64 位十六进制串（疑似 Key；sha256 请写在 scope.md 而不是仓库）"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "Google API Key"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI 风格 Key"),
    (re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"), "私钥"),
]
TEXT_EXT = {".md", ".py", ".gd", ".cfg", ".yaml", ".yml", ".json", ".ps1", ".sh", ".txt"}


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    return dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))


def main():
    errors = []
    for skill in sorted((ROOT / "skills").iterdir()):
        f = skill / "SKILL.md"
        if not f.exists():
            errors.append(f"{skill.name}: 缺少 SKILL.md")
            continue
        text = f.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{skill.name}: 缺少 frontmatter")
            continue
        for k in REQUIRED_FM:
            if not fm.get(k):
                errors.append(f"{skill.name}: frontmatter 缺 {k}")
        if fm.get("name") != skill.name:
            errors.append(f"{skill.name}: name 与目录名不一致（{fm.get('name')}）")
        for s in REQUIRED_SECTIONS:
            if s not in text:
                errors.append(f"{skill.name}: 缺少章节「{s}」")
        n = text.count("\n")
        if n > MAX_LINES:
            errors.append(f"{skill.name}: SKILL.md {n} 行，超过 {MAX_LINES}，请拆到 references/")

    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or p.suffix.lower() not in TEXT_EXT:
            continue
        if p.name == "lint_skills.py":
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(text.splitlines(), 1):
            for pat, why in SECRET_PATTERNS:
                if pat.search(line):
                    errors.append(f"{p.relative_to(ROOT)}:{i}: {why}")

    if errors:
        print("LINT FAIL")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("LINT OK")


if __name__ == "__main__":
    main()
