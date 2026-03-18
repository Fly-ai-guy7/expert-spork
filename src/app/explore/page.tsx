import type { Metadata } from 'next'
import { TopNav } from '@/components/layout/TopNav'
import { ExpertCard } from '@/components/experts/ExpertCard'
import { Search, SlidersHorizontal } from 'lucide-react'
import type { ExpertProfile } from '@/types'

export const metadata: Metadata = {
  title: 'Explore Expert Talent — ExpertSpork',
  description: 'Browse 12,000+ vetted freelance experts. Filter by skill, rate, availability, and rating. Find your perfect match.',
  openGraph: {
    title: 'Hire Expert Freelancers | ExpertSpork',
    description: 'Browse 12,000+ vetted freelance experts across design, engineering, marketing, and strategy.',
  },
}

// Static list for initial SSR (real app: fetched from API with search params)
const CATEGORIES = [
  'All', 'Engineering', 'Design', 'Strategy', 'Marketing', 'Data', 'Content',
]

// Minimal mock for SSR skeleton — real data comes via Client component + React Query
const MOCK_EXPERTS: ExpertProfile[] = [
  {
    id: '1', userId: 'u1', slug: 'sarah-chen-react-developer',
    displayName: 'Sarah Chen', headline: 'Senior React Developer & Design Systems Expert',
    bio: '', hourlyRate: 145, currency: 'USD', availability: 'FULL_TIME',
    aiScore: 96, totalEarnings: 284000, completionRate: 99.1, responseTime: 120,
    location: 'San Francisco', timezone: 'America/Los_Angeles', languages: ['English'],
    isPublic: true, isVerified: true, isFeatured: true, profileViews: 12400, coverColor: '#2563EB',
    skills: [
      { skillId: 's1', skill: { id: 's1', name: 'React', slug: 'react', category: 'Engineering' }, yearsExp: 8, isPrimary: true },
      { skillId: 's2', skill: { id: 's2', name: 'TypeScript', slug: 'typescript', category: 'Engineering' }, yearsExp: 6, isPrimary: true },
      { skillId: 's3', skill: { id: 's3', name: 'Node.js', slug: 'nodejs', category: 'Engineering' }, yearsExp: 5, isPrimary: false },
    ],
    portfolio: [], services: [],
    user: { id: 'u1', email: 's@x.com', name: 'Sarah Chen', image: null, role: 'EXPERT', createdAt: '2023-01-15T00:00:00Z' },
    _count: { reviews: 124 }, averageRating: 4.9, createdAt: '2023-01-15T00:00:00Z',
  },
  // ... more experts would be fetched from API in production
]

