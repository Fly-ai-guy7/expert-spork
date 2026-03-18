# ROLE 1: SYSTEMS ARCHITECT
## ExpertSpork — AI-Powered Freelancer Marketplace + Project Management Platform

---

## PRODUCT DEFINITION

| Attribute | Value |
|-----------|-------|
| Website/App Type | SaaS Marketplace + Project Management Dashboard |
| Primary Audience | High-value freelancers (dev, design, strategy) + scaling startups/agencies hiring talent |
| Core Capabilities | Talent discovery, AI-matched projects, contract management, payments, analytics |
| Technical Priorities | PERFORMANCE · SCALABILITY · SEO · RESPONSIVE |

---

## FULL INFORMATION ARCHITECTURE

```
expertspork.com/
├── / (Landing)
├── /explore (Talent Discovery)
│   ├── /explore/[category] (Category Browse)
│   └── /explore/[profile-slug] (Expert Profile)
├── /projects (Project Board)
│   ├── /projects/post (Post a Project)
│   └── /projects/[id] (Project Detail)
├── /how-it-works
├── /pricing
├── /blog
│   └── /blog/[slug]
├── /about
├── /auth
│   ├── /auth/login
│   ├── /auth/register
│   └── /auth/reset-password
└── /dashboard (Protected)
    ├── /dashboard/overview
    ├── /dashboard/projects
    │   ├── /dashboard/projects/active
    │   ├── /dashboard/projects/[id]
    │   └── /dashboard/projects/new
    ├── /dashboard/contracts
    │   └── /dashboard/contracts/[id]
    ├── /dashboard/payments
    │   ├── /dashboard/payments/invoices
    │   └── /dashboard/payments/history
    ├── /dashboard/messages
    │   └── /dashboard/messages/[thread-id]
    ├── /dashboard/profile
    │   ├── /dashboard/profile/edit
    │   └── /dashboard/profile/portfolio
    ├── /dashboard/reviews
    ├── /dashboard/analytics
    └── /dashboard/settings
        ├── /dashboard/settings/account
        ├── /dashboard/settings/notifications
        ├── /dashboard/settings/billing
        └── /dashboard/settings/integrations
```

---

## 3 KEY USER JOURNEY FLOWS

### JOURNEY 1: Expert Onboarding → First Paid Project
```
Landing Page (hero CTA "Earn More as an Expert")
→ Register (email / OAuth)
→ Profile Builder: Step 1 Skills + Bio
→ Profile Builder: Step 2 Portfolio Upload
→ Profile Builder: Step 3 Rate + Availability
→ AI Profile Score Generated (min 70% to go live)
→ Profile Live → Explore Board Visible
→ AI Suggests 3 Matching Projects → Expert Applies
→ Client Reviews + Accepts → Contract Created
→ Milestone 1 Funded (Escrow) → Work Starts
→ Delivery → Client Approves → Payment Released
→ Review Exchange → Dashboard Updated
```

### JOURNEY 2: Client → Hired Expert in <10 min
```
Landing Page (hero CTA "Hire Top Experts Today")
→ Browse /explore or Use AI Match
→ Filter: Skill · Rate · Availability · Rating
→ View Profile → View Portfolio → Send Proposal
→ OR: Post a Project (structured brief)
→ AI auto-matches top 5 Experts → Client Selects
→ Contract Builder: Milestones + Budget + Timeline
→ Escrow Payment Funded → Work Begins
→ Dashboard: Track progress + Message Expert
→ Approve Milestones → Release Payment
→ Leave Review → Project Archived
```

### JOURNEY 3: Returning Client → Repeat Hire
```
Dashboard Login → "Your Trusted Experts" Section
→ One-click Re-hire from Past Projects
→ New Project Brief Auto-filled from History
→ Contract Template Reused → Minor Edits
→ Expert Notified → Accepts in 1-click
→ Milestone Payments Automated via Saved Card
```

---

## DATA ARCHITECTURE

### Core Entities + Schema Design

