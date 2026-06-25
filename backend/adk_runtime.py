from __future__ import annotations

import os
from typing import Protocol

from backend.data_loader import load_demo_dataset
from backend.gemini_client import GeminiClient, build_synthesis_prompt
from backend.investigator import run_fallback_investigation
from backend.models import Dataset, EvidenceCard, InvestigationReport, InvestigationRequest
from backend.report import render_markdown_report


class TextGenerationClient(Protocol):
    def generate_text(self, prompt: str) -> str: ...


def resolve_runtime_mode() -> str:
    requested = os.getenv("AGENT_RUNTIME", "auto").strip().lower()
    has_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if requested == "fallback":
        return "demo_fallback"
    if requested == "adk" and has_key:
        return "gemini_adk"
    if requested == "adk" and not has_key:
        return "demo_fallback"
    return "gemini_adk" if has_key else "demo_fallback"


def run_investigation(
    request: InvestigationRequest,
    dataset: Dataset | None = None,
    gemini_client: TextGenerationClient | None = None,
) -> InvestigationReport:
    dataset = dataset or load_demo_dataset()
    mode = resolve_runtime_mode()
    report = run_fallback_investigation(dataset, request)
    if mode == "gemini_adk":
        client = gemini_client or GeminiClient()
        report.runtime_mode = "gemini_adk"
        report.evidence_cards.append(
            EvidenceCard(
                title="Gemini synthesis runtime active",
                claim_type="observed",
                summary=(
                    "Gemini API mode is selected; deterministic tools still own "
                    "metric calculations."
                ),
                evidence=[
                    "GEMINI_API_KEY or GOOGLE_API_KEY is configured",
                    "AGENT_RUNTIME permits ADK mode",
                ],
                confidence="medium",
            )
        )
        try:
            report.ai_synthesis = client.generate_text(build_synthesis_prompt(report))
        except Exception as exc:
            report.evidence_cards.append(
                EvidenceCard(
                    title="Gemini synthesis unavailable",
                    claim_type="needs_verification",
                    summary=(
                        "The deterministic investigation completed, but Gemini synthesis failed."
                    ),
                    evidence=[str(exc)],
                    confidence="low",
                )
            )
            report.limitations.append(
                "Gemini synthesis was requested but unavailable during this run."
            )
        report.markdown_report = render_markdown_report(report).replace(
            "# Activation Drop Investigation",
            "# Activation Drop Investigation\n\nRuntime: Gemini API synthesis adapter",
        )
    return report
