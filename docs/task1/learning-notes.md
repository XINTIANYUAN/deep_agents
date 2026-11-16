# Task1 学习笔记 · 从搭建到验收

2026 年 11 月 15 日，在 macOS Apple Silicon 上搭建并验收了 `deepagents/research`。在浏览器发起研究后，页面显示了研究计划和带三条来源链接的 Markdown 报告。LangSmith 记录了三次实际 Tavily 搜索。[查看中文版验收报告](../../frontend/src/task1/report.zh.md)

## 环境与版本

| 项目 | 实测版本或配置 |
| --- | --- |
| 开发工具 | Python 3.13.16、uv 0.13.8、AgentSeek 0.1.6、Node.js 26.12.0、npm 11.20.0 |
| 运行依赖 | Deep Agents 0.7.8、AgentSeek API 0.2.3、嵌入式 SeekDB |
| 追踪工具 | LangSmith CLI 0.4.0 |
| 模板提交 | `7149bf2da837533cec9c738de64a09f90984f76a` |
| 本地地址 | 前端 `127.0.0.1:5174`，后端 `127.0.0.1:2024` |

AgentSeek 的 `create` 生成项目。之后，`info` 查看项目、`task` 执行准备任务、`doctor` 检查环境、`dev` 启动服务。这四个命令读取 [生命周期配置](../../.agentseek/lifecycle.toml)。模板已启用 `TodoListMiddleware`，它将待办写入图状态，再由前端渲染进度。[课程准备篇（上）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre01-agentseek-create/) · [模板快照](https://github.com/agentseek-ai/agentseek-templates/tree/7149bf2da837533cec9c738de64a09f90984f76a/templates/deepagents/research)

## 1. 安装依赖

准备 Python 3.12 或 3.13、uv、Node.js 和 npm。课程用 `agentseek create deepagents/research --checkout main --no-input` 从模板生成项目。本次用 Git 获取并检出上表的模板提交，再用 `agentseek create /绝对路径/agentseek-templates/templates/deepagents/research --no-input` 从本地路径生成。检出本仓库即可复用生成结果。

在项目根目录执行以下命令。若尚未安装 AgentSeek，可先运行 `uv tool install 'agentseek==0.1.6'`。

```sh
export PATH="$HOME/.local/bin:$PATH"
agentseek version
agentseek info
agentseek task --list
agentseek task sync
agentseek task frontend
test -f .env || cp .env.example .env
test -f frontend/.env || cp frontend/.env.example frontend/.env
```

`sync` 使用 `uv sync --frozen`，以仓库中的 [Python 锁文件](../../uv.lock) 安装。`frontend` 安装前端依赖，并使用 [前端锁文件](../../frontend/package-lock.json)。

安装课程使用的 Codex 项目技能后，核对两个入口。`langchain-dev-guide` 用于排查模型与框架配置，`langsmith-trace` 用于分析调用。Deep Agents 运行时通过 `create_deep_agent(skills=[...])` 加载自己的技能。[课程准备篇（下）](https://datawhalechina.github.io/deepagents-in-action/chapters/pre02-agentseek-skills/)

```sh
npx skills add ob-labs/agentseek --skill langchain-dev-guide --skill langsmith-trace --agent codex --yes
npx skills list
```

## 2. 配置模型、搜索和追踪

在根目录的 `.env` 配置下表各项，保留模板的 SeekDB 默认配置。前端的 `.env` 只配置浏览器访问的后端地址和 Vite 端口。真实密钥只保存在本地根目录的 `.env`。

| 配置项 | 用法 |
| --- | --- |
| `AGENTSEEK_MODEL_PROVIDER=openai` | 选择 LangChain 的 `ChatOpenAI` 适配器。 |
| `AGENTSEEK_MODEL` | 当前模板预填 `deepseek-ai/DeepSeek-V3.2`。教程早期实测用 `zai-org/GLM-5.2`。两者是不同模型，选用时核对账号可用的模型 ID 和工具调用能力。 |
| `OPENAI_API_BASE` | 决定请求发到哪个平台。硅基流动中国站用 `https://api.siliconflow.cn/v1`，国际站用 `https://api.siliconflow.com/v1`。使用官方 OpenAI 端点时可清空示例中的硅基流动地址。 |
| `OPENAI_API_KEY` | `ChatOpenAI` 从这个变量读取模型凭证。请求实际发往硅基流动时，这里填硅基流动密钥。 |
| `TAVILY_API_KEY` | 供 `tavily_search` 调用真实搜索。 |
| `LANGSMITH_TRACING=true` | 启用追踪。设置 `LANGSMITH_API_KEY` 和 `LANGSMITH_PROJECT=deepagents-course`，并按工作区区域配置 `LANGSMITH_ENDPOINT`。默认美国端点是 `https://api.smith.langchain.com`。 |

换模型后用一次短研究验证流式响应和工具调用。标准工具调用由兼容接口传递，`reasoning_content` 等供应商扩展字段要按实际适配器确认。模板通过 `AGENTSEEK_PARALLEL_TOOL_CALLS=false` 请求串行工具调用。[模型接入技能](../../.agents/skills/langchain-dev-guide/reference/model-integration.md)

## 3. 启动并验证

```sh
agentseek doctor
agentseek dev --dry-run
agentseek dev
```

保持服务终端运行，在另一个终端进入同一项目目录执行 `agentseek doctor --live`。静态检查确认工具、文件、依赖目录和必需变量。实时检查探测后端 `/health` 和 Vite 首页，确认两个服务可以访问。

打开 [本地研究助手](http://127.0.0.1:5174/)，提交下面的研究指令。检查待办面板、搜索来源和最终 Markdown 中可打开的引用。

> 研究 LangGraph 1.0 相比 0.x 新增了什么。先写简短计划，最多搜索三次官方资料，最后用 Markdown 总结并附上来源链接。

本机的 `doctor` 和 `doctor --live` 均通过。后端 `agentseek task course-check` 通过 6 项测试，覆盖嵌入式 SeekDB 和计划的 SSE 更新。`npm --prefix frontend run build` 构建成功。整理笔记时重新运行 `npm --prefix frontend test`，11 项测试全部通过，包含验收会话的双语展示。

硅基流动国际站的短探针返回 HTTP 200，完整研究请求返回 HTTP 402。验收时临时使用获授权的 OpenAI `gpt-4.1-mini`。该次运行生成四项计划，完成三次真实搜索，报告带三条来源链接，后端状态为 `success`。服务重启后可重新打开报告。计划界面仍显示 3/4，末项停在进行中。官方发布说明可核对核心图 API 的稳定性及 `create_react_agent` 弃用，报告关于 0.x 的概括需要结合具体版本核查。[LangGraph 1.0 发布说明](https://docs.langchain.com/oss/python/releases/langgraph-v1)

## 4. 排障与恢复

| 现象 | 当时的定位与处理 |
| --- | --- |
| 模板目录拉取失败 | 用 `git ls-remote https://github.com/agentseek-ai/agentseek-templates.git HEAD` 单独检查 GitHub。Git 可用时，检出指定提交后走本地模板路径。 |
| Python 依赖下载反复超时 | 本次临时将下载地址切换到阿里云镜像，沿用锁定的版本和校验值。安装后恢复原始 `uv.lock`，并逐字节核对。 |
| 本地端口有监听，探测仍超时 | 用 `curl --noproxy '*' http://127.0.0.1:2024/health` 检查直连。代理可能接管发往 `2024`、`5174` 或本地 Ollama `11434` 的请求。把 `127.0.0.1,localhost` 追加到代理绕过规则。 |
| 静态和实时检查通过，研究请求报 HTTP 402 | 在相同模型和端点下分别核对简单请求和真实工具调用。硅基流动这次返回余额不足，短请求的 HTTP 200 只确认该次请求成功。 |
| LangSmith 中找不到 Trace | 检查是否有重复的 `LANGSMITH_*` 配置，核对追踪开关、项目、工作区区域和密钥。启动进程后重新提交一次研究请求，再按时间和输入查找。 |

[课程排障笔记](https://datawhalechina.github.io/deepagents-in-action/chapters/pre03-task1-faq/)

验收后，开发运行切换到 Ollama 的 `qwen3.5:4b`。本机短研究完成两项待办，执行一次 Tavily 搜索并返回带链接的 Markdown。它引用了 Alpha 公告，正式发布日期应以 1.0.0 发布页为准。[正式版发布页](https://github.com/langchain-ai/langgraph/releases/tag/1.0.0)

首次使用 Ollama 时，启动 `ollama serve` 后另开终端执行 `ollama pull qwen3.5:4b`。确认 Ollama 已启动，再在项目根目录运行下面的命令。四个模型变量只对本次启动生效，Tavily 与 LangSmith 继续读取本地配置。`ollama` 是本机兼容客户端的占位值。[Ollama 兼容接口](https://docs.ollama.com/api/openai-compatibility)

```sh
export PATH="$HOME/.local/bin:$PATH"
export NO_PROXY="${NO_PROXY:+$NO_PROXY,}127.0.0.1,localhost"
export no_proxy="${no_proxy:+$no_proxy,}127.0.0.1,localhost"
AGENTSEEK_MODEL_PROVIDER=openai AGENTSEEK_MODEL=qwen3.5:4b \
  OPENAI_API_BASE=http://127.0.0.1:11434/v1 OPENAI_API_KEY=ollama \
  agentseek dev
```

## 5. 用 LangSmith 找瓶颈

按官方文档安装独立的 LangSmith CLI。在本地终端加载项目配置，确认能看到追踪项目。应用的图 ID 是 `research`，本次根运行在 LangSmith 内显示为 `LangGraph`，按研究指令和时间选中已完成的运行。[LangSmith CLI 官方文档](https://docs.langchain.com/langsmith/langsmith-cli)

```sh
set -a
source .env
set +a
langsmith project list
langsmith trace list --project deepagents-course --include-metadata --limit 5
```

将选中的 ID 设为 `TRACE_ID`，将要检查的具体模型或工具调用 ID 设为 `RUN_ID`。若运行归入 `default`，将命令里的项目名换成 `default`。

```sh
langsmith trace get "$TRACE_ID" --project deepagents-course --include-metadata
langsmith run list --trace-ids "$TRACE_ID" --project deepagents-course --run-type llm --include-metadata --limit 100
langsmith run list --trace-ids "$TRACE_ID" --project deepagents-course --run-type tool --include-metadata --limit 100
langsmith run get "$RUN_ID" --include-io --include-metadata
```

本次根运行耗时 **79.2 秒**，共 **128 个 Run**，其中 14 次实际模型调用、3 次 Tavily 搜索，记录到 0 个错误。子 Agent 的 `task` 包装耗时 50.8 秒，包含了下层调用。按类型筛选后，最慢的实际调用如下。

| 实际调用 | 耗时 | 脱敏记录 |
| --- | ---: | --- |
| `ChatOpenAI` | 7.45 秒 | 可读取模型输入与生成结果，错误为空。 |
| `tavily_search` | 8.30 秒 | 查询 LangGraph 1.0 官方发布说明，错误为空。该次序列化输出约 71.7 万字符。 |

该 Trace 的 Token 用量和费用字段为空。本次流式请求未启用 usage 返回，无法根据这条记录核算成本。需要计量时，在支持 `stream_options.include_usage` 的接口上开启用量返回，再按实际模型 Run 统计，避免重复累加包装层数据。

报告和引用确认了功能路径。评估运行质量还要看耗时、错误、用量和来源质量。整页正文进入历史后，后续模型可能反复读取同样的内容。遇到高 Token 用量，先核对叶子模型 Run 的输入里有多少重复正文，再比较缩短正文或减少搜索后的结果。

## 下次复跑

按 `doctor` → `dev` → `doctor --live` 的顺序核对服务。在浏览器用一个短问题确认计划、真实来源和报告，再在 LangSmith 核对实际调用。跑完记录所用模型、搜索次数、计划状态和可获得的用量。

[学习心得](learning-reflections.md) · [课程反馈](course-feedback.md)
