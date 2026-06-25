from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import date, datetime
from typing import Any

from backend.models import (
    Dataset,
    FunnelFinding,
    MetricSummary,
    Period,
    ReleaseFinding,
    SegmentFinding,
)

FUNNEL_STEPS = ["signup", "workspace_created", "invite_sent", "project_created", "activated"]
SEGMENT_DIMENSIONS = ["company_size", "plan", "acquisition_channel", "region", "browser"]


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value[:10]).date()


def _in_period(value: str, period: Period) -> bool:
    parsed = _parse_date(value)
    return _parse_date(period.start) <= parsed <= _parse_date(period.end)


def calculate_activation_rate(rows: Iterable[dict[str, Any]]) -> float:
    rows = list(rows)
    if not rows:
        return 0.0
    activated = sum(1 for row in rows if bool(row.get("activated_flag")))
    return activated / len(rows)


def _joined_users(dataset: Dataset) -> list[dict[str, Any]]:
    activations = {row["user_id"]: row for row in dataset.tables["activations"]}
    rows = []
    for user in dataset.tables["users"]:
        activation = activations.get(user["user_id"], {})
        rows.append({**user, **activation})
    return rows


def _period_rows(dataset: Dataset, period: Period) -> list[dict[str, Any]]:
    return [row for row in _joined_users(dataset) if _in_period(row["signup_date"], period)]


def calculate_metric_summary(dataset: Dataset, baseline: Period, current: Period) -> MetricSummary:
    baseline_rows = _period_rows(dataset, baseline)
    current_rows = _period_rows(dataset, current)
    baseline_rate = calculate_activation_rate(baseline_rows)
    current_rate = calculate_activation_rate(current_rows)
    absolute_delta = current_rate - baseline_rate
    relative_delta = absolute_delta / baseline_rate if baseline_rate else 0.0
    return MetricSummary(
        baseline_rate=baseline_rate,
        current_rate=current_rate,
        absolute_delta=absolute_delta,
        relative_delta=relative_delta,
        baseline_users=len(baseline_rows),
        current_users=len(current_rows),
    )


def _rate_for_segment(
    rows: list[dict[str, Any]], dimension: str, segment: str
) -> tuple[float, int]:
    segment_rows = [row for row in rows if row.get(dimension) == segment]
    return calculate_activation_rate(segment_rows), len(segment_rows)


def rank_segment_drops(dataset: Dataset, baseline: Period, current: Period) -> list[SegmentFinding]:
    baseline_rows = _period_rows(dataset, baseline)
    current_rows = _period_rows(dataset, current)
    findings: list[SegmentFinding] = []
    for dimension in SEGMENT_DIMENSIONS:
        segments = sorted({row[dimension] for row in baseline_rows + current_rows})
        for segment in segments:
            baseline_rate, _ = _rate_for_segment(baseline_rows, dimension, segment)
            current_rate, current_count = _rate_for_segment(current_rows, dimension, segment)
            absolute_delta = current_rate - baseline_rate
            if current_count == 0:
                continue
            findings.append(
                SegmentFinding(
                    dimension=dimension,
                    segment=segment,
                    baseline_rate=baseline_rate,
                    current_rate=current_rate,
                    absolute_delta=absolute_delta,
                    affected_users=current_count,
                    contribution_score=abs(absolute_delta) * current_count,
                )
            )
    return sorted(findings, key=lambda item: item.contribution_score, reverse=True)


def _users_for_period(dataset: Dataset, period: Period) -> set[str]:
    return {
        row["user_id"] for row in dataset.tables["users"] if _in_period(row["signup_date"], period)
    }


def _step_counts(dataset: Dataset, period: Period) -> dict[str, int]:
    period_users = _users_for_period(dataset, period)
    seen: dict[str, set[str]] = defaultdict(set)
    for event in dataset.tables["onboarding_events"]:
        if event["user_id"] in period_users:
            seen[event["event_name"]].add(event["user_id"])
    return {step: len(seen[step]) for step in FUNNEL_STEPS}


def analyze_funnel(dataset: Dataset, baseline: Period, current: Period) -> list[FunnelFinding]:
    baseline_counts = _step_counts(dataset, baseline)
    current_counts = _step_counts(dataset, current)
    findings: list[FunnelFinding] = []
    for previous_step, step in zip(FUNNEL_STEPS[:-1], FUNNEL_STEPS[1:], strict=True):
        baseline_denominator = baseline_counts.get(previous_step, 0)
        current_denominator = current_counts.get(previous_step, 0)
        baseline_conversion = (
            baseline_counts.get(step, 0) / baseline_denominator if baseline_denominator else 0.0
        )
        current_conversion = (
            current_counts.get(step, 0) / current_denominator if current_denominator else 0.0
        )
        findings.append(
            FunnelFinding(
                step=step,
                baseline_conversion=baseline_conversion,
                current_conversion=current_conversion,
                absolute_delta=current_conversion - baseline_conversion,
            )
        )
    return sorted(findings, key=lambda item: item.absolute_delta)


def correlate_releases(
    dataset: Dataset, current: Period, window_days: int = 10
) -> list[ReleaseFinding]:
    current_start = _parse_date(current.start)
    findings: list[ReleaseFinding] = []
    for release in dataset.tables["releases"]:
        release_date = _parse_date(release["release_date"])
        days_from_current_start = (release_date - current_start).days
        if abs(days_from_current_start) <= window_days:
            findings.append(
                ReleaseFinding(
                    release_id=release["release_id"],
                    release_date=release["release_date"],
                    component=release["component"],
                    description=release["description"],
                    days_from_current_start=days_from_current_start,
                )
            )
    return findings
