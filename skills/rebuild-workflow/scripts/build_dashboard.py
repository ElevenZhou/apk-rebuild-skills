#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目看板生成器 — apk-rebuild-skills / rebuild-workflow

扫描 <root>/项目*/project.json，生成离线单页 HTML 看板。
零第三方依赖；数据内嵌 HTML，双击即可打开，不需要起服务或联网。

用法：
  python build_dashboard.py --root "<项目父目录>" --out "<输出 index.html>"
  python build_dashboard.py --root "<项目父目录>" --check      # 只做规范/schema 检查
规则见 references/project-layout.md。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

SCHEMA_VERSION = "1.0"
STAGES = ["A0", "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"]
STATUS = {"active", "blocked", "waiting-human", "not-started", "parked", "done"}
TRACKS = {"rebuild", "prototype", "research"}
SEVERITY = {"blocking", "waiting", "risk", "info"}
OWNERSHIP = {"自有已确认", "权属待确认", "第三方", "来源未知"}
PUBLISH_GATE = {"not-applicable", "pending-human", "confirmed"}
REQUIRED = [
    "schema_version", "id", "name", "product", "package", "engine", "track",
    "status", "stage", "completed", "progress", "owner", "operator",
    "updated_at", "ownership", "publish_gate", "summary", "next_action", "blockers",
]
# 标准目录项（仅用于 --check 与详情展示；存量项目渐进迁移，不强制）
CORE_DIRS = ["docs", "recon", "extracted", "evidence", "assets", "rebuild", "runs", "report"]
CORE_FILES = ["project.json", "README.md", "scope.md"]
STALE_DAYS = 7


def scan(root: Path):
    projects, issues, unregistered = [], [], []
    today = dt.date.today()
    dirs = sorted([d for d in root.iterdir() if d.is_dir() and d.name.startswith("项目")],
                  key=lambda d: d.name)
    for d in dirs:
        f = d / "project.json"
        if not f.is_file():
            unregistered.append(d.name)
            issues.append((d.name, "未建档", "缺少 project.json，看板无法读取该项目状态"))
            continue
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            issues.append((d.name, "解析失败", f"project.json 不是合法 JSON：{e}"))
            continue

        for k in REQUIRED:
            if k not in p:
                issues.append((d.name, "字段缺失", f"缺少必填字段 {k}"))
        if p.get("status") not in STATUS:
            issues.append((d.name, "枚举非法", f"status={p.get('status')!r} 不在 {sorted(STATUS)}"))
        if p.get("track") not in TRACKS:
            issues.append((d.name, "枚举非法", f"track={p.get('track')!r} 不在 {sorted(TRACKS)}"))
        if p.get("ownership") not in OWNERSHIP:
            issues.append((d.name, "枚举非法", f"ownership={p.get('ownership')!r}"))
        if p.get("publish_gate") not in PUBLISH_GATE:
            issues.append((d.name, "枚举非法", f"publish_gate={p.get('publish_gate')!r}"))
        if not isinstance(p.get("progress"), int) or not 0 <= p.get("progress", -1) <= 100:
            issues.append((d.name, "取值非法", "progress 必须是 0–100 的整数"))
        if not isinstance(p.get("completed"), list):
            issues.append((d.name, "取值非法", "completed 必须是数组"))
        else:
            bad = [s for s in p["completed"] if s not in STAGES]
            if bad:
                issues.append((d.name, "阶段非法", f"completed 含未知阶段 {bad}"))
        if p.get("schema_version") != SCHEMA_VERSION:
            issues.append((d.name, "版本提示", f"schema_version={p.get('schema_version')!r}，当前规范 {SCHEMA_VERSION}"))

        blockers = p.get("blockers") or []
        if not isinstance(blockers, list):
            issues.append((d.name, "取值非法", "blockers 必须是数组"))
            blockers = []
        for b in blockers:
            if b.get("severity") not in SEVERITY:
                issues.append((d.name, "卡点枚举", f"{b.get('id')}: severity={b.get('severity')!r}"))
            for k in ("title", "waiting_for", "action"):
                if not b.get(k):
                    issues.append((d.name, "卡点缺项", f"{b.get('id', '?')} 缺 {k}（卡在哪/等谁/做什么必须写全）"))

        stale = None
        try:
            stale = (today - dt.date.fromisoformat(p["updated_at"])).days
        except Exception:
            issues.append((d.name, "日期非法", f"updated_at={p.get('updated_at')!r}，应为 YYYY-MM-DD"))
        if stale is not None and stale > STALE_DAYS:
            issues.append((d.name, "数据可能过时", f"距上次回写 {stale} 天（阈值 {STALE_DAYS} 天）"))

        missing = [x for x in CORE_FILES if not (d / x).exists()]
        missing += [x + "/" for x in CORE_DIRS if not (d / x).is_dir()]

        p["_dir"] = d.name
        p["_path"] = d.as_posix()
        p["_stale"] = stale
        p["_missing"] = missing
        p["_blocking"] = sum(1 for b in blockers if b.get("severity") == "blocking")
        p["_waiting"] = sum(1 for b in blockers if b.get("severity") == "waiting")
        p["_risks"] = sum(1 for b in blockers if b.get("severity") == "risk")
        projects.append(p)
    return projects, issues, unregistered, dirs


