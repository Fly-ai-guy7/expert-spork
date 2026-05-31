export type CaseStatus = "DRAFT" | "RUNNING" | "PAUSED_HIL" | "COMPLETE" | "FAILED";
export type CaseSource = "USER_AUTHORED" | "AI_GENERATED";
export type AgentRole = "PROSECUTION" | "DEFENSE" | "JUDICIAL" | "TRAINEE";
export type TraineeRole = "PROSECUTION" | "DEFENSE";

export interface CaseSummary {
  id: string;
  title_en: string | null;
  title_ar: string | null;
  status: CaseStatus;
  source: CaseSource;
  area_of_law: string | null;
  difficulty: number | null;
  created_at: string;
}

export interface Party {
  id: string;
  role: "PLAINTIFF" | "DEFENDANT" | "THIRD_PARTY";
  kind: "NATURAL" | "LEGAL";
  name_en: string | null;
  name_ar: string | null;
}

export interface CaseDetail extends CaseSummary {
  summary_en: string | null;
  summary_ar: string | null;
  language_primary: string;
  parties: Party[];
  facts: { id: string; text_en: string | null; text_ar: string | null; disputed: boolean; order_index: number }[];
  evidence: { id: string; kind: string; title_en: string | null; title_ar: string | null; missing: boolean }[];
}

export interface ArgumentRecord {
  id: string;
  agent: AgentRole;
  round_no: number;
  content_en: string | null;
  content_ar: string | null;
  llm_used: string | null;
  score_overall: number | null;
}

export interface CaseStatusPayload {
  case_id: string;
  status: CaseStatus;
  rounds_complete: number;
  rounds_total: number;
  arguments: ArgumentRecord[];
  pending_checkpoint_id: string | null;
  pending_checkpoint_stage: string | null;
}

export interface CoachingReport {
  grade: string;
  total_score: number;
  per_round: {
    round_no: number;
    factual: number;
    provable: number;
    unbiased: number;
    legal_law_based: number;
    overall: number;
    rationale_en: string | null;
    rationale_ar: string | null;
  }[];
  missed_citations: string[];
  evidence_gaps_to_address: string[];
  weak_patterns: string[];
}

export interface TrainingSessionRecord {
  training_session_id: string;
  case_id: string;
  trainee_role: TraineeRole;
  difficulty: number;
  total_score: number | null;
  coaching_report: CoachingReport | Record<string, never>;
  started_at: string | null;
  completed_at: string | null;
}

export interface OverdueItem {
  checkpoint_id: string;
  case_id: string;
  title_en: string | null;
  title_ar: string | null;
  stage: string;
  created_at: string;
  age_hours: number;
}

export interface RiskCell {
  area_of_law: string;
  difficulty: number | null;
  avg_risk: number;
  count: number;
}

export type ActivityType =
  | "case_created"
  | "ruling_issued"
  | "training_completed"
  | "checkpoint_responded";

export interface ActivityEvent {
  type: ActivityType;
  at: string;
  case_id: string;
  title_en: string | null;
  title_ar: string | null;
  detail: string;
}

export interface Dashboard {
  generated_at: string;
  open_issues: {
    by_status: Record<CaseStatus, number>;
    open_total: number;
    pending_checkpoints: number;
    awaiting_trainee: number;
  };
  overdue: {
    threshold_hours: number;
    count: number;
    items: OverdueItem[];
  };
  risk_heatmap: {
    areas: string[];
    difficulties: number[];
    cells: RiskCell[];
    max_risk: number;
  };
  recent_activity: ActivityEvent[];
  disclaimer: { en: string; ar: string };
}
