# A0 原包获取（流程第一步）

> v1.4.1 新增。**A0 不占 S 阶段编号**：八阶段 S0–S7、铁律、决策门、G-PUBLISH 全部不变。A0 的产出就是输入检查表 **#1 原包文件 + sha256**。
> 配套脚本：`skills/rebuild-workflow/scripts/fetch_artifact.py`。

## 一、决策树（先判断要不要下载）

```
用户给了什么？
├─ 本地已有 APK/XAPK/APKS/AAB/EXE 路径  → 不下载！校验 + 归档 + 登记来源 → 直接进 S0
├─ 游戏名（如 "Mochichat"）            → 搜候选包名 → 人工确认是哪款 → 下载
├─ Google Play 详情页链接              → 取 ?id= 包名 → 走公开镜像下载（Play 不给 APK 直链）
└─ 三方市场下载页 / 直链               → 直接下载（APKPure / APKCombo / APKMirror 等）
```

**口诀：有包就进，没包才下。** 已经提供 APK 时不得重新下载一个"看起来更新"的版本替换掉，那会改变基线、让 sha256 与后续所有证据脱节；确需换版本必须由负责人决定并重新走 A0 + S0。

## 二、四种输入怎么用

统一命令（输出目录建议 `项目X/input/`）：

```bash
# 1) 已有本地包 → 跳过下载，直接进 S0
python fetch_artifact.py --from-file "D:/apk/foo.xapk" --out "项目X/input"

# 2) 游戏名 → 先出候选，人工确认序号后重跑
python fetch_artifact.py --name "Mochichat" --out "项目X/input"          # 返回 need-confirm + 候选包名
python fetch_artifact.py --name "Mochichat" --pick 1 --out "项目X/input" # 确认后下载
python fetch_artifact.py --name "Mochichat" --package com.yuedong.mochi --out "项目X/input"  # 已知包名跳过搜索

# 3) Google Play 链接
python fetch_artifact.py --play-url "https://play.google.com/store/apps/details?id=com.yuedong.mochi" --out "项目X/input"

# 4) 三方市场下载页或直链
python fetch_artifact.py --market-url "https://apkcombo.com/mochichat/com.yuedong.mochi/download/apk" --out "项目X/input"
python fetch_artifact.py --market-url "https://.../foo.xapk" --out "项目X/input"

# 可选：--proxy http://127.0.0.1:7897（缺省读 HTTPS_PROXY 环境变量）
#      --chrome <Chrome 路径>（缺省自动探测本机 Chrome / Playwright chromium）
```

依赖：`pip install playwright`（`--from-file` 与纯直链不需要浏览器）。代理、Chrome 路径、输出目录全部由参数给，**脚本内不写死任何路径、账号或密钥**。

### 退出码与返回状态

| stdout `status` | 含义 | Agent 该怎么办 |
|---|---|---|
| `ok` | 拿到合法包，含 `file` / `size_bytes` / `sha256` / `source` | 把结果写进 `scope.md`，进 S0 |
| `need-confirm` | 游戏名搜到多个候选 | **停下来让负责人确认**，用 `--pick N` 重跑；禁止 Agent 自己选 |
| `need-input` | 搜索无结果 / 网络受限 | 请负责人改给 Play 链接、三方链接或本地包 |
| `failed` | 下载或校验失败，附 `reason` / `next_steps` | 按下面第三节降级；不得伪造包或跳过 #1 |

## 三、源优先级与失败降级

包名已知时按此顺序试（脚本已实现）：

1. **APKCombo downloader** — 按包名生成直链，最通用；
2. **APKCombo 变体页** — `ul.file-list li a.variant`，2026-09 六个项目实测全部命中；
3. **APKPure** — `a.download-start-btn`，但**会员墙 / Cloudflare 拦截很常见**，命中率最低；
4. 全部失败 → 换一个三方市场的 `--market-url`，或请负责人用 `--from-file` 提供包体。

