from adk_app.agent import root_agent
from backend.adk_agent import describe_agent_skills, describe_investigation_scope


def test_adk_agent_helpers_expose_skills_and_scope():
    skills = describe_agent_skills()
    scope = describe_investigation_scope()

    assert len(skills["skills"]) == 5
    assert scope["metric"] == "activation_rate"
    assert "run_metric_query" in scope["mcp_tools"]
    assert root_agent is None or root_agent.name == "activation_drop_investigator"