export default function ExplorePage({
  searchParams,
}: {
  searchParams: { q?: string; category?: string; sort?: string; page?: string }
}) {
  const query    = searchParams.q ?? ''
  const category = searchParams.category ?? 'All'

  return (
    <>
      <TopNav />
      <div className="min-h-screen bg-slate-50 pt-16">
        {/* Page header */}
        <div className="border-b border-slate-200 bg-white">
          <div className="container py-8">
            <h1 className="mb-4 text-3xl font-bold tracking-tight text-slate-900">
              Find Your Expert
            </h1>
            {/* Search bar */}
            <div className="relative max-w-2xl">
              <Search
                className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400"
                aria-hidden="true"
              />
              <input
                type="search"
                defaultValue={query}
                placeholder="Search by skill, name, or keyword..."
                className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-12 pr-4 text-sm text-slate-900 placeholder:text-slate-400 shadow-xs transition-all focus:border-primary-500 focus:outline-none focus:ring-3 focus:ring-primary-500/20"
                aria-label="Search experts"
              />
            </div>

            {/* Category filter pills */}
            <div className="mt-4 flex flex-wrap gap-2" role="group" aria-label="Filter by category">
              {CATEGORIES.map(cat => (
                <a
                  key={cat}
                  href={`/explore?category=${cat === 'All' ? '' : cat}`}
                  className={`rounded-full px-4 py-1.5 text-sm font-medium transition-all duration-200 ${
                    category === cat || (cat === 'All' && !category)
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'bg-white border border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                  aria-current={category === cat ? 'true' : undefined}
                >
                  {cat}
                </a>
              ))}
            </div>
          </div>
        </div>

        {/* Results area */}
        <div className="container py-8">
          <div className="flex gap-8">
            {/* Filter sidebar */}
            <aside className="hidden w-56 shrink-0 lg:block" aria-label="Search filters">
              <div className="rounded-xl border border-slate-200 bg-white p-5">
                <div className="mb-4 flex items-center justify-between">
                  <span className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                    <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
                    Filters
                  </span>
                  <a href="/explore" className="text-xs font-medium text-primary-600 hover:underline">
                    Clear all
                  </a>
                </div>

                {/* Rate range */}
                <div className="mb-5">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Hourly Rate
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder="Min"
                      className="h-8 w-full rounded-md border border-slate-200 px-2 text-xs focus:border-primary-500 focus:outline-none"
                      min={0}
                    />
                    <span className="flex items-center text-slate-400">–</span>
                    <input
                      type="number"
                      placeholder="Max"
                      className="h-8 w-full rounded-md border border-slate-200 px-2 text-xs focus:border-primary-500 focus:outline-none"
                      max={500}
                    />
                  </div>
                </div>

                {/* Availability */}
                <div className="mb-5">
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Availability
                  </p>
                  <div className="space-y-2">
                    {['Full-time', 'Part-time'].map(opt => (
                      <label key={opt} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                        <input type="checkbox" className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
                        {opt}
                      </label>
                    ))}
                  </div>
                </div>

                {/* Rating */}
                <div>
                  <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Min Rating
                  </p>
                  <div className="space-y-1.5">
                    {[4, 4.5, 4.8].map(r => (
                      <label key={r} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                        <input type="radio" name="rating" className="h-4 w-4 border-slate-300 text-primary-600" />
                        <span className="text-amber-500">{'★'.repeat(Math.round(r))}</span>
                        <span className="text-slate-500">{r}+</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </aside>

            {/* Results grid */}
            <div className="flex-1">
              {/* Results header */}
              <div className="mb-5 flex items-center justify-between">
                <p className="text-sm text-slate-500">
                  <strong className="text-slate-900">1,240</strong> experts found
                </p>
                <select
                  className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-primary-500 focus:outline-none"
                  aria-label="Sort experts by"
                >
                  <option value="relevance">Relevance</option>
                  <option value="rating">Highest Rating</option>
                  <option value="rate_asc">Rate: Low to High</option>
                  <option value="rate_desc">Rate: High to Low</option>
                  <option value="newest">Newest</option>
                </select>
              </div>

              {/* Expert grid */}
              <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                {MOCK_EXPERTS.map(expert => (
                  <ExpertCard key={expert.id} expert={expert} />
                ))}
                {/* Skeleton placeholders */}
                {[...Array(5)].map((_, i) => (
                  <div
                    key={`skeleton-${i}`}
                    className="h-72 animate-shimmer rounded-2xl bg-gradient-to-r from-slate-100 via-slate-200 to-slate-100 bg-[length:200%_100%]"
                    aria-hidden="true"
                  />
                ))}
              </div>

              {/* Pagination */}
              <nav className="mt-10 flex justify-center" aria-label="Pagination">
                <div className="flex items-center gap-1">
                  <button className="h-9 w-9 rounded-lg border border-slate-200 text-sm text-slate-400 hover:bg-slate-50 disabled:opacity-40" disabled>
                    ←
                  </button>
                  {[1, 2, 3, '...', 104].map((page, i) => (
                    <button
                      key={i}
                      className={`h-9 w-9 rounded-lg text-sm font-medium transition-colors ${
                        page === 1
                          ? 'bg-primary-600 text-white'
                          : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                  <button className="h-9 w-9 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50">
                    →
                  </button>
                </div>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
