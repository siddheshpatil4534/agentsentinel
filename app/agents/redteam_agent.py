"""
RedTeamAgent v1
---------------
Maintains a library of attack payloads and answers three questions:

    1. What attacks do you have?            -> get_all()
    2. What attacks do you have for X?      -> get_by_category(category)
    3. Give me that in a shape my pipeline understands -> to_pipeline_format()

Deliberately does NOT call your pipeline, generate new payloads, or judge
whether an attack "succeeded" — that's the next increment (a separate
RedTeamRunner/Evaluator that takes this agent's output and actually drives
your existing AgentSentinelPipeline). Keeping that out of this class means
RedTeamAgent stays a pure, dependency-free library you can unit test in
milliseconds, and the runner can be swapped or rewritten later without
touching this file at all.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from app.models.redteam_schemas import AttackPayload
from app.models.schemas import ThreatType
from app.redteam.loader import DEFAULT_PAYLOADS_DIR, load_payloads


class RedTeamAgent:
    def __init__(self, payloads: list[AttackPayload]):
        self._payloads: list[AttackPayload] = list(payloads)

        self._by_category: dict[ThreatType, list[AttackPayload]] = defaultdict(list)
        for payload in self._payloads:
            self._by_category[payload.category].append(payload)

    @classmethod
    def from_directory(cls, directory: str | Path = DEFAULT_PAYLOADS_DIR) -> "RedTeamAgent":
        """Convenience constructor — load straight from the YAML library."""
        return cls(load_payloads(directory))

    # -- the 3 required methods ----------------------------------------------

    def get_all(self) -> list[AttackPayload]:
        return list(self._payloads)

    def get_by_category(self, category: ThreatType | str) -> list[AttackPayload]:
        if isinstance(category, str):
            category = ThreatType(category)
        return list(self._by_category.get(category, []))

    def to_pipeline_format(
        self,
        payloads: list[AttackPayload] | None = None,
        user: str = "redteam_agent",
    ) -> list[dict]:
        """
        Shapes payloads to match your pipeline's EvaluateRequest fields
        (user, text, tool, action, metadata) so a future runner can do:

            for req in redteam.to_pipeline_format():
                result = pipeline.evaluate(**req)

        without RedTeamAgent ever importing or calling the pipeline itself.
        """
        target = payloads if payloads is not None else self._payloads
        return [
            {
                "user": user,
                "text": p.text,
                "tool": p.suggested_tool,
                "action": p.suggested_action,
                "metadata": {
                    "attack_id": p.id,
                    "attack_name": p.name,
                    "category": p.category.value,
                    "severity": p.severity,
                },
            }
            for p in target
        ]

    # -- small extras that fall out almost for free ---------------------------

    def categories(self) -> list[ThreatType]:
        """Which categories actually have at least one payload loaded."""
        return list(self._by_category.keys())

    def count_by_category(self) -> dict[str, int]:
        return {cat.value: len(items) for cat, items in self._by_category.items()}
