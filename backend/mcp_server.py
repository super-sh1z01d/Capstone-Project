from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from backend.analytics import (
    analyze_funnel,
    calculate_metric_summary,
    correlate_releases,
    rank_segment_drops,
)
from backend.data_loader import load_demo_dataset, validate_dataset
from backend.models import Period

mcp = FastMCP("Activation Drop Investigator Analytics", json_response=True)


def _dataset(dataset_id: str):
    if dataset_id != "demo":
        raise ValueError("Only the built-in demo dataset is available through this MCP server.")
    return load_demo_dataset()


def list_datasets_payload() -> list[dict[str, str]]:
    dataset = load_demo_dataset()
    return [{"dataset_id": dataset.dataset_id, "name": dataset.name}]


def get_schema_payload(dataset_id: str) -> dict[str, list[str]]:
    dataset = _dataset(dataset_id)
    return {
        table_name: sorted(rows[0].keys()) if rows else []
        for table_name, rows in dataset.tables.items()
    }


def data_quality_check_payload(dataset_id: str) -> dict:
    return validate_dataset(_dataset(dataset_id)).model_dump()


def run_metric_query_payload(
    dataset_id: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> dict:
    summary = calculate_metric_summary(
        _dataset(dataset_id),
        Period(start=baseline_start, end=baseline_end),
        Period(start=current_start, end=current_end),
    )
    return summary.model_dump()


def segment_breakdown_payload(
    dataset_id: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> list[dict]:
    return [
        item.model_dump()
        for item in rank_segment_drops(
            _dataset(dataset_id),
            Period(start=baseline_start, end=baseline_end),
            Period(start=current_start, end=current_end),
        )
    ]


def funnel_analysis_payload(
    dataset_id: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> list[dict]:
    return [
        item.model_dump()
        for item in analyze_funnel(
            _dataset(dataset_id),
            Period(start=baseline_start, end=baseline_end),
            Period(start=current_start, end=current_end),
        )
    ]


def release_events_payload(dataset_id: str, current_start: str, current_end: str) -> list[dict]:
    return [
        item.model_dump()
        for item in correlate_releases(
            _dataset(dataset_id), Period(start=current_start, end=current_end)
        )
    ]


@mcp.tool()
def list_datasets() -> list[dict[str, str]]:
    """List available investigation datasets."""
    return list_datasets_payload()


@mcp.tool()
def get_schema(dataset_id: str) -> dict[str, list[str]]:
    """Return table schemas for a dataset."""
    return get_schema_payload(dataset_id)


@mcp.tool()
def data_quality_check(dataset_id: str) -> dict:
    """Validate required tables and columns."""
    return data_quality_check_payload(dataset_id)


@mcp.tool()
def run_metric_query(
    dataset_id: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> dict:
    """Calculate activation metric summary for two periods."""
    return run_metric_query_payload(
        dataset_id, baseline_start, baseline_end, current_start, current_end
    )


@mcp.tool()
def segment_breakdown(
    dataset_id: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> list[dict]:
    """Rank segment drops by contribution score."""
    return segment_breakdown_payload(
        dataset_id, baseline_start, baseline_end, current_start, current_end
    )


@mcp.tool()
def funnel_analysis(
    dataset_id: str,
    baseline_start: str,
    baseline_end: str,
    current_start: str,
    current_end: str,
) -> list[dict]:
    """Analyze onboarding funnel conversion by step."""
    return funnel_analysis_payload(
        dataset_id, baseline_start, baseline_end, current_start, current_end
    )


@mcp.tool()
def release_events(dataset_id: str, current_start: str, current_end: str) -> list[dict]:
    """Find release events close to the current investigation period."""
    return release_events_payload(dataset_id, current_start, current_end)


if __name__ == "__main__":
    mcp.run()
