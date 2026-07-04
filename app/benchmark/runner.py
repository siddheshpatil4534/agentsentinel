from app.redteam.loader import load_payloads


class BenchmarkRunner:
    def __init__(self, adapter):
        self.adapter = adapter

    def run(self):
        payloads = load_payloads()

        total = len(payloads)
        detected = 0
        results = []

        for payload in payloads:
            response = self.adapter.invoke(payload.text)

            threats = []
            decision = "UNKNOWN"

            if hasattr(response, "threats"):
                threats = [
                    t.value if hasattr(t, "value") else str(t)
                    for t in response.threats
                ]

            if hasattr(response, "decision"):
                decision = (
                    response.decision.value
                    if hasattr(response.decision, "value")
                    else str(response.decision)
                )

            if threats:
                detected += 1

            results.append(
                {
                    "attack_id": payload.id,
                    "decision": decision,
                    "threats": threats,
                }
            )

        coverage = round((detected / total) * 100, 2)

        return {
            "agent": self.adapter.name,
            "total_attacks": total,
            "detected_attacks": detected,
            "coverage": coverage,
            "results": results,
        }