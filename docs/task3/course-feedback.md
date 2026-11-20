# Task3 课程反馈

第 3 章把文件工具、上下文卸载和 Backend 选择连接起来，正文也补充了 v0.7 的覆盖写入、分页、截断、Backend 实例和命名空间约定。这些说明能帮助从 Task2 单脚本继续动手。以下建议来自本次文件与存储实验。 [第 3 章](https://datawhalechina.github.io/deepagents-in-action/chapters/ch03-virtual-filesystem/)

1. **配一段能够稳定触发默认卸载的完整代码。** 建议用公开的合成文本作为工具结果，在中间放一个只靠首尾预览看不到的标记，让模型分页读回。本次 285,492 字符的结果足以触发默认阈值，也能通过全文相等检查验证资料保存成功。 [本次可运行实验](../../examples/task3/filesystem_lab.py)

2. **给 Trace 检查标出两个位置。** 先看原工具节点的输出，再看下一次模型节点 Input 中对应的工具消息。建议教材并排展示这两处，并标清字符计数、估算 token 阈值、实际 usage 的含义。这样学员能根据真实输入判断卸载效果。 [本次 Trace 截图](langsmith-offload.jpg)

3. **用同一份笔记完成 Backend 对照。** 建议沿用相同路径和正文，统一检查同线程、新线程、重建图和新进程四种情况。正文已说明 `InMemoryStore` 的生命周期，配上自动启动新进程的验收步骤，可以直接看到跨线程共享与进程重启恢复的边界。 [本次对比表](learning-notes.md#实验三--backend-生命周期对比)

4. **在本地示例中给出独立文件根目录。** 用专门的实验目录配合 `virtual_mode=True`，再显示虚拟路径到本机文件的对应关系，读者能立即核对落盘位置。Store 示例也可以紧邻给出本地 namespace，方便和部署时的用户身份配置对应起来。

本次已读取章节正文并完成代码实验。章节底部两个 B 站视频链接在自动读取时返回 HTTP 412，视频内容未核验。学习与实验记录依据章节当前说明、锁定版本源码及实际运行结果整理。 [Lec 04 视频入口](https://www.bilibili.com/video/BV1V4daBnEtP/) · [Lec 05 视频入口](https://www.bilibili.com/video/BV1zAouBhENj/)
