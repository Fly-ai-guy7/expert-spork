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
  counsel_calls_count?: number;
  council_alignment?: "WON" | "LOST";
  council_for_trainee?: number;
  council_against_trainee?: number;
  council_supporters?: string[];
  council_dissenters?: string[];
}

export interface TrainingSessionSummary {
  id: string;
  case_id: string;
  user_id: string;
  trainee_role: TraineeRole;
  difficulty: number;
  total_score: number | null;
  completed_at: string | null;
  grade: string | null;
  council_alignment: "WON" | "LOST" | null;
  counsel_calls_count: number;
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

export type CouncilVote = "FOR_PLAINTIFF" | "FOR_DEFENDANT";

export interface CouncilVerdictRecord {
  member_llm: string;
  verdict: CouncilVote;
  plaintiff_success_prob: number;
  override_flagged: boolean;
  reasoning_en: string | null;
  reasoning_ar: string | null;
}

export interface RulingPayload {
  plaintiff_success_prob: number | null;
  text_en: string | null;
  text_ar: string | null;
  critical_evidence_gaps: string[];
  precedent_refs: string[];
  override_applied: boolean;
  council_size: number | null;
  council_vote: { for_plaintiff: number; for_defendant: number } | null;
  dissent_en: string | null;
  dissent_ar: string | null;
  council_verdicts: CouncilVerdictRecord[];
}

export interface CaseReportPayload {
  disclaimer: { en: string; ar: string };
  case: { id: string; title_en: string | null; title_ar: string | null };
  ruling: RulingPayload | null;
  outcome: {
    projected_prob: number | null;
    risk_score: number | null;
    pretrial_resolution_en: string | null;
    pretrial_resolution_ar: string | null;
  } | null;
}

export interface CounselAdvice {
  strategy_en: string | null;
  strategy_ar: string | null;
  suggested_citations: string[];
  strengths: string[];
  risks: string[];
  missing_arguments: string[];
}

export interface CounselResponse {
  disclaimer: { en: string; ar: string };
  advice: CounselAdvice;
  llm_used: string;
}

export interface InstructorPerUser {
  user_id: string;
  sessions: number;
  avg_score: number;
  latest_grade: string | null;
  latest_completed_at: string | null;
}

export interface InstructorAttentionRow {
  session_id: string;
  user_id: string;
  trainee_role: TraineeRole;
  grade: string | null;
  total_score: number | null;
  council_alignment: "WON" | "LOST" | null;
  counsel_calls_count: number;
  completed_at: string | null;
}

export interface InstructorOverview {
  total_sessions: number;
  completed_sessions: number;
  avg_score: number;
  grade_distribution: Record<string, number>;
  per_user: InstructorPerUser[];
  top_missed_citations: { citation: string; count: number }[];
  top_weak_patterns: { pattern: string; count: number }[];
  council_lost_rate: number | null;
  needs_attention: InstructorAttentionRow[];
}

export interface CounselLogEntry {
  id: string;
  created_at: string;
  trainee_role: string;
  draft_en: string | null;
  draft_ar: string | null;
  citations: string[];
  advice: CounselAdvice;
  llm_used: string | null;
}
