from app.agents.redteam_agent import RedTeamAgent
from app.services.orchestrator import pipeline


class RedTeamRunner:
    def __init__(self):
        self.agent = RedTeamAgent.from_directory()

    def run(self):
        results = []

        attacks = self.agent.to_pipeline_format()

        for attack in attacks:
            response = pipeline.evaluate(
                user=attack["user"],
                text=attack["text"],
                tool=attack["tool"],
                action=attack["action"],
                metadata=attack["metadata"],
            )

            results.append(
                {
                    "attack_id": attack["metadata"]["attack_id"],
                    "category": attack["metadata"]["category"],
                    "decision": response.decision.value,
                    "risk_score": response.risk_score,
                    "threats": [t.value for t in response.threats],
                }
            )

        return results
    