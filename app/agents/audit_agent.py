"""
Audit Agent
-----------
Persists every decision to Supabase if configured, otherwise falls back
to a local JSON file.
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
                payload = json.loads(record.model_dump_json())

                print("\n===== Saving record to Supabase =====")
                print(payload)

                client.table("audit_logs").upsert(payload).execute()

                print("===== Saved to Supabase successfully! =====\n")
                return

            except Exception as e:
                print("\n===== Supabase insert failed =====")
                print(e)
                print("===================================\n")

        # fallback
        self._append_local(record)

    def update_resolution(
        self,
        request_id: str,
        resolved_by: str,
    ) -> None:
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

                print(
                    f"Updated resolution for {request_id} in Supabase."
                )
                return

            except Exception as e:
                print("\n===== Supabase update failed =====")
                print(e)
                print("==================================\n")

        self._rewrite_local()

    def get_log(self) -> list[AuditRecord]:
        if self._memory:
            return self._memory
        return self._read_local()

    # ---------- local JSON fallback ----------

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
            json.dumps(
                [json.loads(r.model_dump_json()) for r in records],
                indent=2,
            )
        )