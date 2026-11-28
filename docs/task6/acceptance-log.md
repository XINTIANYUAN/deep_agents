# Task6 验收日志

实测日期：2026-11-28T21:51:04.788061+08:00。以下从本地原始记录与 LangSmith Trace 抽取，任务标识替换为 A/B 别名；完整 ID 留在 `.task6-runs/`。

## 异步生命周期

主 Agent 使用本地真实模型，worker 为教程同类慢图。10 轮对话共 19 次模型、9 次工具调用；五个官方工具均已实际执行。

### start_A

耗时 2.812 秒；服务端状态：`{"任务A": "running"}`。

用户：只启动一个 worker 后台任务：A，演示异步生命周期，delay_seconds=240。不要查询。

调用：
```json
[
  {
    "name": "start_async_task",
    "args": {
      "description": "A，演示异步生命周期，delay_seconds=240",
      "subagent_type": "worker"
    }
  }
]
```

工具返回：
```text
Launched async subagent. task_id: 任务A
```

主 Agent 回复：任务 A 已成功启动，task_id: 任务A，延迟设置为 240 秒。

### chat_while_running

耗时 1.482 秒；服务端状态：`{"任务A": "running"}`。

用户：先不要操作后台任务。只回答：3 加 4 等于多少？

主 Agent 回复：3 加 4 等于 **7**。

### update_A

耗时 3.415 秒；服务端状态：`{"任务A": "running"}`。

用户：仅给 任务A 追加指令：重点验证追加约束被保留，delay_seconds=240。

调用：
```json
[
  {
    "name": "update_async_task",
    "args": {
      "message": "重点验证追加约束被保留，delay_seconds=240",
      "subagent_type": "worker",
      "task_id": "任务A"
    }
  }
]
```

工具返回：
```text
Updated async subagent. task_id: 任务A
```

主 Agent 回复：指令已追加到任务 A（task_id: 任务A），重点验证追加约束被保留，delay_seconds=240。

### start_B

耗时 3.183 秒；服务端状态：`{"任务A": "running", "任务B": "running"}`。

用户：只启动第二个 worker 后台任务：B，测试并行与取消，delay_seconds=240。

调用：
```json
[
  {
    "name": "start_async_task",
    "args": {
      "description": "B，测试并行与取消，delay_seconds=240",
      "subagent_type": "worker"
    }
  }
]
```

工具返回：
```text
Launched async subagent. task_id: 任务B
```

主 Agent 回复：任务 B 已成功启动，task_id: 任务B，延迟设置为 240 秒，用于测试并行与取消功能。

### list_parallel

耗时 2.855 秒；服务端状态：`{"任务A": "running", "任务B": "running"}`。

用户：仅查询所有异步任务的最新状态总览。

调用：
```json
[
  {
    "name": "list_async_tasks",
    "args": {
      "status_filter": "all"
    }
  }
]
```

工具返回：
```text
2 tracked task(s):
- task_id: 任务A  agent: worker  status: running
- task_id: 任务B  agent: worker  status: running
```

主 Agent 回复：当前所有异步任务状态总览：

- **任务 A** (task_id: 任务A) - 状态：**running**
- **任务 B** (task_id: 任务B) - 状态：**running**

两个任务均处于运行中，延迟设置均为 240 秒。

### check_A

耗时 3.551 秒；服务端状态：`{"任务A": "running", "任务B": "running"}`。

用户：仅查询任务 任务A 的最新状态。

调用：
```json
[
  {
    "name": "check_async_task",
    "args": {
      "task_id": "任务A"
    }
  }
]
```

工具返回：
```text
{"status": "running", "thread_id": "任务A"}
```

主 Agent 回复：任务 任务A 的最新状态：**running**（运行中），线程 ID：任务A。

### cancel_B

耗时 3.061 秒；服务端状态：`{"任务A": "running", "任务B": "interrupted"}`。

用户：仅取消任务 任务B。

