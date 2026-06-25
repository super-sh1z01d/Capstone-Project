import {
  Activity,
  CheckCircle2,
  Download,
  FileUp,
  PlayCircle,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { runInvestigation, uploadDataset } from "./api";
import type { InvestigationReport } from "./types";

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function formatLabel(value: string): string {
  return value.replaceAll("_", " ");
}

export function App() {
  const [report, setReport] = useState<InvestigationReport | null>(null);
  const [datasetId, setDatasetId] = useState("demo");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);

  async function investigate(targetDataset = datasetId) {
    setLoading(true);
    setError(null);
    try {
      setReport(await runInvestigation(targetDataset));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Investigation failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(files: FileList | null) {
    if (!files || files.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const uploaded = await uploadDataset(files);
      if (!uploaded.quality.valid) {
        setUploadMessage(`Upload rejected: ${uploaded.quality.issues.join("; ")}`);
        return;
      }
      setDatasetId(uploaded.dataset_id);
      setUploadMessage(`Uploaded dataset ready: ${uploaded.dataset_id}`);
      await investigate(uploaded.dataset_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    investigate("demo");
  }, []);

  const metricData = useMemo(() => {
    if (!report) return [];
    return [
      { period: "Baseline", activation: report.metric_summary.baseline_rate },
      { period: "Current", activation: report.metric_summary.current_rate },
    ];
  }, [report]);

  const segmentData =
    report?.top_segments.slice(0, 5).map((segment) => ({
      name: `${segment.dimension}: ${segment.segment}`,
      delta: Math.abs(segment.absolute_delta),
    })) ?? [];

  const funnelData =
    report?.funnel_findings.map((step) => ({
      step: formatLabel(step.step),
      baseline: step.baseline_conversion,
      current: step.current_conversion,
    })) ?? [];

  function exportMarkdown() {
    if (!report) return;
    const blob = new Blob([report.markdown_report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "activation-drop-investigation.md";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>Activation Drop Investigator</h1>
          <p>Evidence-first investigation for SaaS onboarding regressions.</p>
        </div>
        <div className="top-actions">
          <span className="runtime">
            <ShieldCheck size={16} />
            {report?.runtime_mode === "gemini_adk" ? "Gemini ADK" : "Demo Fallback"}
          </span>
          <button className="icon-button" onClick={exportMarkdown} disabled={!report} title="Export Markdown">
            <Download size={18} />
          </button>
        </div>
      </header>

      <section className="layout">
        <aside className="control-panel">
          <div>
            <h2>Investigation setup</h2>
            <p>Use the demo dataset or upload six CSV files matching the documented schema.</p>
          </div>
          <label>
            Dataset
            <select value={datasetId} onChange={(event) => setDatasetId(event.target.value)}>
              <option value="demo">Demo SaaS Onboarding Dataset</option>
              {datasetId !== "demo" && <option value={datasetId}>Uploaded CSV Dataset</option>}
            </select>
          </label>
          <label>
            CSV upload
            <span className="file-input">
              <FileUp size={16} />
              <input
                type="file"
                accept=".csv"
                multiple
                onChange={(event) => handleUpload(event.currentTarget.files)}
              />
            </span>
          </label>
          {uploadMessage && <p className="upload-message">{uploadMessage}</p>}
          <label>
            Metric
            <select value="activation_rate" disabled>
              <option>Activation rate</option>
            </select>
          </label>
          <div className="period-grid">
            <label>
              Baseline
              <input value="Apr 1-20, 2026" disabled />
            </label>
            <label>
              Current
              <input value="May 1-20, 2026" disabled />
            </label>
          </div>
          <button className="run-button" onClick={() => investigate()} disabled={loading}>
            <PlayCircle size={18} />
            {loading ? "Investigating" : "Run Investigation"}
          </button>
          {error && <p className="error">{error}</p>}

          <div className="schema-note">
            <Sparkles size={16} />
            <span>Agent stack: Metric Analyst, Segment Detective, Funnel Analyst, Release Correlator, Guardrails.</span>
          </div>
        </aside>

        <section className="dashboard">
          {report && (
            <>
              <section className="metric-strip">
                <div>
                  <p>Baseline activation</p>
                  <strong>{pct(report.metric_summary.baseline_rate)}</strong>
                </div>
                <div>
                  <p>Current activation</p>
                  <strong>{pct(report.metric_summary.current_rate)}</strong>
                </div>
                <div>
                  <p>Absolute delta</p>
                  <strong className="negative">{pct(report.metric_summary.absolute_delta)}</strong>
                </div>
                <div>
                  <p>Evidence confidence</p>
                  <strong>High</strong>
                </div>
              </section>

              <section className="chart-grid">
                <div className="panel">
                  <div className="panel-heading">
                    <h2>Activation Trend</h2>
                    <span>baseline vs current</span>
                  </div>
                  <ResponsiveContainer width="100%" height={230}>
                    <LineChart data={metricData} margin={{ left: 0, right: 18, top: 12, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="period" tickLine={false} axisLine={false} />
                      <YAxis tickFormatter={pct} tickLine={false} axisLine={false} width={48} />
                      <Tooltip formatter={(value: number) => pct(value)} />
                      <Line type="monotone" dataKey="activation" stroke="#2563eb" strokeWidth={3} dot={{ r: 5 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="panel">
                  <div className="panel-heading">
                    <h2>Top Segment Contributions</h2>
                    <span>absolute impact</span>
                  </div>
                  <ResponsiveContainer width="100%" height={230}>
                    <BarChart data={segmentData} layout="vertical" margin={{ left: 16, right: 18, top: 12, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                      <XAxis type="number" tickFormatter={pct} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="name" width={118} tickLine={false} axisLine={false} />
                      <Tooltip formatter={(value: number) => pct(value)} />
                      <Bar dataKey="delta" fill="#0f766e" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </section>

              <section className="middle-grid">
                <div className="panel">
                  <div className="panel-heading">
                    <h2>Funnel Conversion</h2>
                    <span>step-level loss</span>
                  </div>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={funnelData} margin={{ left: 0, right: 16, top: 12, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="step" tickLine={false} axisLine={false} interval={0} angle={-18} textAnchor="end" height={60} />
                      <YAxis tickFormatter={pct} tickLine={false} axisLine={false} width={48} />
                      <Tooltip formatter={(value: number) => pct(value)} />
                      <Bar dataKey="baseline" fill="#93c5fd" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="current" fill="#f97316" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="panel agent-panel">
                  <div className="panel-heading">
                    <h2>Agent Investigation</h2>
                    <span>{report.agent_steps.length} agents completed</span>
                  </div>
                  <ul className="agent-list">
                    {report.agent_steps.map((step) => (
                      <li key={step.agent}>
                        <CheckCircle2 size={18} />
                        <div>
                          <strong>{step.agent}</strong>
                          <p>{step.finding}</p>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </section>

              <section className="evidence-grid">
                {report.evidence_cards.map((card) => (
                  <article className="evidence-card" key={card.title}>
                    <div className="card-heading">
                      <Activity size={18} />
                      <span>{formatLabel(card.claim_type)}</span>
                    </div>
                    <h3>{card.title}</h3>
                    <p>{card.summary}</p>
                    <ul>
                      {card.evidence.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </article>
                ))}
              </section>

              <section className="panel report-panel">
                <div className="panel-heading">
                  <h2>Executive Report</h2>
                  <span>exportable Markdown</span>
                </div>
                <p>{report.executive_summary}</p>
                <div className="report-columns">
                  <div>
                    <h3>Ranked hypotheses</h3>
                    <ol>
                      {report.ranked_hypotheses.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ol>
                  </div>
                  <div>
                    <h3>Recommended actions</h3>
                    <ol>
                      {report.recommended_actions.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ol>
                  </div>
                </div>
              </section>
            </>
          )}
        </section>
      </section>
    </main>
  );
}
