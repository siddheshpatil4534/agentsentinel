import json
from pathlib import Path

from app.services.supabase_client import get_supabase_client


class RedTeamReport:
    def __init__(self, results):
        self.results = results

    def generate(self):
        total = len(self.results)

        detected = sum(
            1 for r in self.results
            if len(r["threats"]) > 0
        )

        blocked = sum(
            1 for r in self.results
            if r["decision"] == "BLOCK"
        )

        human_review = sum(
            1 for r in self.results
            if r["decision"] == "HUMAN_APPROVAL"
        )

        allowed = sum(
            1 for r in self.results
            if r["decision"] == "ALLOW"
        )

        coverage = round((detected / total) * 100, 2)

        risk_distribution = {
            "BLOCK": blocked,
            "HUMAN_APPROVAL": human_review,
            "ALLOW": allowed,
        }

        category_breakdown = {}

        for r in self.results:
            category = r["category"]
            category_breakdown[category] = (
                category_breakdown.get(category, 0) + 1
            )

        recommendations = []

        if human_review:
            recommendations.append(
                "Review all HUMAN_APPROVAL cases before production deployment."
            )

        if blocked:
            recommendations.append(
                "Destructive actions were successfully blocked."
            )

        if allowed:
            recommendations.append(
                "Some attacks were allowed and require additional security rules."
            )

        if detected < total:
            recommendations.append(
                "Some attacks were missed and require new detection patterns."
            )

        security_score = round((detected / total) * 100)

        return {
            "total_attacks": total,
            "detected_attacks": detected,
            "missed_attacks": total - detected,
            "coverage_percent": coverage,
            "security_score": security_score,
            "blocked": blocked,
            "human_approval": human_review,
            "allowed": allowed,
            "risk_distribution": risk_distribution,
            "category_breakdown": category_breakdown,
            "recommendations": recommendations,
            "results": self.results,
        }

    def save(self, filename="redteam_report.json"):
        report = self.generate()

        Path(filename).write_text(
            json.dumps(report, indent=4)
        )

        client = get_supabase_client()

        if client:
            try:
                client.table("redteam_results").insert({
                    "attack_name": "Red Team Evaluation",
                    "payload": f"{report['detected_attacks']}/{report['total_attacks']} attacks detected",
                    "success": report["security_score"] == 100,
                    "score": report["security_score"],
                    "recommendation": "\n".join(report["recommendations"])
                }).execute()

                print("Saved Red Team results to Supabase!")

            except Exception as e:
                print("Failed to save Red Team results:", e)

        return filename