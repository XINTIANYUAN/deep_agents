# Task1 课程反馈

准备篇已经把 AgentSeek 的生成、安装、检查和启动串起来，也带学员用 LangSmith 定位模型和工具调用。以下建议来自本次搭建和验收，目的是让学员遇到版本变化、额度不足或 Trace 查不到时，能用更短的步骤定位问题。 [Task1 学习笔记与实测记录](learning-notes.md)

1. **在生成命令旁提供一组已验证的固定版本。** 上篇已说明可以用完整提交 SHA 复现。建议把经过验证的 AgentSeek 版本、模板 SHA、Python 和 Node.js 版本放在首条命令旁，再给出 `agentseek info` 应看到的模板和任务。学员可以先按这组组合完成首次运行，再用 `main` 观察版本变化。 [课程准备篇（上）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre01-agentseek-create/)

2. **在完整研究前加入一次单搜索验收。** 上篇已有静态检查、实时检查和浏览器验收。本机两项检查通过，硅基流动短请求返回 HTTP 200，完整工具调用因余额不足返回 HTTP 402。建议先用同一模型和端点运行一个只做一次搜索、返回一条可点击引用的短题。端口无法访问时检查进程与代理，遇到余额不足提示时核对服务额度，再用原短题复验。

3. **把搜索、引用、报告和计划终态写成可独立核对的验收项。** 上篇已说明待办支持随模板变化。本次后端返回 `success`，报告重启后仍可打开，计划面板停在 3/4。建议让学员分别记录搜索是否实际执行、来源是否支持结论、Markdown 是否完整，以及待办最终状态。示例可限定最多三次搜索，并要求优先引用正式版发布说明。

4. **给 LangSmith 查询和用量缺失各补一个实测示例。** 下篇已教如何区分根流程、子 Agent 和实际模型与工具调用。本次图 ID 是 `research`，根运行名为 `LangGraph`。建议在按名称过滤前先用 `langsmith trace list --project deepagents-course --include-metadata --limit 5`，再按时间、输入和状态定位。另可让学员把空的 Token 和费用字段标为未上报，在端点支持时验证流式用量。以一次约 71.7 万字符的 Tavily 响应为例，比较结果大小与后续模型输入，判断是否值得缩小抓取范围。 [课程准备篇（下）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)
