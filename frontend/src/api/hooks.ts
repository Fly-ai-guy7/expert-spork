import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import type {
  CaseDetail,
  CaseStatusPayload,
  CaseSummary,
  TrainingSessionRecord,
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

export function useCancelCase() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) =>
      (await api.post(`/api/v1/cases/${id}/cancel`, {})).data,
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ["case", id] });
      qc.invalidateQueries({ queryKey: ["case-status", id] });
    },
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

export function useCoachingReport(sessionId: string | undefined) {
  return useQuery({
    queryKey: ["coaching", sessionId],
    queryFn: async () =>
      (await api.get<TrainingSessionRecord>(`/api/training/${sessionId}/coaching`)).data,
    enabled: !!sessionId,
  });
}

export function useTrainingSessions(userId?: string) {
  return useQuery({
    queryKey: ["training-sessions", userId],
    queryFn: async () =>
      (
        await api.get<TrainingSessionRecord[]>(`/api/training/sessions`, {
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
