# Task1 学习笔记 · 跑起 DeepAgents 研究助手

这次用 AgentSeek 生成 `deepagents/research`。生命周期配置在 `.agentseek/lifecycle.toml`，集中声明系统依赖、环境变量、安装任务和前后端启动命令。应用逻辑在 `src/research_deepagent/`，前端在 `frontend/`。

## 本机环境

本次安装的工具版本为 Python 3.13.16、uv 0.13.8、AgentSeek 0.1.6、Node.js 26.12.0、npm 11.20.0 和 LangSmith CLI 0.4.0。在新终端执行 `export PATH="$HOME/.local/bin:$PATH"` 后可找到本机安装的 CLI。

课程模板取自 `7149bf2da837533cec9c738de64a09f90984f76a`。先用 Git 获取模板，再让 AgentSeek 从本地模板路径生成到临时目录，最后将生成内容放进指定项目根目录。实际默认模型为 `deepseek-ai/DeepSeek-V3.2`，计划由 `TodoListMiddleware` 提供，后端使用 AgentSeek API 与嵌入式 SeekDB。 [模板源码](https://github.com/agentseek-ai/agentseek-templates/tree/7149bf2da837533cec9c738de64a09f90984f76a/templates/deepagents/research)

## 本机实测记录 · 2026-11-15

- `agentseek info` 和 `agentseek task --list` 确认了模板及三个生命周期任务。npm 安装成功并生成 `frontend/package-lock.json`，两项 Codex 技能通过 `npx skills list` 核对。
- 锁文件中的 PyPI 下载地址多次超时。安装时临时改用阿里云镜像，保留锁定版本和包校验值。安装完成后恢复原始 `uv.lock`，并逐字节比对。
- `agentseek task course-check` 通过 6 项测试，包含嵌入式 SeekDB 和计划的 SSE 更新。前端 10 项测试通过，`npm --prefix frontend run build` 成功。
- `agentseek dev --dry-run` 显示后端 `2024` 和前端 `5174` 的启动计划。首次 `doctor` 发现模型和 Tavily 凭证缺失。将三个服务的密钥写入本地 `.env` 后，`doctor` 和 `doctor --live` 均通过。
- 硅基流动国际站对短探针返回 HTTP 200，但完整工具调用返回 HTTP 402（余额不足）。在浏览器中临时用获授权的 OpenAI `gpt-4.1-mini` 完成了一次验收。围绕课程题目，限制最多三次搜索，实际观察到四项计划、三次 Tavily 搜索和一份带三条引用的 Markdown 报告。后端将该次运行记为 `success`，报告重启后仍可打开。计划面板停在 3/4，最后一项仍标为进行中。
- 报告引用了 LangGraph 1.0 发布说明、更新日志和 GitHub Releases。发布说明确认了核心图 API 的稳定性以及 `create_react_agent` 弃用。报告里关于 0.x 的概括仍需按具体版本核查。 [LangGraph 1.0 发布说明](https://docs.langchain.com/oss/python/releases/langgraph-v1)

## 从生成到验收

1. 准备 Python 3.12 或 3.13、uv、Node.js 和 npm。用 `uv tool install --upgrade agentseek` 安装 CLI，再用 `agentseek version` 确认终端调用的是预期版本。
2. 课程的生成命令是 `agentseek create deepagents/research --checkout main --no-input`。拿到本仓库后，在项目根目录用 `agentseek info` 和 `agentseek task --list` 读取实际配置，再执行 `agentseek task sync` 和 `agentseek task frontend`。两项任务分别安装 Python 和前端依赖。
3. 在全新检出时，把根目录和 `frontend/` 的 `.env.example` 各自复制成所在目录的 `.env`。后端按模板填写模型服务和 `TAVILY_API_KEY`。开启 LangSmith 时，把 `LANGSMITH_TRACING` 设为 `true`、项目设为 `deepagents-course`，填写与工作区同一区域的 `LANGSMITH_API_KEY` 和 `LANGSMITH_ENDPOINT`。真实 Key 保存在本地 `.env`。
4. 运行 `agentseek doctor` 静态检查工具、文件、安装目录和环境变量。用 `agentseek dev --dry-run` 核对进程命令，再用 `agentseek dev` 启动。另开终端在同一目录执行 `agentseek doctor --live`，探测后端 `2024` 和前端 `5174` 的本地进程。模型、搜索和报告仍须通过真实研究请求逐项验证。
5. 打开 [本地研究助手](http://127.0.0.1:5174/)，输入 `Research what LangGraph 1.0 added vs 0.x. Cite sources.`，观察 Todo 计划、搜索结果或来源链接，以及带引用的 Markdown 报告。检查 Agent 配置是否启用了 `TodoListMiddleware`，因为课程模板随版本更新。
6. 在项目根目录执行 `npx skills add ob-labs/agentseek --skill langchain-dev-guide --skill langsmith-trace --agent codex --yes`，运行 `npx skills list` 核对。两个技能装在 `.agents/skills/`，分别帮助编码助手检查模型兼容、读取运行追踪。DeepAgents 运行时技能由 `create_deep_agent(skills=[...])` 加载。 [课程准备篇（上）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre01-agentseek-create/) · [课程准备篇（下）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)

当前模板通过 `ChatOpenAI` 接入硅基流动。`base_url`、密钥和标准工具调用属于兼容接口。`reasoning_content` 是供应商扩展，普通 `ChatOpenAI` 不保证保留并回传；指定工具和并行工具参数也需要在实际端点验证。课程配置显式设置 `AGENTSEEK_PARALLEL_TOOL_CALLS=false`。 [模型接入技能](.agents/skills/langchain-dev-guide/reference/model-integration.md)

## 三个问题

1. **硅基流动的 Key 为什么写在 `OPENAI_API_KEY`？** 模板用 `openai` 选择 OpenAI 兼容客户端，客户端从这个变量读凭证。`OPENAI_API_BASE` 决定请求发往哪个服务。硅基流动中国站使用 `https://api.siliconflow.cn/v1`，本次登录的国际站使用 `https://api.siliconflow.com/v1`，再由 `AGENTSEEK_MODEL` 选择具体模型。换模型时需要实际验证流式输出和工具调用能否正常工作。
2. **`NO_PROXY=127.0.0.1,localhost` 解决什么问题？** 配置了 HTTP 代理时，遵循代理环境变量的客户端会按 `NO_PROXY` 对回环地址直连。缺少这两项时，本机请求可能被送给代理，出现超时或代理错误。排查时可以用 `curl --noproxy '*' http://127.0.0.1:2024/health` 检查本机 API，再单独排查 GitHub、模型和搜索服务。已有绕过规则时把回环地址追加进去。
3. **页面有报告，几百万 Token 算健康吗？** 报告和引用验证了功能路径。运行质量还要结合总时长、Token、费用、错误和引用质量判断。整页搜索内容留在消息历史里时，多个模型调用可能反复读入同一段内容。先看单个模型 Run 的输入长度和重复正文，再决定缩短原文、减少搜索次数或缩小研究范围。 [课程排障笔记](https://datawhalechina.github.io/deepagents-in-action/chapters/pre03-task1-faq/)

## 用一次真实 Trace 核对成本和延迟

用 [LangSmith CLI 官方文档](https://docs.langchain.com/langsmith/langsmith-cli) 安装独立 CLI。在项目根目录的本地终端用 `set -a; source .env; set +a` 加载自己的配置后，先用 `langsmith --format pretty project list` 核对项目和认证。按时间和输入选择已完成的根 Trace。课程图 ID 是 `research`，当前 AgentSeek API 在本次实测中将根运行记为 `LangGraph`。

```sh
langsmith trace list --project deepagents-course --include-metadata --limit 5
langsmith trace get "$TRACE_ID" --project deepagents-course --include-metadata
langsmith run list --trace-ids "$TRACE_ID" --project deepagents-course --run-type llm --include-metadata --limit 100
langsmith run list --trace-ids "$TRACE_ID" --project deepagents-course --run-type tool --include-metadata --limit 100
langsmith run get "$RUN_ID" --include-io --include-metadata
```

把变量替换为实际 Trace ID 和候选 Run ID。若已有运行在 `default`，将项目名换为 `default`。先记录根 Trace 状态、墙钟耗时、输入/输出 Token 和可用费用，再按实际模型 Run 和真实搜索工具 Run 分别找出最慢调用，记录 ID、耗时、状态和脱敏证据。分析耗时时区分根流程、子 Agent 包装层、模型调用和工具调用。统计 Token 时只汇总实际模型调用一次，避免把包装层的累计用量重复相加。Trace 缺失时检查追踪开关、重复配置项、项目、API Key 和组织区域。 [LangSmith Trace 实操](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)

### 本次验收的 Trace

`deepagents-course` 中的根运行耗时 79.2 秒，共 128 个 Run，14 次实际模型调用、3 次 Tavily 搜索，记录到 0 个错误。子 Agent 任务用时 50.8 秒，包含自己的模型和工具调用。最慢的实际叶子调用如下。

| 调用 | 耗时 | 检查结果 |
| --- | ---: | --- |
| `ChatOpenAI` | 7.45 秒 | `run get --include-io` 返回模型消息与生成结果，错误为空。 |
| `tavily_search` | 8.30 秒 | 查询 LangGraph 1.0 官方发布说明，错误为空，序列化输出约 71.7 万字符。 |

本次流式 Trace 的 `token_usage` 和费用字段为空。这套 `ChatOpenAI` 配置显式指定了兼容 API 地址，默认未请求流式 usage。计量时可用支持 `stream_options.include_usage` 的端点启用流式用量，再核对实际模型 Run 的输入、输出和总 Token。搜索工具会抓取并转写整页，单次返回就可能很大。结合该次实际输出规模，可以先检查大工具结果是否被重复读回模型，再评估缩小抓取范围的效果。

### 在本机继续使用

验收后我结束了临时 OpenAI 对接，把本机运行切换到 Ollama 的 `qwen3.5:4b`。它走 `127.0.0.1:11434` 的 OpenAI 兼容接口，真实搜索和追踪继续使用 Tavily 与 LangSmith。本机已验证模型的流式工具调用以及前后端连通。另用本地模型完成了一次短研究，计划 2/2，执行一次 Tavily 搜索，返回带链接的 Markdown。该回答引用了 1.0 Alpha 公告，仍需用正式版发布页核对 GA 日期。硅基流动国际站的密钥和配置保存在仓库忽略的 `.env`。 [正式版发布页](https://github.com/langchain-ai/langgraph/releases/tag/1.0.0)

重启后如果需要手动恢复，先在一个终端运行 `ollama serve`。另开终端进入项目根目录，再运行以下命令。新机器第一次使用需先运行 `ollama pull qwen3.5:4b`。

```sh
export PATH="$HOME/.local/bin:$PATH"
export NO_PROXY="${NO_PROXY:+$NO_PROXY,}127.0.0.1,localhost"
export no_proxy="${no_proxy:+$no_proxy,}127.0.0.1,localhost"
AGENTSEEK_MODEL_PROVIDER=openai AGENTSEEK_MODEL=qwen3.5:4b \
  OPENAI_API_BASE=http://127.0.0.1:11434/v1 OPENAI_API_KEY=ollama \
  agentseek dev
```

[Ollama 的 OpenAI 兼容接口](https://docs.ollama.com/api/openai-compatibility)
