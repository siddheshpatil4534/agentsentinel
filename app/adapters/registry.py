class AdapterRegistry:
    def __init__(self):
        self._adapters = {}

    def register(self, adapter):
        self._adapters[adapter.name] = adapter

    def get(self, name):
        return self._adapters.get(name)

    def list(self):
        return list(self._adapters.keys())