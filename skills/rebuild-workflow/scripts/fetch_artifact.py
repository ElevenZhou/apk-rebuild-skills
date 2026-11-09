#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_artifact.py — A0 原包获取（rebuild-workflow）

把四种输入统一成一个可校验的安装包，并产出来源留痕：

    --from-file <path>     本地已有 APK/XAPK/EXE  → 只校验 + 归档 + 登记，直接进入 S0
    --name <游戏名>        搜索候选包名 → 人工确认（--pick N 或改用 --play-url）
    --play-url <URL>       Google Play 详情页 → 提取包名 → 走公开镜像下载
    --market-url <URL>     APKPure / APKCombo / APKMirror 等下载页或直链 → 下载

输出：<out>/artifact-source.json（A0 留痕），stdout 打印同一份 JSON。

依赖：Python 3.10+；网络下载需要 `pip install playwright`（用本机 Chrome 或 Playwright chromium）。
不硬编码任何路径、代理、账号或密钥；代理用 --proxy 或 HTTPS_PROXY 环境变量。

合规：只取公开可免费获取的安装包用于分析，不绕过登录 / 付费 / 验证码 / 区域限制；
付费或需授权的应用请由负责人自行提供已合法取得的包体（--from-file）。详见 artifact-acquisition.md。
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SUFFIX = (".apk", ".xapk", ".apks", ".aab", ".exe", ".zip")
MIN_SIZE = 1_000_000
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
PLAY_ID = re.compile(r"[?&]id=([\w.]+)")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(path: Path):
    """返回 (是否合法, 原因)。APK 系 zip 头 PK；EXE 为 MZ。"""
    if not path.exists():
        return False, "文件不存在"
    if path.stat().st_size < MIN_SIZE:
        return False, f"小于 {MIN_SIZE} 字节，疑似错误页/空文件"
    with open(path, "rb") as f:
        head = f.read(2)
    if head not in (b"PK", b"MZ"):
        return False, f"文件头异常 {head!r}，不是 APK/ZIP/PE"
    return True, "ok"


def record(out: Path, **kw) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    data = dict(kw)
    (out / "artifact-source.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return data


def finish(out: Path, path: Path, kind, source, package="", note=""):
    ok, why = validate(path)
    if not ok:
        path.unlink(missing_ok=True)
        return record(out, status="failed", kind=kind, source=source, package=package,
                      reason=why, next_steps="见 artifact-acquisition.md 的失败降级；可换源或由负责人提供本地包")
    return record(out, status="ok", kind=kind, source=source, package=package,
                  file=str(path.resolve()), filename=path.name,
                  size_bytes=path.stat().st_size, sha256=sha256(path), note=note)


def proxy_of(arg):
    return arg or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") or ""


def find_chrome(explicit):
    if explicit:
        return explicit
    hits = sorted(glob.glob(str(Path.home() / ".agent-browser" / "browsers" / "chrome-*" / "chrome.exe")))
    if hits:
        return hits[-1]
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              "/usr/bin/google-chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if Path(p).exists():
            return p
    return ""  # 交给 Playwright 用自带 chromium


def browser(explicit_chrome, proxy):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("缺少 playwright：先执行 pip install playwright（或 python -m playwright install chromium）")
    pw = sync_playwright().start()
    launch = {"headless": True, "args": ["--no-sandbox", "--disable-blink-features=AutomationControlled"]}
    chrome = find_chrome(explicit_chrome)
    if chrome:
        launch["executable_path"] = chrome
    if proxy:
        launch["proxy"] = {"server": proxy}
    b = pw.chromium.launch(**launch)
    ctx = b.new_context(user_agent=UA, accept_downloads=True, locale="zh-CN")
    ctx.set_default_timeout(30000)
    return pw, b, ctx


def direct_download(url, out: Path, proxy, suggested=""):
    """直链下载（.apk/.xapk 或 CDN 链接），返回保存路径。"""
    opener = urllib.request.build_opener()
    if proxy:
        opener.add_handler(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    name = suggested or Path(urllib.parse.urlparse(url).path).name or "artifact.apk"
    if not name.lower().endswith(SUFFIX):
        name += ".apk"
    path = out / name
    with opener.open(req, timeout=120) as r, open(path, "wb") as f:
        while True:
            buf = r.read(1 << 20)
            if not buf:
                break
            f.write(buf)
    return path


def search_play(name, ctx):
    """按游戏名搜 Play，返回候选包名（不自动选定，避免同名误选）。"""
    url = "https://play.google.com/store/search?q=" + urllib.parse.quote(name) + "&c=apps"
    page = ctx.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3000)
    hrefs = page.eval_on_selector_all(
        "a[href*='details?id=']", "els => els.map(e => e.href)")
    pkgs = []
    for h in hrefs:
        m = PLAY_ID.search(h)
        if m and m.group(1) not in pkgs:
            pkgs.append(m.group(1))
    return url, pkgs[:8]


def market_urls(pkg):
    return {
        "apkcombo_downloader": "https://apkcombo.com/downloader/",
        "apkcombo_variant": f"https://apkcombo.com/{pkg}/{pkg}/download/apk",
        "apkpure": f"https://apkpure.com/search?q={urllib.parse.quote(pkg)}",
    }


def click_download(page, url, selectors, out: Path, pkg):
    """打开下载页，按已知选择器触发下载；返回路径或 None。"""
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)
    title = page.title()
    if "Attention Required" in title or "Just a moment" in title:
        raise RuntimeError("页面被 Cloudflare / 反爬拦截 —— 不绕过，改用其他源或人工提供包体")
    for sel in selectors:
        el = page.query_selector(sel)
        if not el:
            continue
        try:
            with page.expect_download(timeout=180000) as di:
                el.click(force=True)
            d = di.value
            path = out / (d.suggested_filename or (pkg + ".apk"))
            d.save_as(str(path))
            return path
        except Exception as e:
            print(f"[warn] 选择器 {sel} 触发下载失败：{type(e).__name__}", file=sys.stderr)
    # 兜底：页面上所有直链
    hrefs = page.eval_on_selector_all(
        "a[href]", "els => els.map(e => e.href).filter(h => /\\.xapk|\\.apks|\\.apk(\\?|$)|download\\.apkcombo|\\/d\\?u=/i.test(h))")
    if hrefs:
        return direct_download(hrefs[0], out, "", pkg + ".apk")
    return None


