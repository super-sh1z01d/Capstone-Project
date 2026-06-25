# Activation Drop Investigator

**Subtitle:** An evidence-first AI agent dashboard for investigating SaaS activation-rate drops  
**Track:** Agents for Business  
**Project link:** https://github.com/super-sh1z01d/Capstone-Project

## Summary

Activation Drop Investigator is an AI agent system for product and business analysts who need to understand why a key SaaS metric suddenly moved. The first use case focuses on B2B SaaS onboarding: activation rate drops after a product release, and the analyst needs a fast, evidence-backed answer before deciding whether to rollback, investigate further, or change the onboarding flow.

The project is built as a web dashboard backed by a multi-agent investigation workflow. It does not simply generate a narrative from a metric. It calculates the metric movement, ranks affected segments, analyzes funnel conversion, checks nearby release events, and then generates a report with evidence cards, confidence labels, recommended actions, and limitations.

The demo uses a deterministic synthetic dataset for a B2B productivity SaaS product. In the current period, activation drops from **70.0%** to **63.3%**. The largest affected segment is **SMB**, where activation falls from **70.0%** to **50.0%**. The largest funnel loss appears at the **invite teammates** step, where conversion moves from **100.0%** to **88.3%**. A new onboarding wizard release shipped on **2026-05-06**, near the start of the affected period. The system reports this as a likely contributing factor, not as proven causality.

## Problem

Product teams often discover metric drops before they understand them. A dashboard might show that activation is down, but the real work begins after that: which users were affected, which funnel step changed, what product release or experiment overlaps with the drop, and which claims are actually supported by data?

This process is usually slow because it crosses several tools and roles. A product analyst may check event data, a product manager may review release notes, a growth analyst may inspect acquisition channels, and an engineering team may look for regressions. The result is often a loose Slack thread instead of a structured investigation.

Activation Drop Investigator turns that messy workflow into a repeatable agentic investigation. It is designed for business impact: activation loss affects revenue, onboarding efficiency, user experience, and team prioritization.

## Solution

The app gives analysts a focused workflow:

1. Select the demo dataset or upload CSV files matching the documented schema.
2. Choose activation rate and compare a baseline period with a current period.
3. Run the investigation.
4. Review metric movement, affected segments, funnel loss, release correlation, and data quality signals.
5. Export a Markdown report that can be shared with product, growth, or engineering teams.

The key design principle is **evidence first**. Each important claim is tied to observed data and labeled as `observed`, `likely`, or `needs verification`. This guardrail matters because metric investigations can easily overstate causality. The system can say that a release is temporally aligned with a drop, but it avoids saying the release definitively caused the drop unless the data supports that conclusion.

## Agent Architecture

The investigation is organized as a specialist-agent workflow:

- **Investigation Orchestrator:** coordinates the investigation and assembles the final report.
- **Metric Analyst:** calculates baseline activation, current activation, absolute delta, relative delta, and sample sizes.
- **Segment Detective:** ranks segments by contribution to the drop across dimensions such as company size, plan, acquisition channel, region, and browser.
- **Funnel Analyst:** compares onboarding funnel conversion across steps such as signup, workspace creation, invite sent, project creation, and activation.
- **Release Correlator:** checks releases and feature flags near the current-period start.
- **Risk & Guardrails Agent:** downgrades unsupported causal claims and adds limitations.

This structure mirrors how a real product organization investigates incidents. Each agent has a narrow responsibility, and the final report combines their findings into one decision-ready artifact.

The project also includes an explicit **agent skills** layer. Five skills are declared in code: metric drop quantification, segment driver detection, funnel step diagnosis, release correlation review, and claim guardrail review. Each skill states which tool it uses and what output contract it returns. This makes the agent behavior easier to inspect than a single opaque prompt.

## MCP Tool Layer

The project includes an MCP analytics server so agent reasoning is separated from deterministic analytics tools. Agents do not need to read CSV files directly. They call tool-style functions that return structured results.

Implemented MCP tools include:

- `list_datasets`
- `get_schema`
- `data_quality_check`
- `run_metric_query`
- `segment_breakdown`
- `funnel_analysis`
- `release_events`

This makes the architecture easier to extend. A future version could replace the synthetic dataset with warehouse, Mixpanel, Amplitude, or Segment connectors while keeping the agent workflow stable.

