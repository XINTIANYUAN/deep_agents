"""Run Task3 file tools, default result offloading, and backend lifetime experiments."""

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend, StoreBackend
from deepagents.backends.utils import file_data_to_string
from deepagents.middleware.filesystem import FilesystemState
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_core.utils.uuid import uuid7
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.memory import InMemoryStore
from langsmith import tracing_context

PROJECT = "deepagents-task3"
NOTE_PATH = "/notes/task3.md"
NOTE = "# Task3\nContext Engineering uses files on demand.\nBackend controls storage."
NEEDLE = "TASK3_NEEDLE=Read relevant data on demand."


def large_result() -> str:
    """Return a large synthetic document with a target on line 1201 (offset 1200)."""
    lines = ["TASK3_HEAD Synthetic public experiment data"]
    lines.extend(
        f"Record {index:04d} | Store source material in files. Read only relevant pages. "
        "Context Engineering keeps model input focused."
        for index in range(1, 2400)
    )
    lines[1200] = NEEDLE
    lines.append("TASK3_TAIL End of synthetic experiment data")
    return "\n".join(lines)


def run_agent(step: str, prompt: str, tools: list, output_dir: Path) -> dict:
    """Run a real local model, retaining compact call evidence and the final state."""
    model = ChatOpenAI(
        model=os.environ.get("TASK3_MODEL", "qwen3.5:4b"),
        base_url=os.environ.get("TASK3_OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
        api_key=os.environ.get("TASK3_OPENAI_API_KEY", "ollama"),
        temperature=0,
        timeout=120,
        model_kwargs={"parallel_tool_calls": False},
    )
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "Follow the requested steps in order. Call one tool at a time. "
            "Use the actual results of tools. Finish with a short Chinese answer."
        ),
    )
    tracing = os.environ.get("LANGSMITH_TRACING", "").lower() == "true"
    run_id = uuid7()
    print(f"开始 {step} · {model.model_name}", flush=True)
    try:
        with tracing_context(enabled=tracing, project_name=PROJECT, parent=False):
            result = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config={"run_name": f"task3-{step}", "run_id": run_id, "recursion_limit": 30},
            )
    finally:
        if tracing:
            wait_for_all_tracers()
            print(f"LangSmith {PROJECT} · {run_id}", flush=True)

    messages = result["messages"]
    calls = [call for msg in messages if isinstance(msg, AIMessage) for call in msg.tool_calls]
    responses = {msg.tool_call_id: msg for msg in messages if isinstance(msg, ToolMessage)}
    for call in calls:
        response = responses[call["id"]]
        assert response.status == "success", response.content
        print(f"  {call['name']} {json.dumps(call['args'], ensure_ascii=False)}", flush=True)
    assert isinstance(messages[-1], AIMessage) and messages[-1].text
    evidence = {
        "model": model.model_name,
        "trace_project": PROJECT if tracing else None,
        "trace_id": str(run_id) if tracing else None,
        "llm_messages": sum(isinstance(msg, AIMessage) for msg in messages),
        "tool_calls": [{"name": call["name"], "args": call["args"]} for call in calls],
        "final_answer": messages[-1].text,
    }
    (output_dir / f"{step}-messages.json").write_text(
        json.dumps([msg.model_dump(mode="json") for msg in messages], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"state": result, "calls": calls, "responses": responses, "evidence": evidence}


def file_tools(output_dir: Path) -> dict:
    run = run_agent(
        "files",
        f"依次使用内置工具。先用 write_file 在 {NOTE_PATH} 写入以下完整内容：\n{NOTE}\n"
        f"然后用 read_file 读回 {NOTE_PATH}，再用 grep 在 /notes/ 中按字面搜索 "
        "Context Engineering，output_mode 使用 content。最后简述读写与搜索结果。",
        [],
        output_dir,
    )
    assert [call["name"] for call in run["calls"]] == ["write_file", "read_file", "grep"]
    stored = file_data_to_string(run["state"]["files"][NOTE_PATH])
    assert stored == NOTE
    read, search = [run["responses"][call["id"]].text for call in run["calls"][1:]]
    assert "Context Engineering" in read and "Context Engineering" in search
    assert NOTE_PATH in search
    return {**run["evidence"], "virtual_path": NOTE_PATH, "stored_note": stored}


def offload(output_dir: Path) -> dict:
    run = run_agent(
        "offload",
        "先调用 large_result 一次。它的超长结果会由框架自动保存。"
        "从工具返回的文件引用中取得路径，然后用 read_file 读取该路径的 "
        "offset=1200、limit=1。最后仅回答该行的 TASK3_NEEDLE 内容。",
        [large_result],
        output_dir,
    )
    calls = run["calls"]
    assert [call["name"] for call in calls] == ["large_result", "read_file"]
    preview = run["responses"][calls[0]["id"]].text
    files = run["state"]["files"]
    paths = [path for path in files if "/large_tool_results/" in path]
    assert len(paths) == 1
    path = paths[0]
    original = large_result()
    assert file_data_to_string(files[path]) == original
    assert len(original) > 20_000 * 4
    assert path in preview and "TASK3_HEAD" in preview and "TASK3_TAIL" in preview
    assert "lines truncated" in preview and NEEDLE not in preview
    assert calls[1]["args"] == {"file_path": path, "offset": 1200, "limit": 1}
    assert NEEDLE in run["responses"][calls[1]["id"]].text
    (output_dir / "large-result.txt").write_text(original, encoding="utf-8")
    return {
        **run["evidence"],
        "threshold_estimated_tokens": 20_000,
        "threshold_characters": 80_000,
        "original_characters": len(original),
        "replacement_characters": len(preview),
        "saved_full_content_sha256": hashlib.sha256(original.encode()).hexdigest(),
        "virtual_path": path,
        "replacement_tool_message": preview,
        "readback": run["responses"][calls[1]["id"]].text,
    }


class BackendState(FilesystemState):
    action: str
    observation: dict


def backend_graph(kind: str, disk_root: Path, saver: InMemorySaver, store: InMemoryStore):
    """Exercise real backend methods inside graph execution, without LLM decisions."""
    backends = {
        "state": StateBackend(),
        "filesystem": FilesystemBackend(root_dir=disk_root, virtual_mode=True),
        "store": StoreBackend(namespace=lambda _runtime: ("task3", "learner")),
    }
    backend = backends[kind]

    def operate(state: BackendState) -> dict:
        if state["action"] == "write":
            result = backend.write(NOTE_PATH, NOTE)
            assert not result.error, result.error
        result = backend.read(NOTE_PATH)
        content = None if result.error else file_data_to_string(result.file_data)
        return {"observation": {"found": not bool(result.error), "content": content}}

    graph = StateGraph(BackendState)
    graph.add_node("backend_operation", operate)
    graph.add_edge(START, "backend_operation")
    graph.add_edge("backend_operation", END)
    return graph.compile(checkpointer=saver, store=store)


def observe(graph, action: str, thread: str) -> dict:
    state = graph.invoke(
        {"messages": [], "action": action},
        config={"configurable": {"thread_id": thread}},
    )
    return state["observation"]


def compare_backends(output_dir: Path) -> list[dict]:
    """Compare shared resources, different threads, and a genuinely fresh process."""
    rows = []
    for kind in ("state", "filesystem", "store"):
        saver, store = InMemorySaver(), InMemoryStore()
        disk_root = output_dir / "disk"
        disk_root.mkdir(exist_ok=True)
        graph = backend_graph(kind, disk_root, saver, store)
        assert observe(graph, "write", "writer")["content"] == NOTE
        same = observe(graph, "read", "writer")
        other = observe(graph, "read", "reader")
        rebuilt = observe(backend_graph(kind, disk_root, saver, store), "read", "writer")
        child = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--restart-probe", kind,
             "--output-dir", str(output_dir)],
            check=True, capture_output=True, text=True, timeout=30,
        )
        fresh = json.loads(child.stdout)
        assert same["content"] == rebuilt["content"] == NOTE
        assert other["found"] == (kind != "state")
        assert fresh["found"] == (kind == "filesystem")
        assert not other["found"] or other["content"] == NOTE
        assert not fresh["found"] or fresh["content"] == NOTE
        row = {
            "backend": kind,
            "same_thread": same["found"],
            "other_thread_same_resources": other["found"],
            "rebuilt_graph_same_resources": rebuilt["found"],
            "fresh_process": fresh["found"],
        }
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    assert (output_dir / "disk/notes/task3.md").read_text(encoding="utf-8") == NOTE
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 Task3 文件系统与 Backend 实验。")
    parser.add_argument("--step", choices=("files", "offload", "backends", "all"), default="all")
    parser.add_argument("--output-dir", type=Path, help="保存实测记录与落盘样例的独立目录。")
    parser.add_argument("--restart-probe", choices=("state", "filesystem", "store"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    output_dir = (args.output_dir or Path(".task3-runs") / uuid4().hex).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.restart_probe:
        with tracing_context(enabled=False):
            graph = backend_graph(args.restart_probe, output_dir / "disk", InMemorySaver(), InMemoryStore())
            print(json.dumps(observe(graph, "read", "writer"), ensure_ascii=False))
        return

    record = {"date": datetime.now().astimezone().isoformat(), "step": args.step}
    for name, experiment in (("files", file_tools), ("offload", offload), ("backends", compare_backends)):
        if args.step in (name, "all"):
            with tracing_context(enabled=False):
                record[name] = experiment(output_dir)
            (output_dir / "results.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8",
            )
    print(f"验收通过 · 本地实测记录 {output_dir / 'results.json'}")


if __name__ == "__main__":
    main()
