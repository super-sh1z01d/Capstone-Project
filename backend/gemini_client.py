from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

from backend.models import InvestigationReport

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

GeminiTransport = Callable[[str, dict[str, Any], float], dict[str, Any]]


def _default_transport(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        transport: GeminiTransport = _default_transport,
        timeout: float = 20.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
        self.transport = transport
        self.timeout = timeout

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY must be configured.")
        model = urllib.parse.quote(self.model, safe="")
        key = urllib.parse.quote(self.api_key, safe="")
        url = f"{GEMINI_ENDPOINT.format(model=model)}?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 700,
            },
        }
        response = self.transport(url, payload, self.timeout)
        return _extract_text(response)


def _extract_text(response: dict[str, Any]) -> str:
    candidates = response.get("candidates") or []
    for candidate in candidates:
        content = candidate.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
    raise RuntimeError("Gemini response did not include text output.")


def build_synthesis_prompt(report: InvestigationReport) -> str:
    evidence = "\n".join(f"- {card.title}: {card.summary}" for card in report.evidence_cards)
    agent_steps = "\n".join(f"- {step.agent}: {step.finding}" for step in report.agent_steps)
    skills = "\n".join(f"- {skill.name}: {skill.output_contract}" for skill in report.skills_used)
    return "\n".join(
        [
            "You are a product analytics agent investigating a SaaS activation-rate drop.",
            "Return a concise executive synthesis in 3 bullets. Do not invent numbers.",
            "Use only the deterministic tool evidence below.",
            "",
            "Metric:",
            (
                f"Activation moved from {report.metric_summary.baseline_rate:.1%} "
                f"to {report.metric_summary.current_rate:.1%}; "
                f"absolute delta {report.metric_summary.absolute_delta:.1%}."
            ),
            "",
            "Agent steps:",
            agent_steps,
            "",
            "Skills used:",
            skills,
            "",
            "Evidence:",
            evidence,
            "",
            "Limitations:",
            "\n".join(f"- {item}" for item in report.limitations),
        ]
    )
