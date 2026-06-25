# Activation Drop Investigator

Activation Drop Investigator is an evidence-first AI agent dashboard for investigating SaaS activation-rate drops. It was built for the Kaggle AI Agents Intensive Vibe Coding Capstone Project in the Agents for Business track.

## What It Does

The demo investigates a B2B productivity SaaS onboarding drop. A new onboarding wizard was released near the current period, and activation dropped most strongly for SMB users around the invite teammates step. The system surfaces the metric drop, affected segments, funnel evidence, release correlation, recommended actions, and limitations.

## Course Concepts Demonstrated

- ADK-style multi-agent investigation architecture with specialist agents and an optional ADK entrypoint.
- Explicit agent skills for metric quantification, segment analysis, funnel diagnosis, release correlation, and claim guardrails.
- MCP analytics server exposing metric, segment, funnel, release, and data quality tools.
- Gemini API synthesis mode for executive narrative generation from deterministic tool evidence.
- Security guardrails: no secrets in repo, environment-only API key, local demo data, CSV validation.
- Evaluation and deployability: deterministic fallback mode, tests, reproducible demo data, clear setup.

## Architecture

```text
React Dashboard
  -> FastAPI backend
    -> Investigation orchestrator
      -> Agent skills manifest
      -> Analytics functions
      -> MCP tool payloads
      -> Gemini API synthesis adapter
      -> Optional ADK root_agent entrypoint
    -> Markdown report export
```

## Visual Concept

The dashboard concept used for the first implementation is saved at:

`docs/assets/activation-drop-investigator-dashboard-concept.png`

## Setup

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m backend.demo_data
python -m pytest -v
```

Run the backend:

```bash
uvicorn backend.main:app --reload
```

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Runtime Modes

Default mode is deterministic Demo Fallback. It requires no API key and produces a full investigation report from the built-in dataset.

To select Gemini API synthesis mode:

```bash
cp .env.example .env
export GEMINI_API_KEY="your-key"
export AGENT_RUNTIME=adk
```

`GOOGLE_API_KEY` is also supported for compatibility. Numerical calculations remain deterministic even when Gemini mode is active; the model only synthesizes narrative from tool evidence.

## Agent Skills

The investigation exposes five explicit skills in `backend/agent_skills.py`:

- Metric Drop Quantification
- Segment Driver Detection
- Funnel Step Diagnosis
- Release Correlation Review
- Claim Guardrail Review

Each skill declares the tools it uses and its output contract. The dashboard and exported Markdown report include the skill manifest.

## ADK Entrypoint

The project includes `adk_app/agent.py`, which exposes `root_agent` when the optional ADK dependency is installed:

```bash
pip install -e ".[adk,dev]"
adk run adk_app
```

The ADK agent is intentionally conservative: it describes skills and investigation scope, while deterministic MCP/analytics tools remain responsible for numbers.

## MCP Server

Run the MCP analytics server:

```bash
python -m backend.mcp_server
```

Exposed tools include:

- `list_datasets`
- `get_schema`
- `data_quality_check`
- `run_metric_query`
- `segment_breakdown`
- `funnel_analysis`
- `release_events`

## Demo Script

1. Open the dashboard.
2. Confirm the mode badge says Demo Fallback or Gemini API.
3. Click Run Investigation.
4. Review activation drop summary.
5. Review the SMB segment evidence.
6. Review the invite-step funnel loss.
7. Review the agent skills and optional Gemini synthesis.
8. Export the Markdown report.

## Sample CSV Schema

The upload flow expects six CSV files with these names and columns:

- `users.csv`: `user_id`, `signup_date`, `company_size`, `plan`, `acquisition_channel`, `region`, `browser`
- `onboarding_events.csv`: `user_id`, `event_time`, `event_name`, `step_order`, `session_id`
- `activations.csv`: `user_id`, `activated_at`, `activated_flag`, `time_to_activation_hours`
- `releases.csv`: `release_id`, `release_date`, `component`, `rollout_percent`, `description`
- `feature_flags.csv`: `user_id`, `flag_name`, `variant`, `assigned_at`
- `support_tickets.csv`: `ticket_time`, `topic`, `severity`, `browser`, `related_step`

## Safety Notes

Do not commit `.env` or API keys. The demo dataset contains no personal data. Uploaded CSV handling is local to the running backend process by default.

## Kaggle Submission Assets

Recommended assets for the Kaggle Writeup:

- Public GitHub repository link.
- YouTube video under 5 minutes.
- Dashboard screenshot.
- Architecture diagram based on the architecture block above.
- Exported Markdown report from the demo run.
