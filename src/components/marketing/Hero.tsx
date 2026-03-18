'use client'

import React from 'react'
import Link from 'next/link'
import { ArrowRight, Zap, Shield, Star } from 'lucide-react'
import { Button } from '@/components/ui/Button'

const SOCIAL_PROOF = [
  { icon: Star,   text: '4.9/5 rating' },
  { icon: Zap,    text: '$48M+ paid to experts' },
  { icon: Shield, text: '98% on-time delivery' },
]

export function Hero() {
  return (
    <section
      className="relative overflow-hidden bg-gradient-to-b from-blue-50 via-white to-white py-20 lg:py-32"
      aria-labelledby="hero-heading"
    >
      {/* Background decorative radial gradient */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-96 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(59,130,246,0.15),transparent)]"
        aria-hidden="true"
      />

      <div className="container relative">
        <div className="mx-auto max-w-4xl text-center">
          {/* Eyebrow badge */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary-200 bg-primary-50 px-4 py-1.5 text-sm font-medium text-primary-700">
            <Zap className="h-3.5 w-3.5" aria-hidden="true" />
            Trusted by 12,000+ vetted experts
          </div>

          {/* H1 */}
          <h1
            id="hero-heading"
            className="mb-6 text-5xl font-black tracking-tighter text-slate-900 sm:text-6xl lg:text-7xl"
          >
            Work with the{' '}
            <span className="bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">
              Best.
            </span>{' '}
            Get Paid What You&apos;re{' '}
            <span className="bg-gradient-to-r from-primary-600 to-indigo-700 bg-clip-text text-transparent">
              Worth.
            </span>
          </h1>

          {/* Subheadline */}
          <p className="mx-auto mb-8 max-w-2xl text-lg leading-relaxed text-slate-500 sm:text-xl">
            ExpertSpork connects world-class freelance talent with ambitious companies — with AI
            matching, escrow payments, and zero-hassle contracts. Start in minutes.
          </p>

          {/* CTAs */}
          <div className="mb-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Button asChild size="xl" variant="primary" rightIcon={<ArrowRight className="h-5 w-5" />}>
              <Link href="/explore">Hire an Expert Today</Link>
            </Button>
            <Button asChild size="xl" variant="outline">
              <Link href="/auth/register?role=expert">Earn More as an Expert</Link>
            </Button>
          </div>

          {/* Social proof micro-stats */}
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            {SOCIAL_PROOF.map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-1.5 text-sm font-medium text-slate-500">
                <Icon className="h-4 w-4 text-primary-400" aria-hidden="true" />
                {text}
              </div>
            ))}
          </div>
        </div>

        {/* Dashboard mockup (decorative) */}
        <div className="mt-16 flex justify-center" aria-hidden="true">
          <div className="relative w-full max-w-5xl animate-slide-up">
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
              {/* Mock browser chrome */}
              <div className="flex items-center gap-1.5 border-b border-slate-100 px-4 py-3">
                <div className="h-3 w-3 rounded-full bg-red-400" />
                <div className="h-3 w-3 rounded-full bg-amber-400" />
                <div className="h-3 w-3 rounded-full bg-green-400" />
                <div className="ml-3 h-5 flex-1 rounded-full bg-slate-100" />
              </div>

              {/* Mock dashboard content */}
              <div className="flex h-64 gap-0 sm:h-80">
                {/* Sidebar mock */}
                <div className="hidden w-48 border-r border-slate-100 bg-slate-900 p-4 sm:block">
                  <div className="mb-4 h-6 w-24 rounded-md bg-slate-700" />
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="mb-2 flex items-center gap-2">
                      <div className="h-4 w-4 rounded bg-slate-700" />
                      <div
                        className={`h-3 rounded bg-slate-700 ${
                          i === 0 ? 'w-20 bg-primary-500/40' : 'w-16'
                        }`}
                      />
                    </div>
                  ))}
                </div>

                {/* Main content mock */}
                <div className="flex-1 bg-slate-50 p-4 sm:p-6">
                  {/* Stats row */}
                  <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    {[
                      { label: 'Total Earnings', value: '$24,800', color: 'bg-green-100' },
                      { label: 'Active Projects', value: '3',       color: 'bg-blue-100' },
                      { label: 'Completion Rate', value: '98%',     color: 'bg-purple-100' },
                      { label: 'Rating',          value: '4.9 ★',   color: 'bg-amber-100' },
                    ].map(stat => (
                      <div key={stat.label} className="rounded-xl border border-slate-200 bg-white p-3">
                        <div className={`mb-2 h-6 w-6 rounded-lg ${stat.color}`} />
                        <div className="mb-1 text-xs text-slate-400">{stat.label}</div>
                        <div className="font-bold text-slate-800">{stat.value}</div>
                      </div>
                    ))}
                  </div>

                  {/* Chart mock */}
                  <div className="rounded-xl border border-slate-200 bg-white p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <div className="h-3 w-24 rounded bg-slate-200" />
                      <div className="h-5 w-16 rounded-full bg-slate-100" />
                    </div>
                    <div className="flex h-20 items-end gap-1.5">
                      {[40, 60, 45, 80, 65, 90, 75, 85, 70, 95, 80, 100].map((h, i) => (
                        <div
                          key={i}
                          className="flex-1 rounded-sm bg-primary-200"
                          style={{ height: `${h}%` }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating cards */}
            <div className="absolute -left-4 top-1/2 hidden -translate-y-1/2 lg:block">
              <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xl">
                <div className="mb-1 text-xs font-medium text-slate-500">New match!</div>
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-500" />
                  <div>
                    <div className="text-sm font-semibold text-slate-800">Sarah Chen</div>
                    <div className="text-xs text-amber-500">★ 4.9 · React Expert</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="absolute -right-4 top-8 hidden lg:block">
              <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-xl">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100 text-green-600">
                    <Shield className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-xs font-medium text-slate-500">Milestone paid</div>
                    <div className="text-sm font-bold text-green-600">+$2,400</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
