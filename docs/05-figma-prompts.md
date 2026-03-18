# ROLE 5: FIGMA MAKE PROMPT TRANSLATOR
## ExpertSpork — 5 High-Precision Figma Make Prompts

---

## PROMPT 1: LANDING PAGE — HERO + TRUST

```
Create a high-converting SaaS marketplace landing page for "ExpertSpork" — an AI-powered
freelancer marketplace — with a bold, modern, trustworthy aesthetic using a deep blue
primary palette (#2563EB, #1D4ED8) and clean white/slate neutrals (#F8FAFC, #1E293B).

Typography: Inter 900 for headlines (clamp 48px-72px, letter-spacing -0.05em),
Inter 400 for body (18px, 1.65 line-height). All type is left-aligned on desktop,
centered on mobile.

SECTIONS TO BUILD:

1) NAVIGATION BAR (sticky, glassmorphism on scroll):
   - Left: "ExpertSpork" wordmark in Inter 700 with a lightning bolt icon in #2563EB
   - Center: Nav links — How It Works · Explore · Pricing · Blog (Inter 500, 14px,
     #475569, hover→#2563EB with 200ms ease)
   - Right: "Sign In" (ghost button) + "Get Started Free" (filled blue button,
     rounded-lg, with subtle arrow icon →)
   - Mobile: hamburger menu → full-screen overlay slide from right (300ms spring easing)

2) HERO SECTION (full viewport height, radial blue gradient top-center):
   - EYEBROW: small badge chip "✦ Trusted by 12,000+ Vetted Experts" — blue border,
     blue text, subtle shimmer animation on load
   - H1: "Work with the Best. Get Paid What You're Worth." — 3 lines, 72px,
     weight 900, tracking -0.05em. Words "Best" and "Worth" in gradient
     (#3B82F6 → #2563EB) with -webkit-background-clip
   - SUBHEADLINE: 20px Inter 400, #64748B, max-width 560px,
     "ExpertSpork connects world-class freelance talent with ambitious companies —
     with AI matching, escrow payments, and zero-hassle contracts."
   - CTAs: Side by side — Primary "Hire an Expert Today" (blue filled, lg,
     padding 14px 32px) + Secondary "Earn More as an Expert" (outline blue, same size).
     Gap 12px. On mobile: stacked, full-width.
   - SOCIAL PROOF ROW below CTAs: "★ 4.9/5 rating · $48M+ paid to experts ·
     98% on-time delivery" — dots separating items, Inter 500 14px, #64748B
   - HERO VISUAL: right side (desktop) or below (mobile) — dashboard mockup screenshot
     with subtle shadow-2xl, 8° rotation, floating in. Animate: fade up + rotate to 0°
     on page load (800ms spring).

3) TRUST BAR (full-width, subtle top/bottom border, #F1F5F9 bg):
   - "Trusted by teams at:" label in Inter 500 12px uppercase tracked
   - 8 grayscale company logos (filter: grayscale(1) opacity(0.5),
     hover → grayscale(0) opacity(1) with 200ms ease)
   - Infinite horizontal scroll marquee animation on mobile (paused on hover)

Interactions:
- Scroll-triggered animations: sections fade-up with translateY(24px→0) as they enter viewport (Intersection Observer, threshold 0.2)
- CTA buttons: hover lifts (translateY(-1px) + shadow-md), active presses (translateY(1px))
- Navbar: background transitions from transparent to white/80 backdrop-blur on scroll > 60px

Responsive: 1-column mobile (375px+), 2-column desktop (1024px+). Full-width CTA buttons on mobile. Dashboard mockup below hero on mobile.
```

---

## PROMPT 2: EXPERT DISCOVERY — SEARCH + FILTER + CARDS

