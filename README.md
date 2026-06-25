# Activation Drop Investigator

Activation Drop Investigator is an evidence-first AI agent dashboard for investigating SaaS activation-rate drops. It was built for the Kaggle AI Agents Intensive Vibe Coding Capstone Project in the Agents for Business track.

## What It Does

The demo investigates a B2B productivity SaaS onboarding drop. A new onboarding wizard was released near the current period, and activation dropped most strongly for SMB users around the invite teammates step. The system surfaces the metric drop, affected segments, funnel evidence, release correlation, recommended actions, and limitations.

## Course Concepts Demonstrated

- ADK-style multi-agent investigation architecture with specialist agents.
- MCP analytics server exposing metric, segment, funnel, release, and data quality tools.
- Security guardrails: no secrets in repo, environment-only API key, local demo data, CSV validation.
- Evaluation and deployability: deterministic fallback mode, tests, reproducible demo data, clear setup.

## Architecture

```text
React Dashboard
  -> FastAPI backend
    -> Investigation orchestrator
      -> Analytics functions
      -> MCP tool payloads
      -> Optional Gemini/ADK runtime adapter
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

To select Gemini/ADK mode:

```bash
cp .env.example .env
export GOOGLE_API_KEY="your-key"
export AGENT_RUNTIME=adk
```

Numerical calculations remain deterministic even when ADK mode is active.

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
2. Confirm the mode badge says Demo Fallback or Gemini ADK.
3. Click Run Investigation.
4. Review activation drop summary.
5. Review the SMB segment evidence.
6. Review the invite-step funnel loss.
7. Export the Markdown report.

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

