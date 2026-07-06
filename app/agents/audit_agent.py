"""
Audit Agent
-----------
Last stop in the pipeline. Persists every decision -- ALLOW, BLOCK, or
HUMAN_APPROVAL plus its eventual resolution -- with enough detail to
reconstruct why the system did what it did.

Writes to Supabase's `audit_log` table if SUPABASE_URL/SUPABASE_KEY are
configured; otherwise falls back to a local JSON file so the demo still works
with zero external accounts set up.

Suggested Supabase schema:

    create table audit_log (
        request_id   text primary key,
        user_id      text,
        tool         text,
        text         text,
        threats      text[],
        risk_score   int,
        decision     text,
        reason       text,
        timestamp    timestamptz,
        resolved_by  text
    );
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import AuditRecord
from app.services.supabase_client import get_supabase_client

LOCAL_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "audit_log.json"


class AuditAgent:
    def __init__(self) -> None:
        self._memory: list[AuditRecord] = []

    def log(self, record: AuditRecord) -> None:
        self._memory.append(record)

        client = get_supabase_client()
        if client is not None:
            try:
                client.table("audit_logs").upsert(
                    json.loads(record.model_dump_json())
                ).execute()
                return
            except Exception:
                pass  # fall through to local log on any Supabase error

        self._append_local(record)

    def update_resolution(self, request_id: str, resolved_by: str) -> None:
        for record in self._memory:
            if record.request_id == request_id:
                record.resolved_by = resolved_by
                break

        client = get_supabase_client()
        if client is not None:
            try:
                client.table("audit_logs").update(
                    {"resolved_by": resolved_by}
                ).eq("request_id", request_id).execute()
                return
            except Exception:
                pass

        self._rewrite_local()

    def get_log(self) -> list[AuditRecord]:
        if self._memory:
            return self._memory
        return self._read_local()

    # -- local JSON fallback -------------------------------------------------

    def _append_local(self, record: AuditRecord) -> None:
        records = self._read_local()
        records.append(record)
        self._write_local(records)

    def _rewrite_local(self) -> None:
        self._write_local(self._memory)

    def _read_local(self) -> list[AuditRecord]:
        if not LOCAL_LOG_PATH.exists():
            return []
        raw = json.loads(LOCAL_LOG_PATH.read_text())
        return [AuditRecord(**r) for r in raw]

    def _write_local(self, records: list[AuditRecord]) -> None:
        LOCAL_LOG_PATH.write_text(
            json.dumps([json.loads(r.model_dump_json()) for r in records], indent=2)
        )
