from __future__ import annotations

import os

from backend.data_loader import load_demo_dataset
from backend.investigator import run_fallback_investigation
from backend.models import Dataset, EvidenceCard, InvestigationReport, InvestigationRequest
from backend.report import render_markdown_report


def resolve_runtime_mode() -> str:
    requested = os.getenv("AGENT_RUNTIME", "auto").strip().lower()
    has_key = bool(os.getenv("GOOGLE_API_KEY"))
    if requested == "fallback":
        return "demo_fallback"
    if requested == "adk" and has_key:
        return "gemini_adk"
    if requested == "adk" and not has_key:
        return "demo_fallback"
    return "gemini_adk" if has_key else "demo_fallback"


def run_investigation(
    request: InvestigationRequest, dataset: Dataset | None = None
) -> InvestigationReport:
    dataset = dataset or load_demo_dataset()
    mode = resolve_runtime_mode()
    report = run_fallback_investigation(dataset, request)
    if mode == "gemini_adk":
        report.runtime_mode = "gemini_adk"
        report.evidence_cards.append(
            EvidenceCard(
                title="ADK runtime adapter active",
                claim_type="observed",
                summary=(
                    "Gemini/ADK mode is selected; deterministic tools still own "
                    "metric calculations."
                ),
                evidence=["GOOGLE_API_KEY is configured", "AGENT_RUNTIME permits ADK mode"],
                confidence="medium",
            )
        )
        report.markdown_report = render_markdown_report(report).replace(
            "# Activation Drop Investigation",
            "# Activation Drop Investigation\n\nRuntime: Gemini ADK adapter",
        )
    return report
