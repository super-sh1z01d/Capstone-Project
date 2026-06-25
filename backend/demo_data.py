from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DEMO_DATA_DIR = ROOT_DIR / "data" / "demo"

BASELINE_START = date(2026, 4, 1)
CURRENT_START = date(2026, 5, 1)
RELEASE_DATE = date(2026, 5, 6)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _segment_for_user(index: int) -> dict[str, str]:
    company_sizes = ["SMB", "Mid-Market", "Enterprise"]
    channels = ["organic", "paid_search", "partner", "content"]
    browsers = ["Chrome", "Safari", "Firefox", "Edge"]
    regions = ["NA", "EU", "LATAM", "APAC"]
    plans = ["trial", "starter", "business"]
    return {
        "company_size": company_sizes[index % len(company_sizes)],
        "acquisition_channel": channels[index % len(channels)],
        "browser": browsers[index % len(browsers)],
        "region": regions[index % len(regions)],
        "plan": plans[index % len(plans)],
    }


def _should_activate(period: str, segment: dict[str, str], index: int) -> bool:
    if period == "baseline":
        return index % 10 < 7
    if segment["company_size"] == "SMB" and segment["browser"] in {"Chrome", "Safari"}:
        return index % 10 < 3
    return index % 10 < 7


def generate_demo_data(output_dir: Path = DEMO_DATA_DIR) -> None:
    users: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    activations: list[dict[str, object]] = []
    flags: list[dict[str, object]] = []
    tickets: list[dict[str, object]] = []

    user_index = 0
    for period, start_date in [("baseline", BASELINE_START), ("current", CURRENT_START)]:
        for day_offset in range(20):
            signup_date = start_date + timedelta(days=day_offset)
            for _ in range(12):
                user_index += 1
                user_id = f"u{user_index:04d}"
                segment = _segment_for_user(user_index)
                activated = _should_activate(period, segment, user_index)

                users.append(
                    {"user_id": user_id, "signup_date": signup_date.isoformat(), **segment}
                )
                flags.append(
                    {
                        "user_id": user_id,
                        "flag_name": "onboarding_wizard_v2",
                        "variant": "new" if signup_date >= RELEASE_DATE else "classic",
                        "assigned_at": signup_date.isoformat(),
                    }
                )

                completed_steps = ["signup", "workspace_created"]
                affected_current = (
                    period == "current"
                    and segment["company_size"] == "SMB"
                    and segment["browser"] in {"Chrome", "Safari"}
                )
                if activated or not affected_current:
                    completed_steps.append("invite_sent")
                if activated:
                    completed_steps.extend(["project_created", "activated"])

                for step_order, event_name in enumerate(completed_steps, start=1):
                    events.append(
                        {
                            "user_id": user_id,
                            "event_time": (signup_date + timedelta(hours=step_order)).isoformat(),
                            "event_name": event_name,
                            "step_order": step_order,
                            "session_id": f"s{user_index:04d}",
                        }
                    )

                activations.append(
                    {
                        "user_id": user_id,
                        "activated_at": (signup_date + timedelta(hours=8)).isoformat()
                        if activated
                        else "",
                        "activated_flag": activated,
                        "time_to_activation_hours": 8 if activated else "",
                    }
                )

                if affected_current and not activated and user_index % 3 == 0:
                    tickets.append(
                        {
                            "ticket_time": (signup_date + timedelta(hours=5)).isoformat(),
                            "topic": "Invite step confusion",
                            "severity": "medium",
                            "browser": segment["browser"],
                            "related_step": "invite_sent",
                        }
                    )

    releases = [
        {
            "release_id": "rel_2026_05_06_wizard_v2",
            "release_date": RELEASE_DATE.isoformat(),
            "component": "onboarding_wizard",
            "rollout_percent": 100,
            "description": "New onboarding wizard with redesigned invite teammates step",
        }
    ]

    _write_csv(
        output_dir / "users.csv",
        [
            "user_id",
            "signup_date",
            "company_size",
            "plan",
            "acquisition_channel",
            "region",
            "browser",
        ],
        users,
    )
    _write_csv(
        output_dir / "onboarding_events.csv",
        ["user_id", "event_time", "event_name", "step_order", "session_id"],
        events,
    )
    _write_csv(
        output_dir / "activations.csv",
        ["user_id", "activated_at", "activated_flag", "time_to_activation_hours"],
        activations,
    )
    _write_csv(
        output_dir / "releases.csv",
        ["release_id", "release_date", "component", "rollout_percent", "description"],
        releases,
    )
    _write_csv(
        output_dir / "feature_flags.csv", ["user_id", "flag_name", "variant", "assigned_at"], flags
    )
    _write_csv(
        output_dir / "support_tickets.csv",
        ["ticket_time", "topic", "severity", "browser", "related_step"],
        tickets,
    )


if __name__ == "__main__":
    generate_demo_data()