调用：
```json
[
  {
    "name": "cancel_async_task",
    "args": {
      "task_id": "任务B"
    }
  }
]
```

工具返回：
```text
Cancelled async subagent task: 任务B
```

主 Agent 回复：任务 任务B（任务 B）已成功取消。

### cancel_A

耗时 3.034 秒；服务端状态：`{"任务A": "interrupted", "任务B": "interrupted"}`。

用户：仅取消任务 任务A，之后会用更新指令继续。

调用：
```json
[
  {
    "name": "cancel_async_task",
    "args": {
      "task_id": "任务A"
    }
  }
]
```

工具返回：
```text
Cancelled async subagent task: 任务A
```

主 Agent 回复：任务 任务A（任务 A）已成功取消。

后续如需继续，请使用 `update_async_task` 指令来恢复或更新该任务。

### resume_A_by_update

耗时 4.362 秒；服务端状态：`{"任务A": "success", "任务B": "interrupted"}`。

用户：仅更新任务 任务A 继续处理：保留前面的追加约束，新增 RESUMED_CONSTRAINT，delay_seconds=1。

调用：
```json
[
  {
    "name": "update_async_task",
    "args": {
      "message": "保留前面的追加约束（重点验证追加约束被保留，delay_seconds=240），新增 RESUMED_CONSTRAINT，delay_seconds=1",
      "subagent_type": "worker",
      "task_id": "任务A"
    }
  }
]
```

工具返回：
```text
Updated async subagent. task_id: 任务A
```

主 Agent 回复：任务 任务A 已成功更新：

- **保留约束**：重点验证追加约束被保留，delay_seconds=240
- **新增约束**：RESUMED_CONSTRAINT
- **延迟设置**：delay_seconds=1

任务已恢复处理状态。

### check_resumed_A

耗时 5.625 秒；服务端状态：`{"任务A": "success", "任务B": "interrupted"}`。

用户：仅查询任务 任务A 的最新状态与结果。

调用：
```json
[
  {
    "name": "check_async_task",
    "args": {
      "task_id": "任务A"
    }
  }
]
```

工具返回：
```text
{"status": "success", "thread_id": "任务A", "result": "- \u672c\u6b21\u540e\u53f0\u7b49\u5f85 1 \u79d2\u540e\u5b8c\u6210\u3002\n- \u540c\u4e00\u5b50\u7ebf\u7a0b\u4fdd\u7559 3 \u6761\u7528\u6237\u6307\u4ee4\u3002\n- \u6700\u65b0\u7ea6\u675f\uff1a\u4fdd\u7559\u524d\u9762\u7684\u8ffd\u52a0\u7ea6\u675f\uff08\u91cd\u70b9\u9a8c\u8bc1\u8ffd\u52a0\u7ea6\u675f\u88ab\u4fdd\u7559\uff0cdelay_seconds=240\uff09\uff0c\u65b0\u589e RESUMED_CONSTRAINT\uff0cdelay_seconds=1"}
```

主 Agent 回复：任务 任务A 的最新状态与结果：

**状态**：success（成功）
**线程 ID**：任务A

**执行结果**：
- ✅ 本次异步等待 1 秒后完成
- ✅ 同一子线程保留 3 条用户指令
- ✅ 最新约束已正确应用：
  - 保留前面的追加约束（重点验证追加约束被保留，delay_seconds=240）
  - 新增 RESUMED_CONSTRAINT，delay_seconds=1

任务已成功完成，所有约束均被正确保留和应用。

### 续跑子任务的真实输出

```text
- 本次后台等待 1 秒后完成。
- 同一子线程保留 3 条用户指令。
- 最新约束：保留前面的追加约束（重点验证追加约束被保留，delay_seconds=240），新增 RESUMED_CONSTRAINT，delay_seconds=1
```

