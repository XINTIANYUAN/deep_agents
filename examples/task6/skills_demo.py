"""Observe metadata discovery -> model-selected reads -> instructions and file output."""

import argparse
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
from uuid import uuid4
from zoneinfo import ZoneInfo

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_core.utils.uuid import uuid7
from langchain_openai import ChatOpenAI
from langsmith import tracing_context

BODY = "TASK6_SKILL_BODY_LOADED"
RULE = "TASK6_REFERENCE_RULE_27"
UNRELATED = "TASK6_UNRELATED_INVOICE_BODY"
SKILL = "/skills/lifecycle-review/SKILL.md"
REFERENCE = "/skills/lifecycle-review/references/review-rules.md"


def run(lifecycle: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    workspace = output / "workspace"
    shutil.copytree(Path(__file__).parent / "skills", workspace / "skills")
    (workspace / "inputs").mkdir()
    (workspace / "outputs").mkdir()
    measured = json.loads(lifecycle.read_text())
    # Give the model measured acceptance facts without private thread/trace identifiers.
    evidence = {"checks": measured["checks"], "resume_semantics": "cancel then update, same thread, new run"}
    (workspace / "inputs/lifecycle.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
    views = []

    class ObserveDisclosure(AgentMiddleware):
        def wrap_model_call(self, request, handler):
            system = request.system_message.text
            tools = [m for m in request.messages if isinstance(m, ToolMessage)]
            views.append({
                "model_turn": len(views) + 1,
                "metadata_names": [s["name"] for s in request.state.get("skills_metadata", [])],
                "system_has_skill_name": "lifecycle-review" in system,
                "system_has_skill_description": "核对取消与续跑证据" in system,
                "system_has_skill_body": BODY in system,
                "system_has_reference_body": RULE in system,
                "tool_context_has_skill_body": any(BODY in m.text for m in tools),
                "tool_context_has_reference": any(RULE in m.text for m in tools),
                "tool_context_has_unrelated_body": any(UNRELATED in m.text for m in tools),
            })
            (output / "disclosure.json").write_text(json.dumps(views, ensure_ascii=False, indent=2))
            return handler(request)

    model = ChatOpenAI(
        model=os.getenv("TASK6_MODEL", "qwen3.5:4b"),
        base_url=os.getenv("TASK6_BASE_URL", "http://127.0.0.1:11434/v1"),
        api_key=os.getenv("TASK6_API_KEY", "ollama"), temperature=0, timeout=120,
    )
    agent = create_deep_agent(
        model=model, backend=FilesystemBackend(root_dir=workspace, virtual_mode=True),
        skills=["/skills/"], middleware=[ObserveDisclosure()],
        permissions=[FilesystemPermission(operations=["write"], paths=["/skills/**", "/inputs/**"], mode="deny")],
        system_prompt="你负责按需使用可用技能。根据描述选择相关技能，读完整指令再执行。文件操作使用明确的虚拟路径。不要委派。",
    )
    trace_id = uuid7()
    tracing = os.getenv("LANGSMITH_TRACING", "").lower() == "true"
    try:
        with tracing_context(enabled=tracing, project_name="deepagents-task6", parent=False):
            result = agent.invoke({"messages": [{"role": "user", "content":
                "请根据 /inputs/lifecycle.json 核对异步子 Agent 生命周期实验，撰写一份简短中文验收说明并保存文件。请使用与你判断相关的技能。"}]},
                config={"run_id": trace_id, "run_name": "task6-progressive-disclosure", "recursion_limit": 36})
    finally:
        if tracing:
            wait_for_all_tracers()
        print(f"Skills Trace: {trace_id}", flush=True)
    messages = result["messages"]
    (output / "messages.json").write_text(json.dumps([m.model_dump(mode="json") for m in messages], ensure_ascii=False, indent=2))
    calls = [c for m in messages if isinstance(m, AIMessage) for c in m.tool_calls]
    reads = [c["args"].get("file_path") for c in calls if c["name"] == "read_file"]
    report = (workspace / "outputs/acceptance.md").read_text()
    errors = [m.text for m in messages if isinstance(m, ToolMessage) and m.status == "error"]
    checks = {
        "first_model_sees_metadata_and_description": views[0]["system_has_skill_name"] and views[0]["system_has_skill_description"],
        "first_model_has_no_skill_body_or_reference": not any(views[0][k] for k in ["system_has_skill_body","system_has_reference_body","tool_context_has_skill_body","tool_context_has_reference"]),
        "skill_read_before_reference": SKILL in reads and REFERENCE in reads and reads.index(SKILL) < reads.index(REFERENCE),
        "later_model_receives_body_and_reference": any(v["tool_context_has_skill_body"] and v["tool_context_has_reference"] for v in views),
        "skill_body_never_injected_in_system": not any(v["system_has_skill_body"] or v["system_has_reference_body"] for v in views),
        "unrelated_skill_discovered_not_opened": "invoice-summary" in views[0]["metadata_names"] and not any(v["tool_context_has_unrelated_body"] for v in views),
        "report_has_required_sections_and_code": all(s in report for s in ["## 验证结论","## 证据摘要","## 边界与限制", RULE]),
        "report_read_back": "/outputs/acceptance.md" in reads,
        "report_avoids_invented_placeholder_date": "2024" not in report and "01-XX" not in report,
        "no_tool_errors": not errors,
    }
    summary = {"date": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(), "trace_id": str(trace_id),
               "model_calls": len(views), "tool_counts": dict(Counter(c["name"] for c in calls)),
               "reads": reads, "checks": checks, "errors": errors}
    (output / "results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    assert all(checks.values()), "See results.json for failed Skills checks"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lifecycle", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(".task6-runs") / uuid4().hex)
    args = parser.parse_args()
    run(args.lifecycle, args.output_dir.resolve())
