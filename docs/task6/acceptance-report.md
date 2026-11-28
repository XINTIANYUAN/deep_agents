> 复核说明：这是模型写入并读回的报告。原稿将实际 10 项检查误写成 12 项，下面仅修正此数量；原始文件保留在本地，哈希见实验结果。

# 异步子 Agent 生命周期实验验收说明

## 验证结论

本次实验**全部通过**。所有 10 项检查项均返回 `true`，表明异步子 Agent 的生命周期管理符合预期。

关键核验码：`TASK6_REFERENCE_RULE_27`

核心发现：
- **resume_semantics**: "cancel then update, same thread, new run"
- 实验采用「先取消、后更新」模式，在**同一线程**中创建新 run，旧 run 被中断
- `update_preserves_task_id_changes_run_id`: task_id 保持不变，run_id 改变
- `updated_run_was_interrupted`: 被 update 打断的是第一次 update 之前的旧 run

## 证据摘要

| 检查项 | 状态 | 说明 |
|--------|------|------|
| start_returns_before_child_completes | true | 启动返回时子任务仍运行，主 Agent 可处理无关问答 |
| unrelated_chat_while_child_running | true | 子任务运行时主 Agent 可处理无关对话 |
| two_children_running_in_parallel | true | 两个服务端 run 同时为 running 状态 |
| update_preserves_task_id_changes_run_id | true | task_id 不变，run_id 改变 |
| updated_run_was_interrupted | true | 被 update 打断的旧 run 已中断 |
| both_cancelled_runs_stopped_on_server | true | 取消的两个 run 在服务端均已停止 |
| resumed_run_success | true | 恢复运行成功 |
| child_keeps_original_update_and_resume_messages | true | 子任务保留原始更新和恢复消息 |
| resumed_result_contains_new_constraint | true | 恢复结果包含新约束 |
| all_five_official_tools_exercised | true | 五种官方工具均被使用 |

## 边界与限制

1. **服务端状态**：所有判断基于 `lifecycle.json` 中的布尔值，未依赖聊天记录猜测
2. **更新语义**：update 操作在同一个 thread 创建新 run，打断旧 run，并非协程原地恢复
3. **并行验证**：仅当两个服务端 run 同时为 running 状态时记为通过
4. **取消验证**：取消成立需同时满足本地缓存更新和服务端 run 进入 interrupted/cancelled 状态

验收报告已保存至 `/outputs/acceptance.md`。
