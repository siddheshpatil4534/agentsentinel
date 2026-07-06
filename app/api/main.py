"""
AgentSentinel API
------------------
Thin FastAPI layer over AgentSentinelPipeline. Serves the static demo console
at "/" so the whole thing is clickable for a demo video without needing React.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    AuditRecord,
    BenchmarkRequest,
    BenchmarkResponse,
)
from app.services.orchestrator import pipeline
from app.redteam.runner import RedTeamRunner
from app.redteam.report import RedTeamReport
from app.adapters.setup import registry
from app.benchmark.runner import BenchmarkRunner
from app.benchmark.history import BenchmarkHistory

app = FastAPI(
    title="AgentSentinel",
    description="Multi-agent security & governance gateway for AI agents.",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(body: EvaluateRequest) -> EvaluateResponse:
    return pipeline.evaluate(
        user=body.user,
        text=body.text,
        tool=body.tool,
        action=body.action,
        metadata=body.metadata,
    )


@app.post("/approve/{request_id}", response_model=EvaluateResponse)
def approve(request_id: str, approved: bool) -> EvaluateResponse:
    try:
        return pipeline.resolve_approval(request_id, approved=approved)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/pending", response_model=list[dict])
def pending() -> list[dict]:
    return [
        {
            "request_id": p["request"].request_id,
            "user": p["request"].user,
            "text": p["request"].text,
            "risk_score": p["risk"].score,
        }
        for p in pipeline.approval.get_pending()
    ]


@app.get("/audit-log", response_model=list[AuditRecord])
def audit_log() -> list[AuditRecord]:
    return pipeline.audit.get_log()

@app.post("/redteam/run")
def run_redteam():
    runner = RedTeamRunner()
    results = runner.run()

    report = RedTeamReport(results)
    final_report = report.generate()

    report.save()

    return final_report
@app.post(
    "/benchmark/run",
    response_model=BenchmarkResponse,
)
def run_benchmark(
    body: BenchmarkRequest,
):
    adapter = registry.get(body.adapter)

    if adapter is None:
        raise HTTPException(
            status_code=404,
            detail=f"Adapter '{body.adapter}' not found",
        )

    runner = BenchmarkRunner(adapter)

    report = runner.run()

    history = BenchmarkHistory()
    history.save(report)

    return report

@app.get("/benchmark/history")
def benchmark_history():
    history = BenchmarkHistory()
    return history.load()
from app.services.integration_status import get_all_statuses

@app.get("/integrations/status")
def integrations_status():
    return get_all_statuses()