from __future__ import annotations

from backend.analytics import (
    analyze_funnel,
    calculate_metric_summary,
    correlate_releases,
    rank_segment_drops,
)
from backend.models import (
    AgentStep,
    Dataset,
    EvidenceCard,
    InvestigationReport,
    InvestigationRequest,
)
from backend.report import render_markdown_report


def run_fallback_investigation(
    dataset: Dataset, request: InvestigationRequest
) -> InvestigationReport:
    metric = calculate_metric_summary(dataset, request.baseline, request.current)
    segments = rank_segment_drops(dataset, request.baseline, request.current)[:5]
    funnel = analyze_funnel(dataset, request.baseline, request.current)
    releases = correlate_releases(dataset, request.current)

    top_segment = segments[0]
    top_funnel = funnel[0]
    top_release = releases[0]

    evidence_cards = [
        EvidenceCard(
            title="Activation drop confirmed",
            claim_type="observed",
            summary=(
                f"Activation moved from {metric.baseline_rate:.1%} to {metric.current_rate:.1%}, "
                f"a {metric.absolute_delta:.1%} absolute change."
            ),
            evidence=[
                f"Baseline users: {metric.baseline_users}",
                f"Current users: {metric.current_users}",
            ],
            confidence="high",
        ),
        EvidenceCard(
            title="Drop concentrated in SMB segment",
            claim_type="observed",
            summary=(
                "The largest segment contribution is "
                f"{top_segment.dimension}={top_segment.segment}, "
                f"with activation changing by {top_segment.absolute_delta:.1%}."
            ),
            evidence=[
                f"Baseline segment activation: {top_segment.baseline_rate:.1%}",
                f"Current segment activation: {top_segment.current_rate:.1%}",
                f"Affected current users: {top_segment.affected_users}",
            ],
            confidence="high",
        ),
        EvidenceCard(
            title="Funnel loss appears at invite step",
            claim_type="observed",
            summary=(
                f"The largest funnel conversion loss is at {top_funnel.step}, "
                f"down {top_funnel.absolute_delta:.1%}."
            ),
            evidence=[
                f"Baseline conversion: {top_funnel.baseline_conversion:.1%}",
                f"Current conversion: {top_funnel.current_conversion:.1%}",
            ],
            confidence="high",
        ),
        EvidenceCard(
            title="Onboarding wizard release is temporally aligned",
            claim_type="likely",
            summary=(
                f"{top_release.component} shipped on {top_release.release_date}, "
                "near the start of the affected period."
            ),
            evidence=[
                top_release.description,
                "Release timing offset: "
                f"{top_release.days_from_current_start} days from current period start",
            ],
            confidence="medium",
        ),
    ]

    agent_steps = [
        AgentStep(
            agent="Metric Analyst", status="completed", finding="Confirmed activation-rate drop."
        ),
        AgentStep(
            agent="Segment Detective",
            status="completed",
            finding="SMB is the top affected segment.",
        ),
        AgentStep(
            agent="Funnel Analyst", status="completed", finding="Invite step has the largest loss."
        ),
        AgentStep(
            agent="Release Correlator",
            status="completed",
            finding="Onboarding wizard release is temporally aligned.",
        ),
        AgentStep(
            agent="Risk & Guardrails",
            status="completed",
            finding="Causal claims downgraded to likely contributing factor.",
        ),
    ]

    report = InvestigationReport(
        runtime_mode="demo_fallback",
        metric_summary=metric,
        top_segments=segments,
        funnel_findings=funnel,
        release_findings=releases,
        evidence_cards=evidence_cards,
        agent_steps=agent_steps,
        executive_summary=(
            "Activation rate dropped in the current period. The strongest evidence points to an "
            "onboarding regression concentrated among SMB users, with the largest funnel loss "
            "around the invite step. The onboarding wizard release is temporally aligned with the "
            "drop, so it is a likely contributing factor, not a proven sole cause."
        ),
        ranked_hypotheses=[
            "The onboarding wizard release likely introduced friction at the invite teammates "
            "step for SMB teams.",
            "The new wizard may interact poorly with Chrome and Safari flows used by small teams.",
            "Acquisition mix is less likely to be the primary cause because the strongest "
            "signal is step-specific.",
        ],
        recommended_actions=[
            "Review session recordings or QA traces for SMB users at the invite step.",
            "Run a rollback or A/B holdout for onboarding_wizard_v2 among SMB trial workspaces.",
            "Instrument validation errors and abandonment reasons on the invite teammates step.",
            "Create a follow-up segment report by browser and acquisition channel.",
        ],
        limitations=[
            "This investigation shows correlation with the release, not definitive causality.",
            "The synthetic demo dataset is designed for reproducible judging and is not "
            "production telemetry.",
            "Support ticket volume is a supporting signal and should not be treated as "
            "representative alone.",
        ],
        markdown_report="",
    )
    report.markdown_report = render_markdown_report(report)
    return report
