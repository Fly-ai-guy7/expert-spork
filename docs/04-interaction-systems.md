# ROLE 4: INTERACTION SYSTEMS ENGINEER
## ExpertSpork — State Machines, Data Flow & React Architecture

---

## MODULE 1: MULTI-STEP ONBOARDING FORM

### State Machine
```
IDLE
  → [start] → STEP_1_ROLE_SELECT
    → [selectRole(CLIENT)] → STEP_2_CLIENT_INFO
    → [selectRole(EXPERT)] → STEP_2_EXPERT_INFO

STEP_2_CLIENT_INFO
  → [submit] → VALIDATING_STEP_2
    → [valid] → STEP_3_COMPANY
    → [invalid] → STEP_2_CLIENT_INFO (with errors)
  → [back] → STEP_1_ROLE_SELECT

STEP_2_EXPERT_INFO
  → [submit] → VALIDATING_STEP_2
    → [valid] → STEP_3_SKILLS
    → [invalid] → STEP_2_EXPERT_INFO (with errors)
  → [back] → STEP_1_ROLE_SELECT

STEP_3_SKILLS (Expert)
  → [addSkill / removeSkill] → STEP_3_SKILLS (updated)
  → [submit (min 3 skills)] → STEP_4_PORTFOLIO
  → [back] → STEP_2_EXPERT_INFO

STEP_4_PORTFOLIO (Expert)
  → [uploadFile] → UPLOADING_FILE
    → [success] → STEP_4_PORTFOLIO (file added)
    → [error] → STEP_4_PORTFOLIO (file error)
  → [removeFile] → STEP_4_PORTFOLIO (file removed)
  → [submit] → STEP_5_RATE

STEP_5_RATE (Expert)
  → [setRate / setCurrency / setAvailability] → STEP_5_RATE (updated)
  → [submit] → SUBMITTING_PROFILE
    → [success] → AI_SCORING
      → [score >= 70] → PROFILE_LIVE
      → [score < 70] → PROFILE_INCOMPLETE (with suggestions)
    → [error] → SUBMISSION_ERROR

SUBMITTING_PROFILE
  → [apiSuccess] → AI_SCORING
  → [apiError] → STEP_5_RATE (with error toast)
```

### React Component Architecture
```tsx
// src/components/onboarding/OnboardingFlow.tsx
interface OnboardingState {
  step: number
  role: 'CLIENT' | 'EXPERT' | null
  data: {
    name: string
    email: string
    company?: string
    headline?: string
    skills: string[]
    portfolioFiles: UploadedFile[]
    hourlyRate: number
    currency: string
    availability: 'FULL_TIME' | 'PART_TIME' | 'UNAVAILABLE'
  }
  errors: Record<string, string>
  isSubmitting: boolean
  aiScore?: number
}

// Hooks
const useOnboardingForm = () => {
  const [state, dispatch] = useReducer(onboardingReducer, initialState)
  const { mutateAsync: submitProfile } = useMutation(api.profiles.create)
  const { mutateAsync: scoreProfile } = useMutation(api.ai.scoreProfile)
  // ...handlers
}

// Sub-components
<OnboardingFlow>          // orchestrator, manages step state
  <StepIndicator />       // visual progress (Step 1 of 5)
  <StepRoleSelect />      // Step 1: Client vs Expert
  <StepClientInfo />      // Step 2a: Client details
  <StepExpertInfo />      // Step 2b: Expert headline + bio
  <StepSkills />          // Step 3: Skill tag selector + search
  <StepPortfolio />       // Step 4: File upload with preview grid
  <StepRate />            // Step 5: Rate + availability
  <StepAIScore />         // Completion: AI score animation
  <NavigationButtons />   // Back / Continue / Submit
</OnboardingFlow>
```

### Error Handling
- Field-level validation on blur via Zod schema
- Form-level validation on submit
- API errors shown as toast + field highlighting
- File upload errors shown inline below dropzone
- Recovery: "Save progress" stored in localStorage every step change

### Loading States
- `StepIndicator` shows animated pulse on current step during validation
- Submit button shows spinner + "Saving..." text
- AI Score step shows animated progress bar + "Our AI is reviewing your profile..."

### Empty States
- Skills step: "Start typing to search 200+ skill categories"
- Portfolio step: Full drag-drop zone with illustrated upload icon
- Rate step: Pre-populated with median rate for top skills in region