```
Create an expert talent discovery interface for "ExpertSpork" with a clean,
functional, data-dense layout. Design language: neutral slate (#F8FAFC background,
#1E293B text), blue accents (#2563EB), card-based grid with hover depth effects.

Typography: Inter throughout. Card titles: 600 16px. Labels: 500 12px uppercase.
Body: 400 14px #64748B.

SECTIONS TO BUILD:

1) PAGE HEADER:
   - H1: "Find Your Expert" (Inter 700 30px, #0F172A)
   - Large SearchBar: full-width white input with blue focus ring, magnifier icon left,
     placeholder "Search by skill, name, or keyword...", voice input icon right
   - Below search: horizontal scrollable filter pills — "Design · Engineering ·
     Strategy · Marketing · Data · Content" — active pill: blue filled,
     inactive: white with border, 6px radius, 200ms transition

2) FILTER SIDEBAR (240px, sticky, scrollable):
   Panel title "Filters" + "Clear all" link (right-aligned, #2563EB)

   FILTER GROUPS (each collapsible with animated chevron):
   a) Category: checkbox list (Design, Engineering, Strategy, Marketing, Data...)
   b) Skills: searchable chip selector — type to filter, selected chips appear blue
   c) Hourly Rate: dual-thumb range slider ($0–$500), live label shows "Up to $150/hr"
   d) Availability: toggle group (Full-time | Part-time | Either)
   e) Minimum Rating: star selector (click to set minimum: ★ ★★ ★★★ ★★★★ ★★★★★)
   f) Location: text input with autocomplete dropdown

   Active filter count badge on sidebar header when filters applied.

3) RESULTS AREA:
   RESULTS HEADER: "1,240 experts found" (Inter 400 14px) + Sort dropdown right
   (Relevance | Rating | Rate ↑ | Rate ↓ | Newest) + Grid/List toggle icons

   EXPERT CARD (grid: 3-col desktop, 2-col tablet, 1-col mobile):
   Card dimensions: auto height, border 1px #E2E8F0, radius 16px, white bg
   Layout:
   - TOP: Cover image strip (80px, auto-generated gradient from skill category)
     with AVAILABLE badge absolute top-right (green #22C55E)
   - Avatar: 56px circle, absolute overlap at cover/content boundary,
     white 3px ring border, shadow-md
   - Name: Inter 600 16px + Verified checkmark (blue, 14px)
   - Headline: Inter 400 14px #64748B, max 2 lines, ellipsis
   - AI MATCH BADGE (when shown): orange gradient pill "⚡ 97% match"
     with tooltip on hover
   - Skill tags: wrap, each tag rounded-full, #EFF6FF bg, #2563EB text,
     11px Inter 500. Max 3 visible + "+4 more" chip
   - Bottom row: "★ 4.9 (124)" left | "$145/hr" right (Inter 600 15px #0F172A)
   - CTA: "Hire Now" button appears on hover (translateY from 8px, opacity 0→1,
     200ms ease), blue filled, full-width

4) PAGINATION:
   Centered. Prev/Next arrows + page numbers. Active page: blue filled circle.
   Mobile: simplified "← 2 of 104 pages →"

Interactions:
- Card hover: translateY(-2px) + shadow-md + border-color #2563EB (200ms)
- Filter changes trigger skeleton shimmer on result grid while fetching
- Sidebar collapses to icon-only strip on < 1024px, opens as sheet/drawer
- Filter pill updates URL query params (shareable URLs)

Loading state: skeleton cards (gray animated shimmer) in exact same grid layout.
Empty state: centered illustration + "No experts match your filters" + "Clear filters" CTA.
```

---

## PROMPT 3: EXPERT PROFILE PAGE

