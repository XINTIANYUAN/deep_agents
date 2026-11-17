"""Run the Task2 model–tool loop against an OpenAI-compatible endpoint."""

import argparse
import json
import operator
import os
from typing import Literal

from deepagents import create_deep_agent
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_core.utils.uuid import uuid7
from langchain_openai import ChatOpenAI
from langsmith import tracing_context

TRACE_PROJECT = "deepagents-task2"
TRACE_NAME = "task2-model-tool-loop"
CALCULATION_PROMPT = "调用 calculate，传入 a=18.5 和 b=3.5，省略 operation，使用工具的默认运算。"
WEATHER_PROMPT = "北京今天天气怎么样？请调用 get_weather，传入 city=北京，并注明天气是演示数据。"
PROMPTS = {
    "weather": WEATHER_PROMPT,
    "calculator": CALCULATION_PROMPT,
    "both": (
        f"{WEATHER_PROMPT} 收到天气工具结果后，再{CALCULATION_PROMPT}"
        "最后用中文回答两项结果，并注明天气是演示数据。"
    ),
}


def get_weather(city: str) -> str:
    """Return simulated weather for a given city."""
    return f"It's always sunny in {city}!"


def calculate(
    a: float,
    b: float,
    operation: Literal["add", "subtract", "multiply", "divide"] = "add",
) -> float:
    """Calculate with two numbers. Omit operation for addition."""
    operations = {
        "add": operator.add,
        "subtract": operator.sub,
        "multiply": operator.mul,
        "divide": operator.truediv,
    }
    return operations[operation](a, b)


TOOLS = {
    "weather": [get_weather],
    "calculator": [calculate],
    "both": [get_weather, calculate],
}


def show_evidence(messages: list[BaseMessage], expected_tools: list[str]) -> None:
    """Print the actual calls and responses, and verify the demo's interaction."""
    calls = {}
    results = {}
    events = []
    for message in messages:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                name = call["name"]
                calls[call["id"]] = call
                events.append(("call", name))
                print(f"模型请求 {name} {json.dumps(call['args'], ensure_ascii=False)}")
        elif isinstance(message, ToolMessage) and message.tool_call_id in calls:
            call = calls[message.tool_call_id]
            name = call["name"]
            events.append(("result", name))
            results[name] = (call["args"], message.content, message.status)
            print(f"工具返回 {name} {message.content}")

    final = messages[-1]
    if isinstance(final, AIMessage) and final.text:
        print(f"\n最终回复\n{final.text}")
    else:
        raise SystemExit("验收失败：模型未生成最终回复。")

    expected_events = [
        (event, name) for name in expected_tools for event in ("call", "result")
    ]
    if events != expected_events:
        raise SystemExit("验收失败：实际工具调用或执行顺序与示例不符。")

    if "get_weather" in results:
        args, content, status = results["get_weather"]
        if args != {"city": "北京"} or content != "It's always sunny in 北京!" or status != "success":
            raise SystemExit("验收失败：未看到北京的固定天气工具结果。")
        print(f"验收通过 · 模拟天气 {content}")

    if "calculate" in results:
        args, content, status = results["calculate"]
        if args != {"a": 18.5, "b": 3.5} or content != "22.0" or status != "success":
            raise SystemExit("验收失败：未看到省略 operation 后的默认加法结果。")
        print(f"验收通过 · 省略 operation 后由工具默认执行加法，结果 {content}")


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 Task2 的天气和计算器工具示例。")
    parser.add_argument(
        "--step",
        choices=tuple(PROMPTS),
        default="both",
        help="选择天气、计算器，或依次执行两项（默认）。",
    )
    step = parser.parse_args().step

    model_name = os.environ.get("TASK2_MODEL", "qwen3.5:4b")
    model = ChatOpenAI(
        model=model_name,
        base_url=os.environ.get("TASK2_OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
        api_key=os.environ.get("TASK2_OPENAI_API_KEY", "ollama"),
        temperature=0,
        model_kwargs={"parallel_tool_calls": False},
    )
    agent = create_deep_agent(
        model=model,
        tools=TOOLS[step],
        system_prompt=(
            "You are a helpful assistant. Follow the requested tool order. "
            "Call one tool at a time and wait for its response before deciding the next action."
        ),
    )
    print(f"模型 {model_name}\n用户指令 {PROMPTS[step]}")

    tracing = os.environ.get("LANGSMITH_TRACING", "").strip().lower() == "true"
    run_id = uuid7()
    try:
        with tracing_context(enabled=tracing, project_name=TRACE_PROJECT, parent=False):
            result = agent.invoke(
                {"messages": [{"role": "user", "content": PROMPTS[step]}]},
                config={"run_name": TRACE_NAME, "run_id": run_id},
            )
    finally:
        if tracing:
            wait_for_all_tracers()
            print(f"LangSmith 项目 {TRACE_PROJECT} · 追踪 ID {run_id}")

    show_evidence(result["messages"], [tool.__name__ for tool in TOOLS[step]])


if __name__ == "__main__":
    main()
