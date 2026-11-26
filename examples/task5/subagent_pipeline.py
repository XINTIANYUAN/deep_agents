"""Run a researcher/writer pipeline and measure isolated contexts with shared files."""

import argparse
import ast
from collections import Counter
import json
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime

import httpx
from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.utils import create_file_data, file_data_to_string
from langchain.agents.middleware import AgentMiddleware, TodoListMiddleware
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_core.utils.uuid import uuid7
from langchain_openai import ChatOpenAI
from langsmith import tracing_context

PROJECT = "deepagents-task5"
SOURCE = "https://github.com/langchain-ai/deepagents/blob/deepagents%3D%3D0.7.8/libs/deepagents/deepagents/middleware/subagents.py"
RAW_SOURCE = "https://raw.githubusercontent.com/langchain-ai/deepagents/deepagents%3D%3D0.7.8/libs/deepagents/deepagents/middleware/subagents.py"
ANALYSIS_PATH = "/handoff/findings.md"
REPORT_PATH = "/handoff/report.md"
SYSTEM_MARKERS = {
    "coordinator": "MAIN_SYSTEM_ONLY_MARKER",
    "researcher": "RESEARCHER_SYSTEM_ONLY_MARKER",
    "writer": "WRITER_SYSTEM_ONLY_MARKER",
}
SKILLS = {
    "coordinator": "main-coordination-skill",
    "researcher": "research-analysis-skill",
    "writer": "writing-summary-skill",
}
HISTORY_MARKER = "PARENT_HISTORY_ONLY_MARKER"
RAW_MARKER = "RESEARCH_RAW_ONLY_MARKER"


