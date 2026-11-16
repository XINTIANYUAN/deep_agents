# Task1 学习心得

## 先确认问题出在哪一层

AgentSeek 的 `create → info → task → doctor → dev` 让我知道从哪里查起。Python 依赖下载超时后，我把排查范围缩到锁文件记录的下载地址，临时换镜像获取同一批锁定版本，保留包校验值。安装完成后，我恢复并逐字节比对了原始 `uv.lock`。以后复现环境时，我会先记录模板提交和工具版本，再排查下载渠道。

模型接入也要沿请求路径检查。`OPENAI_API_KEY` 是兼容客户端读取凭证的位置，`OPENAI_API_BASE` 决定请求发往哪个服务。本机两项 `doctor` 检查通过，硅基流动的短请求返回 HTTP 200，完整工具调用却因余额不足返回 HTTP 402。下次我会先确认 `127.0.0.1` 和 `localhost` 走直连，再用同一模型和端点跑一次短工具调用，最后发起完整研究。 [课程准备篇（上）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre01-agentseek-create/)

## 把验收做完，也把引用点开

第一次浏览器验收执行了三次 Tavily 搜索，后端记录为 `success`，报告重启后仍可打开。运行结束时，第四项待办仍在进行中。后来用本地模型跑短题，两项待办都完成了，回答里有一条引用指向 LangGraph 1.0 Alpha 公告。以后我会分别记录计划终态、实际搜索和最终报告，再打开来源，核对它是否支持正文里的具体版本和日期。 [LangGraph 1.0 正式版发布页](https://github.com/langchain-ai/langgraph/releases/tag/1.0.0)

## 用运行记录解释耗时

在 LangSmith 中，我先看根 Trace 的 79.2 秒，再检查 14 次实际模型调用和三次 Tavily 搜索。一次搜索的序列化输出约 71.7 万字符，本次流式 Trace 的 Token 和费用字段都为空。我会把空字段记为未上报，并沿后续模型调用检查这些网页正文是否被重复读入。下次对照实验固定问题、模型和环境，只调整抓取范围，再比较引用质量、耗时和端点实际返回的用量。 [课程准备篇（下）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)

[查看 Task1 学习笔记与实测记录](learning-notes.md)
