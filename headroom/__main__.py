"""Headroom CLI.

    python -m headroom ab      tasks/task01_report_mean     # the comparison
    python -m headroom agent   tasks/task01_report_mean     # one arm only
    python -m headroom serve                                # dashboard
    python -m headroom stats                                # live proxy totals
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ab import format_comparison, proxy_stats, run_arm, run_pair
from .config import DEFAULT_MODEL, PROXY_BASE_URL
from .store import Store

TASKS_DIR = Path(__file__).resolve().parent.parent / "tasks"


def _resolve_task(name: str) -> Path:
    p = Path(name)
    if p.is_dir():
        return p.resolve()
    p = TASKS_DIR / name
    if p.is_dir():
        return p.resolve()
    sys.exit(f"no such task: {name}\navailable: " + ", ".join(
        sorted(d.name for d in TASKS_DIR.iterdir() if d.is_dir() and (d / 'TASK.md').exists())
    ))


def _require_proxy() -> None:
    if proxy_stats() is None:
        sys.exit(
            f"The Paritok proxy is not answering at {PROXY_BASE_URL}.\n"
            "Start it in another terminal first — see RUNME.md step 1:\n\n"
            "  cd ~/Projects/headroom\n"
            "  export PARITOK_API_KEY=...\n"
            "  .venv/bin/paritok proxy --port 8080 --config-file paritok.yaml \\\n"
            "      --openai-url https://api.featherless.ai/v1/chat/completions\n"
        )


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="headroom", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ab = sub.add_parser("ab", help="run a task twice, with and without Paritok")
    p_ab.add_argument("task")
    p_ab.add_argument("--model", default=DEFAULT_MODEL)
    p_ab.add_argument("--max-turns", type=int, default=40)
    p_ab.add_argument("--json", action="store_true", help="emit the result as JSON")

    p_one = sub.add_parser("agent", help="run a single arm")
    p_one.add_argument("task")
    p_one.add_argument("--paritok", action="store_true", help="route through the proxy")
    p_one.add_argument("--model", default=DEFAULT_MODEL)
    p_one.add_argument("--max-turns", type=int, default=40)

    p_srv = sub.add_parser("serve", help="run the comparison dashboard")
    p_srv.add_argument("--port", type=int, default=8900)

    sub.add_parser("stats", help="print the proxy's live compression totals")
    sub.add_parser("tasks", help="list the seeded tasks")

    args = ap.parse_args(argv)

    if args.cmd == "stats":
        st = proxy_stats()
        print(json.dumps(st, indent=2) if st else "proxy not reachable on port 8080")
        return

    if args.cmd == "tasks":
        for d in sorted(TASKS_DIR.iterdir()):
            if d.is_dir() and (d / "TASK.md").exists():
                print(f"{d.name}\n    {(d / 'TASK.md').read_text().strip().splitlines()[-1][:100]}")
        return

    if args.cmd == "serve":
        import uvicorn
        from .server import app
        print(f"dashboard → http://127.0.0.1:{args.port}")
        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
        return

    store = Store()

    if args.cmd == "ab":
        _require_proxy()
        pair = run_pair(_resolve_task(args.task), store,
                        model=args.model, max_turns=args.max_turns)
        print(format_comparison(pair))
        if args.json:
            print(json.dumps(pair, indent=2, default=str))
        return

    if args.cmd == "agent":
        if args.paritok:
            _require_proxy()
        import uuid
        result = run_arm(_resolve_task(args.task), uuid.uuid4().hex[:12], args.paritok, store,
                         model=args.model, max_turns=args.max_turns)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
