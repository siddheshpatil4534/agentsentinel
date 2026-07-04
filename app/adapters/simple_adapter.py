from app.adapters.base import BaseAdapter


class SimpleAdapter(BaseAdapter):
    """
    A simple demo agent used for testing the adapter system.
    """

    name = "simple"

    def invoke(self, prompt: str):
        return f"SimpleAgent received: {prompt}"

    def metadata(self):
        return {
            "name": self.name,
            "framework": "Demo",
            "description": "Simple test adapter",
        }