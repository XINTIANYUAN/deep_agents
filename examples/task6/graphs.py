"""Isolated Task6 ASGI supervisor and deliberately slow, deterministic worker."""

import asyncio
import os
import re

from deepagents import AsyncSubAgent, create_deep_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph


async def slow_worker(state: MessagesState):
    """Keep real background runs observable without paid models or fake API calls."""
    requests = [m.text for m in state["messages"] if m.type == "human"]
    latest = requests[-1]
    # A model may repeat an earlier constraint in its new message: the final
    # explicit delay directive is the current override.
    matches = re.findall(r"delay_seconds=(\d+)", latest)
    delay = min(int(matches[-1]) if matches else 120, 300)
    await asyncio.sleep(delay)
    return {"messages": [{"role": "assistant", "content": (
        f"- 本次后台等待 {delay} 秒后完成。\n"
        f"- 同一子线程保留 {len(requests)} 条用户指令。\n"
        f"- 最新约束：{latest}"
    )}]}


builder = StateGraph(MessagesState)
builder.add_node("slow_worker", slow_worker)
builder.add_edge(START, "slow_worker")
builder.add_edge("slow_worker", END)
worker = builder.compile()

model = ChatOpenAI(
    model=os.getenv("TASK6_MODEL", "qwen3.5:4b"),
    base_url=os.getenv("TASK6_BASE_URL", "http://127.0.0.1:11434/v1"),
    api_key=os.getenv("TASK6_API_KEY", "ollama"),
    temperature=0,
    timeout=120,
    max_retries=1,
)
supervisor = create_deep_agent(
    model=model,
    name="task6_supervisor",
    system_prompt=(
        "你是异步任务调度台。只执行用户本轮要求的一项操作。"
        "启动任务用 start_async_task，追加要求用 update_async_task，"
        "查询用 check_async_task，任务总览用 list_async_tasks，取消用 cancel_async_task。"
        "原样保留完整 task_id。传给 worker 的描述须保留 delay_seconds 数值。"
        "每次工具返回后立即用一句中文回答用户并结束本轮；禁止自行轮询或自动追加工具。"
        "无关闲聊直接回答，不调用工具。暂停后的续跑也使用 update_async_task，"
        "它会在原子线程创建新 run，不是从暂停的 Python 协程恢复。"
    ),
    subagents=[AsyncSubAgent(
        name="worker",
        description="后台生命周期演示；故意等待指定秒数后回显最新指令，不进行真实网络研究。",
        graph_id="task6_worker",
    )],
)
