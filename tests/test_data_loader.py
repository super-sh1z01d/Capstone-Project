from pathlib import Path

from backend.data_loader import load_demo_dataset, validate_dataset
from backend.demo_data import DEMO_DATA_DIR, generate_demo_data


def test_generate_demo_data_writes_expected_csv_files(tmp_path: Path):
    output_dir = tmp_path / "demo"

    generate_demo_data(output_dir)

    expected = {
        "users.csv",
        "onboarding_events.csv",
        "activations.csv",
        "releases.csv",
        "feature_flags.csv",
        "support_tickets.csv",
    }
    assert {path.name for path in output_dir.glob("*.csv")} == expected


def test_demo_data_dir_points_to_repo_data_folder():
    assert DEMO_DATA_DIR.as_posix().endswith("data/demo")


def test_load_demo_dataset_returns_named_tables():
    dataset = load_demo_dataset()

    assert set(dataset.tables) == {
        "users",
        "onboarding_events",
        "activations",
        "releases",
        "feature_flags",
        "support_tickets",
    }
    assert len(dataset.tables["users"]) > 0


def test_validate_dataset_reports_missing_required_table():
    dataset = load_demo_dataset()
    dataset.tables.pop("activations")

    result = validate_dataset(dataset)

    assert result.valid is False
    assert "Missing table: activations" in result.issues
