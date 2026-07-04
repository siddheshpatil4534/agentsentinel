"""
Traffic Agent
-------------
First stop in the pipeline. Takes whatever the Business AI Agent sends —
a tool call, a free-text intent, or both — and normalizes it into an
AgentRequest every downstream agent can rely on.
"""

from app.models.schemas import AgentRequest


class TrafficAgent:
    def normalize(
        self,
        user: str,
        text: str,
        tool: str | None = None,
        action: str | None = None,
        metadata: dict | None = None,
    ) -> AgentRequest:
        return AgentRequest(
            user=user,
            text=text.strip(),
            tool=tool,
            action=action,
            metadata=metadata or {},
        )
