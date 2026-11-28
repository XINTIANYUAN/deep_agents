# 验收规则

核验码：TASK6_REFERENCE_RULE_27

- 启动返回时子任务仍运行，且主 Agent 可以处理无关问答，才证明本次未等待子任务完成。
- 两个服务端 run 同时为 running，才把并行记为通过。
- 取消工具会更新本地缓存；取消成立还要看服务端对应 run 已进入 interrupted 或 cancelled。
- update 会在同一个 thread 创建新的 run，并打断旧 run。本实验的「续跑」指取消后再次 update；保留会话历史，不代表原 Python 协程原地恢复。
- `update_preserves_task_id_changes_run_id` 对应「task_id 不变、run_id 改变」；`updated_run_was_interrupted` 在本实验中检查第一次 update 之前的旧 run 已中断。
- 按检查项的真实布尔值报告；出现 false 就写待解决，禁止把「模型说完成」作为通过依据。
