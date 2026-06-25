from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Dataset(BaseModel):
    dataset_id: str
    name: str
    tables: dict[str, list[dict[str, Any]]]


class DataQualityResult(BaseModel):
    valid: bool
    issues: list[str] = Field(default_factory=list)
    row_counts: dict[str, int] = Field(default_factory=dict)


class Period(BaseModel):
    start: str
    end: str


class InvestigationRequest(BaseModel):
    dataset_id: str = "demo"
    metric: str = "activation_rate"
    baseline: Period = Period(start="2026-04-01", end="2026-04-20")
    current: Period = Period(start="2026-05-01", end="2026-05-20")


class MetricSummary(BaseModel):
    baseline_rate: float
    current_rate: float
    absolute_delta: float
    relative_delta: float
    baseline_users: int
    current_users: int


class SegmentFinding(BaseModel):
    dimension: str
    segment: str
    baseline_rate: float
    current_rate: float
    absolute_delta: float
    affected_users: int
    contribution_score: float


class FunnelFinding(BaseModel):
    step: str
    baseline_conversion: float
    current_conversion: float
    absolute_delta: float


class ReleaseFinding(BaseModel):
    release_id: str
    release_date: str
    component: str
    description: str
    days_from_current_start: int


class EvidenceCard(BaseModel):
    title: str
    claim_type: Literal["observed", "likely", "needs_verification"]
    summary: str
    evidence: list[str]
    confidence: Literal["high", "medium", "low"]


class AgentStep(BaseModel):
    agent: str
    status: Literal["completed", "skipped"]
    finding: str


class InvestigationReport(BaseModel):
    runtime_mode: Literal["demo_fallback", "gemini_adk"]
    metric_summary: MetricSummary
    top_segments: list[SegmentFinding]
    funnel_findings: list[FunnelFinding]
    release_findings: list[ReleaseFinding]
    evidence_cards: list[EvidenceCard]
    agent_steps: list[AgentStep]
    executive_summary: str
    ranked_hypotheses: list[str]
    recommended_actions: list[str]
    limitations: list[str]
    markdown_report: str