```
Create a detailed expert profile page for "ExpertSpork" with a premium,
credibility-driven layout. Think: LinkedIn meets Dribbble — clean white
content areas, generous whitespace, blue accent highlights.

Color: White bg, #0F172A headings, #64748B body, #2563EB links/accents,
#22C55E availability badge. Typography: Inter family throughout.

SECTIONS TO BUILD:

1) PROFILE HERO (full-width):
   - Cover: 200px gradient bg (category-based: Engineering→blue gradient,
     Design→purple-pink gradient, etc.)
   - DESKTOP LAYOUT: Avatar (112px, overlapping cover bottom edge, white ring)
     left-aligned + info stack right
   - Name: Inter 800 30px #0F172A + blue verified checkmark SVG
   - Headline: Inter 400 18px #64748B
   - Stats row: "★ 4.9 · 124 reviews · $145/hr · San Francisco · Usually responds in 2hr"
     Each item separated by centered dot, Inter 500 14px
   - Tags row: Availability badge (green pill "● Available") + Top Rated badge
     (orange star "⭐ Top Rated")

   STICKY HIRE SIDEBAR (desktop right, 320px):
   White card, shadow-xl, radius-2xl, padding 24px
   - "$145 / hr" — Inter 800 28px #0F172A
   - Availability: green dot + "Available for new projects"
   - [Hire {Name}] button: blue filled, full-width, lg, Inter 600
   - [Send Message] button: outline, full-width, below
   - Microcopy: "Response time: < 2 hours · Free to contact"
   - Divider + "Member since Jan 2023 · 28 projects · $184K earned"

2) ABOUT SECTION:
   Left column (main content):
   H2: "About" (Inter 700 22px, underline accent: 3px blue bar left border)
   Bio text: 400 16px #475569, line-height 1.7

   SKILLS section:
   H3: "Skills & Expertise"
   Skill tags: rounded-full, white bg, border #E2E8F0, #475569 text,
   hover→#EFF6FF border-#2563EB (200ms). Wrap layout.

3) SERVICES SECTION:
   H2: "What I Offer"
   3 service cards in row (stack on mobile):
   Each card: white, border, radius-xl, padding 24px
   - Service title: Inter 600 16px
   - Price: Inter 700 22px blue (#2563EB)
   - Timeline badge: "Delivered in 3 days" (neutral pill)
   - Description: 400 14px #64748B, 3 lines max
   - Includes list: checkmarks (green ✓) + items
   - CTA: "Get Started" (ghost blue button, full-width)
   Middle card: slight shadow-md, blue top border accent (3px) to indicate "popular"

4) PORTFOLIO GRID:
   H2: "Portfolio"
   Masonry 2-col grid (1-col mobile):
   Each item: radius-xl overflow-hidden, aspect-ratio auto
   Hover overlay: black 60% overlay + "View Project" button (white filled)
   + external link icon. Animate: opacity 0→1 (200ms ease)

5) REVIEWS:
   H2: "Client Reviews" + overall rating display
   Rating breakdown: "4.9 overall" (large) + category breakdown bars:
   [Communication ████████████░ 5.0]
   [Quality        ███████████░░ 4.9]
   [Timeliness     ██████████░░░ 4.8]

   Review cards: avatar + name + date + star rating + body text +
   project reference ("On: Brand Redesign")

Interactions:
- "Hire" sidebar: follows scroll until footer
- Portfolio items: lightbox on click (modal overlay, prev/next navigation)
- Reviews: "Show more" expand (animated max-height)
- Skills: tooltip on hover showing proficiency level

Mobile: sidebar becomes full-width CTA bar fixed to bottom of screen,
above the fold hero collapses to compact.
```

---

## PROMPT 4: USER DASHBOARD — ANALYTICS + PROJECT MANAGEMENT