### Edge Cases
- User navigates away mid-form: confirm dialog "You have unsaved progress. Continue?"
- Image upload > 10MB: inline error "Max file size is 10MB"
- Duplicate skill added: silently ignore, no error
- AI Score below 70: show specific suggestions modal before forcing re-edit

---

## MODULE 2: REAL-TIME PROJECT BUDGET CALCULATOR

### State Machine
```
IDLE
  → [selectBudgetType(FIXED)] → FIXED_PRICE_MODE
  → [selectBudgetType(HOURLY)] → HOURLY_MODE

FIXED_PRICE_MODE
  → [updateBudget] → CALCULATING_FIXED
    → [complete] → FIXED_PRICE_DISPLAY (with fee breakdown)
  → [toggleType] → HOURLY_MODE

HOURLY_MODE
  → [updateRate / updateHours / updateWeeks] → CALCULATING_HOURLY
    → [complete] → HOURLY_DISPLAY (with totals + fee)
  → [toggleType] → FIXED_PRICE_MODE
```

### Data Flow
```tsx
interface CalculatorState {
  budgetType: 'FIXED' | 'HOURLY'
  // Fixed
  fixedBudget: number
  // Hourly
  hourlyRate: number
  hoursPerWeek: number
  durationWeeks: number
  // Computed
  subtotal: number
  platformFee: number     // 8% (or 5% for Pro)
  expertReceives: number
  clientPays: number
  isPro: boolean
}

// Computed values (pure functions — no side effects)
const computeFixedBreakdown = (budget: number, isPro: boolean) => ({
  subtotal: budget,
  platformFee: budget * (isPro ? 0.05 : 0.08),
  expertReceives: budget * (isPro ? 0.95 : 0.92),
  clientPays: budget,
})

const computeHourlyBreakdown = (rate, hoursPerWeek, weeks, isPro) => {
  const subtotal = rate * hoursPerWeek * weeks
  return computeFixedBreakdown(subtotal, isPro)
}
```

### Component
```tsx
<BudgetCalculator>
  <ToggleGroup value={type} onChange={setType}>
    <Toggle value="FIXED">Fixed Price</Toggle>
    <Toggle value="HOURLY">Hourly Rate</Toggle>
  </ToggleGroup>

  {type === 'FIXED' && (
    <BudgetInput value={budget} onChange={setBudget} />
  )}
  {type === 'HOURLY' && (
    <HourlyInputGroup
      rate={rate} hours={hours} weeks={weeks}
      onChange={...} />
  )}

  <BreakdownTable breakdown={breakdown} />  {/* animates on change */}
  <ProUpgradeBanner saving={saving} />      {/* shows if not Pro */}
</BudgetCalculator>
```

---

## MODULE 3: FACETED EXPERT SEARCH

### State Machine
```
LOADING_INITIAL
  → [dataReady] → IDLE_WITH_RESULTS

IDLE_WITH_RESULTS
  → [search(query)] → SEARCHING
  → [applyFilter(filter)] → FILTERING
  → [changeSort(sort)] → SORTING
  → [changePage(page)] → PAGINATING
  → [clearFilters] → IDLE_WITH_RESULTS (reset)

SEARCHING | FILTERING | SORTING | PAGINATING
  → [apiResponse(results)] → IDLE_WITH_RESULTS
  → [apiError] → ERROR_STATE

ERROR_STATE
  → [retry] → LOADING_INITIAL

IDLE_WITH_RESULTS (0 results)
  → renders EmptyState component
```

### Data Flow
```tsx
// URL-driven state — all filters in searchParams
// /explore?q=react&category=engineering&rate_min=80&rate_max=200&availability=FULL_TIME&sort=rating&page=2

interface SearchState {
  query: string
  filters: {
    category: string[]
    skills: string[]
    rateMin: number
    rateMax: number
    availability: ('FULL_TIME' | 'PART_TIME')[]
    rating: number               // minimum stars
    location: string[]
  }
  sort: 'relevance' | 'rating' | 'rate_asc' | 'rate_desc' | 'newest'
  page: number
  pageSize: 12 | 24 | 48
}

// Hooks
const useExpertSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const state = parseSearchParams(searchParams)

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['experts', state],
    queryFn: () => api.experts.search(state),
    keepPreviousData: true,   // no flash between pages
  })

  const updateFilter = (key, value) => {
    setSearchParams({ ...state, [key]: value, page: 1 })
    // page resets to 1 on any filter change
  }

  return { results: data?.experts, total: data?.total, isLoading, isFetching, state, updateFilter }
}
```

