# CLAUDE.md

本仓库是公众号内容样式库:五套视觉样式 + 文章导读模板 + 渲染工具链,同时是一个可安装的 Claude Code Skill(根目录 SKILL.md,可 `git clone` 到 `~/.claude/skills/style-templates` 使用)。

**Agent 接手任何任务前,先读 README.md**——选型决策表、模式 A(导读长文)/ 模式 B(版式成品)流程、常见坑都在那;进公众号的适配规则在 `样式模板库/公众号适配指南.md`。

红线:

1. HTML 进公众号必须过内联生成脚本,禁止直接贴原始 HTML
2. 全页图源码禁用 `position:fixed`(裁边失效)
3. 本仓库即模板本体:改完 commit + push,使用方 pull 即得最新
