"""
Risk Scoring Agent
------------------
Turns a list of detected threats into a single 0-100 risk score.

Scoring is severity-led rather than purely additive: the score starts at the
weight of the single most severe threat found, then adds a smaller bump for
every additional distinct threat category present. A request that trips three
low-severity patterns isn't automatically as dangerous as one destructive
action -- but stacking threats should still push the score up.
"""

from __future__ import annotations

from app.models.schemas import RiskAssessment, ThreatType

WEIGHTS: dict[ThreatType, int] = {
    ThreatType.PROMPT_INJECTION: 50,
    ThreatType.DATA_EXFILTRATION: 45,
    ThreatType.PII_ACCESS: 45,
    ThreatType.SECRET_ACCESS: 65,
    ThreatType.DESTRUCTIVE_ACTION: 80,
    ThreatType.PERMISSION_ABUSE: 60,
}

ADDITIONAL_THREAT_BUMP = 10  # per extra distinct threat type beyond the first


class RiskScoringAgent:
    def score(self, threats: list[ThreatType]) -> RiskAssessment:
        if not threats:
            return RiskAssessment(score=0, threats=[])

        base = max(WEIGHTS[t] for t in threats)
        bump = ADDITIONAL_THREAT_BUMP * (len(threats) - 1)
        score = min(100, base + bump)

        return RiskAssessment(score=score, threats=threats)
