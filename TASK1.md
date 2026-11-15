# Task1 学习笔记 · 跑起 DeepAgents 研究助手

这次用 AgentSeek 生成 `deepagents/research`。生命周期配置在 `.agentseek/lifecycle.toml`，集中声明系统依赖、环境变量、安装任务和前后端启动命令。应用逻辑在 `src/research_deepagent/`，前端在 `frontend/`。

## 本机环境

项目根目录为 `/Users/xintianyuan/project/deep-agents`。工具版本为 Python 3.13.16、uv 0.13.8、AgentSeek 0.1.6、Node.js 26.12.0、npm 11.20.0 和 LangSmith CLI 0.4.0。在新终端执行 `export PATH="$HOME/.local/bin:$PATH"` 后可找到本机安装的 CLI。

课程模板取自 `7149bf2da837533cec9c738de64a09f90984f76a`。先用 Git 获取模板，再让 AgentSeek 从本地模板路径生成到临时目录，最后将生成内容放进指定项目根目录。实际默认模型为 `deepseek-ai/DeepSeek-V3.2`，计划由 `TodoListMiddleware` 提供，后端使用 AgentSeek API 与嵌入式 SeekDB。 [模板源码](https://github.com/agentseek-ai/agentseek-templates/tree/7149bf2da837533cec9c738de64a09f90984f76a/templates/deepagents/research)

## 本机实测记录 · 2026-11-15

- `agentseek info` 和 `agentseek task --list` 确认了模板及三个生命周期任务。npm 安装成功并生成 `frontend/package-lock.json`，两项 Codex 技能通过 `npx skills list` 核对。
- 锁文件中的 PyPI 下载地址多次超时。安装时临时改用阿里云镜像，保留锁定版本和包校验值。安装完成后恢复原始 `uv.lock`，并逐字节比对。
- `agentseek task course-check` 通过 6 项测试，包含嵌入式 SeekDB 和计划的 SSE 更新。前端 10 项测试通过，`npm --prefix frontend run build` 成功。
- `agentseek dev --dry-run` 显示后端 `2024` 和前端 `5174` 的启动计划。`agentseek doctor` 已通过工具和文件检查，模型与 Tavily 密钥两项仍为空，`agentseek dev` 因此在启动检查阶段退出。我单独启动了前端验证界面可打开。待登录服务并配置有效凭证后，需停止前端预览，再启动完整服务、执行 `agentseek doctor --live`，并确认页面报告和 LangSmith Trace。

## 从生成到验收

1. 准备 Python 3.12 或 3.13、uv、Node.js 和 npm。用 `uv tool install --upgrade agentseek` 安装 CLI，再用 `agentseek version` 确认终端调用的是预期版本。
2. 课程的生成命令是 `agentseek create deepagents/research --checkout main --no-input`。拿到本仓库后，在项目根目录用 `agentseek info` 和 `agentseek task --list` 读取实际配置，再执行 `agentseek task sync` 和 `agentseek task frontend`。两项任务分别安装 Python 和前端依赖。
3. 在全新检出时，把根目录和 `frontend/` 的 `.env.example` 各自复制成所在目录的 `.env`。后端按模板填写模型服务和 `TAVILY_API_KEY`。开启 LangSmith 时，把 `LANGSMITH_TRACING` 设为 `true`、项目设为 `deepagents-course`，填写与工作区同一区域的 `LANGSMITH_API_KEY` 和 `LANGSMITH_ENDPOINT`。真实 Key 保存在本地 `.env`。
4. 运行 `agentseek doctor` 静态检查工具、文件、安装目录和环境变量。用 `agentseek dev --dry-run` 核对进程命令，再用 `agentseek dev` 启动。另开终端在同一目录执行 `agentseek doctor --live`，探测后端 `2024` 和前端 `5174` 的本地进程。模型、搜索和报告仍须通过真实研究请求逐项验证。
5. 打开 [本地研究助手](http://127.0.0.1:5174/)，输入 `Research what LangGraph 1.0 added vs 0.x. Cite sources.`，观察 Todo 计划、搜索结果或来源链接，以及带引用的 Markdown 报告。检查 Agent 配置是否启用了 `TodoListMiddleware`，因为课程模板随版本更新。
6. 在项目根目录执行 `npx skills add ob-labs/agentseek --skill langchain-dev-guide --skill langsmith-trace --agent codex --yes`，运行 `npx skills list` 核对。两个技能装在 `.agents/skills/`，分别帮助编码助手检查模型兼容、读取运行追踪。DeepAgents 运行时技能由 `create_deep_agent(skills=[...])` 加载。 [课程准备篇（上）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre01-agentseek-create/) · [课程准备篇（下）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)

当前模板通过 `ChatOpenAI` 接入硅基流动。`base_url`、密钥和标准工具调用属于兼容接口。`reasoning_content` 是供应商扩展，普通 `ChatOpenAI` 不保证保留并回传；指定工具和并行工具参数也需要在实际端点验证。课程配置显式设置 `AGENTSEEK_PARALLEL_TOOL_CALLS=false`。 [模型接入技能](.agents/skills/langchain-dev-guide/reference/model-integration.md)

## 三个问题

1. **硅基流动的 Key 为什么写在 `OPENAI_API_KEY`？** 模板用 `openai` 选择 OpenAI 兼容客户端，客户端从这个变量读凭证。把 `OPENAI_API_BASE` 设为 `https://api.siliconflow.cn/v1`，就会把请求交给硅基流动，再由 `AGENTSEEK_MODEL` 选择具体模型。换模型时需要实际验证流式输出和工具调用能否正常工作。
2. **`NO_PROXY=127.0.0.1,localhost` 解决什么问题？** 配置了 HTTP 代理时，遵循代理环境变量的客户端会按 `NO_PROXY` 对回环地址直连。缺少这两项时，本机请求可能被送给代理，出现超时或代理错误。排查时可以用 `curl --noproxy '*' http://127.0.0.1:2024/health` 检查本机 API，再单独排查 GitHub、模型和搜索服务。已有绕过规则时把回环地址追加进去。
3. **页面有报告，几百万 Token 算健康吗？** 报告和引用验证了功能路径。运行质量还要结合总时长、Token、费用、错误和引用质量判断。整页搜索内容留在消息历史里时，多个模型调用可能反复读入同一段内容。先看单个模型 Run 的输入长度和重复正文，再决定缩短原文、减少搜索次数或缩小研究范围。 [课程排障笔记](https://datawhalechina.github.io/deepagents-in-action/chapters/pre03-task1-faq/)

## 用一次真实 Trace 核对成本和延迟

用 [LangSmith CLI 官方文档](https://docs.langchain.com/langsmith/langsmith-cli) 安装独立 CLI。在项目根目录的本地终端用 `set -a; source .env; set +a` 加载自己的配置后，先用 `langsmith --format pretty project list` 核对项目和认证。按时间选择最近一条已完成的 `research` 根 Trace。

```sh
langsmith trace list --project deepagents-course --name research --include-metadata --limit 5
langsmith trace get "$TRACE_ID" --project deepagents-course --include-metadata
langsmith run list --trace-ids "$TRACE_ID" --project deepagents-course --run-type llm --include-metadata --limit 100
langsmith run list --trace-ids "$TRACE_ID" --project deepagents-course --run-type tool --include-metadata --limit 100
langsmith run get "$RUN_ID" --include-io --include-metadata
```

把变量替换为实际 Trace ID 和候选 Run ID。若已有运行在 `default`，将项目名换为 `default`。先记录根 Trace 状态、墙钟耗时、输入/输出 Token 和可用费用，再按实际模型 Run 和真实搜索工具 Run 分别找出最慢调用，记录 ID、耗时、状态和脱敏证据。分析耗时时区分根流程、子 Agent 包装层、模型调用和工具调用。统计 Token 时只汇总实际模型调用一次，避免把包装层的累计用量重复相加。Trace 缺失时检查追踪开关、重复配置项、项目、API Key 和组织区域。 [LangSmith Trace 实操](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)
