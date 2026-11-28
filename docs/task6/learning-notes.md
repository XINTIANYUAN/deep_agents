# Task6 学习笔记：异步子 Agent 与 Skills

## 学习范围与实验设计

阅读[第 6 章](https://datawhalechina.github.io/deepagents-in-action/chapters/ch06-async-subagents/)与[第 7 章](https://datawhalechina.github.io/deepagents-in-action/chapters/ch07-skills/)，分别验证后台任务生命周期和 Skill 的渐进式披露。章节示例以 0.7.10 核对，本项目继续使用 Deep Agents 0.7.8，以安装版本源码为准：

- [异步中间件源码](https://github.com/langchain-ai/deepagents/blob/deepagents%3D%3D0.7.8/libs/deepagents/deepagents/middleware/async_subagents.py)
- [Skills 中间件源码](https://github.com/langchain-ai/deepagents/blob/deepagents%3D%3D0.7.8/libs/deepagents/deepagents/middleware/skills.py)

模型为本地 Ollama `qwen3.5:4b`。主 Agent 由真实模型选择并调用异步工具；worker 使用教程同类的确定性慢图，故意等待后回显指令，不代表完成真实网络调研。服务在 `127.0.0.1:2026`，六个 worker slots；其虚拟环境、checkpoint、日志和实验文件统一保存在被 Git 忽略的 `.task6-runs/`。Task1 仍使用 2024/5174。

## 环境准备与复现

在仓库根目录执行。需要已运行 Ollama 且已安装 `qwen3.5:4b`；LangSmith 凭据沿用本地 `.env`，不要提交该文件。

```sh
export PATH="$HOME/.local/bin:$PATH"
export NO_PROXY=127.0.0.1,localhost
export no_proxy="$NO_PROXY"
uv venv .task6-runs/venv --python .venv/bin/python
uv pip install --python .task6-runs/venv/bin/python -r examples/task6/requirements.lock.txt
.task6-runs/venv/bin/python examples/task6/start_server.py
```

下载遇到连接问题时，可在 `uv pip install` 中加入 `--index-url https://pypi.tuna.tsinghua.edu.cn/simple`。本次用此镜像完成安装。锁定文件记录完整实测依赖，主要版本是 CLI 0.4.44、API 0.18.0、in-memory runtime 0.38.6、SDK 0.4.6、LangGraph 1.2.14、LangSmith 0.14.4。它们安装在独立环境，根目录 `pyproject.toml`、`uv.lock` 没有变动。

另开终端运行生命周期实验，等待正常退出：

```sh
export NO_PROXY=127.0.0.1,localhost
export no_proxy="$NO_PROXY"
.task6-runs/venv/bin/python examples/task6/run_lifecycle.py \
  --output-dir .task6-runs/my-lifecycle
```

然后运行 Skills。每次选一个尚未使用的输出目录，避免覆盖已有实验：

```sh
uv run --frozen --env-file .env python examples/task6/skills_demo.py \
  --lifecycle .task6-runs/my-lifecycle/results.json \
  --output-dir .task6-runs/my-skills
```

需要上传 Skills Trace 时，在该命令前设置 `LANGSMITH_TRACING=true`。异步服务启动器已开启项目 `deepagents-task6` 的追踪；不要把追踪系统误当作运行后台任务的服务。实验结束可在服务终端按 Ctrl+C，仅停止 Task6。

## 异步生命周期怎么验证

完整顺序是：启动 A → 后台运行期间无关问答 → 更新 A → 启动 B → 列出并行任务 → 查询 A → 取消 B → 取消 A → 更新 A 续跑 → 查询续跑结果。

每轮都通过 SDK 调用同一个 supervisor thread，模型实际执行 `start_async_task`、`update_async_task`、`list_async_tasks`、`check_async_task`、`cancel_async_task`。驱动程序核对本轮工具名称，再直接查询服务端，保存实际 run 状态。240 秒的演示等待确保有足够时间观察并行和取消；续跑请求把等待改为 1 秒。

任务 ID 就是子线程 ID，`async_tasks` 独立保存任务元数据。update 使用 `multitask_strategy="interrupt"`，原 thread 不变，run ID 改变。取消后的续跑再次 update，保留原任务与追加指令的消息历史，重新执行慢节点。

## Skills 怎么验证

[lifecycle-review/SKILL.md](../../examples/task6/skills/lifecycle-review/SKILL.md) 的 description 明确匹配生命周期验收；正文要求读取参考规则、读取输入、写中文报告、读回核查。另一个发票技能用于观察无关正文是否会被读取。

演示用 `FilesystemBackend(root_dir=workspace, virtual_mode=True)`，传入 `skills=["/skills/"]`；配置路径指向包含 Skill 子目录的父目录。输入和 Skill 目录禁止 Agent 写入，产物写入 `/outputs/acceptance.md`。被动观测中间件只记录请求特征，不修改提示词、消息或工具结果。

首轮检查名称、description 是否进入系统提示词，以及正文专有标记是否缺席。后续检查模型是否调用 `read_file` 打开 SKILL.md，再读取 references，并按正文生成与读回报告。正文和参考规则应通过工具消息进入后续上下文。此实验能验证可观察的选择行为，无法直接证明模型内部的匹配理由。

## 操作中的踩坑

1. 官方文件站的大文件连接超时，改镜像完成依赖下载。保留版本清单，避免下次无约束安装导致结果变化。
2. CLI 的 `inmem` extra 与最新 API 的本地运行依赖没有完整配套：API 0.19.1 启动报缺少 `langgraph-api[inmem]`，镜像中又没有其 core-bin 依赖。本次固定到 API 0.18.0 与 runtime 0.38.6 后启动成功。
3. 不能在 Task1 的目录直接复用服务状态文件。启动器生成独立配置，在 `.task6-runs/server/` 工作目录运行，并使用新端口。
4. 慢图固定等待 8 秒，可能比本地模型两次生成还短；本次延长等待，并用真实 run 状态证明启动返回与后台执行重叠。
5. `cancel_async_task` 写入本地 cancelled 不等于服务端已停止。实验另外查询具体 run；服务端以 interrupted 表示本次取消。
6. 最新官方文档可能描述 0.7.8 不具备的能力。配置和行为按固定版本源码验证；本次不引入新版本的恢复或自动通知接口。
7. 首轮续跑时，模型把旧的 `delay_seconds=240` 放在括号内，又追加 `delay_seconds=1`。worker 最初取第一个匹配值，导致续跑继续等待；改为使用最后一个显式指令。验收也要求最后一条消息确为助手输出，防止只看到用户输入里的标记就误判完成。修正后重新运行完整生命周期。
8. 第一份 Skills 报告虽然完成加载与写回，却自行添加了 `2024-01-XX` 占位日期，并把任务 ID 与 run ID 的描述写得含糊。补充 Skill 的事实边界与精确措辞后重新运行，日期问题消除。重新生成稿又把实际 10 项检查写成了 12 项；公开验收稿仅修正这个数量，并标明复核；原始输出留在本地，哈希列入实验结果。加载流程通过与生成文本完全准确，仍然要分别检查。

## 实测证据入口

2026-11-28 最终实测：启动 A 返回用时 2.812 秒，随后无关问答用时 1.482 秒，两次返回时子任务仍为 running。主线程 10 轮对话包含 19 次模型、9 次异步工具调用；生命周期 10 项检查全部通过。取消后服务端为 interrupted，续跑在同一子线程保留 3 条用户指令，新 run 最终 success。

Skills 使用 6 次模型调用、4 次 read_file 和 1 次 write_file，实际顺序为：输入 JSON → SKILL.md → references → 写报告 → 读回。首轮只见元数据，第 3 轮已见正文，第 4 轮已见参考规则；无关技能正文始终未进入工具上下文。两份最终实验均已从 LangSmith 导出完整 Trace 核对。

文件读写通过 Skills 的 FilesystemBackend 实际完成；另复用 Task3 存储实验重新运行三种 Backend：State+InMemorySaver 在同线程保留、换线程或进程不保留；Filesystem 在新进程仍可读；Store+InMemoryStore 可跨同进程线程，新进程不保留。复现命令：

```sh
LANGSMITH_TRACING=false uv run --frozen python examples/task3/filesystem_lab.py \
  --step backends --output-dir .task6-runs/backend-recheck
```

完整步骤、模型工具调用与 Skills 分层加载记录见[验收日志](acceptance-log.md)，机器可读结论见[实验结果](experiment-results.json)，模型写入的中文产物见[验收报告](acceptance-report.md)。本地原始日志保留完整 task/thread/run ID，便于在 LangSmith 串联主子运行；公开记录用 A/B 别名。

回归验证：原有 pytest 6 项通过；`agentseek doctor --live` 全部通过；Task1 历史线程仍有 3 次成功运行，原报告 SHA256 与开始前一致。Task1–Task5 的运行源码、前端与根依赖锁文件未修改。

[学习心得](learning-reflections.md) · [课程反馈](course-feedback.md)
