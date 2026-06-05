export type CaseStatus = "DRAFT" | "RUNNING" | "PAUSED_HIL" | "COMPLETE" | "FAILED" | "CANCELLED";
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
  cancel_requested?: boolean;
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
