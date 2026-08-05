"""SQLite persistence for runs, turns, and the full message transcript.

Kept deliberately boring — the dashboard and the examples/ exporter both read
straight out of this, so the schema is the contract.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id           TEXT NOT NULL,          -- groups the two arms of one A/B
    task              TEXT NOT NULL,
    paritok           INTEGER NOT NULL,       -- 1 = compression on
    strategy          TEXT DEFAULT 'paginate',-- truncate | paginate | paritok
    truncations       INTEGER DEFAULT 0,      -- tool results that lost content
    model             TEXT NOT NULL,
    started_at        REAL NOT NULL,
    finished_at       REAL,
    outcome           TEXT,                   -- solved | overflow | max_turns | error
    turns_completed   INTEGER DEFAULT 0,
    total_prompt_tokens INTEGER DEFAULT 0,
    peak_prompt_tokens  INTEGER DEFAULT 0,
    overflow_at_turn  INTEGER,
    overflow_tokens   INTEGER,
    tests_passed      INTEGER,                -- 1/0/NULL
    patches_applied   INTEGER DEFAULT 0,
    wall_time_s       REAL,
    paritok_stats     TEXT,                   -- JSON snapshot of /stats delta
    error             TEXT
);

CREATE TABLE IF NOT EXISTS turns (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id            INTEGER NOT NULL REFERENCES runs(id),
    turn              INTEGER NOT NULL,
    tool_name         TEXT,
    tool_args         TEXT,
    estimated_prompt_tokens INTEGER,
    actual_prompt_tokens    INTEGER,
    completion_tokens INTEGER,
    latency_s         REAL,
    tool_output_chars INTEGER,
    error             TEXT
);

CREATE TABLE IF NOT EXISTS transcript (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id   INTEGER NOT NULL REFERENCES runs(id),
    seq      INTEGER NOT NULL,
    role     TEXT NOT NULL,
    content  TEXT
);

CREATE INDEX IF NOT EXISTS idx_turns_run ON turns(run_id);
CREATE INDEX IF NOT EXISTS idx_transcript_run ON transcript(run_id);
CREATE INDEX IF NOT EXISTS idx_runs_pair ON runs(pair_id);
"""

DEFAULT_DB = Path(__file__).resolve().parent.parent / "headroom.db"


class Store:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self) -> None:
        """CREATE TABLE IF NOT EXISTS won't add columns to an existing table, so
        databases from an earlier run need the new ones backfilled."""
        have = {r["name"] for r in self.conn.execute("PRAGMA table_info(runs)")}
        for col, ddl in (
            ("strategy", "TEXT DEFAULT 'paginate'"),
            ("truncations", "INTEGER DEFAULT 0"),
        ):
            if col not in have:
                self.conn.execute(f"ALTER TABLE runs ADD COLUMN {col} {ddl}")

    def start_run(self, pair_id: str, task: str, paritok: bool, model: str,
                  strategy: str = "paginate") -> int:
        cur = self.conn.execute(
            "INSERT INTO runs (pair_id, task, paritok, model, started_at, strategy) "
            "VALUES (?,?,?,?,?,?)",
            (pair_id, task, int(paritok), model, time.time(), strategy),
        )
        self.conn.commit()
        return cur.lastrowid

    def add_turn(self, run_id: int, rec, tool_args: dict | None = None) -> None:
        self.conn.execute(
            """INSERT INTO turns (run_id, turn, tool_name, tool_args, estimated_prompt_tokens,
                                  actual_prompt_tokens, completion_tokens, latency_s,
                                  tool_output_chars, error)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (run_id, rec.turn, rec.tool_name, json.dumps(tool_args) if tool_args else None,
             rec.estimated_prompt_tokens, rec.actual_prompt_tokens, rec.completion_tokens,
             rec.latency_s, rec.tool_output_chars, rec.error),
        )
        self.conn.commit()

    def save_transcript(self, run_id: int, messages: list[dict]) -> None:
        rows = [
            (run_id, i, m.get("role", "?"),
             m.get("content") if isinstance(m.get("content"), str) else json.dumps(m, default=str))
            for i, m in enumerate(messages)
        ]
        self.conn.executemany(
            "INSERT INTO transcript (run_id, seq, role, content) VALUES (?,?,?,?)", rows
        )
        self.conn.commit()

    def finish_run(self, run_id: int, **fields) -> None:
        fields["finished_at"] = time.time()
        cols = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(f"UPDATE runs SET {cols} WHERE id = ?", (*fields.values(), run_id))
        self.conn.commit()

    # -- reads used by the dashboard and the exporter ---------------------
    def pairs(self) -> list[dict]:
        """Only comparisons with at least two arms. A single `headroom agent`
        run has nothing to compare against and renders as an empty screen."""
        rows = self.conn.execute(
            "SELECT pair_id, task, MIN(started_at) AS started, COUNT(*) AS n "
            "FROM runs GROUP BY pair_id HAVING n >= 2 ORDER BY started DESC"
        ).fetchall()
        return [{k: r[k] for k in ("pair_id", "task", "started")} for r in rows]

    def runs_for_pair(self, pair_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM runs WHERE pair_id = ? ORDER BY paritok", (pair_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def turns_for_run(self, run_id: int) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM turns WHERE run_id = ? ORDER BY turn", (run_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def transcript_for_run(self, run_id: int) -> list[dict]:
        rows = self.conn.execute(
            "SELECT seq, role, content FROM transcript WHERE run_id = ? ORDER BY seq", (run_id,)
        ).fetchall()
        return [dict(r) for r in rows]
