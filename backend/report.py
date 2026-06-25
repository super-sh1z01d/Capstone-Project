from __future__ import annotations

from backend.models import InvestigationReport


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown_report(report: InvestigationReport) -> str:
    lines = [
        "# Activation Drop Investigation",
        "",
        "## Executive Summary",
        "",
        report.executive_summary,
        "",
        "## Metric Summary",
        "",
        f"- Baseline activation: {_pct(report.metric_summary.baseline_rate)}",
        f"- Current activation: {_pct(report.metric_summary.current_rate)}",
        f"- Absolute delta: {_pct(report.metric_summary.absolute_delta)}",
        f"- Relative delta: {_pct(report.metric_summary.relative_delta)}",
        "",
        "## Evidence Cards",
        "",
    ]
    for card in report.evidence_cards:
        lines.extend(
            [
                f"### {card.title}",
                "",
                f"- Claim type: {card.claim_type}",
                f"- Confidence: {card.confidence}",
                f"- Summary: {card.summary}",
                "- Evidence:",
                *[f"  - {item}" for item in card.evidence],
                "",
            ]
        )
    if report.ai_synthesis:
        lines.extend(["## Gemini Synthesis", "", report.ai_synthesis, ""])
    lines.extend(["## Agent Skills", ""])
    for skill in report.skills_used:
        lines.extend(
            [
                f"### {skill.name}",
                "",
                f"- Skill ID: {skill.skill_id}",
                f"- Tools: {', '.join(skill.tool_names)}",
                f"- Output contract: {skill.output_contract}",
                "",
            ]
        )
    lines.extend(["## Ranked Hypotheses", ""])
    lines.extend(
        [f"{index}. {item}" for index, item in enumerate(report.ranked_hypotheses, start=1)]
    )
    lines.extend(["", "## Recommended Actions", ""])
    lines.extend(
        [f"{index}. {item}" for index, item in enumerate(report.recommended_actions, start=1)]
    )
    lines.extend(["", "## Limitations", ""])
    lines.extend([f"- {item}" for item in report.limitations])
    return "\n".join(lines).strip() + "\n"
