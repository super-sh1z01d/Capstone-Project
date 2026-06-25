import type { InvestigationReport, UploadedDatasetResponse } from "./types";

export async function runInvestigation(datasetId = "demo"): Promise<InvestigationReport> {
  const response = await fetch("/api/investigate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dataset_id: datasetId,
      metric: "activation_rate",
      baseline: { start: "2026-04-01", end: "2026-04-20" },
      current: { start: "2026-05-01", end: "2026-05-20" }
    })
  });
  if (!response.ok) {
    throw new Error(`Investigation failed: ${response.status}`);
  }
  return response.json();
}

export async function uploadDataset(files: FileList): Promise<UploadedDatasetResponse> {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));
  const response = await fetch("/api/upload", { method: "POST", body: formData });
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`);
  }
  return response.json();
}
