import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.redteam_agent import RedTeamAgent
from app.models.schemas import ThreatType


def make_agent() -> RedTeamAgent:
    return RedTeamAgent.from_directory()


def test_loads_all_five_categories():
    agent = make_agent()
    counts = agent.count_by_category()
    assert set(counts.keys()) == {
    "PROMPT_INJECTION",
    "SECRET_ACCESS",
    "DATA_EXFILTRATION",
    "DESTRUCTIVE_ACTION",
    "PERMISSION_ABUSE",
    "PII_ACCESS",

    }


def test_get_all_returns_every_payload():
    agent = make_agent()
    all_payloads = agent.get_all()
    assert len(all_payloads) == 18  # 3 per category x 5 categories
    assert len({p.id for p in all_payloads}) == 18  # all ids unique


def test_get_by_category_filters_correctly():
    agent = make_agent()
    pi_only = agent.get_by_category(ThreatType.PROMPT_INJECTION)
    assert len(pi_only) == 3
    assert all(p.category == ThreatType.PROMPT_INJECTION for p in pi_only)


def test_get_by_category_accepts_string():
    agent = make_agent()
    by_string = agent.get_by_category("SECRET_ACCESS")
    by_enum = agent.get_by_category(ThreatType.SECRET_ACCESS)
    assert [p.id for p in by_string] == [p.id for p in by_enum]


def test_get_by_category_pii_access():
    agent = make_agent()
    assert len(agent.get_by_category(ThreatType.PII_ACCESS)) == 3


def test_to_pipeline_format_shape():
    agent = make_agent()
    requests = agent.to_pipeline_format()
    assert len(requests) == 18
    sample = requests[0]
    assert set(sample.keys()) == {"user", "text", "tool", "action", "metadata"}
    assert sample["metadata"]["attack_id"]
    assert sample["metadata"]["category"]


def test_to_pipeline_format_accepts_filtered_subset():
    agent = make_agent()
    destructive = agent.get_by_category(ThreatType.DESTRUCTIVE_ACTION)
    requests = agent.to_pipeline_format(destructive)
    assert len(requests) == 3
    assert all(r["metadata"]["category"] == "DESTRUCTIVE_ACTION" for r in requests)


def test_agent_works_from_in_memory_list_no_disk_io():
    from app.models.redteam_schemas import AttackPayload

    payload = AttackPayload(
        id="TEST-001",
        category=ThreatType.PROMPT_INJECTION,
        name="Unit test payload",
        text="irrelevant",
    )
    agent = RedTeamAgent([payload])
    assert agent.get_all() == [payload]
    assert agent.get_by_category(ThreatType.PROMPT_INJECTION) == [payload]
