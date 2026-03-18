# ExpertSpork

**AI-Powered Freelancer Marketplace & Project Management Platform**

> Work with the Best. Get Paid What You're Worth.

---

## Overview

ExpertSpork connects world-class freelance talent with ambitious companies through AI matching, escrow payments, milestone-based contracts, and a real-time project dashboard.

---

## Product System Documents

| Document | Description |
|----------|-------------|
| [`docs/01-systems-architecture.md`](docs/01-systems-architecture.md) | Full IA, user journeys, data schema, API surface, component inventory, tech stack, SEO framework |
| [`design-system/tokens.json`](design-system/tokens.json) | Design tokens: colors, typography, spacing, motion (JSON) |
| [`src/styles/globals.css`](src/styles/globals.css) | CSS variables + full component base styles |
| [`docs/03-copy-architecture.md`](docs/03-copy-architecture.md) | All page copy, CTAs, FAQs, conversion strategy |
| [`docs/04-interaction-systems.md`](docs/04-interaction-systems.md) | State machines, data flows, React component architecture |
| [`docs/05-figma-prompts.md`](docs/05-figma-prompts.md) | 5 high-precision Figma Make prompts |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS + CSS Variables |
| Database | PostgreSQL (Supabase) |
| ORM | Prisma 5 |
| Auth | NextAuth.js v5 |
| Payments | Stripe Connect |
| Search | Algolia |
| Media | Cloudinary |
| Email | Resend |
| Real-time | Pusher |
| AI | OpenAI GPT-4o |
| Hosting | Vercel |

---

## Project Structure

```
src/
├── app/                    Next.js App Router pages
│   ├── page.tsx            Landing page
│   ├── explore/            Expert discovery
│   ├── pricing/            Pricing page
│   ├── how-it-works/       How it works
│   ├── auth/               Login, Register, Reset Password
│   └── dashboard/          Protected user dashboard
├── components/
│   ├── ui/                 Button, Badge, Avatar, Input, Card
│   ├── layout/             TopNav, Footer, SideNav
│   ├── marketing/          Hero, HowItWorks, Testimonials, FAQ
│   ├── experts/            ExpertCard, ExpertProfile
│   ├── dashboard/          StatsCard, Charts
│   └── auth/               LoginForm, RegisterForm
├── hooks/                  Custom React hooks
├── lib/                    API client, validators, utilities
├── styles/                 Global CSS (design system)
└── types/                  TypeScript type definitions
```

---

## Getting Started

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local
# Fill in your API keys

# Push database schema
npm run db:push

# Seed initial data
npm run db:seed

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the result.

---

## Design System

### Colors
- **Primary**: Blue (#2563EB) — buttons, links, accents
- **Accent**: Green (#22C55E) — success, earnings
- **Highlight**: Orange (#F97316) — AI match, premium
- **Neutral**: Slate scale — backgrounds, text, borders

### Typography
- **Font**: Inter (display + body)
- **Scale**: 12px → 72px (9 steps)

### Spacing
- 8px grid system

### Core Web Vitals Targets
- LCP < 1.5s · INP < 50ms · CLS < 0.05 · Lighthouse > 95

---

## Figma Make Prompts

5 production-ready prompts in [`docs/05-figma-prompts.md`](docs/05-figma-prompts.md):
1. Landing Page — Hero + Trust bar
2. Expert Discovery — Search + Filter + Cards
3. Expert Profile — Full profile page
4. Dashboard — Analytics + Project management
5. Auth Flows — Login, Register, Multi-step Onboarding

---

*Built with the ExpertSpork AI Product Team System — 5 roles executed simultaneously.*
