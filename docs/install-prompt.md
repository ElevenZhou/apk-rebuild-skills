# 给 AI 的安装提示词（apk-rebuild-skills）

把下面整段发给要安装的 AI（WorkBuddy / Claude Code / Codex / Trae CN 等），把 `<目标目录>` 换成该 AI 的技能目录。

| AI | 技能目录 | `-Targets` 参数 |
|---|---|---|
| WorkBuddy | `C:\Users\<用户>\.workbuddy\skills` | `workbuddy` |
| Claude Code | `C:\Users\<用户>\.claude\skills` | `claude` |
| OpenCode | 不单独装，自动读 Claude 的目录 | — |
| Codex | `$CODEX_HOME\skills`（本机为 `E:\AI_Dev\Codex\home\skills`） | `codex` |
| Trae CN | `C:\Users\<用户>\.trae-cn\skills` | `trae` |

源：`Y:\Skills\apk-rebuild-skills`（NAS 不可用时用 `\\192.168.31.121\projects\Skills\apk-rebuild-skills`，或直接 clone GitHub 私有仓库 `ElevenZhou/apk-rebuild-skills`）。

```text
请安装 apk-rebuild-skills 技能包，按下面执行，做完再汇报，中途不要问我。

源目录：Y:\Skills\apk-rebuild-skills
目标目录：<目标目录>

1. 执行 git -C Y:\Skills\apk-rebuild-skills pull 拿到最新版。
2. 运行：powershell -ExecutionPolicy Bypass -File Y:\Skills\apk-rebuild-skills\install\install.ps1 -Dest "<目标目录>"
   （脚本会把 skills\ 下 7 个 rebuild-* 目录整体复制过去；同名旧目录自动改名备份，不删除。）
   如果不能运行 PowerShell，就手工把 Y:\Skills\apk-rebuild-skills\skills\ 下 7 个目录整个复制到目标目录，保持 SKILL.md、references\、scripts\ 结构不变；已有同名目录先改名为 <名字>.bak-日期。
3. 不修改技能内容；不读取、不打印任何 API key 或 .env。
4. 验收并回报：
   a. 7 个技能的安装路径和 SKILL.md frontmatter 里的 version：
      rebuild-workflow / rebuild-recon / rebuild-asset-recovery / rebuild-product-design /
      rebuild-dev-milestones / rebuild-device-evidence / rebuild-build-release
   b. 路由自测（只回答会调用哪个技能，不要真正执行）：
      “源码丢了只剩 APK，帮我重建这个项目” → rebuild-workflow
      “分析一下这个 apk 是什么引擎” → rebuild-recon
      “把包里的图片音频导出来” → rebuild-asset-recovery
      “写重建后的产品文档和开发计划” → rebuild-product-design
      “用 ADB 截图并点开始按钮” → rebuild-device-evidence
      “打一个签名试玩 APK” → rebuild-build-release
   c. 如需重启或新开会话才能识别新技能，告诉我。
```

## 更新

```text
git -C Y:\Skills\apk-rebuild-skills pull
powershell -ExecutionPolicy Bypass -File Y:\Skills\apk-rebuild-skills\install\install.ps1 -Dest "<目标目录>"
```

本机若是 `git clone` 到本地盘再安装（目录联接模式），之后只需 `git pull`，无需重跑脚本。
