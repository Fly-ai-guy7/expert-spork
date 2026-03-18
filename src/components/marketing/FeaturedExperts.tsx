import React from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { ExpertCard } from '@/components/experts/ExpertCard'
import type { ExpertProfile } from '@/types'

// Static featured experts for SSG/ISR
const FEATURED_EXPERTS: ExpertProfile[] = [
  {
    id: '1', userId: 'u1', slug: 'sarah-chen-react-designer',
    displayName: 'Sarah Chen', headline: 'Senior React Developer & Design Systems Architect',
    bio: 'I build beautiful, performant web applications with React and TypeScript. 8 years of experience shipping products used by millions.',
    hourlyRate: 145, currency: 'USD', availability: 'FULL_TIME',
    aiScore: 96, totalEarnings: 284000, completionRate: 99.1, responseTime: 120,
    location: 'San Francisco', timezone: 'America/Los_Angeles', languages: ['English', 'Mandarin'],
    isPublic: true, isVerified: true, isFeatured: true, profileViews: 12400, coverColor: '#2563EB',
    skills: [
      { skillId: 's1', skill: { id: 's1', name: 'React', slug: 'react', category: 'Engineering' }, yearsExp: 8, isPrimary: true },
      { skillId: 's2', skill: { id: 's2', name: 'TypeScript', slug: 'typescript', category: 'Engineering' }, yearsExp: 6, isPrimary: true },
      { skillId: 's3', skill: { id: 's3', name: 'Node.js', slug: 'nodejs', category: 'Engineering' }, yearsExp: 5, isPrimary: true },
      { skillId: 's4', skill: { id: 's4', name: 'GraphQL', slug: 'graphql', category: 'Engineering' }, yearsExp: 4, isPrimary: false },
    ],
    portfolio: [], services: [],
    user: { id: 'u1', email: 's@example.com', name: 'Sarah Chen', image: null, role: 'EXPERT', createdAt: '2023-01-15T00:00:00Z' },
    _count: { reviews: 124 }, averageRating: 4.9,
    createdAt: '2023-01-15T00:00:00Z',
  },
  {
    id: '2', userId: 'u2', slug: 'marcus-kim-product-design',
    displayName: 'Marcus Kim', headline: 'Product Designer — SaaS, Fintech & B2B',
    bio: 'I design products people actually love using. Deep expertise in user research, interaction design, and design systems.',
    hourlyRate: 120, currency: 'USD', availability: 'PART_TIME',
    aiScore: 93, totalEarnings: 198000, completionRate: 97.8, responseTime: 90,
    location: 'New York', timezone: 'America/New_York', languages: ['English', 'Korean'],
    isPublic: true, isVerified: true, isFeatured: true, profileViews: 8900, coverColor: '#7C3AED',
    skills: [
      { skillId: 's5', skill: { id: 's5', name: 'Product Design', slug: 'product-design', category: 'Design' }, yearsExp: 7, isPrimary: true },
      { skillId: 's6', skill: { id: 's6', name: 'Figma', slug: 'figma', category: 'Design' }, yearsExp: 5, isPrimary: true },
      { skillId: 's7', skill: { id: 's7', name: 'User Research', slug: 'user-research', category: 'Design' }, yearsExp: 6, isPrimary: false },
    ],
    portfolio: [], services: [],
    user: { id: 'u2', email: 'm@example.com', name: 'Marcus Kim', image: null, role: 'EXPERT', createdAt: '2022-06-10T00:00:00Z' },
    _count: { reviews: 89 }, averageRating: 4.8,
    createdAt: '2022-06-10T00:00:00Z',
  },
  {
    id: '3', userId: 'u3', slug: 'aria-patel-growth-marketing',
    displayName: 'Aria Patel', headline: 'Growth Marketing Strategist — Seed to Series B',
    bio: 'I\'ve helped 30+ startups hit their first $1M ARR through data-driven growth loops, paid acquisition, and content strategy.',
    hourlyRate: 175, currency: 'USD', availability: 'FULL_TIME',
    aiScore: 91, totalEarnings: 340000, completionRate: 98.5, responseTime: 60,
    location: 'London', timezone: 'Europe/London', languages: ['English', 'Hindi'],
    isPublic: true, isVerified: true, isFeatured: true, profileViews: 15200, coverColor: '#059669',
    skills: [
      { skillId: 's8', skill: { id: 's8', name: 'Growth Marketing', slug: 'growth-marketing', category: 'Marketing' }, yearsExp: 9, isPrimary: true },
      { skillId: 's9', skill: { id: 's9', name: 'SEO', slug: 'seo', category: 'Marketing' }, yearsExp: 7, isPrimary: true },
      { skillId: 's10', skill: { id: 's10', name: 'Paid Acquisition', slug: 'paid-acquisition', category: 'Marketing' }, yearsExp: 8, isPrimary: false },
    ],
    portfolio: [], services: [],
    user: { id: 'u3', email: 'a@example.com', name: 'Aria Patel', image: null, role: 'EXPERT', createdAt: '2022-03-22T00:00:00Z' },
    _count: { reviews: 156 }, averageRating: 4.9,
    createdAt: '2022-03-22T00:00:00Z',
  },
  {
    id: '4', userId: 'u4', slug: 'james-okonkwo-backend-devops',
    displayName: 'James Okonkwo', headline: 'Backend Engineer & DevOps — Scalable Systems at Speed',
    bio: 'Ex-Stripe, ex-AWS. I architect and build backend systems that scale from 1 to 1 million users without breaking a sweat.',
    hourlyRate: 195, currency: 'USD', availability: 'FULL_TIME',
    aiScore: 98, totalEarnings: 520000, completionRate: 100, responseTime: 45,
    location: 'Lagos', timezone: 'Africa/Lagos', languages: ['English', 'Igbo'],
    isPublic: true, isVerified: true, isFeatured: true, profileViews: 22000, coverColor: '#0891B2',
    skills: [
      { skillId: 's11', skill: { id: 's11', name: 'Go', slug: 'go', category: 'Engineering' }, yearsExp: 6, isPrimary: true },
      { skillId: 's12', skill: { id: 's12', name: 'Kubernetes', slug: 'kubernetes', category: 'Engineering' }, yearsExp: 5, isPrimary: true },
      { skillId: 's13', skill: { id: 's13', name: 'PostgreSQL', slug: 'postgresql', category: 'Engineering' }, yearsExp: 8, isPrimary: false },
    ],
    portfolio: [], services: [],
    user: { id: 'u4', email: 'j@example.com', name: 'James Okonkwo', image: null, role: 'EXPERT', createdAt: '2021-11-05T00:00:00Z' },
    _count: { reviews: 203 }, averageRating: 5.0,
    createdAt: '2021-11-05T00:00:00Z',
  },
]

export function FeaturedExperts() {
  return (
    <section className="section bg-slate-50" aria-labelledby="featured-heading">
      <div className="container">
        {/* Header */}
        <div className="mb-12 flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-primary-600">
              Featured Experts
            </p>
            <h2
              id="featured-heading"
              className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl"
            >
              The top 3% of talent,
              <br />ready to work for you.
            </h2>
          </div>
          <Button
            asChild
            variant="secondary"
            rightIcon={<ArrowRight className="h-4 w-4" />}
          >
            <Link href="/explore">Browse all 12,000+ experts</Link>
          </Button>
        </div>

        {/* Expert cards grid */}
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURED_EXPERTS.map(expert => (
            <ExpertCard key={expert.id} expert={expert} />
          ))}
        </div>
      </div>
    </section>
  )
}
