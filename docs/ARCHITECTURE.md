# Architecture Notes

## Pipeline

```
Business AI Agent
       │
       ▼
 Traffic Agent          normalize the raw request into AgentRequest
       │
       ▼
 Threat Detection Agent  pattern-match for PROMPT_INJECTION / DATA_EXFILTRATION /
       │                 PII_ACCESS / SECRET_ACCESS / DESTRUCTIVE_ACTION
       ▼
 Risk Scoring Agent      threats -> 0-100 score (severity-led, see risk_agent.py)
       │
       ▼
 Policy Gate Agent       0-30 ALLOW · 31-70 HUMAN_APPROVAL · 71-100 BLOCK
       │
   ┌───┴────┐
   │        │
 ALLOW/   HUMAN_APPROVAL
 BLOCK        │
   │      Human Approval Agent (holds it until a person approves/rejects)
   │          │
   └────┬─────┘
        ▼
   Audit Agent          persists request, threats, score, decision, reason, timestamp
```

Every agent is a single class with one public method (`normalize`, `detect`,
`score`, `decide`, `queue`/`resolve`, `log`) so each can be swapped or unit
tested independently. `app/services/orchestrator.py` is the only file that
knows the order they run in.

## Threat model (STRIDE-informed)

The five threat categories map onto STRIDE roughly like this:

| Threat type | STRIDE category | What it catches |
|---|---|---|
| `PROMPT_INJECTION` | Spoofing / Tampering | Attempts to override the agent's instructions or persona |
| `DATA_EXFILTRATION` | Information Disclosure | Bulk export/download/dump requests |
| `PII_ACCESS` | Information Disclosure | Requests touching salaries, SSNs, customer PII |
| `SECRET_ACCESS` | Information Disclosure / Elevation of Privilege | Requests for API keys, passwords, tokens |
| `DESTRUCTIVE_ACTION` | Denial of Service / Tampering | Delete/drop/wipe/truncate-style requests |

If you already have a full STRIDE threat model from the Day 4 work on the
Shopping Assistant Agent, drop it in this folder (`docs/stride-model.md`) and
cross-reference these five categories against it — it's the same threat
surface, just generalized from one agent's tool calls to any agent's tool calls.

## Known limitations of the MVP threat detector

This is intentionally a regex/keyword matcher, not a model. It will:

- Miss paraphrased or obfuscated attacks ("disregard everything above" might
  not match every pattern variant).
- Occasionally false-positive on legitimate requests that happen to contain a
  trigger word (e.g. "what's our password reset policy?" contains "password").

The fix for both is the same: replace `ThreatDetectionAgent.detect()` with a
Gemini-based classifier (via `google-genai` or an ADK Agent Skill) that takes
the request text and returns the same `ThreatFinding` shape. Nothing else in
the pipeline needs to change — that's the whole point of the agent boundary.

## Supabase schema (optional persistent audit log)

```sql
create table audit_log (
    request_id   text primary key,
    user_id      text,
    tool         text,
    text         text,
    threats      text[],
    risk_score   int,
    decision     text,
    reason       text,
    timestamp    timestamptz,
    resolved_by  text
);
```

Without `SUPABASE_URL`/`SUPABASE_KEY` set, `AuditAgent` writes to a local
`audit_log.json` file instead — the app behaves identically either way.