def main() -> None:
    parser = argparse.ArgumentParser(description="运行 Task5 子 Agent 委派与上下文隔离实验。")
    parser.add_argument("--output-dir", type=Path, help="保存本次运行记录的独立目录。")
    args = parser.parse_args()
    output = (args.output_dir or Path(".task5-runs") / uuid4().hex).resolve()
    output.mkdir(parents=True, exist_ok=True)
    observations = {}

    class ObserveContext(AgentMiddleware):
        """Observe state and model requests without modifying them."""

        def __init__(self, role: str):
            self.role = role

        def before_agent(self, state, runtime):
            observations[self.role] = {
                "initial_messages": [{"type": m.type, "text": m.text} for m in state["messages"]],
                "initial_todos": state.get("todos", []),
                "initial_file_paths": list(state.get("files", {})),
                "initial_skill_names": [s["name"] for s in state.get("skills_metadata", [])],
                "model_views": [],
            }

        def wrap_model_call(self, request, handler):
            system = request.system_message.text if request.system_message else ""
            observations[self.role]["model_views"].append({
                "system_markers": [role for role, marker in SYSTEM_MARKERS.items() if marker in system],
                "skill_names_in_prompt": [name for name in SKILLS.values() if name in system],
                "tools": [tool.name if hasattr(tool, "name") else tool.get("name") for tool in request.tools],
            })
            return handler(request)

        def after_agent(self, state, runtime):
            observations[self.role].update({
                "final_todos": state.get("todos", []),
                "final_skill_names": [s["name"] for s in state.get("skills_metadata", [])],
                "messages": [m.model_dump(mode="json") for m in state["messages"]],
                "final_answer": state["messages"][-1].text,
            })
            (output / "contexts.json").write_text(
                json.dumps(observations, ensure_ascii=False, indent=2), encoding="utf-8",
            )

    def collect_reference() -> dict:
        """Read context routing in the official Deep Agents 0.7.8 source."""
        response = httpx.get(RAW_SOURCE, follow_redirects=True, timeout=45)
        response.raise_for_status()
        source = response.text
        excluded_keys = next(
            ast.literal_eval(node.value)
            for node in ast.parse(source).body
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "_EXCLUDED_STATE_KEYS"
                for target in node.targets
            )
        )
        excluded = source.index("_EXCLUDED_STATE_KEYS =")
        prepare = source.index("    def _validate_and_prepare_state(")
        returned = source.index("    def _return_command_with_state_update(")
        return {
            "source_url": SOURCE,
            "version": "0.7.8",
            "excluded_state_keys": sorted(excluded_keys),
            "files_passes_the_exclusion_filter": "files" not in excluded_keys,
            "excluded_channels": source[excluded:source.index("class TaskToolSchema", excluded)],
            "child_input": source[prepare:source.index("    def task(", prepare)],
            "child_return": source[returned:source.index("    def _select_subagent(", returned)],
            "raw_probe": RAW_MARKER,
        }

    model = ChatOpenAI(
        model=os.environ.get("TASK5_MODEL", "qwen3.5:4b"),
        base_url=os.environ.get("TASK5_OPENAI_BASE_URL", "http://127.0.0.1:11434/v1"),
        api_key=os.environ.get("TASK5_OPENAI_API_KEY", "ollama"),
        temperature=0,
        timeout=180,
        model_kwargs={"parallel_tool_calls": False},
    )
    researcher = {
        "name": "researcher",
        "description": "收集官方资料并分析上下文隔离与共享文件，保存发现后返回简短摘要。",
        "system_prompt": (
            f"{SYSTEM_MARKERS['researcher']} 你是研究员，只负责收集和分析。"
            "先用 write_todos 为自己的研究创建一项 in_progress 任务。"
            "调用 collect_reference 一次，只依据这份 0.7.8 源码分析消息、todos、私有状态的过滤和文件状态共享。"
            "files_passes_the_exclusion_filter 为 true 表示 files 可以随状态传入与回传。"
            "只写三至五条事实，不提出接口改造或权限审计方案，不引入其他版本参数。附完整 source_url。"
            f"用 write_file 将发现保存到 {ANALYSIS_PATH}，然后将自己的任务标为 completed。"
            f"文件路径必须逐字使用 {ANALYSIS_PATH}，这是虚拟根路径，不加 /app 前缀。"
            "最终只返回 120 字以内的发现摘要和文件路径。raw_probe 是工具内部检测标记，不写入笔记或回复。"
        ),
        "tools": [collect_reference],
        "skills": ["/skills/researcher/"],
        "middleware": [TodoListMiddleware(), ObserveContext("researcher")],
        "permissions": [
            FilesystemPermission(operations=["write"], paths=[ANALYSIS_PATH], mode="allow"),
            FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
        ],
    }
    writer = {
        "name": "writer",
        "description": "读取研究员的共享发现文件，整理为中文短报告并保存，不负责检索资料。",
        "system_prompt": (
            f"{SYSTEM_MARKERS['writer']} 你是写手，只负责基于已有发现写作。"
            f"必须先用 read_file 读取 {ANALYSIS_PATH}。"
            "写一份 400 字以内的中文报告，二级标题严格为‘隔离内容’、‘共享文件’、‘实践建议’，附笔记中的完整来源 URL。"
            f"用 write_file 保存到 {REPORT_PATH}。最终仅回复报告路径和一句概括。"
            "所有路径是虚拟根路径，逐字按指定路径操作，不加 /app 前缀。"
        ),
        "tools": [],
        "skills": ["/skills/writer/"],
        "middleware": [ObserveContext("writer")],
        "permissions": [
            FilesystemPermission(operations=["write"], paths=[REPORT_PATH], mode="allow"),
            FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
        ],
    }
    agent = create_deep_agent(
        model=model,
        tools=[],
        backend=StateBackend(),
        skills=["/skills/coordinator/"],
        middleware=[TodoListMiddleware(), ObserveContext("coordinator")],
        subagents=[researcher, writer],
        permissions=[FilesystemPermission(operations=["write"], paths=["/**"], mode="deny")],
        system_prompt=(
            f"{SYSTEM_MARKERS['coordinator']} 你是协调者，只管委派和验收。"
            "先用 write_todos 创建一项名为 MAIN_COORDINATION_TODO 的 in_progress 任务。"
            "先 task(subagent_type='researcher')，要求读取 0.7.8 上下文路由源码，只分析 messages、todos、私有状态过滤与 files 共享，保存发现和完整来源 URL。"
            "等待研究员返回后再 task(subagent_type='writer')，要求按‘隔离内容’、‘共享文件’、‘实践建议’三个二级标题写 400 字以内报告，附完整来源 URL。"
            "委派时保留指定的虚拟路径，所有路径不加 /app 前缀。只要求概括材料，不进行项目审计或提出源码改造。"
            f"委派给写手时只说明读取 {ANALYSIS_PATH}，不要复制研究正文。"
            f"最后用 read_file 读取 {REPORT_PATH} 验收，再将自己的任务标为 completed。"
            "不要把管理标记、历史检测标记或角色标记复制到委派 description。最终简短总结已完成的文件。"
        ),
    )
    files = {
        f"/skills/{role}/{name}/SKILL.md": create_file_data(
            f"---\nname: {name}\ndescription: 本角色使用的独立技能目录。\n---\n"
            "按照本角色分工完成任务，返回简洁结果。\n"
        )
        for role, name in SKILLS.items()
    }
    run_id = uuid7()
    tracing = os.environ.get("LANGSMITH_TRACING", "").strip().lower() == "true"
    print(f"开始 Task5 · {model.model_name}", flush=True)
    try:
        with tracing_context(enabled=tracing, project_name=PROJECT, parent=False):
            result = agent.invoke(
                {"messages": [{"role": "user", "content": (
                    f"{HISTORY_MARKER} 这是只留在主对话的检测标记，请不要转交。"
                    "请通过 researcher 和 writer 完成‘子 Agent 上下文隔离与共享文件’的收集、分析、写作小流水线。"
                    "严格依次委派，等待研究员完成并保存发现后，再让写手读取共享文件成文。"
                )}], "files": files},
                config={"run_name": "task5-subagent-pipeline", "run_id": run_id, "recursion_limit": 70},
            )
    finally:
        if tracing:
            wait_for_all_tracers()
            print(f"LangSmith {PROJECT} · {run_id}", flush=True)
        (output / "contexts.json").write_text(json.dumps(observations, ensure_ascii=False, indent=2), encoding="utf-8")

    parent_messages = result["messages"]
    calls = [c for m in parent_messages if isinstance(m, AIMessage) for c in m.tool_calls]
    tasks = [c for c in calls if c["name"] == "task"]
    responses = {m.tool_call_id: m for m in parent_messages if isinstance(m, ToolMessage)}
    parent_text = json.dumps([m.model_dump(mode="json") for m in parent_messages], ensure_ascii=False)
    final_files = result["files"]
    report = file_data_to_string(final_files[REPORT_PATH])
    findings = file_data_to_string(final_files[ANALYSIS_PATH])
    (output / "report.md").write_text(report, encoding="utf-8")
    (output / "findings.md").write_text(findings, encoding="utf-8")
    observations_path = output / "contexts.json"
    checks = {
        "researcher_then_writer": [t["args"]["subagent_type"] for t in tasks] == ["researcher", "writer"],
        "child_history_not_inherited": all(
            len(observations[role]["initial_messages"]) == 1
            and HISTORY_MARKER not in observations[role]["initial_messages"][0]["text"]
            for role in ("researcher", "writer")
        ),
        "separate_system_prompts": all(
            all(view["system_markers"] == [role] for view in observations[role]["model_views"])
            for role in SKILLS
        ),
        "separate_skills": all(observations[role]["final_skill_names"] == [name] for role, name in SKILLS.items()),
        "separate_skill_prompts": all(
            all(view["skill_names_in_prompt"] == [name] for view in observations[role]["model_views"])
            for role, name in SKILLS.items()
        ),
        "child_todos_not_inherited": all(not observations[role]["initial_todos"] for role in ("researcher", "writer")),
        "research_todos_not_returned": (
            result.get("todos", []) == [c for c in calls if c["name"] == "write_todos"][-1]["args"]["todos"]
            and not {t["content"] for t in result.get("todos", [])}.intersection(
                t["content"] for t in observations["researcher"]["final_todos"]
            )
        ),
        "task_returns_only_final_answer": all(
            responses[t["id"]].text.strip() == observations[t["args"]["subagent_type"]]["final_answer"].strip()
            for t in tasks
        ),
        "writer_has_no_todo_tool": all("write_todos" not in view["tools"] for view in observations["writer"]["model_views"]),
        "raw_research_isolated": RAW_MARKER not in parent_text and RAW_MARKER in json.dumps(observations["researcher"]["messages"]),
        "parent_has_no_collect_reference_call": all(c["name"] != "collect_reference" for c in calls),
        "writer_reads_shared_findings": any(
            c["name"] == "read_file" and c["args"].get("file_path") == ANALYSIS_PATH
            for m in observations["writer"]["messages"] for c in m.get("tool_calls", [])
        ),
        "shared_findings_present_on_writer_entry": ANALYSIS_PATH in observations["writer"]["initial_file_paths"],
        "report_has_sections": all(f"## {heading}" in report for heading in ("隔离内容", "共享文件", "实践建议")),
        "source_cited": all(
            SOURCE in text or SOURCE.replace("%3D", "=") in text
            for text in (findings, report)
        ),
    }
    record = {
        "date": datetime.now().astimezone().isoformat(),
        "model": model.model_name, "trace_project": PROJECT if tracing else None,
        "trace_id": str(run_id) if tracing else None,
        "parent_tool_counts": dict(Counter(c["name"] for c in calls)),
        "parent_tool_errors": [
            {"name": c["name"], "error": responses[c["id"]].text}
            for c in calls if responses[c["id"]].status == "error"
        ],
        "task_response_characters": {
            t["args"]["subagent_type"]: len(responses[t["id"]].text) for t in tasks
        },
        "delegations": [{"role": t["args"]["subagent_type"], "description": t["args"]["description"]} for t in tasks],
        "roles": {role: {
            "initial_message_count": len(data["initial_messages"]),
            "initial_todos": data["initial_todos"], "final_todos": data["final_todos"],
            "skill_names": data["final_skill_names"],
            "llm_calls": len(data["model_views"]),
            "tool_counts": dict(Counter(c["name"] for m in data["messages"] for c in m.get("tool_calls", []))),
        } for role, data in observations.items()},
        "files": [ANALYSIS_PATH, REPORT_PATH],
        "checks": checks,
    }
    (output / "results.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False), flush=True)
    assert all(checks.values()), f"请复盘 {observations_path} 与 results.json 中未通过的检查。"
    print(f"验收通过 · 实测记录 {output / 'results.json'}", flush=True)


if __name__ == "__main__":
    main()
