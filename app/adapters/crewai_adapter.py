from app.adapters.base import BaseAdapter


class CrewAIAdapter(BaseAdapter):
    name = "crewai"

    def invoke(self, prompt: str):
        raise NotImplementedError(
            "CrewAI adapter not implemented yet."
        )