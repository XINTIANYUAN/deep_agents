相比 0.x 系列，LangGraph 1.0 带来了多项改进，重点是稳定性、开发体验，以及与 LangChain v1 的集成。核心图构件和执行模型维持稳定，以保证向后兼容，同时改进了类型安全和文档。检查点和持久化等持久执行能力仍是核心功能。0.x 提供的 `create_react_agent` 已弃用，推荐改用 LangChain 更简洁的 `create_agent` API。1.0 也提供了清晰的迁移指南。

0.x 系列主要在迭代功能，包括改进流式输出、CLI 与 SDK 工具及优化性能，当时尚未达到正式稳定发布的里程碑，也未提供完整的迁移支持。

完整对照见下文。

# LangGraph 1.0 与 0.x 系列对比

## 简介

本文总结 LangGraph 1.0 相比 0.x 系列的重要新增能力、改进和变化。LangGraph 是基于图的 AI 智能体运行时。早期版本专注于功能迭代，1.0 则成为可用于生产环境的稳定版本。

## LangGraph 0.x 系列概览

0.x 系列以快速迭代和逐步改进为主，主要工作包括：

- 引入并优化流式输出，提供严格的恢复控制
- 改进 SDK 和 CLI，扩大对生命周期和工具的支持
- 优化消息处理与状态更新的性能
- 修复命名空间冲突和依赖安全问题
- API 与执行模型逐步成熟，尚未稳定
- 尚无正式的迁移指南或稳定发布里程碑

## LangGraph 1.0 概览

LangGraph 1.0 是一个重要的版本里程碑，着重改进稳定性与开发体验：

- 稳定核心图构件与运行时执行模型，保持向后兼容
- 加强类型安全，减少运行时错误，提高健壮性
- 改善文档与开发体验
- 检查点、持久化、流式输出与人在回路等持久执行功能仍是核心能力
- 与 LangChain v1 集成，作为 LangChain 智能体的后端运行时
- 弃用 `create_react_agent`，推荐使用 LangChain 更简洁、可定制性更高的 `create_agent` API
- 提供清晰的迁移路径和升级指南

## 详细对照

| 维度 | LangGraph 0.x | LangGraph 1.0 |
| --- | --- | --- |
| API 稳定性 | 持续演进，更新频繁 | 稳定并保持向后兼容 |
| 执行模型 | 已具备，仍在演进 | 核心图构件保持稳定 |
| 开发体验 | 逐步改进 | 加强类型安全并改善文档 |
| 集成 | 可独立使用，初步支持 LangChain | 与 LangChain v1 全面集成 |
| 版本重点 | 功能与流式输出的改进 | 稳定性、可靠性和持久执行 |
| 弃用功能 | 引入 `create_react_agent` | 弃用该工具，推荐 LangChain 的 `create_agent` |
| 文档 | 持续补充，覆盖范围有限 | 文档覆盖更全面 |
| 迁移支持 | 尚未形成正式指南 | 提供清晰的迁移指南 |

## 结论

LangGraph 1.0 是 0.x 系列的一次重要演进，优先考虑稳定性、开发效率和 LangChain v1 集成。它将 0.x 快速迭代积累的功能和 API 整合为可靠、文档完善的基础，适合用于生产环境。

### 来源

[1] [LangGraph v1 官方发布说明和公告](https://docs.langchain.com/oss/python/releases/langgraph-v1)\
[2] [LangGraph 0.x 与通用更新日志](https://docs.langchain.com/oss/python/releases/changelog)\
[3] [LangGraph GitHub 发布记录](https://github.com/langchain-ai/langgraph/releases)
