from backend.analytics import (
    analyze_funnel,
    calculate_activation_rate,
    calculate_metric_summary,
    correlate_releases,
    rank_segment_drops,
)
from backend.data_loader import load_demo_dataset
from backend.models import Period

BASELINE = Period(start="2026-04-01", end="2026-04-20")
CURRENT = Period(start="2026-05-01", end="2026-05-20")


def test_calculate_activation_rate_counts_activated_users():
    rows = [
        {"user_id": "u1", "activated_flag": True},
        {"user_id": "u2", "activated_flag": False},
        {"user_id": "u3", "activated_flag": True},
    ]

    result = calculate_activation_rate(rows)

    assert result == 2 / 3


def test_calculate_metric_summary_detects_activation_drop():
    dataset = load_demo_dataset()

    summary = calculate_metric_summary(dataset, BASELINE, CURRENT)

    assert summary.baseline_rate > summary.current_rate
    assert summary.absolute_delta < 0
    assert summary.baseline_users == 240
    assert summary.current_users == 240


def test_rank_segment_drops_surfaces_smb_segment():
    dataset = load_demo_dataset()

    findings = rank_segment_drops(dataset, BASELINE, CURRENT)

    assert findings[0].dimension == "company_size"
    assert findings[0].segment == "SMB"
    assert findings[0].absolute_delta < 0


def test_analyze_funnel_finds_invite_step_loss():
    dataset = load_demo_dataset()

    findings = analyze_funnel(dataset, BASELINE, CURRENT)

    assert findings[0].step == "invite_sent"
    assert findings[0].absolute_delta < 0


def test_correlate_releases_returns_onboarding_release():
    dataset = load_demo_dataset()

    findings = correlate_releases(dataset, CURRENT)

    assert findings[0].component == "onboarding_wizard"
