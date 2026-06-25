from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.adk_runtime import resolve_runtime_mode, run_investigation
from backend.data_loader import load_dataset_from_dir, load_demo_dataset, validate_dataset
from backend.models import Dataset, InvestigationReport, InvestigationRequest

app = FastAPI(title="Activation Drop Investigator")
DATASET_STORE: dict[str, Dataset] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "runtime_mode": resolve_runtime_mode()}


@app.get("/api/datasets")
def datasets() -> list[dict[str, str]]:
    dataset = load_demo_dataset()
    uploaded = [
        {"dataset_id": dataset_id, "name": value.name}
        for dataset_id, value in sorted(DATASET_STORE.items())
    ]
    return [{"dataset_id": dataset.dataset_id, "name": dataset.name}, *uploaded]


@app.get("/api/datasets/demo/quality")
def demo_quality() -> dict:
    return validate_dataset(load_demo_dataset()).model_dump()


@app.post("/api/investigate", response_model=InvestigationReport)
def investigate(request: InvestigationRequest) -> InvestigationReport:
    if request.dataset_id == "demo":
        dataset = load_demo_dataset()
    else:
        dataset = DATASET_STORE.get(request.dataset_id)
        if dataset is None:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {request.dataset_id}")
    return run_investigation(request, dataset)


@app.post("/api/upload")
async def upload_dataset(files: list[UploadFile]) -> dict:
    dataset_id = f"uploaded_{uuid4().hex[:8]}"
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        for upload in files:
            destination = directory / Path(upload.filename or "").name
            destination.write_bytes(await upload.read())
        dataset = load_dataset_from_dir(dataset_id, "Uploaded CSV Dataset", directory)
    quality = validate_dataset(dataset)
    if quality.valid:
        DATASET_STORE[dataset_id] = dataset
    return {"dataset_id": dataset_id, "quality": quality.model_dump()}
