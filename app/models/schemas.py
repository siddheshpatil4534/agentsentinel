"""
Shared data contracts that pass between agents in the pipeline.

Keeping these in one place means every agent (traffic, threat, risk, policy,
approval, audit) imports the same shapes instead of redefining dicts -- it's
the difference between "multi-agent system" and "five functions that happen
to call each other."
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ThreatType(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    PII_ACCESS = "PII_ACCESS"
    SECRET_ACCESS = "SECRET_ACCESS"
    DESTRUCTIVE_ACTION = "DESTRUCTIVE_ACTION"
    PERMISSION_ABUSE = "PERMISSION_ABUSE"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    BLOCK = "BLOCK"


class AgentRequest(BaseModel):
    """Output of the Traffic Agent: a normalized request entering the pipeline."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user: str
    tool: Optional[str] = None
    action: Optional[str] = None
    text: str  # the natural-language intent, e.g. "Delete customer database."
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ThreatFinding(BaseModel):
    """Output of the Threat Detection Agent."""

    threats: list[ThreatType] = Field(default_factory=list)
    matched_phrases: dict[str, list[str]] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    """Output of the Risk Scoring Agent."""

    score: int
    threats: list[ThreatType]


class PolicyDecision(BaseModel):
    """Output of the Policy Gate Agent."""

    decision: Decision
    reason: str


class AuditRecord(BaseModel):
    """What the Audit Agent persists for every request."""

    request_id: str
    user: str
    tool: Optional[str]
    text: str
    threats: list[ThreatType]
    risk_score: int
    decision: Decision
    reason: str
    timestamp: datetime
    resolved_by: Optional[str] = None  # set when a HUMAN_APPROVAL is resolved


class EvaluateRequest(BaseModel):
    """Shape of the body for POST /evaluate."""

    user: str
    text: str
    tool: Optional[str] = None
    action: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class EvaluateResponse(BaseModel):
    """Full pipeline trace returned to the caller -- useful for the demo console."""

    request_id: str
    decision: Decision
    reason: str
    risk_score: int
    threats: list[ThreatType]
    pending_approval: bool

class BenchmarkRequest(BaseModel):
    adapter: str


class BenchmarkResponse(BaseModel):
    agent: str
    total_attacks: int
    detected_attacks: int
    coverage: float
    results: list[dict]