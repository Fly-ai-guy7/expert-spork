import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import type {
  CaseDetail,
  CaseReportPayload,
  CaseStatusPayload,
  CaseSummary,
  CounselLogEntry,
  CounselResponse,
  InstructorOverview,
  TrainingSessionRecord,
  TrainingSessionSummary,
} from "./types";

export function useCases() {
  return useQuery({
    queryKey: ["cases"],
    queryFn: async () => (await api.get<CaseSummary[]>("/api/cases")).data,
  });
}

export function useCase(id: string | undefined) {
  return useQuery({
    queryKey: ["case", id],
    queryFn: async () => (await api.get<CaseDetail>(`/api/cases/${id}`)).data,
    enabled: !!id,
  });
}

export function useCaseStatus(id: string | undefined, pollMs = 2000) {
  return useQuery({
    queryKey: ["case-status", id],
    queryFn: async () => (await api.get<CaseStatusPayload>(`/api/cases/${id}/status`)).data,
    enabled: !!id,
    refetchInterval: pollMs,
  });
}

export function useGenerateCase() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { area_of_law: string; difficulty: number; language: string }) =>
      (await api.post<CaseDetail>("/api/cases/generate", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["cases"] }),
  });
}

export function useCreateCase() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Partial<CaseDetail>) =>
      (await api.post<CaseDetail>("/api/cases", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["cases"] }),
  });
}

export function useRunCase() {
  return useMutation({
    mutationFn: async (id: string) =>
      (await api.post(`/api/cases/${id}/run`, { max_rounds: null })).data,
  });
}

export function useRunTraining() {
  return useMutation({
    mutationFn: async (args: { case_id: string; trainee_role: "PROSECUTION" | "DEFENSE"; user_id: string; difficulty: number }) =>
      (await api.post(`/api/cases/${args.case_id}/run-training`, {
        trainee_role: args.trainee_role,
        user_id: args.user_id,
        difficulty: args.difficulty,
      })).data,
  });
}

export function useSubmitTrainee() {
  return useMutation({
    mutationFn: async (args: { checkpoint_id: string; content_en: string; citations: string[] }) =>
      (await api.post(`/api/hil/${args.checkpoint_id}/submit-trainee`, {
        content_en: args.content_en,
        citations: args.citations,
      })).data,
  });
}

export function useCounsel() {
  return useMutation({
    mutationFn: async (args: {
      checkpoint_id: string;
      content_en: string;
      citations: string[];
    }) =>
      (
        await api.post<CounselResponse>(`/api/hil/${args.checkpoint_id}/counsel`, {
          content_en: args.content_en,
          citations: args.citations,
        })
      ).data,
  });
}

export function useCaseCounsel() {
  return useMutation({
    mutationFn: async (args: {
      case_id: string;
      content_en?: string;
      citations?: string[];
      trainee_role?: "PROSECUTION" | "DEFENSE";
    }) =>
      (
        await api.post<CounselResponse>(`/api/cases/${args.case_id}/counsel`, {
          content_en: args.content_en,
          citations: args.citations,
          trainee_role: args.trainee_role,
        })
      ).data,
  });
}

export function useCaseReport(id: string | undefined) {
  return useQuery({
    queryKey: ["case-report", id],
    queryFn: async () => (await api.get<CaseReportPayload>(`/api/cases/${id}/report`)).data,
    enabled: !!id,
  });
}

export function useCoachingReport(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["coaching", sessionId],
    queryFn: async () =>
      (await api.get<TrainingSessionRecord>(`/api/training/${sessionId}/coaching`)).data,
    enabled: !!sessionId,
  });
}

export function useCounselLog(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["counsel-log", sessionId],
    queryFn: async () =>
      (await api.get<CounselLogEntry[]>(`/api/training/${sessionId}/counsel-log`)).data,
    enabled: !!sessionId,
  });
}

export function useInstructorOverview(userId?: string) {
  return useQuery({
    queryKey: ["instructor-overview", userId],
    queryFn: async () =>
      (
        await api.get<InstructorOverview>(`/api/training/instructor/overview`, {
          params: userId ? { user_id: userId } : {},
        })
      ).data,
  });
}

export function useTrainingSessions(userId?: string) {
  return useQuery({
    queryKey: ["training-sessions", userId],
    queryFn: async () =>
      (
        await api.get<TrainingSessionSummary[]>(`/api/training/sessions`, {
          params: userId ? { user_id: userId } : {},
        })
      ).data,
  });
}

export function useStatutes() {
  return useQuery({
    queryKey: ["statutes"],
    queryFn: async () => (await api.get("/api/statutes")).data,
  });
}