def report(projects, issues, unregistered, dirs, root: Path):
    print(f"扫描目录：{root}")
    print(f"项目目录 {len(dirs)} 个 / 已建档 {len(projects)} 个 / 未建档 {len(unregistered)} 个")
    if unregistered:
        print("  未建档：" + "、".join(unregistered))
    print("-" * 66)
    for p in projects:
        b = f"卡点 {p['_blocking']} 阻塞 / {p['_waiting']} 待人工 / {p['_risks']} 风险"
        miss = f"；目录缺 {len(p['_missing'])} 项" if p["_missing"] else "；目录完整"
        stale = f"；已 {p['_stale']} 天未回写 ⚠" if p["_stale"] and p["_stale"] > STALE_DAYS else ""
        print(f"  {p['name']:<22} {p['status']:<14} {p['stage']:<12} {p['progress']:>3}%  {b}{miss}{stale}")
    print("-" * 66)
    if issues:
        print(f"提示 {len(issues)} 条：")
        for name, kind, msg in issues:
            print(f"  [{kind}] {name}: {msg}")
    else:
        print("schema 与目录检查全部通过。")
    print("\n说明：目录缺项仅作提示，存量项目按 project-layout.md §5 渐进迁移，不强制搬动文件。")


HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>项目看板 · 逆向重建工作台</title>
<style>
:root{
  --bg:#f4f6f9; --card:#fff; --ink:#19212f; --sub:#4c5666; --muted:#828c9c;
  --line:#e2e7ef; --brand:#3059e3; --brand-soft:#eef2ff;
  --red:#d93f46; --red-soft:#fff2f2; --amber:#c9800b; --amber-soft:#fff8e9;
  --green:#158a63; --green-soft:#eaf8f1; --slate:#7c8697; --slate-soft:#f0f2f6;
  --shadow:0 1px 2px rgba(20,32,56,.04),0 6px 20px rgba(20,32,56,.06);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei","PingFang SC",sans-serif;
  font-size:14px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1440px;margin:0 auto;padding:28px 28px 80px}