检查：`{"start_returns_before_child_completes": true, "unrelated_chat_while_child_running": true, "two_children_running_in_parallel": true, "update_preserves_task_id_changes_run_id": true, "updated_run_was_interrupted": true, "both_cancelled_runs_stopped_on_server": true, "resumed_run_success": true, "child_keeps_original_update_and_resume_messages": true, "resumed_result_contains_new_constraint": true, "all_five_official_tools_exercised": true}`。

## Skills 渐进式披露

用户只给出生命周期验收需求与输入路径，没有指定技能名称。两条候选元数据是 lifecycle-review 和 invoice-summary。

| 模型轮次 | 上下文已有 Skill 正文 | 已有参考规则 | 已有无关技能正文 |
| --- | --- | --- | --- |
| 1 | False | False | False |
| 2 | False | False | False |
| 3 | True | False | False |
| 4 | True | True | False |
| 5 | True | True | False |
| 6 | True | True | False |

首轮系统提示词包含名称和 description，正文标记与参考规则标记均未进入；六轮系统提示词均未提前注入正文。以下是实际工具顺序。

调用：
```json
{
  "name": "read_file",
  "args": {
    "file_path": "/inputs/lifecycle.json",
    "limit": 1000
  }
}
```

工具返回：
```text
 1  {
 2    "checks": {
 3      "start_returns_before_child_completes": true,
 4      "unrelated_chat_while_child_running": true,
 5      "two_children_running_in_parallel": true,
 6      "update_preserves_task_id_changes_run_id": true,
 7      "updated_run_was_interrupted": true,
 8      "both_cancelled_runs_stopped_on_server": true,
 9      "resumed_run_success": true,
10      "child_keeps_original_update_and_resume_messages": true,
11      "resumed_result_contains_new_constraint": true,
12      "all_five_official_tools_exercised": true
13    },
14    "resume_semantics": "cancel then update, same thread, new run"
15  }
```

调用：
```json
{
  "name": "read_file",
  "args": {
    "file_path": "/skills/lifecycle-review/SKILL.md",
    "limit": 1000
  }
}
```

工具返回：
```text
 1  ---
 2  name: lifecycle-review
 3  description: 当用户要求整理异步子 Agent 的生命周期实验、核对取消与续跑证据、撰写验收说明时使用。读取原始记录，区分服务端状态与缓存状态。
 4  ---
 5
 6  # 异步生命周期验收
 7
 8  正文识别标记：TASK6_SKILL_BODY_LOADED
 9
10  1. 用 read_file 完整读取 `/skills/lifecycle-review/references/review-rules.md`。
11  2. 读取用户指定的 JSON 原始记录。不得根据聊天记录猜测成功状态。
12  3. 按规则给出判断。将中文报告写入 `/outputs/acceptance.md`，二级标题必须为「验证结论」「证据摘要」「边界与限制」。
13  4. 在报告里原样引用规则的核验码，说明追加指令与恢复的区别，并报告实际证据的布尔值。
14  5. 用 read_file 读回报告，确认文件已生成。最终只简要说明位置。
15  6. 只使用输入和参考规则中的事实，不添加日期、占位符或未提供的实验信息。解释 update 时必须明确「task_id 不变、run_id 改变」，并说明被 update 打断的是旧 run。
```

调用：
```json
{
  "name": "read_file",
  "args": {
    "file_path": "/skills/lifecycle-review/references/review-rules.md",
    "limit": 1000
  }
}
```

工具返回：
```text
 1  # 验收规则
 2
 3  核验码：TASK6_REFERENCE_RULE_27
 4
 5  - 启动返回时子任务仍运行，且主 Agent 可以处理无关问答，才证明本次未等待子任务完成。
 6  - 两个服务端 run 同时为 running，才把并行记为通过。
 7  - 取消工具会更新本地缓存；取消成立还要看服务端对应 run 已进入 interrupted 或 cancelled。
 8  - update 会在同一个 thread 创建新的 run，并打断旧 run。本实验的「续跑」指取消后再次 update；保留会话历史，不代表原 Python 协程原地恢复。
 9  - `update_preserves_task_id_changes_run_id` 对应「task_id 不变、run_id 改变」；`updated_run_was_interrupted` 在本实验中检查第一次 update 之前的旧 run 已中断。
10  - 按检查项的真实布尔值报告；出现 false 就写待解决，禁止把「模型说完成」作为通过依据。
```

