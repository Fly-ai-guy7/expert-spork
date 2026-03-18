/**
 * ExpertSpork API Client
 * Typed wrapper around Axios for all API calls
 */

import axios, { type AxiosError, type AxiosResponse } from 'axios'
import type {
  ExpertProfile, Project, Contract, Milestone, Payment,
  Review, MessageThread, Message, Notification,
  PaginatedResponse, ExpertSearchFilters,
  AnalyticsOverview, DashboardStats,
} from '@/types'

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'

export const axiosInstance = axios.create({
  baseURL: `${BASE_URL}/api`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// Response interceptor: unwrap data
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error: AxiosError) => {
    const message =
      (error.response?.data as { message?: string })?.message ??
      error.message ??
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

type APIResponse<T> = Promise<T>

// ─── Auth ────────────────────────────────────────────────

export const auth = {
  me:            (): APIResponse<{ user: { id: string; email: string; name: string; role: string } }> =>
    axiosInstance.get('/auth/me'),
  login:         (data: { email: string; password: string }) =>
    axiosInstance.post('/auth/login', data),
  register:      (data: { email: string; password: string; name: string; role: string; headline?: string }) =>
    axiosInstance.post('/auth/register', data),
  logout:        () => axiosInstance.post('/auth/logout'),
  refresh:       () => axiosInstance.post('/auth/refresh'),
  forgotPassword:(data: { email: string }) => axiosInstance.post('/auth/forgot-password', data),
  resetPassword: (data: { token: string; password: string }) =>
    axiosInstance.post('/auth/reset-password', data),
  verifyEmail:   (data: { token: string }) => axiosInstance.post('/auth/verify-email', data),
}

// ─── Experts ─────────────────────────────────────────────

export const experts = {
  list: (filters: Partial<ExpertSearchFilters>): APIResponse<PaginatedResponse<ExpertProfile>> =>
    axiosInstance.get('/experts', { params: filters }),

  getBySlug: (slug: string): APIResponse<ExpertProfile> =>
    axiosInstance.get(`/experts/${slug}`),

  update: (id: string, data: Partial<ExpertProfile>): APIResponse<ExpertProfile> =>
    axiosInstance.put(`/experts/${id}`, data),

  getReviews: (id: string): APIResponse<PaginatedResponse<Review>> =>
    axiosInstance.get(`/experts/${id}/reviews`),

  getStats: (id: string): APIResponse<{ totalEarnings: number; completionRate: number; avgRating: number }> =>
    axiosInstance.get(`/experts/${id}/stats`),

  uploadPortfolio: (id: string, formData: FormData): APIResponse<{ url: string; publicId: string }> =>
    axiosInstance.post(`/experts/${id}/portfolio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  aiScore: (id: string): APIResponse<{ score: number; breakdown: Record<string, number> }> =>
    axiosInstance.post(`/experts/${id}/ai-score`),
}

// ─── Projects ────────────────────────────────────────────

export const projects = {
  list: (params?: { status?: string; page?: number; pageSize?: number }): APIResponse<PaginatedResponse<Project>> =>
    axiosInstance.get('/projects', { params }),

  get: (id: string): APIResponse<Project> =>
    axiosInstance.get(`/projects/${id}`),

  create: (data: {
    title: string; description: string; budget: number;
    budgetType: string; timeline?: number; skillIds: string[]
  }): APIResponse<Project> =>
    axiosInstance.post('/projects', data),

  update: (id: string, data: Partial<Project>): APIResponse<Project> =>
    axiosInstance.put(`/projects/${id}`, data),

  delete: (id: string): APIResponse<void> =>
    axiosInstance.delete(`/projects/${id}`),

  apply: (id: string, data: { coverLetter: string; proposedRate?: number }): APIResponse<void> =>
    axiosInstance.post(`/projects/${id}/apply`, data),

  getApplicants: (id: string): APIResponse<PaginatedResponse<ExpertProfile>> =>
    axiosInstance.get(`/projects/${id}/applicants`),

  aiMatch: (data: { description: string; budget: number; skillIds: string[] }): APIResponse<ExpertProfile[]> =>
    axiosInstance.post('/projects/ai-match', data),
}

// ─── Contracts ───────────────────────────────────────────

export const contracts = {
  list: (): APIResponse<PaginatedResponse<Contract>> =>
    axiosInstance.get('/contracts'),

  get: (id: string): APIResponse<Contract> =>
    axiosInstance.get(`/contracts/${id}`),

  create: (data: {
    projectId: string; expertId: string; title: string;
    terms: string; totalValue: number; milestones: Array<{
      title: string; description: string; amount: number; dueDate?: string
    }>
  }): APIResponse<Contract> =>
    axiosInstance.post('/contracts', data),

  sign: (id: string): APIResponse<Contract> =>
    axiosInstance.post(`/contracts/${id}/sign`),

  addMilestone: (id: string, data: {
    title: string; description: string; amount: number; dueDate?: string
  }): APIResponse<Milestone> =>
    axiosInstance.post(`/contracts/${id}/milestones`, data),

  updateMilestone: (contractId: string, milestoneId: string, data: Partial<Milestone>): APIResponse<Milestone> =>
    axiosInstance.put(`/contracts/${contractId}/milestones/${milestoneId}`, data),

  submitMilestone: (contractId: string, milestoneId: string, data: { note?: string; files?: string[] }): APIResponse<Milestone> =>
    axiosInstance.post(`/contracts/${contractId}/milestones/${milestoneId}/submit`, data),

  approveMilestone: (contractId: string, milestoneId: string): APIResponse<Milestone> =>
    axiosInstance.post(`/contracts/${contractId}/milestones/${milestoneId}/approve`),

  dispute: (id: string, data: { reason: string; description: string }): APIResponse<Contract> =>
    axiosInstance.post(`/contracts/${id}/dispute`, data),
}

// ─── Payments ────────────────────────────────────────────

export const payments = {
  createIntent: (data: { amount: number; currency: string; milestoneId: string }): APIResponse<{ clientSecret: string }> =>
    axiosInstance.post('/payments/intent', data),

  fundEscrow: (data: { milestoneId: string; paymentIntentId: string }): APIResponse<Payment> =>
    axiosInstance.post('/payments/escrow', data),

  release: (data: { milestoneId: string }): APIResponse<Payment> =>
    axiosInstance.post('/payments/release', data),

  history: (params?: { page?: number; pageSize?: number }): APIResponse<PaginatedResponse<Payment>> =>
    axiosInstance.get('/payments/history', { params }),

  balance: (): APIResponse<{ available: number; pending: number; currency: string }> =>
    axiosInstance.get('/payments/balance'),

  payout: (data: { amount: number }): APIResponse<{ transferId: string }> =>
    axiosInstance.post('/payments/payout', data),
}

// ─── Messages ────────────────────────────────────────────

export const messages = {
  getThreads: (): APIResponse<PaginatedResponse<MessageThread>> =>
    axiosInstance.get('/messages/threads'),

  createThread: (data: { participantIds: string[]; projectId?: string }): APIResponse<MessageThread> =>
    axiosInstance.post('/messages/threads', data),

  getThread: (id: string): APIResponse<MessageThread> =>
    axiosInstance.get(`/messages/threads/${id}`),

  sendMessage: (threadId: string, data: { body: string; attachments?: string[] }): APIResponse<Message> =>
    axiosInstance.post(`/messages/threads/${threadId}/messages`, data),
}

// ─── Reviews ─────────────────────────────────────────────

export const reviews = {
  create: (data: {
    contractId: string; rating: number; communication: number;
    quality: number; timeliness: number; body: string
  }): APIResponse<Review> =>
    axiosInstance.post('/reviews', data),
}

// ─── Notifications ───────────────────────────────────────

export const notifications = {
  list: (): APIResponse<PaginatedResponse<Notification>> =>
    axiosInstance.get('/notifications'),

  markRead: (id: string): APIResponse<void> =>
    axiosInstance.post(`/notifications/${id}/read`),

  markAllRead: (): APIResponse<void> =>
    axiosInstance.post('/notifications/read-all'),
}

// ─── Analytics ───────────────────────────────────────────

export const analytics = {
  overview: (): APIResponse<AnalyticsOverview> =>
    axiosInstance.get('/analytics/overview'),

  dashboard: (): APIResponse<DashboardStats> =>
    axiosInstance.get('/analytics/dashboard'),

  earnings: (params?: { period: '7d' | '30d' | '3m' | '1y' }): APIResponse<{ data: Array<{ date: string; amount: number }> }> =>
    axiosInstance.get('/analytics/earnings', { params }),
}

// ─── Search ──────────────────────────────────────────────

export const search = {
  experts: (params: ExpertSearchFilters): APIResponse<PaginatedResponse<ExpertProfile>> =>
    axiosInstance.get('/search', { params }),
}

// ─── AI ──────────────────────────────────────────────────

export const ai = {
  generateBrief: (data: { title: string; category: string; budget: number }): APIResponse<{ brief: string }> =>
    axiosInstance.post('/ai/generate-brief', data),

  scoreProfile: (data: { profileId: string }): APIResponse<{ score: number; suggestions: string[] }> =>
    axiosInstance.post('/ai/score-profile', data),

  matchExperts: (data: { projectId: string }): APIResponse<Array<{ expert: ExpertProfile; score: number; reasoning: string }>> =>
    axiosInstance.post('/ai/match-experts', data),
}

// Export everything as a single API object
export const api = { auth, experts, projects, contracts, payments, messages, reviews, notifications, analytics, search, ai }
export default api
