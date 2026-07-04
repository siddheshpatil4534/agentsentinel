from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """
    Every agent adapter must implement this interface.
    """

    name: str

    @abstractmethod
    def invoke(self, prompt: str):
        """
        Send a prompt to the agent and return its response.
        """
        pass

    def metadata(self):
        """
        Optional information about the adapter.
        """
        return {
            "name": self.name,
        }