def download_by_package(pkg, ctx, out: Path, proxy):
    """包名 → APKCombo downloader → 变体页 → APKPure（站点结构变化时需按指引改选择器）。"""
    page = ctx.new_page()
    errors = []
    # 1) APKCombo downloader：输入框填包名，等生成链接
    try:
        page.goto(market_urls(pkg)["apkcombo_downloader"], wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        inp = page.query_selector("input[placeholder*='Package'], input[placeholder*='Play Store']")
        if inp:
            inp.fill(pkg)
            btn = page.query_selector("button.button-search, form button[type='submit'], button.is-link")
            if btn:
                btn.click()
            for _ in range(12):
                page.wait_for_timeout(5000)
                links = page.eval_on_selector_all(
                    "a[href]", "els => els.map(e => e.href).filter(h => /download\\.apkcombo|\\/d\\?u=|\\.xapk|\\.apk(\\?|$)/i.test(h))")
                if links:
                    return direct_download(links[0], out, proxy, pkg + ".apk")
        errors.append("apkcombo downloader 未产出链接")
    except Exception as e:
        errors.append(f"apkcombo downloader: {type(e).__name__} {str(e)[:100]}")
    # 2) APKCombo 变体页
    try:
        p = click_download(page, market_urls(pkg)["apkcombo_variant"],
                           ["ul.file-list li a.variant", "a.variant", "a.download-start-btn"], out, pkg)
        if p:
            return p
        errors.append("apkcombo 变体页无下载链接")
    except Exception as e:
        errors.append(f"apkcombo 变体页: {type(e).__name__} {str(e)[:100]}")
    # 3) APKPure 搜索页
    try:
        p = click_download(page, market_urls(pkg)["apkpure"], ["a.download-start-btn"], out, pkg)
        if p:
            return p
        errors.append("apkpure 无下载按钮 / 会员墙")
    except Exception as e:
        errors.append(f"apkpure: {type(e).__name__} {str(e)[:100]}")
    raise RuntimeError("所有公开源均失败：" + " | ".join(errors))


def main():
    ap = argparse.ArgumentParser(description="A0 原包获取（rebuild-workflow）")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--from-file", help="本地已有 APK/XAPK/EXE 路径")
    g.add_argument("--name", help="游戏名（搜索候选包名）")
    g.add_argument("--play-url", help="Google Play 详情页链接")
    g.add_argument("--market-url", help="三方市场下载页或直链")
    ap.add_argument("--out", required=True, help="输出目录（项目X/input/ 或项目X/）")
    ap.add_argument("--package", help="已知包名，配合 --name 跳过搜索歧义")
    ap.add_argument("--pick", type=int, help="配合 --name，指定候选序号（1 起）后直接下载")
    ap.add_argument("--chrome", help="Chrome 可执行文件路径（缺省自动探测）")
    ap.add_argument("--proxy", help="代理，如 http://127.0.0.1:7897（缺省读 HTTPS_PROXY）")
    a = ap.parse_args()

    out = Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    proxy = proxy_of(a.proxy)

    # 情况 1：已提供本地包 → 不下载，校验 + 归档 + 登记，直接进 S0
    if a.from_file:
        src = Path(a.from_file).expanduser().resolve()
        if not src.is_file():
            record(out, status="failed", kind="from-file", source=str(src), reason="本地文件不存在")
            return 2
        dst = out / src.name
        if src != dst:
            shutil.copy2(src, dst)
        r = finish(out, dst, "from-file", str(src), note="用户提供本地包，跳过下载，直接进入 S0")
        return 0 if r["status"] == "ok" else 2

    # 情况 2：游戏名 → 先搜候选，交人工确认（同名产品很多，禁止 Agent 自选）
    if a.name:
        pkg = a.package
        if not pkg or a.pick:
            pw, b, ctx = browser(a.chrome, proxy)
            try:
                search_url, candidates = search_play(a.name, ctx)
                if not candidates:
                    record(out, status="need-input", kind="name", source=search_url,
                           reason="搜索未返回候选包名（可能网络/区域限制）",
                           next_steps="改给 --play-url、--market-url 或 --package <包名>；也可由负责人提供 --from-file")
                    return 3
                if not a.pick:
                    record(out, status="need-confirm", kind="name", source=search_url,
                           candidates=[{"pick": i + 1, "package": p,
                                        "play_url": f"https://play.google.com/store/apps/details?id={p}"}
                                       for i, p in enumerate(candidates)],
                           next_steps="人工确认是哪款产品，再用 --name <名字> --pick N 重跑（或改给 --play-url）")
                    return 3
                if a.pick < 1 or a.pick > len(candidates):
                    record(out, status="failed", kind="name", reason=f"--pick 超出候选范围 1..{len(candidates)}")
                    return 2
                pkg = candidates[a.pick - 1]
            except Exception as e:
                record(out, status="failed", kind="name", reason=f"{type(e).__name__}: {str(e)[:200]}")
                return 2
            finally:
                b.close()
                pw.stop()
        pw, b, ctx = browser(a.chrome, proxy)
        try:
            path = download_by_package(pkg, ctx, out, proxy)
            r = finish(out, path, "name", f"play-search:{a.name}", package=pkg,
                       note="由游戏名检索并人工确认包名后下载")
        except Exception as e:
            r = record(out, status="failed", kind="name", package=pkg,
                       reason=f"{type(e).__name__}: {str(e)[:300]}",
                       next_steps="见 artifact-acquisition.md 降级顺序；或由负责人提供 --from-file")
        finally:
            b.close()
            pw.stop()
        return 0 if r["status"] == "ok" else 2

    # 情况 3：Google Play 链接 → 提取包名，Play 不提供 APK 直链，走公开镜像
    if a.play_url:
        m = PLAY_ID.search(a.play_url)
        if not m:
            record(out, status="failed", kind="play-url", source=a.play_url,
                   reason="链接里没有 ?id=<包名>",
                   next_steps="确认是 https://play.google.com/store/apps/details?id=... 形式")
            return 2
        pkg = m.group(1)
        pw, b, ctx = browser(a.chrome, proxy)
        try:
            path = download_by_package(pkg, ctx, out, proxy)
            r = finish(out, path, "play-url", a.play_url, package=pkg,
                       note="Play 链接仅用于取包名，包体来自公开镜像；需在 scope.md 记录商店页")
        except Exception as e:
            r = record(out, status="failed", kind="play-url", package=pkg, source=a.play_url,
                       reason=f"{type(e).__name__}: {str(e)[:300]}",
                       next_steps="换 --market-url / --from-file；付费或区域受限应用须由负责人提供包体")
        finally:
            b.close()
            pw.stop()
        return 0 if r["status"] == "ok" else 2

    # 情况 4：三方市场链接 / 直链
    url = a.market_url
    parsed = urllib.parse.urlparse(url)
    looks_direct = (parsed.path.lower().endswith((".apk", ".xapk", ".apks"))
                    or "download.apkcombo" in parsed.netloc or "/d?u=" in url)
    try:
        if looks_direct:
            path = direct_download(url, out, proxy, Path(parsed.path).name or "artifact.apk")
        else:
            pw, b, ctx = browser(a.chrome, proxy)
            try:
                page = ctx.new_page()
                path = click_download(page, url,
                                      ["a.download-start-btn", "ul.file-list li a.variant", "a.variant", "a[download]"],
                                      out, "artifact")
                if not path:
                    raise RuntimeError("页面未找到下载按钮或直链（站点结构可能已变，见 artifact-acquisition.md）")
            finally:
                b.close()
                pw.stop()
        r = finish(out, path, "market-url", url, note="三方市场来源，须核对包名/版本与来源可信度")
    except Exception as e:
        r = record(out, status="failed", kind="market-url", source=url,
                   reason=f"{type(e).__name__}: {str(e)[:300]}",
                   next_steps="换源或由负责人提供 --from-file；不绕过会员墙/验证码")
    return 0 if r["status"] == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
