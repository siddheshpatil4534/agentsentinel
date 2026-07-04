class Leaderboard:
    def __init__(self):
        self.results = []

    def add(self, report):
        self.results.append(report)

    def rankings(self):
        return sorted(
            self.results,
            key=lambda r: r["coverage"],
            reverse=True,
        )