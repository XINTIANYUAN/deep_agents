"""Exercise all five real AsyncSubAgent tools through model-driven supervisor turns."""

import argparse
import asyncio
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from zoneinfo import ZoneInfo

from langgraph_sdk import get_client


async def run(url: str, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    client = get_client(url=url)
    thread = await client.threads.create()
    parent = thread["thread_id"]
    turns = []
    child_ids = set()

    def save():
        (output / "lifecycle.json").write_text(json.dumps({
            "date": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            "supervisor_thread_id": parent, "turns": turns,
        }, ensure_ascii=False, indent=2))

    async def turn(label, prompt, expected_tool=None):
        before = await client.threads.get_state(parent)
        count = len((before.get("values") or {}).get("messages", []))
        start = perf_counter()
        result = await client.runs.wait(parent, "task6_supervisor", input={
            "messages": [{"role": "user", "content": prompt}]
        }, config={"recursion_limit": 12})
        elapsed = perf_counter() - start
        if "__error__" in result:
            raise RuntimeError(result["__error__"])
        messages = result["messages"][count:]
        calls = [c for m in messages for c in m.get("tool_calls", [])]
        tasks = result.get("async_tasks", {})
        child_ids.update(tasks)
        actual = {t: await client.runs.get(t, task["run_id"]) for t, task in tasks.items()}
        record = {
            "label": label, "prompt": prompt, "elapsed_seconds": round(elapsed, 3),
            "calls": calls, "messages": messages, "async_tasks": tasks,
            "server_runs": actual,
        }
        turns.append(record)
        save()
        print(json.dumps({"step": label, "seconds": record["elapsed_seconds"],
                          "tools": [c["name"] for c in calls],
                          "server_status": {t:r["status"] for t,r in actual.items()}}, ensure_ascii=False), flush=True)
        assert [c["name"] for c in calls] == ([expected_tool] if expected_tool else []), label
        return tasks

    try:
        tasks = await turn("start_A", "只启动一个 worker 后台任务：A，演示异步生命周期，delay_seconds=240。不要查询。", "start_async_task")
        a = next(iter(tasks))
        original_run = tasks[a]["run_id"]
        await turn("chat_while_running", "先不要操作后台任务。只回答：3 加 4 等于多少？")
        tasks = await turn("update_A", f"仅给 {a} 追加指令：重点验证追加约束被保留，delay_seconds=240。", "update_async_task")
        updated_run = tasks[a]["run_id"]
        tasks = await turn("start_B", "只启动第二个 worker 后台任务：B，测试并行与取消，delay_seconds=240。", "start_async_task")
        b = next(t for t in tasks if t != a)
        await turn("list_parallel", "仅查询所有异步任务的最新状态总览。", "list_async_tasks")
        await turn("check_A", f"仅查询任务 {a} 的最新状态。", "check_async_task")
        await turn("cancel_B", f"仅取消任务 {b}。", "cancel_async_task")
        await turn("cancel_A", f"仅取消任务 {a}，之后会用更新指令继续。", "cancel_async_task")
        tasks = await turn("resume_A_by_update", f"仅更新任务 {a} 继续处理：保留前面的追加约束，新增 RESUMED_CONSTRAINT，delay_seconds=1。", "update_async_task")
        resumed_run = tasks[a]["run_id"]
        # Poll the real server with a bounded wait, rather than trusting cancelled cache.
        for _ in range(40):
            status = await client.runs.get(a, resumed_run)
            if status["status"] in {"success", "error", "timeout", "interrupted"}:
                break
            await asyncio.sleep(0.5)
        await turn("check_resumed_A", f"仅查询任务 {a} 的最新状态与结果。", "check_async_task")
        child_state = await client.threads.get_state(a)
        child_messages = child_state["values"]["messages"]
        runs = {t: await client.runs.list(t) for t in child_ids}
        latest = {r["label"]: r for r in turns}
        checks = {
            "start_returns_before_child_completes": latest["start_A"]["server_runs"][a]["status"] in {"pending", "running"},
            "unrelated_chat_while_child_running": latest["chat_while_running"]["server_runs"][a]["status"] in {"pending", "running"},
            "two_children_running_in_parallel": all(r["status"] == "running" for r in latest["list_parallel"]["server_runs"].values()),
            "update_preserves_task_id_changes_run_id": original_run != updated_run != resumed_run and len({original_run, updated_run,resumed_run}) == 3,
            "updated_run_was_interrupted": any(r["run_id"] == original_run and r["status"] == "interrupted" for r in runs[a]),
            "both_cancelled_runs_stopped_on_server": all(next(r for r in runs[t] if r["run_id"] == latest[f"cancel_{label}"]["async_tasks"][t]["run_id"])["status"] in {"interrupted", "cancelled"} for t,label in [(a,"A"),(b,"B")]),
            "resumed_run_success": latest["check_resumed_A"]["server_runs"][a]["status"] == "success",
            "child_keeps_original_update_and_resume_messages": len([m for m in child_messages if m["type"] == "human"]) == 3,
            "resumed_result_contains_new_constraint": child_messages[-1]["type"] == "ai" and "RESUMED_CONSTRAINT" in child_messages[-1]["content"],
            "all_five_official_tools_exercised": set(Counter(c["name"] for t in turns for c in t["calls"])) == {"start_async_task","check_async_task","update_async_task","cancel_async_task","list_async_tasks"},
        }
        result = {"turns": turns, "child_runs": runs, "child_messages": child_messages, "checks": checks}
        (output / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps({"checks": checks}, ensure_ascii=False), flush=True)
        assert all(checks.values()), "See results.json for failed acceptance checks"
    finally:
        # Ensure failed assertions never leave demonstration workers running.
        for task_id in child_ids:
            for r in await client.runs.list(task_id):
                if r["status"] in {"pending", "running"}:
                    await client.runs.cancel(task_id, r["run_id"], wait=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:2026")
    parser.add_argument("--output-dir", type=Path, default=Path(".task6-runs") / uuid4().hex)
    args = parser.parse_args()
    asyncio.run(run(args.url, args.output_dir))
