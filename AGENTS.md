# AGENTS.md

(Codex 等自动加载本文件;Claude Code 见 CLAUDE.md)

本仓库是公众号内容样式库:五套视觉样式 + 文章导读模板 + 渲染工具链,同时是一个可安装的 Claude Code Skill(根目录 SKILL.md)。

**Agent 接手任何任务前,先读 README.md**——选型决策表、模式 A(导读长文)/ 模式 B(版式成品)流程、常见坑都在那;进公众号的适配规则在 `样式模板库/公众号适配指南.md`。

红线:

1. HTML 进公众号必须过内联生成脚本,禁止直接贴原始 HTML
2. 全页图源码禁用 `position:fixed`(裁边失效)
3. 本仓库即模板本体:改完 commit + push,使用方 pull 即得最新

**Codex 注意**:沙箱 workspace-write 默认禁网,首次 `pip3 install` / `git clone` 需要联网,请求用户放行,或启动时带 `-c 'sandbox_workspace_write.network_access=true'`;装包建议落在本仓库 `.venv` 里,避免写系统 site-packages 越界被拦。