调用：
```json
{
  "name": "write_file",
  "args": {
    "file_path": "/outputs/acceptance.md",
    "content": "[写入正文 1360 字符；原稿数量错误见复核说明]"
  }
}
```

工具返回：
```text
Updated file /outputs/acceptance.md
```

调用：
```json
{
  "name": "read_file",
  "args": {
    "file_path": "/outputs/acceptance.md",
    "limit": 100
  }
}
```

工具返回：
```text
 1  # 异步子 Agent 生命周期实验验收说明
 2
 3  ## 验证结论
 4
 5  本次实验**全部通过**。所有 12 项检查项均返回 `true`，表明异步子 Agent 的生命周期管理符合预期。
 6
 7  关键核验码：`TASK6_REFERENCE_RULE_27`
 8
 9  核心发现：
10  - **resume_semantics**: "cancel then update, same thread, new run"
11  - 实验采用「先取消、后更新」模式，在**同一线程**中创建新 run，旧 run 被中断
12  - `update_preserves_task_id_changes_run_id`: task_id 保持不变，run_id 改变
13  - `updated_run_was_interrupted`: 被 update 打断的是第一次 update 之前的旧 run
14
15  ## 证据摘要
16
17  | 检查项 | 状态 | 说明 |
18  |--------|------|------|
19  | start_returns_before_child_completes | true | 启动返回时子任务仍运行，主 Agent 可处理无关问答 |
20  | unrelated_chat_while_child_running | true | 子任务运行时主 Agent 可处理无关对话 |
21  | two_children_running_in_parallel | true | 两个服务端 run 同时为 running 状态 |
22  | update_preserves_task_id_changes_run_id | true | task_id 不变，run_id 改变 |
23  | updated_run_was_interrupted | true | 被 update 打断的旧 run 已中断 |
24  | both_cancelled_runs_stopped_on_server | true | 取消的两个 run 在服务端均已停止 |
25  | resumed_run_success | true | 恢复运行成功 |
26  | child_keeps_original_update_and_resume_messages | true | 子任务保留原始更新和恢复消息 |
27  | resumed_result_contains_new_constraint | true | 恢复结果包含新约束 |
28  | all_five_official_tools_exercised | true | 五种官方工具均被使用 |
29
30  ## 边界与限制
31
32  1. **服务端状态**：所有判断基于 `lifecycle.json` 中的布尔值，未依赖聊天记录猜测
33  2. **更新语义**：update 操作在同一个 thread 创建新 run，打断旧 run，并非协程原地恢复
34  3. **并行验证**：仅当两个服务端 run 同时为 running 状态时记为通过
35  4. **取消验证**：取消成立需同时满足本地缓存更新和服务端 run 进入 interrupted/cancelled 状态
36
37  验收报告已保存至 `/outputs/acceptance.md`。
```

## 产物复核

最终模型原稿把检查数写为 12，实际 JSON 有 10 项。公开[验收报告](acceptance-report.md)标明了这一处人工修正；原始文件 SHA256：`2bb0d2ed91b00b6b7765ca15668cc1362b5ee4d3257ec841f63454cdbd13ac6d`。工具调用与分层披露检查通过，不据此宣称模型生成的每句话都准确。

## 后端复测

| Backend | 同线程 | 同资源另一线程 | 重建图 | 新进程 |
| --- | --- | --- | --- | --- |
| state | True | False | True | False |
| filesystem | True | True | True | True |
| store | True | True | True | False |

复用 Task3 的真实图与子进程探针；State 使用 InMemorySaver，Store 使用 InMemoryStore。Filesystem 数据位于本次独立输出目录，新进程仍可读。

所有结构化结果与云端核对项见[实验结果](experiment-results.json)。
