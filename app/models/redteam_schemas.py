"""
AttackPayload — one entry in the red-team library.

Deliberately reuses ThreatType from your existing pipeline rather than
defining a separate "AttackCategory" enum. The Threat Detection Agent and
the RedTeamAgent are two views of the *same* taxonomy — what to look for vs.
what to throw at it — so they must share one source of truth. A second,
parallel enum here would drift from the real one the first time someone adds
a category in only one place.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.schemas import ThreatType  # <-- point this at your real schemas.py


class AttackPayload(BaseModel):
    id: str  # stable, human-readable, e.g. "PI-001" — used as a key in reports later
    category: ThreatType
    name: str  # short label, e.g. "Direct instruction override"
    text: str  # the actual payload sent as the request's "text"
    severity: Literal["low", "medium", "high"] = "medium"
    description: str = ""  # what technique this represents, for write-ups/reports

    # Optional hints for how to feed this into the pipeline — safe to leave None.
    suggested_tool: Optional[str] = None
    suggested_action: Optional[str] = None

    # Not used by anything yet. Exists so a future evaluator/runner can compare
    # "what we expected this to trigger" against "what the pipeline actually
    # returned" without a breaking schema change. Leave empty for now.
    expected_threats: list[ThreatType] = Field(default_factory=list)