### Component Architecture
```tsx
<ExploreLayout>
  <FilterSidebar>                    {/* sticky on desktop, sheet on mobile */}
    <SearchInput debounce={300ms} />
    <CategoryFilter multiSelect />
    <SkillsFilter searchable multiSelect />
    <RateRangeSlider min={0} max={500} step={10} />
    <AvailabilityFilter />
    <RatingFilter />
    <ActiveFilterTags onRemove={removeFilter} onClearAll={clearFilters} />
  </FilterSidebar>

  <ResultsArea>
    <ResultsHeader>
      <ResultCount /> {/* "1,240 experts found" */}
      <SortDropdown />
      <ViewToggle /> {/* grid | list */}
    </ResultsHeader>

    {isFetching && <SkeletonGrid count={12} />}
    {!isFetching && results.length === 0 && <EmptySearchState />}
    {!isFetching && results.length > 0 && (
      <ExpertGrid experts={results} />
    )}

    <Pagination total={total} page={page} pageSize={pageSize} />
  </ResultsArea>
</ExploreLayout>
```

### Performance Optimizations
- Debounce text search 300ms
- `keepPreviousData: true` (no content flash)
- URL state = shareable + bookmarkable + browser back-button works
- Virtual scroll for mobile (react-virtual)
- Algolia for sub-50ms search response

---

## MODULE 4: USER DASHBOARD (Analytics + CRUD)

### State Machine
```
DASHBOARD_LOADING
  → [allDataReady] → DASHBOARD_IDLE

DASHBOARD_IDLE
  → [selectTab(PROJECTS)] → PROJECTS_VIEW
  → [selectTab(PAYMENTS)] → PAYMENTS_VIEW
  → [selectTab(ANALYTICS)] → ANALYTICS_VIEW
  → [selectProject(id)] → PROJECT_DETAIL_LOADING
    → [loaded] → PROJECT_DETAIL_VIEW
  → [createProject] → PROJECT_CREATE_FLOW

PROJECT_DETAIL_VIEW
  → [editProject] → PROJECT_EDIT_MODE
    → [save] → SAVING → PROJECT_DETAIL_VIEW (updated)
    → [cancel] → PROJECT_DETAIL_VIEW
  → [archiveProject] → CONFIRM_ARCHIVE_DIALOG
    → [confirm] → ARCHIVING → DASHBOARD_IDLE
    → [cancel] → PROJECT_DETAIL_VIEW
  → [addMilestone] → MILESTONE_FORM
  → [submitMilestone(id)] → MILESTONE_SUBMITTED (status update)
  → [approveMilestone(id)] → PAYMENT_RELEASE_CONFIRM
    → [confirm] → RELEASING_PAYMENT → MILESTONE_PAID
```

### Data Flow
```tsx
// React Query + Optimistic Updates
const useProjects = () => {
  const queryClient = useQueryClient()

  const { data: projects } = useQuery(['projects'], api.projects.list)

  const updateMilestone = useMutation(api.milestones.update, {
    onMutate: async (update) => {
      await queryClient.cancelQueries(['projects'])
      const prev = queryClient.getQueryData(['projects'])
      queryClient.setQueryData(['projects'], (old) =>
        updateMilestoneOptimistically(old, update)
      )
      return { prev }
    },
    onError: (err, update, ctx) => {
      queryClient.setQueryData(['projects'], ctx.prev)
      toast.error('Failed to update milestone')
    },
    onSettled: () => queryClient.invalidateQueries(['projects'])
  })

  return { projects, updateMilestone }
}
```

### Dashboard Components
```tsx
<DashboardLayout>
  <SideNav items={navItems} collapsed={isCollapsed} />
  <MainContent>
    <TopBar>
      <PageHeader />
      <NotificationBell unreadCount={unreadCount} />
      <UserMenu />
    </TopBar>
    <Routes>
      <Route path="overview"   element={<OverviewPage />} />
      <Route path="projects/*" element={<ProjectsSection />} />
      <Route path="contracts/*"element={<ContractsSection />} />
      <Route path="payments/*" element={<PaymentsSection />} />
      <Route path="messages/*" element={<MessagesSection />} />
      <Route path="analytics"  element={<AnalyticsPage />} />
      <Route path="settings/*" element={<SettingsSection />} />
    </Routes>
  </MainContent>
</DashboardLayout>
```

