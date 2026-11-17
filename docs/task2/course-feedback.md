# Task2 课程反馈

第 1 章把能力装配和模型—工具循环联系起来，第 2 章用固定天气和本地计算示例降低了工具练习的门槛。建议在两章之间补一小段可复现的验收路径，让读者能在第一轮运行里看到架构图对应的消息。 [Task2 学习笔记](learning-notes.md)

1. **把模型—工具循环对应到一组实际消息。** 第 1 章已有创建时的架构图，第 2 章也解释了执行循环与完整消息历史。建议在天气示例打印最终回答之后，加一段遍历消息的代码，输出工具名、参数、对应结果和最终回答，并让学员用工具调用 ID 对上结果。这样可以具体检查工具是否被模型选中、是否执行，以及回复是否采用了结果。 [第 1 章 · Agent Harness](https://datawhalechina.github.io/deepagents-in-action/chapters/ch01-agent-harness/) · [第 2 章 · 快速上手](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/)

2. **给默认参数配一组对照输入。** 第 2 章已说明类型标注、说明文字和默认值，并用币种转换展示了可选参数。建议补两条短题，一条让模型省略目标币种并由函数采用默认值，一条明确指定其他目标币种。让学员核对调用参数和计算结果，直观看到可选参数何时由工具补齐。

3. **说明从 Task1 切到单脚本时需要改哪几项配置。** 准备篇模板用 `OPENAI_API_KEY` 和 `AGENTSEEK_MODEL`，快速上手示例读取 `SILICONFLOW_API_KEY` 和 `MODEL_NAME`。建议并排列出模型地址、密钥、模型 ID 与变量名，以及各自在哪个进程中读取。也可以给出 Ollama 等本地兼容端点的短示例，让学员沿用本地推理环境检验工具调用。 [准备篇（上）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre01-agentseek-create/) · [第 2 章 · 快速上手](https://datawhalechina.github.io/deepagents-in-action/chapters/ch02-quickstart/)