```
Create a modern, data-rich SaaS dashboard for "ExpertSpork" — the app for
freelancers managing their active projects and earnings. Dark sidebar,
white content area. Clean, functional, information-dense without feeling crowded.

Color system: Sidebar #0F172A, Content bg #F8FAFC, Cards white,
Primary blue #2563EB, Success green #22C55E, Warning amber #F59E0B.
Typography: Inter 400/500/600/700. Numbers in Inter 700/800 tabular figures.

SECTIONS TO BUILD:

1) SIDE NAVIGATION (240px, dark #0F172A, fixed):
   - Top: ExpertSpork logo (white) + user mini-profile (avatar 32px + name + role badge)
   - Nav items with icons (Lucide icons, 18px, white/60 default, white active):
     ● Overview (active state: blue left border 3px + blue bg 10% + white text)
     ● Projects (with badge count)
     ● Contracts
     ● Payments
     ● Messages (with unread dot)
     ● Analytics
     ─── (divider)
     ● Profile
     ● Settings
   - Bottom: "Upgrade to Pro" upsell card (#1E293B bg, blue CTA button)
   - Collapse toggle (chevron, transitions 300ms spring, icons only when collapsed)

2) TOP BAR (64px, white, shadow-xs):
   - Left: Breadcrumb (Overview) + Page title "Good morning, Sarah 👋"
   - Right: Search (quick-open with ⌘K), Notification bell (orange dot if unread),
     Help (? icon), Avatar (dropdown: profile/settings/logout)

3) STATS ROW (4 cards):
   Each card: white, border, radius-xl, padding 24px
   - Icon (colored square bg 10% opacity, icon 20px)
   - Label: Inter 500 13px uppercase tracked #64748B
   - Value: Inter 800 28px #0F172A tabular figures
   - Delta: green/red pill "↑ +12.4% this month"
   - Mini sparkline (right side, 60px wide, matching delta color)

   Cards: Total Earnings ($24,800) · Active Projects (3) ·
          Completion Rate (98%) · Avg Rating (4.9★)

4) MAIN CONTENT GRID (2-col: 60% left, 40% right):

   LEFT — Active Projects Table:
   Header: "Active Projects" + "View all" link + "New Project" button
   Table rows (each):
   - Project name (Inter 600 14px) + client avatar + client name (14px #64748B)
   - Progress bar (6px, blue fill, gray track, radius-full)
   - "Milestone 2 of 4" label
   - Status badge (In Progress: blue, Under Review: amber, etc.)
   - "Due Jun 12" (14px, red if overdue)
   - Actions: ••• menu (View, Message client, Add milestone)

   RIGHT — Upcoming Milestones:
   H3: "Upcoming Milestones"
   Timeline component (vertical line):
   Each item: colored dot + date + milestone name + amount + status badge
   Colors: pending(gray) → funded(blue) → in-progress(amber) → submitted(purple) → paid(green)

5) BOTTOM ROW:
   LEFT: Earnings chart (area chart, 8px radius line, blue gradient fill below line):
   - Period toggle: 7D · 30D · 3M · 1Y
   - Y-axis in USD, X-axis dates
   - Hover tooltip: date + amount (white card, shadow-md)

   RIGHT: Recent Payments list:
   Each row: left (project name + client) | right (amount in Inter 700 + status badge)
   Alternating row bg (#F8FAFC / white)
   "View all payments" link bottom

Interactions:
- Sidebar nav: active state changes with route
- Stats cards: hover elevates (shadow-md, -1px translate)
- Chart: hover shows crosshair + tooltip (200ms appearance)
- Table rows: hover bg #F8FAFC, click → project detail slide-in from right
- Notifications panel: slides in from right (sheet pattern, 360px)
- ⌘K search: modal, full-width input, recent items + live search results

Responsive (tablet 768px): sidebar collapses to icon-only.
Mobile (< 640px): sidebar hidden, accessed via bottom nav bar (4 main sections).
Stats row scrolls horizontally. Table becomes card list.
```

---

## PROMPT 5: AUTH FLOWS + ONBOARDING MULTI-STEP FORM

