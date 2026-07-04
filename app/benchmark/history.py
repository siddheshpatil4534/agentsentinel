import json
from pathlib import Path


class BenchmarkHistory:
    def __init__(self):
        self.path = Path("benchmark_history.json")

        if not self.path.exists():
            self.path.write_text("[]")

    def save(self, report):
        history = self.load()
        history.append(report)

        with open(self.path, "w") as f:
            json.dump(history, f, indent=4)

    def load(self):
        with open(self.path, "r") as f:
            return json.load(f)