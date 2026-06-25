from backend.data_loader import load_demo_dataset
from backend.investigator import run_fallback_investigation
from backend.models import InvestigationRequest
from backend.report import render_markdown_report


def test_render_markdown_report_contains_kaggle_ready_sections():
    report = run_fallback_investigation(load_demo_dataset(), InvestigationRequest())

    markdown = render_markdown_report(report)

    assert "# Activation Drop Investigation" in markdown
    assert "## Executive Summary" in markdown
    assert "## Ranked Hypotheses" in markdown
    assert "## Limitations" in markdown
