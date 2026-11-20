# DeepAgents 研究助手

这是用 AgentSeek 的 `deepagents/research` 模板搭建的 Task1 项目。后端运行 DeepAgents 研究图，网页展示待办、Tavily 搜索和带引用的 Markdown 报告。

## Task1 学习资料

| 文档 | 内容 |
| --- | --- |
| [学习笔记](docs/task1/learning-notes.md) | 环境配置、操作步骤、踩坑排查和实测记录 |
| [学习心得](docs/task1/learning-reflections.md) | 从实操中学到的排查、验收和 Trace 分析方法 |
| [课程反馈](docs/task1/course-feedback.md) | 结合实测给课程材料的改进建议 |

## Task2 第一个 Deep Agent

| 入口 | 内容 |
| --- | --- |
| [可运行示例](examples/task2/agent.py) | 用本地模型调用模拟天气和计算器工具 |
| [学习笔记](docs/task2/learning-notes.md) | 运行命令、排查过程、验收记录和 LangSmith 截图 |
| [学习心得](docs/task2/learning-reflections.md) | 三层架构、工具参数和调用链的实操体会 |
| [课程反馈](docs/task2/course-feedback.md) | 对第 1、2 章的改进建议 |

## Task3 虚拟文件系统

| 入口 | 内容 |
| --- | --- |
| [可运行实验](examples/task3/filesystem_lab.py) | 文件读写与搜索、大结果自动卸载、三种 Backend 对比 |
| [学习笔记](docs/task3/learning-notes.md) | 复现命令、实测记录、Trace 截图和存储对比结论 |
| [学习心得](docs/task3/learning-reflections.md) | 按需取用上下文与文件生命周期的实操体会 |
| [课程反馈](docs/task3/course-feedback.md) | 对第 3 章实验设计与验收方式的建议 |

## 本地运行

先按[学习笔记](docs/task1/learning-notes.md)配置 Python、Node.js、uv 和 `.env`。然后在项目根目录执行：

```sh
uvx agentseek==0.1.6 task sync
uvx agentseek==0.1.6 task frontend
uvx agentseek==0.1.6 doctor
uvx agentseek==0.1.6 dev
```

另开终端运行 `uvx agentseek==0.1.6 doctor --live`，确认前后端端口可达，再打开[本地研究助手](http://127.0.0.1:5174/)。如需使用 Ollama，可照学习笔记里的本地模型启动命令操作。

[课程模板参考](docs/reference/agentseek-course-template.md)记录上游模板的依赖锁定、计划测试和研究产物检查方法。