```typescript
// User (polymorphic: Expert | Client)
User {
  id: uuid PK
  email: string UNIQUE
  passwordHash: string
  role: enum(EXPERT | CLIENT | ADMIN)
  createdAt: timestamp
  updatedAt: timestamp
  stripeCustomerId: string?
  avatarUrl: string?
  isVerified: boolean
  twoFactorEnabled: boolean
}

// ExpertProfile
ExpertProfile {
  id: uuid PK
  userId: uuid FK → User
  displayName: string
  slug: string UNIQUE
  headline: string (max 120)
  bio: text (max 1000)
  hourlyRate: decimal
  currency: string (default USD)
  availability: enum(FULL_TIME | PART_TIME | UNAVAILABLE)
  aiScore: integer (0–100)
  totalEarnings: decimal
  completionRate: decimal
  responseTime: integer (minutes avg)
  location: string
  timezone: string
  skills: Skill[] (M2M)
  portfolio: PortfolioItem[]
  languages: string[]
  isPublic: boolean
  createdAt: timestamp
}

// Skill (taxonomy)
Skill {
  id: uuid PK
  name: string UNIQUE
  category: string (Design | Engineering | Strategy | Marketing)
  slug: string
}

// Project
Project {
  id: uuid PK
  clientId: uuid FK → User
  title: string
  description: text
  budget: decimal
  budgetType: enum(FIXED | HOURLY)
  timeline: integer (days)
  status: enum(DRAFT | OPEN | IN_REVIEW | ACTIVE | COMPLETED | CANCELLED)
  skillsRequired: Skill[] (M2M)
  visibility: enum(PUBLIC | INVITE_ONLY)
  aiMatchScore: decimal?
  createdAt: timestamp
  closedAt: timestamp?
}

// Contract
Contract {
  id: uuid PK
  projectId: uuid FK → Project
  expertId: uuid FK → User
  clientId: uuid FK → User
  terms: text
  totalValue: decimal
  currency: string
  status: enum(PENDING | ACTIVE | PAUSED | COMPLETED | DISPUTED | CANCELLED)
  startDate: date
  endDate: date?
  milestones: Milestone[]
  createdAt: timestamp
  signedAt: timestamp?
}

// Milestone
Milestone {
  id: uuid PK
  contractId: uuid FK → Contract
  title: string
  description: text
  amount: decimal
  dueDate: date
  status: enum(PENDING | FUNDED | IN_PROGRESS | SUBMITTED | APPROVED | PAID | DISPUTED)
  deliverables: Deliverable[]
  submittedAt: timestamp?
  approvedAt: timestamp?
}

// Payment
Payment {
  id: uuid PK
  milestoneId: uuid FK → Milestone
  fromUserId: uuid FK → User
  toUserId: uuid FK → User
  amount: decimal
  fee: decimal (platform 8%)
  currency: string
  status: enum(PENDING | ESCROWED | RELEASED | REFUNDED | FAILED)
  stripePaymentIntentId: string?
  createdAt: timestamp
  releasedAt: timestamp?
}

// Review
Review {
  id: uuid PK
  contractId: uuid FK → Contract
  authorId: uuid FK → User
  targetId: uuid FK → User
  rating: integer (1–5)
  communication: integer (1–5)
  quality: integer (1–5)
  timeliness: integer (1–5)
  body: text
  isPublic: boolean
  createdAt: timestamp
}

// Message
Message {
  id: uuid PK
  threadId: uuid FK → MessageThread
  senderId: uuid FK → User
  body: text
  attachments: string[]
  readAt: timestamp?
  createdAt: timestamp
}

// MessageThread
MessageThread {
  id: uuid PK
  projectId: uuid FK → Project?
  participants: User[] (M2M)
  lastMessageAt: timestamp
  createdAt: timestamp
}

// Notification
Notification {
  id: uuid PK
  userId: uuid FK → User
  type: enum(PROJECT_MATCH | MESSAGE | PAYMENT | REVIEW | MILESTONE | SYSTEM)
  title: string
  body: string
  link: string?
  isRead: boolean
  createdAt: timestamp
}
```

---

## API SURFACE

### REST Endpoints