header.top{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:20px}
h1{font-size:26px;margin:0 0 4px;letter-spacing:-.4px}
.sub{color:var(--muted);font-size:13px}
.stamp{font-size:12px;color:var(--muted);text-align:right;line-height:1.8}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;min-width:104px;box-shadow:var(--shadow)}
.stat b{display:block;font-size:22px;line-height:1.2;font-variant-numeric:tabular-nums}
.stat span{font-size:12px;color:var(--muted)}
.stat.alert b{color:var(--red)} .stat.warn b{color:var(--amber)} .stat.good b{color:var(--green)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);margin-bottom:20px;overflow:hidden}
.panel-h{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid var(--line);background:#fbfcfe}
.panel-h h2{font-size:15px;margin:0;font-weight:650}
.pill{font-size:11px;padding:2px 9px;border-radius:20px;background:var(--slate-soft);color:var(--sub);font-weight:600}
.attention-list{padding:6px 0}
.att{display:grid;grid-template-columns:96px 1fr auto;gap:14px;align-items:center;padding:11px 18px;border-bottom:1px solid #f0f2f6}
.att:last-child{border-bottom:0}
.att.sev-blocking{background:var(--red-soft)} .att.sev-waiting{background:var(--amber-soft)}
.att .who{font-size:12px;font-weight:700;color:var(--sub);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.att .what{font-size:13.5px;font-weight:600;margin-bottom:2px}
.att .meta{font-size:12px;color:var(--muted)}
.att .meta em{font-style:normal;color:var(--sub)}
.att .acts{display:flex;gap:6px}
button{font:inherit;cursor:pointer;border:1px solid var(--line);background:#fff;color:var(--sub);
  border-radius:7px;padding:5px 11px;font-size:12px;white-space:nowrap;transition:.15s}
button:hover{border-color:var(--brand);color:var(--brand);background:var(--brand-soft)}
button.primary{background:var(--brand);border-color:var(--brand);color:#fff}
button.primary:hover{background:#2447c4;color:#fff}
button.ghost{border-color:transparent;background:transparent}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
.toolbar input[type=search]{flex:1;min-width:220px;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:#fff;font:inherit;outline:none}
.toolbar input[type=search]:focus{border-color:var(--brand);box-shadow:0 0 0 3px var(--brand-soft)}
.toolbar select{padding:9px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;font:inherit;color:var(--sub)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(348px,1fr));gap:16px;align-items:start}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);
  padding:16px 17px 14px;display:flex;flex-direction:column;gap:10px;transition:.15s;position:relative;overflow:hidden}
.card:hover{box-shadow:0 4px 24px rgba(20,32,56,.11);transform:translateY(-1px)}
.card::before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--slate)}
.card.s-blocked::before{background:var(--red)} .card.s-waiting-human::before{background:var(--amber)}
.card.s-active::before{background:var(--brand)} .card.s-done::before{background:var(--green)}
.card-h{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.card-h .nm{font-size:17px;font-weight:700;letter-spacing:-.2px}
.card-h .pd{font-size:12px;color:var(--muted);margin-top:2px}
.badges{display:flex;gap:5px;flex-wrap:wrap;justify-content:flex-end}
.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:5px;white-space:nowrap}
.b-blocked{background:var(--red-soft);color:var(--red)} .b-waiting-human{background:var(--amber-soft);color:var(--amber)}
.b-active{background:var(--brand-soft);color:var(--brand)} .b-done{background:var(--green-soft);color:var(--green)}
.b-not-started,.b-parked{background:var(--slate-soft);color:var(--slate)}
.b-track{background:#f3f0ff;color:#6d51c9}
.engine{font-size:12px;color:var(--sub);background:#f7f9fc;border:1px solid var(--line);border-radius:6px;padding:5px 9px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stages{display:flex;gap:3px;align-items:center}
.st{flex:1;height:7px;border-radius:2px;background:#e8ecf3;position:relative}
.st.done{background:var(--brand)} .st.cur{background:repeating-linear-gradient(45deg,var(--brand),var(--brand) 3px,#a9baf7 3px,#a9baf7 6px)}
.st.future{background:#e8ecf3}
.stages-lbl{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-top:5px}
.stages-lbl b{color:var(--brand);font-variant-numeric:tabular-nums}
.summary{font-size:13px;color:var(--sub);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.next{font-size:12.5px;background:#f7f9fc;border-left:3px solid var(--brand);padding:7px 10px;border-radius:0 6px 6px 0;color:var(--sub)}
.next b{color:var(--ink)}
.blk-line{display:flex;gap:7px;align-items:flex-start;font-size:12px;padding:6px 9px;border-radius:6px}
.blk-line.blocking{background:var(--red-soft);color:var(--red)} .blk-line.waiting{background:var(--amber-soft);color:#9a6408}
.blk-line .ic{font-weight:800}
.card-f{display:flex;justify-content:space-between;align-items:center;gap:8px;border-top:1px solid var(--line);padding-top:10px;margin-top:2px;flex-wrap:wrap}
.card-f .when{font-size:11.5px;color:var(--muted)}
.card-f .when.stale{color:var(--amber);font-weight:600}
.card-f .acts{display:flex;gap:6px;flex-wrap:wrap}
.note{font-size:12px;color:var(--muted);background:#fbfcfe;border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin-bottom:16px}
.note b{color:var(--sub)}
.empty{text-align:center;padding:50px 20px;color:var(--muted)}
/* 抽屉 */
.mask{position:fixed;inset:0;background:rgba(18,26,42,.38);opacity:0;pointer-events:none;transition:.2s;z-index:19}
.mask.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;right:0;top:0;bottom:0;width:min(560px,94vw);background:#fff;z-index:20;
  transform:translateX(102%);transition:.22s ease;box-shadow:-12px 0 40px rgba(18,26,42,.16);overflow-y:auto}
.drawer.on{transform:none}
.dr-h{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:18px 22px;display:flex;justify-content:space-between;align-items:flex-start;z-index:2}
.dr-h h2{margin:0 0 3px;font-size:20px} .dr-h .pd{font-size:12px;color:var(--muted)}
.dr-b{padding:18px 22px 40px}
.sec{margin-bottom:22px}
.sec h3{font-size:12px;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);margin:0 0 9px;font-weight:700}
.kv{display:grid;grid-template-columns:96px 1fr;gap:6px 10px;font-size:13px}
.kv dt{color:var(--muted)} .kv dd{margin:0;color:var(--sub)}
.d-blk{border:1px solid var(--line);border-radius:8px;padding:11px 13px;margin-bottom:8px;font-size:13px}
.d-blk.blocking{border-left:3px solid var(--red);background:var(--red-soft)}
.d-blk.waiting{border-left:3px solid var(--amber);background:var(--amber-soft)}
.d-blk.risk{border-left:3px solid var(--slate)} .d-blk.info{border-left:3px solid var(--line);background:#fafbfd}
.d-blk .t{font-weight:650;margin-bottom:5px}
.d-blk .m{font-size:12px;color:var(--sub);line-height:1.7}
.d-blk .m b{color:var(--ink)}
.files{display:flex;flex-direction:column;gap:5px;font-size:12.5px}
pre.prompt{background:#f7f9fc;border:1px solid var(--line);border-radius:8px;padding:13px;font-size:12px;
  white-space:pre-wrap;word-break:break-word;line-height:1.7;color:var(--sub);font-family:ui-monospace,Consolas,"Microsoft YaHei",monospace}
.toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,20px);background:#19212f;color:#fff;
  padding:10px 18px;border-radius:8px;font-size:13px;opacity:0;pointer-events:none;transition:.2s;z-index:30}
.toast.on{opacity:1;transform:translate(-50%,0)}
@media(max-width:760px){.wrap{padding:18px 14px 60px}.grid{grid-template-columns:1fr}
  .att{grid-template-columns:1fr;gap:6px}.att .acts{justify-content:flex-start}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <h1>项目看板 <span style="font-weight:400;color:var(--muted);font-size:18px">· 逆向重建工作台</span></h1>
      <div class="sub">A0 + S0–S7 主线 · 卡点优先 · 点击「处理提示词」即可把项目交给 AI 工具接手</div>
    </div>
    <div class="stamp">生成时间：__GENERATED_AT__<br>数据源：各项目 <code>project.json</code>（离线内嵌，无需服务）</div>
  </header>

  <div class="stats" id="stats"></div>
  <div id="unregistered"></div>

  <section class="panel">
    <div class="panel-h"><h2>⚑ 需要你处理</h2><span class="pill" id="attCount">0 项</span>
      <span style="margin-left:auto;font-size:12px;color:var(--muted)">按阻塞 → 待人工排序，只列需要人或外部资源的项目</span></div>
    <div class="attention-list" id="attention"></div>
  </section>

  <div class="toolbar">
    <input type="search" id="q" placeholder="搜索项目 / 产品 / 包名 / 引擎 / 卡点…">
    <select id="fstatus"><option value="">全部状态</option><option value="needs">⚑ 需处理</option>
      <option value="blocked">卡住</option><option value="waiting-human">待人工</option>
      <option value="active">进行中</option><option value="not-started">未启动</option>
      <option value="parked">挂起</option><option value="done">已交付</option></select>
    <select id="sort"><option value="priority">按待处理优先</option><option value="stale">按最久未更新</option>
      <option value="progress">按进度</option><option value="name">按项目名</option></select>
    <span style="font-size:12px;color:var(--muted)" id="shown"></span>
  </div>

  <div class="note"><b>状态怎么保持新鲜：</b>AI 每次推进项目（阶段切换、卡点变化、会话结束）必须回写该项目 <code>project.json</code> 的
    <code>stage / completed / progress / blockers / next_action / updated_at</code>，再重新生成看板；超过 7 天未回写会标「数据可能过时」。
    看板只反映状态，不判定出口标准、不替代 G-PUBLISH 人工发布门禁。</div>

  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">没有符合条件的项目</div>
</div>

<div class="mask" id="mask" onclick="closeDrawer()"></div>
<aside class="drawer" id="drawer" aria-label="项目详情">
  <div class="dr-h"><div><h2 id="drName"></h2><div class="pd" id="drProduct"></div></div>
    <button class="ghost" onclick="closeDrawer()" style="font-size:20px;line-height:1">×</button></div>
  <div class="dr-b" id="drBody"></div>
</aside>
<div class="toast" id="toast"></div>

<script id="dashboard-data" type="application/json">__DASHBOARD_DATA__</script>
<script>
const DB = JSON.parse(document.getElementById('dashboard-data').textContent);
const P = DB.projects, ISSUES = DB.issues;
const ST = ['A0','S0','S1','S2','S3','S4','S5','S6','S7'];
const LBL = {active:'进行中',blocked:'卡住','waiting-human':'待人工','not-started':'未启动',parked:'挂起',done:'已交付'};
const SEV = {blocking:'阻塞',waiting:'待人工',risk:'风险',info:'记录'};
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $ = id => document.getElementById(id);

function toast(msg){ const t=$('toast'); t.textContent=msg; t.classList.add('on'); clearTimeout(t._t); t._t=setTimeout(()=>t.classList.remove('on'),1900); }
function copy(text,label){
  const done=()=>toast('已复制：'+(label||'内容'));
  if(navigator.clipboard && window.isSecureContext){ navigator.clipboard.writeText(text).then(done).catch(()=>fallback()); }
  else fallback();
  function fallback(){ const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
    document.body.appendChild(ta); ta.select(); try{document.execCommand('copy'); done();}catch(e){toast('复制失败，请在详情里手动选中');} document.body.removeChild(ta); }
}
function fileUrl(p){ return encodeURI('file:///' + String(p).replace(/\\/g,'/')); }
function promptFor(p){
  const bs=(p.blockers||[]).filter(b=>b.severity==='blocking'||b.severity==='waiting');
  const bt=bs.length? bs.map((b,i)=>`  ${i+1}. [${SEV[b.severity]}] ${b.title}\n     等谁：${b.waiting_for}\n     要做什么：${b.action}`).join('\n') : '  （当前无阻塞卡点）';
  const kf=(p.key_files||[]).slice(0,4).map(f=>f.path).join('、');
  return `用 rebuild-workflow 推进${p.name}（${p.product}）。
项目目录：${p._path}
当前阶段：${p.stage}${p.milestone?' / '+p.milestone:''}，进度 ${p.progress}%，状态 ${LBL[p.status]||p.status}。
引擎：${p.engine}；负责人：${p.owner}；执行：${p.operator}；权属：${p.ownership}。
现状：${p.summary}

当前卡点：
${bt}

本会话任务：${p.next_action}

开工前先读：${p._path}/project.json、README.md、scope.md（若有）${kf?'、'+kf:''}。
要求：
1. 加载 rebuild-workflow，按当前阶段分派对应 skill，执行出口标准与决策门；需要人工决策就停下来问，不要自行拍板。
2. 只做 scope.md 已勾选的分析范围；不确定项登记进待优化清单并标置信度。
3. 会话结束前按 project-layout.md 回写 project.json（stage / completed / progress / blockers / next_action / updated_at），重新生成看板，并说明本次改了什么。`;
}
function stagesBar(p){
  if(p.track!=='rebuild') return `<div class="stages">${ST.map(s=>'<div class="st future"></div>').join('')}</div>
    <div class="stages-lbl"><span>非 S0–S7 主线（${esc(p.track)}）</span><span><b>${p.progress}%</b></span></div>`;
  return `<div class="stages">${ST.map(s=>{
    const cls = (p.completed||[]).includes(s)?'done':(p.stage===s?'cur':'future');
    return `<div class="st ${cls}" title="${s}${(p.completed||[]).includes(s)?' 已完成':(p.stage===s?' 当前':'')}"></div>`;
  }).join('')}</div>
  <div class="stages-lbl"><span>A0 → S7　·　当前 <b>${esc(p.stage)}</b>${p.milestone?' / '+esc(p.milestone):''}</span><span><b>${p.progress}%</b></span></div>`;
}

function renderStats(){
  const c = {blocked:0,'waiting-human':0,active:0,'not-started':0,parked:0,done:0};
  P.forEach(p=>{ if(c[p.status]!==undefined) c[p.status]++; });
  const blocking = P.reduce((n,p)=>n+p._blocking,0), waiting = P.reduce((n,p)=>n+p._waiting,0);
  const stale = P.filter(p=>p._stale!=null && p._stale>7).length;
  const items=[['项目总数',P.length,''],['阻塞卡点',blocking,'alert'],['待人工卡点',waiting,'warn'],
    ['进行中项目',c.active,''],['待人工/挂起项目',c['waiting-human']+c.parked,''],['未启动项目',c['not-started'],''],['已交付项目',c.done,'good'],['数据可能过时',stale,stale?'warn':'']];
  $('stats').innerHTML = items.map(([l,v,k])=>`<div class="stat ${k}"><b>${v}</b><span>${l}</span></div>`).join('');
}

function renderAttention(){
  const rows=[];
  P.forEach(p=>(p.blockers||[]).forEach(b=>{
    if(b.severity==='blocking'||b.severity==='waiting') rows.push({p,b,w:b.severity==='blocking'?0:1});
  }));
  rows.sort((a,b)=>a.w-b.w || (a.b.since||'').localeCompare(b.b.since||''));
  $('attCount').textContent = rows.length+' 项';
  $('attention').innerHTML = rows.length? rows.map(({p,b})=>`
    <div class="att sev-${esc(b.severity)}">
      <div class="who" title="${esc(p.name)}">${esc(p.name)}</div>
      <div><div class="what">${b.severity==='blocking'?'⛔':'⏳'} ${esc(b.title)}</div>
        <div class="meta">等谁：<em>${esc(b.waiting_for)}</em>　·　要做：<em>${esc(b.action)}</em>　·　${esc(b.since||'')} 起　·　${esc(b.id||'')}</div></div>
      <div class="acts"><button class="primary" onclick="copyPrompt('${esc(p.id)}')">处理提示词</button>
        <button onclick="openDir('${esc(p.id)}')">打开目录</button></div>
    </div>`).join('') : '<div class="empty" style="padding:24px">当前没有阻塞或待人工卡点 ✓</div>';
}
const byId = id => P.find(p=>p.id===id);
function copyPrompt(id){ const p=byId(id); if(p) copy(promptFor(p), p.name+' 处理提示词'); }
function copyPath(id){ const p=byId(id); if(p) copy(p._path, '项目路径'); }
function openDir(id){ const p=byId(id); if(p) window.open(fileUrl(p._path),'_blank'); }
function openFile(id,rel){ const p=byId(id); if(p) window.open(fileUrl(p._path+'/'+rel),'_blank'); }

function card(p){
  const bs=(p.blockers||[]).filter(b=>b.severity==='blocking'||b.severity==='waiting');
  const stale=p._stale!=null&&p._stale>7;
  return `<article class="card s-${esc(p.status)}" onclick="openDrawer('${esc(p.id)}')">
    <div class="card-h"><div><div class="nm">${esc(p.name)}</div><div class="pd">${esc(p.product)} · ${esc(p.package)}</div></div>
      <div class="badges"><span class="badge b-${esc(p.status)}">${esc(LBL[p.status]||p.status)}</span>
      ${p.track!=='rebuild'?`<span class="badge b-track">${esc(p.track)}</span>`:''}</div></div>
    <div class="engine">${esc(p.engine)}　·　${esc(p.stage)}${p.milestone?' / '+esc(p.milestone):''}</div>
    ${stagesBar(p)}
    <div class="summary">${esc(p.summary)}</div>
    <div class="next"><b>下一步 →</b> ${esc(p.next_action)}</div>
    ${bs.slice(0,2).map(b=>`<div class="blk-line ${esc(b.severity)}"><span class="ic">${b.severity==='blocking'?'⛔':'⏳'}</span><span>${esc(b.title)}</span></div>`).join('')}
    ${bs.length>2?`<div style="font-size:11.5px;color:var(--muted)">还有 ${bs.length-2} 项卡点，点卡片查看</div>`:''}
    <div class="card-f"><div class="when ${stale?'stale':''}">${esc(p.updated_at)}${stale?` · ${p._stale} 天未回写 ⚠`:''}　·　${esc(p.owner)}</div>
      <div class="acts" onclick="event.stopPropagation()">
        <button class="primary" onclick="copyPrompt('${esc(p.id)}')">处理提示词</button>
        <button onclick="copyPath('${esc(p.id)}')">复制路径</button>
        <button onclick="openDrawer('${esc(p.id)}')">详情</button></div></div>
  </article>`;
}
function render(){
  const q=$('q').value.trim().toLowerCase(), f=$('fstatus').value, sort=$('sort').value;
  let list=P.filter(p=>{
    if(f==='needs' && !(p._blocking||p._waiting)) return false;
    if(f && f!=='needs' && p.status!==f) return false;
    if(!q) return true;
    const hay=[p.name,p.product,p.package,p.engine,p.summary,p.next_action,p.owner,
      ...(p.blockers||[]).map(b=>b.title+' '+b.waiting_for)].join(' ').toLowerCase();
    return hay.includes(q);
  });
  const w = s => (s==='blocked'?0:s==='waiting-human'?1:s==='active'?2:s==='not-started'?3:s==='parked'?4:5);
  list.sort((a,b)=>{
    if(sort==='stale') return (b._stale||0)-(a._stale||0);
    if(sort==='progress') return b.progress-a.progress;
    if(sort==='name') return a.name.localeCompare(b.name,'zh');
    return (b._blocking-a._blocking)||(b._waiting-a._waiting)||(w(a.status)-w(b.status))||((b._stale||0)-(a._stale||0));
  });
  $('grid').innerHTML=list.map(card).join('');
  $('empty').style.display=list.length?'none':'block';
  $('shown').textContent=`显示 ${list.length} / ${P.length} 个项目`;
}

function openDrawer(id){
  const p=byId(id); if(!p) return;
  $('drName').textContent=p.name; $('drProduct').textContent=`${p.product} · ${p.package} · ${p.engine}`;
  const bs=p.blockers||[];
  const files=(p.key_files||[]).map(f=>`<a href="javascript:void(0)" onclick="openFile('${esc(p.id)}','${esc(f.path)}')">📄 ${esc(f.label)} <span style="color:var(--muted)">${esc(f.path)}</span></a>`).join('');
  const links=Object.entries(p.links||{}).map(([k,v])=>`<div>${esc(k)}：<span style="color:var(--sub)">${esc(v)}</span></div>`).join('');
  $('drBody').innerHTML=`
    <div class="sec"><h3>状态</h3><dl class="kv">
      <dt>状态 / 阶段</dt><dd>${esc(LBL[p.status]||p.status)} · ${esc(p.stage)}${p.milestone?' / '+esc(p.milestone):''} · ${p.progress}%</dd>
      <dt>轨道</dt><dd>${esc(p.track)}</dd><dt>已完成阶段</dt><dd>${esc((p.completed||[]).join(' → ')||'—')}</dd>
      <dt>负责人 / 执行</dt><dd>${esc(p.owner)} / ${esc(p.operator)}</dd>
      <dt>权属 / 发布门禁</dt><dd>${esc(p.ownership)} / ${esc(p.publish_gate)}</dd>
      <dt>最后回写</dt><dd>${esc(p.updated_at)}${p._stale!=null?'（'+p._stale+' 天前）':''}${p._stale>7?' ⚠ 数据可能过时':''}</dd>
      <dt>目录</dt><dd><a href="javascript:void(0)" onclick="openDir('${esc(p.id)}')">${esc(p._path)}</a></dd>
    </dl></div>
    <div class="sec"><h3>现状 / 下一步</h3><div style="font-size:13px;color:var(--sub);margin-bottom:8px">${esc(p.summary)}</div>
      <div class="next"><b>下一步 →</b> ${esc(p.next_action)}</div></div>
    <div class="sec"><h3>卡点 ${bs.length?'（'+bs.length+'）':''}</h3>
      ${bs.length?bs.map(b=>`<div class="d-blk ${esc(b.severity)}"><div class="t">[${esc(SEV[b.severity]||b.severity)}] ${esc(b.title)} <span style="font-weight:400;color:var(--muted)">${esc(b.id||'')}</span></div>
        <div class="m"><b>等谁：</b>${esc(b.waiting_for)}<br><b>要做：</b>${esc(b.action)}<br><b>登记：</b>${esc(b.since||'—')}　<b>参见：</b>${esc(b.ref||'—')}</div></div>`).join('')
        :'<div style="font-size:13px;color:var(--muted)">当前无登记卡点 ✓</div>'}</div>
    <div class="sec"><h3>关键文件</h3><div class="files">${files||'<span style="color:var(--muted)">未登记</span>'}</div>
      ${links?`<div style="margin-top:10px;font-size:12.5px;color:var(--sub)">${links}</div>`:''}</div>
    ${p._missing&&p._missing.length?`<div class="sec"><h3>目录规范检查</h3><div style="font-size:12.5px;color:var(--muted)">缺 ${esc(p._missing.join('、'))}（存量项目渐进迁移，不强制补）</div></div>`:''}
    <div class="sec"><h3>处理提示词（复制到 AI 工具即可接手）</h3>
      <div style="display:flex;gap:8px;margin-bottom:9px"><button class="primary" onclick="copyPrompt('${esc(p.id)}')">复制处理提示词</button>
      <button onclick="copyPath('${esc(p.id)}')">复制项目路径</button><button onclick="openDir('${esc(p.id)}')">打开目录</button></div>
      <pre class="prompt">${esc(promptFor(p))}</pre></div>
    ${p.data_source?`<div class="sec"><h3>数据来源</h3><div style="font-size:12px;color:var(--muted)">${esc(p.data_source)}</div></div>`:''}
  `;
  $('drawer').classList.add('on'); $('mask').classList.add('on');
}
function closeDrawer(){ $('drawer').classList.remove('on'); $('mask').classList.remove('on'); }
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer();});
['q','fstatus','sort'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',render));
renderStats(); renderAttention();
$('unregistered').innerHTML = DB.unregistered.length? `<div class="note" style="border-color:#f3d4a8;background:var(--amber-soft)">
  <b>⚠ 未建档目录：</b>${DB.unregistered.map(esc).join('、')} —— 这些目录没有 <code>project.json</code>，看板读不到状态。按 <code>templates/project/project.json</code> 补一份即可。</div>` : '';
render();
</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser(description="生成项目看板（离线单页 HTML）")
    ap.add_argument("--root", default=".", help="项目父目录（其下为 项目* 子目录）")
    ap.add_argument("--out", default="dashboard/index.html", help="输出 HTML 路径")
    ap.add_argument("--check", action="store_true", help="只做 schema / 目录规范检查，不生成 HTML")
    ap.add_argument("--strict", action="store_true", help="--check 时如存在提示项则返回非零退出码")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: 目录不存在 {root}", file=sys.stderr)
        return 2
    projects, issues, unregistered, dirs = scan(root)
    report(projects, issues, unregistered, dirs, root)

    if args.check:
        return 1 if (args.strict and issues) else 0

    payload = {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "root": root.as_posix(),
        "projects": projects,
        "unregistered": unregistered,
        "issues": issues,
    }
    raw = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = HTML.replace("__DASHBOARD_DATA__", raw).replace(
        "__GENERATED_AT__", payload["generated_at"])
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    blocking = sum(p["_blocking"] for p in projects)
    waiting = sum(p["_waiting"] for p in projects)
    print(f"\n看板已生成：{out}")
    print(f"  项目 {len(projects)} 个 | 阻塞卡点 {blocking} 项 | 待人工 {waiting} 项 | 提示 {len(issues)} 条")
    print("  双击 HTML 即可离线打开；数据已内嵌，无需服务。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
