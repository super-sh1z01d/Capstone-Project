export type RuntimeMode = "demo_fallback" | "gemini_adk";

export interface MetricSummary {
  baseline_rate: number;
  current_rate: number;
  absolute_delta: number;
  relative_delta: number;
  baseline_users: number;
  current_users: number;
}

export interface SegmentFinding {
  dimension: string;
  segment: string;
  baseline_rate: number;
  current_rate: number;
  absolute_delta: number;
  affected_users: number;
  contribution_score: number;
}

export interface FunnelFinding {
  step: string;
  baseline_conversion: number;
  current_conversion: number;
  absolute_delta: number;
}

export interface ReleaseFinding {
  release_id: string;
  release_date: string;
  component: string;
  description: string;
  days_from_current_start: number;
}

export interface EvidenceCard {
  title: string;
  claim_type: "observed" | "likely" | "needs_verification";
  summary: string;
  evidence: string[];
  confidence: "high" | "medium" | "low";
}

export interface AgentStep {
  agent: string;
  status: "completed" | "skipped";
  finding: string;
}

export interface AgentSkill {
  skill_id: string;
  name: string;
  description: string;
  tool_names: string[];
  output_contract: string;
}

export interface InvestigationReport {
  runtime_mode: RuntimeMode;
  metric_summary: MetricSummary;
  top_segments: SegmentFinding[];
  funnel_findings: FunnelFinding[];
  release_findings: ReleaseFinding[];
  evidence_cards: EvidenceCard[];
  agent_steps: AgentStep[];
  skills_used: AgentSkill[];
  executive_summary: string;
  ai_synthesis: string | null;
  ranked_hypotheses: string[];
  recommended_actions: string[];
  limitations: string[];
  markdown_report: string;
}

export interface UploadedDatasetResponse {
  dataset_id: string;
  quality: {
    valid: boolean;
    issues: string[];
    row_counts: Record<string, number>;
  };
}
