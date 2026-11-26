# 子 Agent 上下文隔离与共享文件

2026 年 11 月 26 日，根据本次流水线的模型原稿、运行记录和 Deep Agents `0.7.8` 源码复核整理。

## 隔离内容

默认委派为子 Agent 新建一条包含任务描述的 `HumanMessage`。中间消息与工具结果留在子 Agent 的对话里，主 Agent 的任务响应只包含其最终回答。双方使用各自的系统提示词，声明式子 Agent 的 Skills 状态与 Todo 清单也各自管理。本实验研究员单独启用 Todo，写手没有该工具。 [0.7.8 委派实现](https://github.com/langchain-ai/deepagents/blob/deepagents%3D%3D0.7.8/libs/deepagents/deepagents/middleware/subagents.py)

## 共享文件

本次共用 StateBackend，`files` 随允许的状态传入与回传。研究员写入 `/handoff/findings.md`，写手后续委派时读到它，再写出 `/handoff/report.md`，主 Agent 可以读回报告。Skills 的文件也位于这个共享 Backend，独立加载的技能目录与私有元数据决定各角色的技能上下文。

## 实践建议

交接时说明准确路径、产物和返回摘要范围，并检查实际文件。消息隔离与文件权限分别配置，任务返回成功也需结合内容验收。子 Agent 返回状态需要 `messages` 键，框架再根据最终 AI 文本生成主 Agent 收到的 `ToolMessage`。各 Agent 可独立使用自己的 Todo。

模型原稿把返回条件误写为“子 Agent 必须返回 ToolMessage”，并写出“不依赖 todos 追踪”的建议。复核稿按源码与实际独立 Todo 记录修正了这两点，补齐系统提示词和 Skills 的说明。原稿保留在本机实验目录，详见 [学习笔记](learning-notes.md)。
