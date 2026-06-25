from backend.agent_skills import INVESTIGATION_SKILLS, skill_manifest
from backend.data_loader import load_demo_dataset
from backend.investigator import run_fallback_investigation
from backend.models import InvestigationRequest


def test_skill_manifest_exposes_business_analysis_skills():
    manifest = skill_manifest()

    assert len(manifest) >= 4
    assert {skill.skill_id for skill in manifest} == {
        skill.skill_id for skill in INVESTIGATION_SKILLS
    }
    assert "run_metric_query" in manifest[0].tool_names
    assert all(skill.output_contract for skill in manifest)


def test_investigation_report_lists_skills_used():
    report = run_fallback_investigation(load_demo_dataset(), InvestigationRequest())

    assert [skill.skill_id for skill in report.skills_used] == [
        "metric_drop_quantification",
        "segment_driver_detection",
        "funnel_step_diagnosis",
        "release_correlation_review",
        "claim_guardrail_review",
    ]
