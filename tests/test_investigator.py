from backend.adk_runtime import resolve_runtime_mode, run_investigation
from backend.data_loader import load_demo_dataset
from backend.investigator import run_fallback_investigation
from backend.mcp_server import list_datasets_payload, run_metric_query_payload
from backend.models import InvestigationRequest


def test_fallback_investigation_returns_ranked_evidence():
    dataset = load_demo_dataset()
    request = InvestigationRequest()

    report = run_fallback_investigation(dataset, request)

    assert report.runtime_mode == "demo_fallback"
    assert report.metric_summary.absolute_delta < 0
    assert report.top_segments[0].segment == "SMB"
    assert "onboarding wizard" in report.ranked_hypotheses[0].lower()
    assert "correlation" in " ".join(report.limitations).lower()


def test_mcp_payload_functions_expose_demo_dataset_and_metric_query():
    datasets = list_datasets_payload()
    metric = run_metric_query_payload(
        "demo", "2026-04-01", "2026-04-20", "2026-05-01", "2026-05-20"
    )

    assert datasets[0]["dataset_id"] == "demo"
    assert metric["absolute_delta"] < 0


def test_resolve_runtime_mode_defaults_to_fallback_without_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("AGENT_RUNTIME", "auto")

    assert resolve_runtime_mode() == "demo_fallback"


def test_resolve_runtime_mode_uses_adk_when_key_present(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key-for-mode-selection")
    monkeypatch.setenv("AGENT_RUNTIME", "auto")

    assert resolve_runtime_mode() == "gemini_adk"


def test_gemini_runtime_adds_real_synthesis_when_client_succeeds(monkeypatch):
    class FakeGeminiClient:
        def generate_text(self, prompt: str) -> str:
            assert "Activation moved from" in prompt
            return "Gemini synthesis: SMB invite-step regression is the lead hypothesis."

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key-for-runtime-selection")
    monkeypatch.setenv("AGENT_RUNTIME", "adk")

    report = run_investigation(
        InvestigationRequest(),
        load_demo_dataset(),
        gemini_client=FakeGeminiClient(),
    )

    assert report.runtime_mode == "gemini_adk"
    assert (
        report.ai_synthesis
        == "Gemini synthesis: SMB invite-step regression is the lead hypothesis."
    )
    assert "## Gemini Synthesis" in report.markdown_report
