"""
Threat Detection Agent
----------------------
MVP implementation: regex/keyword pattern matching against the request text.
This is intentionally swappable -- the whole point of structuring it as one
agent with a single `detect()` method is that Day 3 work (moving this into a
proper ADK Agent Skill backed by Gemini classification instead of regex) only
touches this one file. Everything downstream consumes `ThreatFinding` either way.

Patterns are informed by the STRIDE-style threat categories from the original
design: prompt injection, data exfiltration, PII access, secret access, and
destructive actions.
"""

from __future__ import annotations

import re

from app.models.schemas import ThreatFinding, ThreatType

# Each pattern is matched case-insensitively against the raw request text.
PATTERNS: dict[ThreatType, list[str]] = {
    ThreatType.PROMPT_INJECTION: [
        r"\[system\]",
        r"new directive",
        r"supersedes all prior rules",
        r"ignore (all |any |the )?(previous |prior )?instructions",
        r"disregard (all |any |the )?(previous |prior )?instructions",
        r"forget (all |your |the )?(previous |prior )?instructions",
        r"new instructions",
        r"system prompt",
        r"you are now",
        r"jailbreak",
        r"bypass (the )?(safety|filter|policy|restrictions?)",
        r"act as (?:an?|the) unrestricted",
    ],
    ThreatType.DATA_EXFILTRATION: [
        r"export .*?(database|customers?|users?|data|table)",
        r"download all",
        r"dump .*?(database|table|data)",
        r"send (all |the )?(data|database|records?) to",
        r"extract (all |the )?(data|database|records?)",
        r"exfiltrate",
    ],
    ThreatType.PII_ACCESS: [
        r"salar(y|ies)",
        r"\bssn\b",
        r"social security",
        r"personal (data|information)\b",
        r"employee records?",
        r"customer (data|records?|information|pii)\b",
        r"credit card",
        r"\bpii\b",
    ],
    ThreatType.SECRET_ACCESS: [
        r"api[\s_-]?keys?",
        r"\bpasswords?\b",
        r"\bcredentials?\b",
        r"\bsecrets?\b",
        r"access token",
        r"private key",
    ],
    ThreatType.DESTRUCTIVE_ACTION: [
    r"delete (all |the )?(customers?|database|tables?|records?|data)",
    r"drop .*?(table|database)",
    r"truncate",
    r"wipe (all |the )?(data|database)",
    r"remove (all |the )?(records?|data|customers?)",
    r"format (the )?(disk|drive)",
    ],
    ThreatType.PERMISSION_ABUSE: [
    r"grant.*admin",
    r"admin access",
    r"super[- ]admin",
    r"elevate.*role",
    r"elevate.*privileges",
    r"elevate.*admin",
    r"bypass.*approval",
    r"bypass.*workflow",
    r"bypass.*authorization",
    r"disable permissions",
    r"administrator access",
    r"change.*role.*admin",
    r"make.*admin",
    r"give.*admin rights",
    ],
}

_COMPILED: dict[ThreatType, list[re.Pattern]] = {
    threat: [re.compile(p, re.IGNORECASE) for p in patterns]
    for threat, patterns in PATTERNS.items()
}


class ThreatDetectionAgent:
    def detect(self, text: str) -> ThreatFinding:
        found: list[ThreatType] = []
        matched_phrases: dict[str, list[str]] = {}

        for threat, patterns in _COMPILED.items():
            hits = [m.group(0) for p in patterns if (m := p.search(text))]
            if hits:
                found.append(threat)
                matched_phrases[threat.value] = hits

        return ThreatFinding(threats=found, matched_phrases=matched_phrases)
