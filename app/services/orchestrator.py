"""
Orchestrator
------------
Wires Traffic -> Threat Detection -> Risk Scoring -> Policy Gate -> [Human
Approval] -> Audit into a single pipeline call. This is the one object the
API layer talks to; it has no idea any of this is FastAPI underneath.
"""

from __future__ import annotations

from app.agents.approval_agent import HumanApprovalAgent
from app.agents.audit_agent import AuditAgent
from app.agents.policy_agent import PolicyGateAgent
from app.agents.risk_agent import RiskScoringAgent
from app.agents.threat_agent import ThreatDetectionAgent
from app.agents.traffic_agent import TrafficAgent
from app.models.schemas import AuditRecord, Decision, EvaluateResponse


class AgentSentinelPipeline:
    def __init__(self) -> None:
        self.traffic = TrafficAgent()
        self.threat = ThreatDetectionAgent()
        self.risk = RiskScoringAgent()
        self.policy = PolicyGateAgent()
        self.approval = HumanApprovalAgent()
        self.audit = AuditAgent()

    def evaluate(
        self,
        user: str,
        text: str,
        tool: str | None = None,
        action: str | None = None,
        metadata: dict | None = None,
    ) -> EvaluateResponse:
        request = self.traffic.normalize(
            user=user, text=text, tool=tool, action=action, metadata=metadata
        )
        finding = self.threat.detect(request.text)
        assessment = self.risk.score(finding.threats)
        policy = self.policy.decide(assessment.score)

        if policy.decision == Decision.HUMAN_APPROVAL:
            self.approval.queue(request, assessment)

        self.audit.log(
            AuditRecord(
                request_id=request.request_id,
                user=request.user,
                tool=request.tool,
                text=request.text,
                threats=assessment.threats,
                risk_score=assessment.score,
                decision=policy.decision,
                reason=policy.reason,
                timestamp=request.timestamp,
            )
        )

        return EvaluateResponse(
            request_id=request.request_id,
            decision=policy.decision,
            reason=policy.reason,
            risk_score=assessment.score,
            threats=assessment.threats,
            pending_approval=policy.decision == Decision.HUMAN_APPROVAL,
        )

    def resolve_approval(self, request_id: str, approved: bool, resolved_by: str = "human") -> EvaluateResponse:
        pending = self.approval.resolve(request_id)
        if pending is None:
            raise KeyError(f"No pending approval found for request_id={request_id}")

        final_decision = Decision.ALLOW if approved else Decision.BLOCK
        reason = f"Human approval: {'approved' if approved else 'rejected'} by {resolved_by}."
        self.audit.update_resolution(request_id, resolved_by=resolved_by)

        return EvaluateResponse(
            request_id=request_id,
            decision=final_decision,
            reason=reason,
            risk_score=pending["risk"].score,
            threats=pending["risk"].threats,
            pending_approval=False,
        )


# Single shared instance for the FastAPI app to import.
pipeline = AgentSentinelPipeline()
