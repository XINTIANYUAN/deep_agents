"""Start the Task6 Agent Server without changing Task1's ports or environment."""

import argparse
import json
import os
from pathlib import Path
import subprocess

from dotenv import load_dotenv


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=2026)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    env = os.environ.copy()
    env.update({
        "LANGSMITH_PROJECT": "deepagents-task6",
        "LANGSMITH_TRACING": "true",
        "LANGGRAPH_AUTH_TYPE": "noop",
        "LANGGRAPH_STORE_ENDPOINT": "",
        "NO_PROXY": "127.0.0.1,localhost",
        "no_proxy": "127.0.0.1,localhost",
    })
    executable = root / ".task6-runs/venv/bin/langgraph"
    if not executable.is_file():
        raise SystemExit("先按 Task6 学习笔记安装隔离环境 .task6-runs/venv。")
    server_dir = root / ".task6-runs/server"
    server_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path(__file__).with_name("langgraph.json").read_text())
    config["dependencies"] = [str(Path(__file__).parent.resolve())]
    config["graphs"] = {name: str(Path(__file__).with_name("graphs.py").resolve()) + ":" + target.split(":")[-1]
                        for name, target in config["graphs"].items()}
    config_path = server_dir / "langgraph.json"
    config_path.write_text(json.dumps(config, indent=2))
    subprocess.run([
        str(executable), "dev", "--config", str(config_path),
        "--host", "127.0.0.1", "--port", str(args.port), "--no-browser",
        "--n-jobs-per-worker", "6", "--no-reload",
    ], cwd=server_dir, env=env, check=True)
