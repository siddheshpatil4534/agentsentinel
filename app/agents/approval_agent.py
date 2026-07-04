"""
Human Approval Agent
--------------------
Holds requests that landed in the HUMAN_APPROVAL band until a person resolves
them. In-memory for the MVP -- swap `_pending` for a real table (Supabase or
otherwise) once this needs to survive a restart or run across multiple workers.
"""

from __future__ import annotations

from app.models.schemas import AgentRequest, RiskAssessment


class HumanApprovalAgent:
    def __init__(self) -> None:
        self._pending: dict[str, dict] = {}

    def queue(self, request: AgentRequest, risk: RiskAssessment) -> None:
        self._pending[request.request_id] = {
            "request": request,
            "risk": risk,
        }

    def get_pending(self) -> list[dict]:
        return list(self._pending.values())

    def resolve(self, request_id: str) -> dict | None:
        """Remove and return the pending entry, or None if it's not there."""
        return self._pending.pop(request_id, None)

    def is_pending(self, request_id: str) -> bool:
        return request_id in self._pending
