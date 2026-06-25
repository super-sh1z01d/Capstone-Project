from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint_returns_runtime_mode():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["runtime_mode"] in {"demo_fallback", "gemini_adk"}


def test_investigate_endpoint_returns_report():
    response = client.post(
        "/api/investigate",
        json={
            "dataset_id": "demo",
            "metric": "activation_rate",
            "baseline": {"start": "2026-04-01", "end": "2026-04-20"},
            "current": {"start": "2026-05-01", "end": "2026-05-20"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["metric_summary"]["absolute_delta"] < 0
    assert body["top_segments"][0]["segment"] == "SMB"


def test_upload_endpoint_accepts_schema_files():
    files = []
    for table in [
        "users",
        "onboarding_events",
        "activations",
        "releases",
        "feature_flags",
        "support_tickets",
    ]:
        files.append(
            (
                "files",
                (
                    f"{table}.csv",
                    Path(f"data/demo/{table}.csv").read_bytes(),
                    "text/csv",
                ),
            )
        )

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_id"].startswith("uploaded_")
    assert body["quality"]["valid"] is True
