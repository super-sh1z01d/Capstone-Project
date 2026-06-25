from __future__ import annotations

import os
from typing import Any

from backend.agent_skills import skill_manifest


def describe_agent_skills() -> dict[str, Any]:
    """Return the skill manifest for ADK tool calls."""
    return {"skills": [skill.model_dump() for skill in skill_manifest()]}


def describe_investigation_scope() -> dict[str, Any]:
    """Describe the deterministic evidence boundaries used by the agent."""
    return {
        "metric": "activation_rate",
        "policy": "Numerical claims must come from deterministic analytics tools.",
        "allowed_claim_types": ["observed", "likely", "needs_verification"],
        "mcp_tools": [
            "data_quality_check",
            "run_metric_query",
            "segment_breakdown",
            "funnel_analysis",
            "release_events",
        ],
    }


try:
    from google.adk import Agent
except ModuleNotFoundError:
    Agent = None  # type: ignore[assignment]


root_agent = None
if Agent is not None:
    root_agent = Agent(
        name="activation_drop_investigator",
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        instruction=(
            "You are an evidence-first product analytics agent. Use the provided skill "
            "manifest and scope tools to explain how activation-rate drops are investigated. "
            "Never invent metric values; deterministic MCP analytics own all calculations."
        ),
        tools=[describe_agent_skills, describe_investigation_scope],
    )