## Runtime Modes

The app supports two runtime modes.

**Demo Fallback Mode** is deterministic and requires no API key. This is the default mode so judges can run the project locally and reproduce the investigation without secrets or paid services.

**Gemini API Mode** runs a real Gemini `generateContent` synthesis step when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is configured and `AGENT_RUNTIME=adk`. The model receives the deterministic evidence cards, agent steps, skills manifest, and limitations, then produces a concise executive synthesis. Metric values still come from testable analytics functions, not from the model.

The repository also includes an optional Google ADK entrypoint at `adk_app/agent.py`. When `google-adk` is installed, it exposes a `root_agent` with tools for describing the skill manifest and investigation scope. This keeps the ADK path visible while preserving the reproducible local demo.

## Demo Result

For the included demo dataset, the system produces the following findings:

- Activation rate dropped from **70.0%** to **63.3%**, a **-6.7 percentage point** absolute change.
- The top affected segment is **company_size = SMB**.
- SMB activation dropped from **70.0%** to **50.0%**.
- The largest funnel conversion loss is at **invite_sent**.
- Invite-step conversion changed from **100.0%** to **88.3%**.
- The onboarding wizard release shipped on **2026-05-06**, five days after the current period started.

The top hypothesis is that the new onboarding wizard likely introduced friction at the invite teammates step for SMB teams. The system recommends reviewing session traces, running a rollback or holdout for the new wizard, instrumenting errors and abandonment reasons, and creating follow-up segment reports by browser and acquisition channel.

## Security And Guardrails

The project includes several safeguards:

- No API keys or passwords are committed.
- `.env.example` documents environment variables.
- Gemini API use is environment-only and optional.
- The demo dataset contains no personal data.
- Uploaded CSV files are validated against a required schema.
- Invalid datasets return data quality issues instead of producing misleading analysis.
- Claims are labeled by evidence strength.
- Correlation is not presented as definitive causation.

These choices reflect the security and evaluation themes from the course. Agentic systems become more useful when they know where their evidence ends.

## Evaluation

The implementation includes deterministic tests for the core investigation behavior:

- Activation-rate calculation.
- Segment contribution ranking.
- Funnel drop detection.
- Release correlation.
- Dataset loading and validation.
- API behavior.
- Markdown report generation.
- Runtime mode selection.
- Gemini API request construction and response parsing.
- Agent skills and ADK entrypoint helpers.

The current test suite covers these behaviors with automated tests. The frontend also builds successfully, and `npm audit --audit-level=moderate` reports **0 vulnerabilities**.

## Deployability And Reproducibility

The repository includes a complete local setup path:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m backend.demo_data
python -m pytest -v
uvicorn backend.main:app --reload
```

The frontend runs with:

```bash
cd frontend
npm install
npm run dev
```

The default demo requires no external API key. This was intentional: a capstone project should be easy to inspect, run, and reproduce.

## What I Learned

The most important lesson was that useful agents need boundaries. In this project, the LLM-facing parts of the architecture are not trusted to invent numbers. They rely on deterministic tools for calculations and use guardrails to phrase findings responsibly.

I also learned that agent design is clearer when it follows the workflow of real teams. Product metric investigations already involve specialist roles: analysts, product managers, growth teams, and engineers. Modeling those responsibilities as agents made the system easier to explain, test, and extend.

## Limitations And Future Work

The current version uses a synthetic dataset. That makes the demo reproducible, but it is not production telemetry. Gemini synthesis requires an API key, and the ADK entrypoint is intentionally conservative: it exposes the agent and its scope, but a future version could add fuller ADK orchestration across live analytics connectors.

Future improvements include:

- Direct connectors for product analytics tools or data warehouses.
- A richer CSV mapping flow for custom schemas.
- A hosted public demo.
- More robust statistical checks for significance and sample-size warnings.
- Session replay or support-ticket mining integrations.
- A stronger evaluation rubric for generated reports.

## Conclusion

Activation Drop Investigator shows how agents can help product teams move from “the metric is down” to “here is the most likely issue, here is the evidence, and here is what to do next.” The project combines multi-agent decomposition, MCP tool interoperability, security guardrails, deterministic evaluation, and a practical dashboard into one business-focused investigation workflow.
