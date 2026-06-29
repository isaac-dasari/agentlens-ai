"""SQLite-backed local trace store."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from agentlens_ai.tracing.events import TraceEvent

DEFAULT_DB_PATH = Path(".agentlens/traces.db")


class SQLiteTraceStore:
    """Local SQLite trace store used by the AgentLens MVP."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms REAL,
                    inputs TEXT,
                    outputs TEXT,
                    error TEXT
                )
                """
            )
            conn.commit()

    def write_event(self, event: TraceEvent) -> None:
        """Persist a trace event."""

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO trace_events (
                    run_id, event_type, name, timestamp,
                    duration_ms, inputs, outputs, error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.run_id,
                    event.event_type.value,
                    event.name,
                    event.timestamp,
                    event.duration_ms,
                    json.dumps(event.inputs) if event.inputs is not None else None,
                    json.dumps(event.outputs) if event.outputs is not None else None,
                    event.error,
                ),
            )
            conn.commit()

    def list_runs(self) -> list[str]:
        """List run ids in reverse event order."""

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT run_id, MAX(id) AS latest_event_id
                FROM trace_events
                GROUP BY run_id
                ORDER BY latest_event_id DESC
                """
            ).fetchall()
        return [row[0] for row in rows]

    def fetch_events(self, run_id: str | None = None) -> list[dict[str, Any]]:
        """Fetch events, optionally scoped to one run id."""

        query = """
            SELECT run_id, event_type, name, timestamp, duration_ms, inputs, outputs, error
            FROM trace_events
        """
        params: tuple[Any, ...] = ()

        if run_id is not None:
            query += " WHERE run_id = ?"
            params = (run_id,)

        query += " ORDER BY id ASC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        events: list[dict[str, Any]] = []
        for row in rows:
            events.append(
                {
                    "run_id": row[0],
                    "event_type": row[1],
                    "name": row[2],
                    "timestamp": row[3],
                    "duration_ms": row[4],
                    "inputs": json.loads(row[5]) if row[5] else None,
                    "outputs": json.loads(row[6]) if row[6] else None,
                    "error": row[7],
                }
            )
        return events
