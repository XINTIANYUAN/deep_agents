## LangGraph 1.0 与 0.x 系列比较：主要新增功能、改进和变化

### LangGraph 1.0 亮点（官方发布）

- **以稳定性为重点。** LangGraph v1 主要致力于提供稳定可靠的智能体运行时。
- **核心图 API 与执行模型。** 基础图构件（状态、节点和边）及运行时执行模型沿用 0.x 系列，以简化升级并保持向后兼容。
- **开发体验改进。**
  - 加强类型安全，提升健壮性并减少运行时错误。
  - 改善文档和开发体验，更便于学习和使用。
  - 检查点、持久化、流式输出与人在回路等持久执行功能仍受核心支持。
- **LangChain v1 集成。** LangGraph v1 与 LangChain v1 配合使用，简化智能体创建的 `create_agent` API 以 LangGraph 为运行时。
- **弃用项。** LangGraph 的 `create_react_agent` 已弃用。LangChain 的 `create_agent` 提供了更简洁的接口，并支持通过中间件定制。
- **升级路径。** 提供清晰的迁移指南和升级说明。

### LangGraph 0.x 系列（1.0 之前）概览

- 多次迭代发布逐步改进了以下方面：
  - 流式输出和工作流控制。例如，严格恢复模式可拒绝过时的中断应答。
  - SDK 及 CLI 工具。例如，扩大对流式模式下的生命周期与工具支持。
  - 消息处理、任务状态检查和状态更新的性能。
  - 修复子图命名空间问题并更新有安全问题的依赖。
- 1.0 之前没有重大破坏性变更或明确的大型稳定版本里程碑。
- 0.x 更侧重功能开发、迭代改进与建立基础 API。

### 1.0 相比 0.x 的主要差异与新增能力

| 维度 | LangGraph 0.x | LangGraph 1.0 |
| --- | --- | --- |
| API 稳定性 | API 持续演进，迭代快 | 核心 API 稳定，向后兼容 |
| 执行模型 | 已具备核心模型，仍在成熟 | 核心构件和执行模型维持稳定 |
| 开发体验 | 逐步改进 | 加强类型安全，改善开发体验和文档 |
| 集成 | 可独立使用，初步支持 LangChain | 作为 LangChain v1 智能体的后端运行时，支撑 `create_agent` |
| 版本重点 | 功能开发，包括流式输出、生命周期和严格恢复控制 | 稳定性、可靠性、持久执行与检查点持久化 |
| 弃用功能 | 引入 `create_react_agent` | 弃用 `create_react_agent`，推荐 LangChain 的 `create_agent` |
| 文档 | 持续补充 | 开发文档更完善 |
| 迁移支持 | 尚未正式成文 | 提供清晰的迁移指南 |

### 来源

1. LangGraph v1 官方发布说明和公告\
   https://docs.langchain.com/oss/python/releases/langgraph-v1

2. LangGraph 0.x 与通用更新日志（包含 CLI 及 SDK 发布）\
   https://docs.langchain.com/oss/python/releases/changelog\
   https://github.com/langchain-ai/langgraph/releases

这份摘要概括了 LangGraph 从 0.x 到 1.0 的演进。早期工作的重心是开发功能和迭代 API，1.0 则迈向可用于生产的稳定平台，并改善了集成与开发体验。
