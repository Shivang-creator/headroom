"""Comparison dashboard.

Reads straight out of the SQLite store the A/B runner writes to, so there is no
separate ingestion path to get out of sync. `/api/stats` proxies Paritok's own
/stats endpoint so the page can show live compression totals next to the run
history.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from .ab import proxy_stats
from .store import Store

app = FastAPI(title="Headroom", docs_url=None, redoc_url=None)
STATIC = Path(__file__).resolve().parent / "static"


def _store() -> Store:
    return Store()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC / "index.html").read_text()


@app.get("/api/stats")
def api_stats() -> JSONResponse:
    st = proxy_stats()
    return JSONResponse(st or {"error": "proxy unreachable on port 8080"})


@app.get("/api/pairs")
def api_pairs() -> list[dict]:
    return _store().pairs()


@app.get("/api/pair/{pair_id}")
def api_pair(pair_id: str) -> dict:
    store = _store()
    runs = store.runs_for_pair(pair_id)
    if not runs:
        raise HTTPException(404, "no such pair")
    for r in runs:
        r["turns"] = store.turns_for_run(r["id"])
        if r.get("paritok_stats"):
            try:
                r["paritok_stats"] = json.loads(r["paritok_stats"])
            except (TypeError, json.JSONDecodeError):
                r["paritok_stats"] = None
    return {"pair_id": pair_id, "task": runs[0]["task"], "runs": runs}


@app.get("/api/run/{run_id}/transcript")
def api_transcript(run_id: int) -> list[dict]:
    return _store().transcript_for_run(run_id)
