from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from backend.demo_data import DEMO_DATA_DIR, generate_demo_data
from backend.models import DataQualityResult, Dataset

REQUIRED_COLUMNS = {
    "users": {
        "user_id",
        "signup_date",
        "company_size",
        "plan",
        "acquisition_channel",
        "region",
        "browser",
    },
    "onboarding_events": {"user_id", "event_time", "event_name", "step_order", "session_id"},
    "activations": {"user_id", "activated_at", "activated_flag", "time_to_activation_hours"},
    "releases": {"release_id", "release_date", "component", "rollout_percent", "description"},
    "feature_flags": {"user_id", "flag_name", "variant", "assigned_at"},
    "support_tickets": {"ticket_time", "topic", "severity", "browser", "related_step"},
}


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _normalize_table(table_name: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        clean = dict(row)
        if table_name == "activations":
            clean["activated_flag"] = _coerce_bool(clean.get("activated_flag"))
            if clean.get("time_to_activation_hours") == "":
                clean["time_to_activation_hours"] = None
            elif clean.get("time_to_activation_hours") is not None:
                clean["time_to_activation_hours"] = float(clean["time_to_activation_hours"])
        if table_name == "onboarding_events" and clean.get("step_order") is not None:
            clean["step_order"] = int(clean["step_order"])
        if table_name == "releases" and clean.get("rollout_percent") is not None:
            clean["rollout_percent"] = int(clean["rollout_percent"])
        normalized.append(clean)
    return normalized


def load_dataset_from_dir(dataset_id: str, name: str, directory: Path) -> Dataset:
    tables: dict[str, list[dict[str, Any]]] = {}
    for table_name in REQUIRED_COLUMNS:
        path = directory / f"{table_name}.csv"
        if path.exists():
            tables[table_name] = _normalize_table(table_name, _read_csv(path))
    return Dataset(dataset_id=dataset_id, name=name, tables=tables)


def load_demo_dataset() -> Dataset:
    if not (DEMO_DATA_DIR / "users.csv").exists():
        generate_demo_data(DEMO_DATA_DIR)
    return load_dataset_from_dir("demo", "Demo SaaS Onboarding Dataset", DEMO_DATA_DIR)


def validate_dataset(dataset: Dataset) -> DataQualityResult:
    issues: list[str] = []
    row_counts = {table_name: len(rows) for table_name, rows in dataset.tables.items()}

    for table_name, required_columns in REQUIRED_COLUMNS.items():
        rows = dataset.tables.get(table_name)
        if rows is None:
            issues.append(f"Missing table: {table_name}")
            continue
        if not rows:
            issues.append(f"Empty table: {table_name}")
            continue
        present = set(rows[0].keys())
        for column in sorted(required_columns - present):
            issues.append(f"Missing column in {table_name}: {column}")

    return DataQualityResult(valid=not issues, issues=issues, row_counts=row_counts)
