from app.adapters.base import BaseAdapter


class LangChainAdapter(BaseAdapter):
    name = "langchain"

    def invoke(self, prompt: str):
        raise NotImplementedError(
            "LangChain adapter not implemented yet."
        )