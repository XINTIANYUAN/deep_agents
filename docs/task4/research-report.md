# 三大 Agent Harness 简要对比

2026 年 11 月 23 日，根据本次 Agent 生成稿和三份官方概览复核整理。资料范围是各框架的官方介绍，场景建议由这些资料归纳。

## Deep Agents

Deep Agents 在 LangChain 与 LangGraph 上组装多步 Agent 能力，包括文件系统上下文、子 Agent、记忆与技能加载、历史摘要和大结果卸载。它支持自定义工具、MCP 和可插拔 Backend。Shell 执行能力取决于所选执行后端，文件和记忆的保存期限也取决于存储配置。本实验使用 `0.7.8`，通过 `TodoListMiddleware()` 显式启用规划。 [Deep Agents 官方概览](https://docs.langchain.com/oss/python/deepagents/overview)

## Claude Agent SDK

Claude Agent SDK 将 Claude Code 的工具、Agent 循环与上下文管理作为库提供给 Python 和 TypeScript 应用。其能力包括文件操作、命令执行、权限控制、会话恢复、Hooks、MCP 和子 Agent。应用可以把这些能力嵌入自己运行的进程，再配置工具和审批行为。 [Claude Agent SDK 官方概览](https://code.claude.com/docs/en/agent-sdk/overview)

## Codex SDK

Codex SDK 用于程序化控制 Codex，官方列举了 CI/CD 编码任务、内部工具和应用集成等用途。概览提供 TypeScript 与 Python 用法，包含线程启动、继续和恢复，以及运行配置。构建处理认证、审批和流式事件的自定义客户端时，可进一步参考文档链接中的 Codex app server。 [Codex SDK 官方概览](https://learn.chatgpt.com/docs/codex-sdk)

## 对比与选择

| 维度 | Deep Agents | Claude Agent SDK | Codex SDK |
| --- | --- | --- | --- |
| 工具与文件 | 应用工具、MCP、虚拟文件工具和可插拔 Backend | Claude Code 工具、MCP、自定义工具与权限控制 | 程序化驱动 Codex 执行工程任务，配置工作范围与运行权限 |
| 上下文管理 | State、文件、摘要与卸载协同，可配置记忆和子 Agent | 会话上下文、恢复与子 Agent | 通过线程继续和恢复工作，保留相关上下文 |
| 扩展方式 | 配置 Middleware、Backend、工具和运行时资源 | 在应用中配置工具、Hooks、MCP、技能和审批 | 将 SDK 接入应用或流水线，按需要使用 app server 构建客户端 |

从这些接口形态归纳，已有 LangChain/LangGraph 工作流、希望组合规划与存储策略的项目，可以考察 Deep Agents。希望在 Python 或 TypeScript 应用中嵌入 Claude Code 能力的项目，可以考察 Claude Agent SDK。希望在工程流水线或内部工具里驱动 Codex 的项目，可以考察 Codex SDK。实际选择仍需用本项目任务测试工具正确性、上下文延续、权限与运行成本。 [Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) · [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) · [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)

## 资料来源

- [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)

本次自动生成稿已有三个框架章节和来源，但遗漏了提示词要求的对比表，并夹杂较多英文。复核稿补充对等维度的表格、整理中文表达，并明确执行后端与保存期限的配置条件。模型原稿与三份笔记保留在本机本次实验目录，路径见 [学习笔记](learning-notes.md)。
