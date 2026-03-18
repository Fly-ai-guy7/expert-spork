// ExpertSpork — Core TypeScript Types

export type UserRole = 'EXPERT' | 'CLIENT' | 'ADMIN'
export type Availability = 'FULL_TIME' | 'PART_TIME' | 'UNAVAILABLE'
export type ProjectStatus = 'DRAFT' | 'OPEN' | 'IN_REVIEW' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED'
export type BudgetType = 'FIXED' | 'HOURLY'
export type ContractStatus = 'PENDING' | 'ACTIVE' | 'PAUSED' | 'COMPLETED' | 'DISPUTED' | 'CANCELLED'
export type MilestoneStatus = 'PENDING' | 'FUNDED' | 'IN_PROGRESS' | 'SUBMITTED' | 'APPROVED' | 'PAID' | 'DISPUTED'
export type PaymentStatus = 'PENDING' | 'ESCROWED' | 'RELEASED' | 'REFUNDED' | 'FAILED'
export type ApplicationStatus = 'PENDING' | 'SHORTLISTED' | 'ACCEPTED' | 'REJECTED' | 'WITHDRAWN'

// ─── Core Models ─────────────────────────────────────────

export interface User {
  id: string
  email: string
  name: string | null
  image: string | null
  role: UserRole
  createdAt: string
}

export interface Skill {
  id: string
  name: string
  slug: string
  category: string
  icon?: string
}

export interface ExpertProfile {
  id: string
  userId: string
  slug: string
  displayName: string
  headline: string
  bio: string
  hourlyRate: number
  currency: string
  availability: Availability
  aiScore: number
  totalEarnings: number
  completionRate: number
  responseTime: number
  location: string | null
  timezone: string | null
  languages: string[]
  isPublic: boolean
  isVerified: boolean
  isFeatured: boolean
  profileViews: number
  coverColor: string
  skills: ExpertSkill[]
  portfolio: PortfolioItem[]
  services: ExpertService[]
  user: User
  _count?: { reviews: number }
  averageRating?: number
  createdAt: string
}

export interface ExpertSkill {
  skillId: string
  skill: Skill
  yearsExp: number | null
  isPrimary: boolean
}

export interface PortfolioItem {
  id: string
  title: string
  description: string | null
  imageUrls: string[]
  projectUrl: string | null
  tags: string[]
  sortOrder: number
  createdAt: string
}

export interface ExpertService {
  id: string
  title: string
  description: string
  price: number
  priceType: 'FIXED' | 'STARTING_FROM' | 'MONTHLY'
  deliveryDays: number | null
  revisions: number | null
  includes: string[]
  sortOrder: number
}

export interface Project {
  id: string
  clientId: string
  title: string
  description: string
  budget: number
  budgetType: BudgetType
  timeline: number | null
  status: ProjectStatus
  applicantCount: number
  viewCount: number
  skills: { skill: Skill }[]
  client: User
  createdAt: string
  closedAt: string | null
}

export interface Contract {
  id: string
  projectId: string
  expertId: string
  clientId: string
  title: string
  terms: string
  totalValue: number
  currency: string
  status: ContractStatus
  startDate: string | null
  endDate: string | null
  milestones: Milestone[]
  expert: User
  client: User
  project: Project
  createdAt: string
}

export interface Milestone {
  id: string
  contractId: string
  title: string
  description: string
  amount: number
  dueDate: string | null
  status: MilestoneStatus
  sortOrder: number
  submittedAt: string | null
  approvedAt: string | null
  deliverables: Deliverable[]
  payment?: Payment
}

export interface Deliverable {
  id: string
  name: string
  fileUrl: string | null
  notes: string | null
  createdAt: string
}

export interface Payment {
  id: string
  milestoneId: string
  fromUserId: string
  toUserId: string
  amount: number
  fee: number
  currency: string
  status: PaymentStatus
  createdAt: string
  releasedAt: string | null
}

export interface Review {
  id: string
  contractId: string
  authorId: string
  targetId: string
  rating: number
  communication: number
  quality: number
  timeliness: number
  body: string
  isPublic: boolean
  author: User
  contract?: { project: { title: string } }
  createdAt: string
}

export interface MessageThread {
  id: string
  contractId: string | null
  title: string | null
  lastMessageAt: string
  participants: { user: User; lastReadAt: string | null }[]
  messages: Message[]
  contract?: Contract
}

export interface Message {
  id: string
  threadId: string
  senderId: string
  body: string
  attachments: string[]
  isEdited: boolean
  readAt: string | null
  sender: User
  createdAt: string
}

export interface Notification {
  id: string
  userId: string
  type: string
  title: string
  body: string
  link: string | null
  isRead: boolean
  createdAt: string
}

// ─── API Response Types ───────────────────────────────────

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface ApiError {
  message: string
  code?: string
  field?: string
}

// ─── Form / Input Types ───────────────────────────────────

export interface ExpertSearchFilters {
  query: string
  category: string[]
  skills: string[]
  rateMin: number
  rateMax: number
  availability: string[]
  rating: number
  sort: 'relevance' | 'rating' | 'rate_asc' | 'rate_desc' | 'newest'
  page: number
  pageSize: number
}

export interface BudgetBreakdown {
  budgetType: BudgetType
  subtotal: number
  feeRate: number
  fee: number
  expertReceives: number
  clientPays: number
}

export interface OnboardingData {
  role: UserRole | null
  name: string
  email: string
  password: string
  // Expert
  headline?: string
  bio?: string
  skills?: string[]
  portfolioFiles?: File[]
  hourlyRate?: number
  currency?: string
  availability?: Availability
  // Client
  companyName?: string
  companySize?: string
  industry?: string
}

// ─── Analytics Types ──────────────────────────────────────

export interface AnalyticsOverview {
  totalEarnings: number
  earningsDelta: number
  activeProjects: number
  projectsDelta: number
  completionRate: number
  completionDelta: number
  averageRating: number
  profileViews: number
  viewsDelta: number
}

export interface EarningsDataPoint {
  date: string
  amount: number
}

export interface DashboardStats {
  overview: AnalyticsOverview
  earningsHistory: EarningsDataPoint[]
  recentPayments: Payment[]
  upcomingMilestones: Milestone[]
  activeProjects: Project[]
}

// ─── Component Prop Types ─────────────────────────────────

export interface BadgeVariant {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'ai'
}

export interface ButtonVariant {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}
