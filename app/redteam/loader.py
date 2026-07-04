"""
Loads AttackPayload entries from the payloads/ directory.

Kept separate from RedTeamAgent on purpose: the agent shouldn't know or care
whether payloads come from YAML files, a database, or a hardcoded list in a
unit test. That separation is what makes RedTeamAgent trivially testable
(construct it with a plain Python list, no disk I/O) and what makes adding a
6th or 20th category a data change instead of a code change.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.models.redteam_schemas import AttackPayload

DEFAULT_PAYLOADS_DIR = Path(__file__).resolve().parent / "payloads"


def load_payloads(directory: str | Path = DEFAULT_PAYLOADS_DIR) -> list[AttackPayload]:
    directory = Path(directory)
    payloads: list[AttackPayload] = []
    seen_ids: set[str] = set()

    for file in sorted(directory.glob("*.yaml")) + sorted(directory.glob("*.yml")):
        raw = yaml.safe_load(file.read_text()) or []
        for entry in raw:
            payload = AttackPayload(**entry)
            if payload.id in seen_ids:
                raise ValueError(f"Duplicate payload id '{payload.id}' found in {file.name}")
            seen_ids.add(payload.id)
            payloads.append(payload)

    return payloads
