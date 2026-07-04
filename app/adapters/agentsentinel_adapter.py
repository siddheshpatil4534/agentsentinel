from app.adapters.base import BaseAdapter
from app.services.orchestrator import pipeline


class AgentSentinelAdapter(BaseAdapter):
    """
    Adapter around the existing AgentSentinel pipeline.
    """

    name = "agentsentinel"

    def invoke(self, prompt: str):
        response = pipeline.evaluate(
            user="redteam_agent",
            text=prompt,
            tool=None,
            action=None,
            metadata={}
        )

        return response

    def metadata(self):
        return {
            "name": self.name,
            "framework": "Custom",
            "description": "AgentSentinel security pipeline",
        }