#### Auth
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
POST   /api/auth/forgot-password
POST   /api/auth/reset-password
GET    /api/auth/me
POST   /api/auth/verify-email
POST   /api/auth/2fa/enable
POST   /api/auth/2fa/verify
```

#### Users & Profiles
```
GET    /api/experts                    (paginated, filtered)
GET    /api/experts/:slug              (public profile)
PUT    /api/experts/:id                (authenticated)
POST   /api/experts/:id/portfolio      (upload)
DELETE /api/experts/:id/portfolio/:pid
GET    /api/experts/:id/reviews
GET    /api/experts/:id/stats
```

#### Projects
```
GET    /api/projects                   (paginated, filtered)
POST   /api/projects                   (create)
GET    /api/projects/:id
PUT    /api/projects/:id
DELETE /api/projects/:id
POST   /api/projects/:id/apply
GET    /api/projects/:id/applicants
POST   /api/projects/ai-match          (AI suggestion)
```

#### Contracts
```
GET    /api/contracts
POST   /api/contracts
GET    /api/contracts/:id
PUT    /api/contracts/:id
POST   /api/contracts/:id/sign
POST   /api/contracts/:id/milestones
PUT    /api/contracts/:id/milestones/:mid
POST   /api/contracts/:id/milestones/:mid/submit
POST   /api/contracts/:id/milestones/:mid/approve
POST   /api/contracts/:id/dispute
```

#### Payments
```
POST   /api/payments/intent            (create Stripe intent)
POST   /api/payments/escrow            (fund escrow)
POST   /api/payments/release           (release milestone)
POST   /api/payments/refund
GET    /api/payments/history
GET    /api/payments/balance           (expert payout balance)
POST   /api/payments/payout
POST   /api/webhooks/stripe            (Stripe webhook)
```

#### Messages
```
GET    /api/messages/threads
POST   /api/messages/threads
GET    /api/messages/threads/:id
POST   /api/messages/threads/:id/messages
DELETE /api/messages/threads/:id/messages/:mid
```

#### Reviews
```
POST   /api/reviews
GET    /api/reviews/:id
PUT    /api/reviews/:id
DELETE /api/reviews/:id
```

#### Analytics (dashboard)
```
GET    /api/analytics/overview
GET    /api/analytics/earnings
GET    /api/analytics/projects
GET    /api/analytics/profile-views
```

#### Search
```
GET    /api/search?q=&category=&skills=&rate_min=&rate_max=&availability=&sort=
```

### Auth Strategy
- **JWT** (access: 15min, refresh: 7d stored in httpOnly cookie)
- **OAuth** providers: Google, GitHub, LinkedIn
- **Row-level security** via user ID claims
- **API rate limiting**: 100req/min authenticated, 20req/min public

### Third-Party Integrations
| Service | Purpose |
|---------|---------|
| Stripe Connect | Payments, escrow, payouts |
| Cloudinary | Portfolio + avatar media |
| Resend | Transactional email |
| OpenAI API | AI matching, profile scoring, brief generation |
| Pusher / Ably | Real-time messaging + notifications |
| Algolia | Expert + project search |
| Sentry | Error monitoring |
| PostHog | Product analytics |

---

## COMPONENT INVENTORY (30+ UI Components)

### Primitives (8)
1. Button (primary/secondary/ghost/danger, sm/md/lg, loading state)
2. Input (text/email/password/number, error/disabled states)
3. Textarea (auto-resize, character count)
4. Select (searchable, multi-select)
5. Checkbox / Radio Group
6. Badge (status: success/warning/error/info/neutral)
7. Avatar (image/initials fallback, sizes: xs/sm/md/lg/xl)
8. Spinner / Skeleton Loader

### Navigation (4)
9. TopNav (logo, links, auth CTAs, mobile hamburger)
10. SideNav (dashboard, icon + label, collapse state)
11. Breadcrumb
12. Pagination

### Feedback (4)
13. Toast / Snackbar (success/error/info)
14. Modal / Dialog (with backdrop, keyboard trap)
15. Tooltip (top/bottom/left/right)
16. Alert Banner (dismissible)

### Data Display (7)
17. Card (expert, project, contract variants)
18. Table (sortable columns, row actions, empty state)
19. Stats Card (metric + delta + sparkline)
20. Progress Bar (milestone completion)
21. Rating Stars (display + input)
22. Tag / Chip List
23. Timeline (contract milestones)

### Forms (5)
24. SearchBar (with suggestions dropdown)
25. FilterPanel (sidebar facets: range, checkbox, toggle)
26. MultiStepForm (progress indicator + step navigation)
27. FileUpload (drag-and-drop, preview, progress)
28. DateRangePicker

### Layout (5)
29. PageHeader (title, breadcrumb, action buttons)
30. SectionWrapper (padding, max-width, bg variants)
31. Grid Layout (1-2-3-4 col responsive)
32. SplitPane (editor/preview pattern)
33. EmptyState (icon + copy + CTA)

### Domain-Specific (7+)
34. ExpertCard (avatar, name, skill tags, rate, rating, CTA)
35. ProjectCard (title, budget, skills, deadline, applicant count)
36. ContractSummary (parties, value, status, milestone progress)
37. MilestoneItem (status stepper, actions: submit/approve/dispute)
38. PaymentRow (amount, status, date, action)
39. ReviewCard (rating breakdown, body, author)
40. MessageBubble (sent/received, timestamp, attachments)
41. NotificationItem (type icon, body, time, read state)
42. AIMatchBadge (score indicator + explanation tooltip)

---

## PAGE BLUEPRINTS

### Landing Page `/`
```
[TopNav: Logo | Links | "Post a Project" | "Become an Expert"]
[Hero: Full-width | H1 | Sub | Dual CTA | Social Proof Numbers]
[Trust Bar: Logo strip of client companies]
[How It Works: 3-step horizontal flow]
[Featured Experts: Horizontal scroll card row]
[Categories Grid: 8 skill categories with icons]
[Why ExpertSpork: 3-column feature grid]
[Testimonials: 3-card carousel]
[Pricing Teaser: 2 plan cards + CTA]
[FAQ: Accordion 8 items]
[Final CTA Banner: Full-width gradient]
[Footer: 5-col links + social + legal]
```

### Explore Page `/explore`
```
[TopNav]
[PageHeader: Search + Active Filter Tags]
[SideBar Filters: Category | Skills | Rate Range | Availability | Rating]
[Results Grid: 3-col ExpertCards | Pagination]
[Sort Controls: Relevance | Rating | Rate | Newest]
```

### Expert Profile `/explore/[slug]`
```
[TopNav]
[ProfileHero: Cover | Avatar | Name | Rate | Rating | Stats | Hire CTA]
[Skills Tags Row]
[Bio Section]
[Portfolio Grid: 2-3 col masonry]
[Services Section: 2-3 packaged offers with prices]
[Work History: Timeline]
[Reviews: Rating breakdown + Review cards]
[Sticky Hire Sidebar (desktop): Rate | Availability | CTA]
```

### Dashboard `/dashboard/overview`
```
[SideNav fixed]
[PageHeader: "Good morning, [Name]"]
[Stats Row: Earnings | Active Projects | Pending Reviews | Unread Messages]
[Active Projects Table]
[Upcoming Milestones Timeline]
[Recent Payments Table]
[Quick Actions: New Project | Invite Expert | View Analytics]
```

---

## RECOMMENDED TECH STACK

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS 3 + CSS Variables |
| Components | shadcn/ui (Radix UI primitives) |
| State | Zustand + React Query (TanStack v5) |
| Forms | React Hook Form + Zod |
| Database | PostgreSQL 16 (Supabase) |
| ORM | Prisma 5 |
| Auth | NextAuth.js v5 (Auth.js) |
| Payments | Stripe Connect |
| Search | Algolia InstantSearch |
| Media | Cloudinary |
| Email | Resend + React Email |
| Realtime | Supabase Realtime |
| AI | OpenAI GPT-4o API |
| Hosting | Vercel (Edge Runtime) |
| CDN | Vercel Edge Network |
| Monitoring | Sentry + Vercel Analytics |
| Analytics | PostHog |

---

## PERFORMANCE BENCHMARKS (Core Web Vitals Targets)

| Metric | Target | Strategy |
|--------|--------|---------|
| LCP | < 1.5s | Image CDN, preload hero, Edge SSR |
| FID / INP | < 50ms | Code-split, defer non-critical JS |
| CLS | < 0.05 | Reserve image dimensions, no layout shift |
| TTFB | < 200ms | Vercel Edge, Postgres connection pooling |
| Lighthouse | > 95 | All categories |
| Bundle Size | < 150KB initial JS | Tree shaking, dynamic imports |

---

## SEO FRAMEWORK

### URL Strategy
- Clean slugs: `/explore/sarah-chen-react-developer`
- Category pages: `/explore/frontend-development`
- Blog: `/blog/how-to-hire-freelance-developers`

### Metadata Strategy
```typescript
// Expert Profile (dynamic)
title: `${name} — ${headline} | ExpertSpork`
description: `Hire ${name}, a ${topSkill} expert. ${rate}/hr. ${rating}★ from ${reviewCount} reviews.`
og:image: Dynamically generated via @vercel/og

// Explore Category
title: `Hire ${category} Experts | ExpertSpork`
description: `Browse ${count}+ vetted ${category} experts. Find the perfect match for your project.`

// Project Listing
canonical: Always set
robots: noindex for /dashboard, /auth
```

### Schema.org
- `Person` schema on expert profiles
- `JobPosting` schema on project listings
- `Review` + `AggregateRating` on profiles
- `BreadcrumbList` on all inner pages
- `FAQPage` schema on landing + how-it-works
- `Organization` on homepage

### Sitemap
- Auto-generated via `next-sitemap`
- Dynamic routes: all public profiles + open projects + blog posts
- Update frequency: daily for experts, hourly for projects