站点结构会变：选择器失效时优先改脚本里 `download_by_package()` / `click_download()` 的选择器并回写本文件；**不要为了提高成功率去绕过反爬、验证码或会员墙**。

## 四、校验、归档与留痕（A0 出口）

A0 完成必须同时满足：

- [ ] 文件头为 `PK`（APK/ZIP 系）或 `MZ`（PE），且 > 1MB —— 挡住"错误页当安装包"；
- [ ] `sha256sum` 结果写入 `scope.md`「原包」与「原包来源」段；XAPK/APKS 内每个分包也列哈希（S1 会复核）；
- [ ] `项目X/input/artifact-source.json` 已生成（脚本自动写）：输入类型、来源 URL、包名、文件名、大小、sha256、备注；
- [ ] **商店页链接 + 在架/下架状态**记进输入检查表 #6（Play 链接天然就是它）；三方来源再补一条"渠道可信度"备注；
- [ ] 文件路径为**纯 ASCII**（中文路径会让 apktool / jadx 静默失败）。

`artifact-source.json` 是 A0 的唯一留痕文件，别删；后续 S1 的哈希基线、docs/01 的版本线、D2 的品牌判断都要回查它。

## 五、人工确认点

| 什么时候停 | 为什么 |
|---|---|
| `--name` 搜出多个候选包名 | 同名/近似名产品极多，选错 = 整个项目分析错对象，**必须人确认** |
| 下载到的包名 / 版本与用户描述不符 | 可能是改包名版、渠道包或旧版本；让负责人确认基线 |
| 来源是可疑站点、包体签名异常 | 可能夹带篡改；换官方或可信渠道 |
| 付费 / 需登录 / 区域受限应用 | **脚本不处理**，由负责人提供已合法取得的包体（`--from-file`） |

## 六、合规边界（与 v1.4.0 一致，不因自动化放宽）

- v1.4.0 的**分析放行**允许第三方作品进入流程，但**下载行为本身**仍要合法：只取公开、免费、无需登录即可获取的安装包；不绕过付费墙、登录、短信验证、验证码、区域限制、反爬或访问控制。
- 不把真实账号 / Token / Cookie 写进脚本、配置、证据或交付物；代理只作网络通道，不用于规避访问控制。
- 下载来源、日期、渠道写进 `scope.md`，**G-PUBLISH 人工所有权确认不因"包是公开下载的"而免除**；不把第三方包体或反编译产物对外分发。
- 遵守来源站服务条款；批量抓取、商业再分发不在本流程范围内。
- 有疑问时由负责人决定，本 skill 不提供法律意见。

## 七、常见坑（2026-09 六个 APK 下载实战）

| 坑 | 处理 |
|---|---|
| APKPure 全面会员墙 | 弃用为主源，改 APKCombo 变体页直链（当时六个项目全命中） |
| Chrome / 代理硬编码 | 原 `通用工程/scripts/download_apks.py` 写死了项目 A–F、Chrome 151 路径、7897 代理、E 盘根目录；**本脚本为参数化通用版**，旧脚本只留作历史参考 |
| Play 链接拿不到 APK | Play 只给元数据；提取 `?id=` 包名后走镜像，**不要伪造 Play 下载接口** |
| XAPK / APKS 分包 | 下载到的往往是容器包，S1 必须解开全部 `config.*.apk` / OBB / assetpack 再逐个登记哈希 |
| 中文路径 | 输出目录与工具链一律纯 ASCII |
| 下载到 1KB HTML | `validate()` 用文件头 + 大小挡掉，失败文件自动删除 |
| 同名游戏 | 靠 `--pick` 人工确认，不靠猜 |

> **验证状态**：脚本由 2026-09 实战脚本参数化改写，逻辑与选择器沿用当时验证过的路线，**未在新站点结构下逐一复测**（🟡）。首次用于新项目时若失败，按第三节降级并把新选择器回写本文件与 CHANGELOG。

## 变更记录

- 1.4.1（2026-11-09）新建：A0 决策树、四种输入命令、源优先级与降级、校验留痕、人工确认点、合规边界、常见坑。