```
Create a polished authentication and onboarding experience for "ExpertSpork".
Split-screen layout on desktop: left panel (branded, visual) and right panel (form).
Mobile: form-only, logo at top.

Brand panel (left 45%):
- Dark blue gradient (#1E3A8A → #1D4ED8)
- Large serif-style quote or platform value prop in white
- Floating card mockups showing dashboard/profile metrics
- Subtle grid dot pattern overlay (opacity 5%)
- Bottom: avatar row "Join 12,000+ experts already earning more"

Form panel (right 55%): white, centered content max-width 440px

Typography: Inter. Form labels: 500 14px #334155. Inputs: 400 15px,
border #E2E8F0 → focus border #3B82F6 + glow ring (shadow: 0 0 0 3px rgba(59,130,246,0.3)).

SCREENS TO BUILD:

A) LOGIN SCREEN:
   - Logo + "ExpertSpork" (top left of form panel)
   - H1: "Welcome back." (Inter 700 28px)
   - Subtext: "Sign in to your account."
   - OAuth buttons row: [G] Google · [GH] GitHub · [in] LinkedIn
     (each: white, border, radius-md, icon + label, hover:#F8FAFC)
   - Divider: "─── or continue with email ───" (#94A3B8 text)
   - Email input + Password input (show/hide toggle eye icon)
   - [Sign In] button: full-width, blue filled, lg
   - Links: "Forgot password?" (right-aligned above button) +
     "Don't have an account? Sign up free →" (centered below)

B) REGISTER SCREEN:
   - Role selector toggle at top: [Hire Experts | Work as Expert]
     Active role: blue filled tab, transition 200ms.
     Selecting role animates in relevant form fields.
   - Common fields: Full name, Work email, Password (strength meter below:
     4 segments, red→yellow→green, label "Weak / Fair / Strong / Excellent")
   - Expert-only: "Professional headline" input
   - Checkbox: terms + privacy with links
   - [Create Account] → loading state → success

C) MULTI-STEP ONBOARDING (Expert):
   5 steps with progress bar at top (5 segments, blue fill animates per step):
   Step labels: Role → Profile → Skills → Portfolio → Rates

   STEP 1 — Role Select:
   2 large cards side-by-side:
   Left: "I want to Hire" — icon (briefcase) + 3 bullet benefits
   Right: "I want to Work as Expert" — icon (lightning) + 3 bullet benefits
   Selected card: blue border 2px + blue bg 5% + blue checkmark top-right

   STEP 2 — Profile Info:
   Character counter on bio textarea (480/1000)
   Profile completion percentage ring (animated SVG donut)

   STEP 3 — Skills:
   Search input + suggestion dropdown (categories)
   Selected skills appear as removable blue chips below input
   Min 3 skills indicator: "3 minimum required (0 of 3 added)"

   STEP 4 — Portfolio:
   Large dashed drop zone (2px dashed #CBD5E1, rounded-2xl, icon + text)
   Drag active state: blue dashed border + blue bg 5% + scale 1.01
   Uploaded items: 3-col thumbnail grid with remove × button top-right
   Progress bar per file during upload

   STEP 5 — Rate & Availability:
   Currency selector (flag + code dropdown) + rate input side by side
   Availability radio cards: Full-time / Part-time / Unavailable
   Budget calculator preview: "Clients pay $145/hr — You receive $133/hr after 8% fee"

   COMPLETION SCREEN:
   Animated checkmark (SVG stroke animation, 600ms)
   AI Score loading state: "Our AI is reviewing your profile..."
   → Score reveal: large circular progress ring animates to score (e.g., 86%)
   Color: < 70 red, 70-85 amber, 85+ green
   Score breakdown: Skills match · Portfolio strength · Rate competitiveness
   CTA: "View My Live Profile →"

D) FORGOT PASSWORD:
   Minimal: email input + submit + back to login link
   Success state: envelope illustration + "Check {email}" + resend link
   Countdown: "Resend in 58s..." (live countdown timer, then button enables)

Interactions:
- Form fields: shake animation on validation error (translateX ±4px, 300ms)
- Step transitions: slide left/right with opacity (300ms ease-in-out)
- OAuth buttons: hover shadow-sm + slight scale(1.01)
- Password strength: smooth color + width transition
- Completion ring: spring animation revealing score

Mobile: single column, left brand panel hidden, form fills full viewport,
progress bar sticks to top below logo.
```
