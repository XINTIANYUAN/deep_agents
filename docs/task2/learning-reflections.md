# Task2 学习心得

## 把三层架构对应到代码

Task1 我从网页看计划和报告，Task2 我把注意力移到 `create_deep_agent()` 和 `invoke()`。创建时，Deep Agents 装配文件、子 Agent 等 Harness 能力和应用注册的工具，LangChain 组织模型与工具循环，LangGraph 执行编译后的图。把创建阶段和运行阶段分开后，我知道该从哪里排查。工具没被注册时看装配，模型选择了工具却执行失败时看调用参数和工具实现。做短练习也可以按需保持配置简洁，例如在 v0.7 需要显式待办时再加入 `TodoListMiddleware`。 [第 1 章 · Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/)

## 通过消息记录确认工具执行

天气工具使用固定数据，适合检验模型能否调用工具。计算器的默认加法则适合检查参数契约。类型标注约束输入，文档字符串说明工具何时使用，默认值让模型可以省略可选参数。验收时，我会沿 `result["messages"]` 依次核对 `AIMessage.tool_calls` 中的工具名和参数、对应 `ToolMessage` 的结果，再读最终回答。要验证默认加法，我会再确认调用参数中是否确实省略了运算参数。这样能把工具的实际结果和模型对结果的转述对应起来。 [第 2 章 · 快速上手](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/)

这次在 LangSmith 点开 `calculate` 后，我看到输入只有两个数，输出为 `22.0`。调用树也显示，每次工具结果返回后，模型都被再次调用。即使脚本只写了一次 `invoke()`，完整的执行顺序仍要到 Trace 里确认。 [实测截图](langsmith-trace.jpg)

[查看 Task2 学习笔记与运行说明](learning-notes.md)