### Analytics Components
```tsx
// Overview stats — fetched in parallel
const useAnalyticsOverview = () => {
  return useQueries([
    { queryKey: ['analytics', 'earnings'],      queryFn: api.analytics.earnings },
    { queryKey: ['analytics', 'projects'],      queryFn: api.analytics.projects },
    { queryKey: ['analytics', 'profile-views'], queryFn: api.analytics.profileViews },
    { queryKey: ['analytics', 'response-rate'], queryFn: api.analytics.responseRate },
  ])
}

<AnalyticsPage>
  <StatsRow>
    <StatCard label="Total Earnings"     value={earnings.total}  delta={earnings.delta}  chart={<Sparkline />} />
    <StatCard label="Active Projects"    value={projects.active} delta={projects.delta} />
    <StatCard label="Profile Views"      value={views.total}     delta={views.delta} />
    <StatCard label="Completion Rate"    value={`${rate}%`}     delta={rate.delta} />
  </StatsRow>
  <EarningsChart period={period} onPeriodChange={setPeriod} />
  <ProjectsTable />
</AnalyticsPage>
```

---

## MODULE 5: FULL AUTH SYSTEM

### State Machine
```
UNAUTHENTICATED
  → [login(credentials)] → AUTHENTICATING
  → [register(data)] → REGISTERING
  → [oauthStart(provider)] → OAUTH_REDIRECT

AUTHENTICATING
  → [success(tokens)] → AUTHENTICATED
  → [error: wrong-password] → UNAUTHENTICATED + error toast
  → [error: unverified] → UNAUTHENTICATED + verify email prompt
  → [error: 2fa-required] → TWO_FACTOR_CHALLENGE

TWO_FACTOR_CHALLENGE
  → [submitCode(code)] → VERIFYING_2FA
    → [valid] → AUTHENTICATED
    → [invalid] → TWO_FACTOR_CHALLENGE + error (attempt count)
    → [maxAttempts] → UNAUTHENTICATED + locked toast

REGISTERING
  → [success] → EMAIL_VERIFICATION_PENDING
  → [error: email-exists] → UNAUTHENTICATED + inline error

EMAIL_VERIFICATION_PENDING
  → [clickLink(token)] → VERIFYING_EMAIL
    → [valid] → AUTHENTICATED (redirects to onboarding)
    → [expired] → EMAIL_VERIFICATION_PENDING + resend prompt

AUTHENTICATED
  → [logout] → UNAUTHENTICATED
  → [tokenExpiry] → REFRESHING_TOKEN
    → [success] → AUTHENTICATED (silent)
    → [failure] → UNAUTHENTICATED + session-expired toast

PASSWORD_RESET_FLOW
  → [requestReset(email)] → RESET_EMAIL_SENT
  → [clickResetLink(token)] → RESET_PASSWORD_FORM
    → [submit] → RESETTING
      → [success] → AUTHENTICATED + success toast
      → [error: expired] → RESET_PASSWORD_FORM + error
```

### Data Flow
```tsx
// src/lib/auth.ts — Auth context
interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthState>(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check session on mount
    api.auth.me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false))
  }, [])

  // Axios interceptor for token refresh
  useEffect(() => {
    const interceptor = axiosInstance.interceptors.response.use(
      (res) => res,
      async (error) => {
        if (error.response?.status === 401) {
          try {
            await api.auth.refresh()
            return axiosInstance(error.config)
          } catch {
            setUser(null)
            router.push('/auth/login?reason=session-expired')
          }
        }
        return Promise.reject(error)
      }
    )
    return () => axiosInstance.interceptors.response.eject(interceptor)
  }, [])

  return <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user }}>
    {children}
  </AuthContext.Provider>
}
```

### Error Handling Summary
| Scenario | Handler | UI |
|---------|---------|---|
| Wrong password | API returns 401 | Inline field error |
| Email not verified | API returns 403 | Alert banner + resend link |
| Rate limited | API returns 429 | Toast "Too many attempts, try in 5min" |
| Network error | Catch in mutation | Toast "Check your connection" |
| Session expired | 401 interceptor | Redirect + toast |
| Token expired (reset) | Validation on submit | Error + request new link CTA |

