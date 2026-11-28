---
name: lifecycle-review
description: 当用户要求整理异步子 Agent 的生命周期实验、核对取消与续跑证据、撰写验收说明时使用。读取原始记录，区分服务端状态与缓存状态。
---

# 异步生命周期验收

正文识别标记：TASK6_SKILL_BODY_LOADED

1. 用 read_file 完整读取 `/skills/lifecycle-review/references/review-rules.md`。
2. 读取用户指定的 JSON 原始记录。不得根据聊天记录猜测成功状态。
3. 按规则给出判断。将中文报告写入 `/outputs/acceptance.md`，二级标题必须为「验证结论」「证据摘要」「边界与限制」。
4. 在报告里原样引用规则的核验码，说明追加指令与恢复的区别，并报告实际证据的布尔值。
5. 用 read_file 读回报告，确认文件已生成。最终只简要说明位置。
6. 只使用输入和参考规则中的事实，不添加日期、占位符或未提供的实验信息。解释 update 时必须明确「task_id 不变、run_id 改变」，并说明被 update 打断的是旧 run。
