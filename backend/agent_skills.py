from __future__ import annotations

from backend.models import AgentSkill

INVESTIGATION_SKILLS = [
    AgentSkill(
        skill_id="metric_drop_quantification",
        name="Metric Drop Quantification",
        description="Compare baseline and current activation-rate windows and size the drop.",
        tool_names=["run_metric_query"],
        output_contract=(
            "MetricSummary with baseline rate, current rate, absolute delta, and volume."
        ),
    ),
    AgentSkill(
        skill_id="segment_driver_detection",
        name="Segment Driver Detection",
        description="Rank customer segments by their contribution to the observed activation drop.",
        tool_names=["segment_breakdown"],
        output_contract="Ordered SegmentFinding list with contribution scores and affected users.",
    ),
    AgentSkill(
        skill_id="funnel_step_diagnosis",
        name="Funnel Step Diagnosis",
        description="Identify the onboarding funnel step with the largest conversion loss.",
        tool_names=["funnel_analysis"],
        output_contract="Ordered FunnelFinding list with baseline/current conversion deltas.",
    ),
    AgentSkill(
        skill_id="release_correlation_review",
        name="Release Correlation Review",
        description="Check release timing near the affected period without overstating causality.",
        tool_names=["release_events"],
        output_contract="ReleaseFinding list with timing offsets and supporting context.",
    ),
    AgentSkill(
        skill_id="claim_guardrail_review",
        name="Claim Guardrail Review",
        description=(
            "Label findings by evidence strength and downgrade unsupported causal language."
        ),
        tool_names=["data_quality_check"],
        output_contract="Evidence cards with observed, likely, or needs_verification claim types.",
    ),
]


def skill_manifest() -> list[AgentSkill]:
    return list(INVESTIGATION_SKILLS)