### Route Protection
```tsx
// middleware.ts (Next.js)
export const config = { matcher: ['/dashboard/:path*'] }

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')
  if (!token) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }
  // Verify JWT signature + expiry
  const payload = verifyToken(token.value)
  if (!payload) {
    const response = NextResponse.redirect(new URL('/auth/login', request.url))
    response.cookies.delete('auth-token')
    return response
  }
  return NextResponse.next()
}
```

---

## REACT COMPONENT ARCHITECTURE — FILE STRUCTURE

```
src/
├── app/                          Next.js App Router
│   ├── layout.tsx                Root layout (providers, fonts)
│   ├── page.tsx                  Landing page
│   ├── explore/
│   │   ├── page.tsx              Expert browse
│   │   └── [slug]/page.tsx       Expert profile (SSG)
│   ├── projects/
│   │   ├── page.tsx
│   │   └── [id]/page.tsx
│   ├── how-it-works/page.tsx
│   ├── pricing/page.tsx
│   ├── blog/
│   │   ├── page.tsx
│   │   └── [slug]/page.tsx
│   ├── auth/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── reset-password/page.tsx
│   └── dashboard/
│       ├── layout.tsx            Dashboard shell (sidenav)
│       ├── page.tsx              Redirect → overview
│       ├── overview/page.tsx
│       ├── projects/
│       │   ├── page.tsx
│       │   ├── [id]/page.tsx
│       │   └── new/page.tsx
│       ├── contracts/
│       ├── payments/
│       ├── messages/
│       ├── analytics/page.tsx
│       └── settings/
│
├── components/
│   ├── ui/                       Primitive components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Badge.tsx
│   │   ├── Avatar.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Toast.tsx
│   │   ├── Modal.tsx
│   │   ├── Tooltip.tsx
│   │   ├── Progress.tsx
│   │   ├── Spinner.tsx
│   │   └── index.ts
│   │
│   ├── layout/
│   │   ├── TopNav.tsx
│   │   ├── SideNav.tsx
│   │   ├── Footer.tsx
│   │   ├── PageHeader.tsx
│   │   └── Container.tsx
│   │
│   ├── marketing/                Landing page sections
│   │   ├── Hero.tsx
│   │   ├── TrustBar.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── FeaturedExperts.tsx
│   │   ├── CategoriesGrid.tsx
│   │   ├── FeatureSection.tsx
│   │   ├── Testimonials.tsx
│   │   ├── PricingCards.tsx
│   │   ├── FAQ.tsx
│   │   └── CTABanner.tsx
│   │
│   ├── experts/
│   │   ├── ExpertCard.tsx
│   │   ├── ExpertGrid.tsx
│   │   ├── ExpertProfile.tsx
│   │   ├── ServiceCard.tsx
│   │   └── ReviewBreakdown.tsx
│   │
│   ├── projects/
│   │   ├── ProjectCard.tsx
│   │   ├── ProjectForm.tsx
│   │   └── AIMatchBadge.tsx
│   │
│   ├── dashboard/
│   │   ├── StatsCard.tsx
│   │   ├── EarningsChart.tsx
│   │   ├── MilestoneTimeline.tsx
│   │   ├── ContractSummary.tsx
│   │   ├── PaymentRow.tsx
│   │   ├── MessageThread.tsx
│   │   └── NotificationPanel.tsx
│   │
│   ├── forms/
│   │   ├── OnboardingFlow.tsx
│   │   ├── BudgetCalculator.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── FileUpload.tsx
│   │   └── SearchBar.tsx
│   │
│   └── auth/
│       ├── LoginForm.tsx
│       ├── RegisterForm.tsx
│       ├── TwoFactorForm.tsx
│       └── ResetPasswordForm.tsx
│
├── hooks/
│   ├── useAuth.ts
│   ├── useExpertSearch.ts
│   ├── useOnboarding.ts
│   ├── useProjects.ts
│   ├── useMessages.ts
│   ├── useNotifications.ts
│   ├── useAnalytics.ts
│   └── useDebounce.ts
│
├── lib/
│   ├── api.ts                    Axios instance + typed API methods
│   ├── auth.ts                   Auth context + provider
│   ├── queryClient.ts            React Query configuration
│   ├── validators/               Zod schemas
│   │   ├── auth.ts
│   │   ├── profile.ts
│   │   ├── project.ts
│   │   └── contract.ts
│   └── utils.ts                  formatCurrency, formatDate, cn()
│
├── styles/
│   └── globals.css               Design system CSS
│
└── types/
    ├── api.ts                    API response types
    ├── models.ts                 Domain model types
    └── index.ts
```
