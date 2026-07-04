"""
Policy Gate Agent
-----------------
Maps a risk score onto a decision using fixed thresholds:

    0-30   -> ALLOW
    31-70  -> HUMAN_APPROVAL
    71-100 -> BLOCK

Thresholds are intentionally just constants here so they're trivial to tune
once you have real usage data instead of four demo scenarios.
"""

from __future__ import annotations

from app.models.schemas import Decision, PolicyDecision

ALLOW_MAX = 30
HUMAN_APPROVAL_MAX = 70


class PolicyGateAgent:
    def decide(self, score: int) -> PolicyDecision:
        if score <= ALLOW_MAX:
            return PolicyDecision(
                decision=Decision.ALLOW,
                reason=f"Risk score {score} is within the auto-allow threshold ({ALLOW_MAX}).",
            )
        if score <= HUMAN_APPROVAL_MAX:
            return PolicyDecision(
                decision=Decision.HUMAN_APPROVAL,
                reason=f"Risk score {score} falls in the human-approval band "
                f"({ALLOW_MAX + 1}-{HUMAN_APPROVAL_MAX}).",
            )
        return PolicyDecision(
            decision=Decision.BLOCK,
            reason=f"Risk score {score} exceeds the block threshold ({HUMAN_APPROVAL_MAX}).",
        )
