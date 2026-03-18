import React from 'react'
import Link from 'next/link'
import { Sparkles, Shield, LayoutDashboard, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'

const FEATURES = [
  {
    badge: 'Powered by AI',
    badgeBg: 'bg-purple-50 text-purple-700 border-purple-200',
    icon: Sparkles,
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
    headline: ['Stop sifting through profiles.', 'Get matched in seconds.'],
    body: 'Our proprietary AI analyses your project brief against 40+ expert signals — skills, past performance, communication style, and timezone — to surface your top 5 matches. Not 500. Five. The right five.',
    proof: '94% of clients hire from their top 3 AI matches.',
    cta: { label: 'Try AI Match Free', href: '/explore' },
    imageRight: false,
    visual: (
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
        <div className="mb-4 flex items-center gap-2">
          <div className="h-6 w-6 rounded-full bg-purple-100 flex items-center justify-center">
            <Sparkles className="h-3.5 w-3.5 text-purple-600" />
          </div>
          <span className="text-sm font-semibold text-slate-800">AI Top Matches</span>
        </div>
        {[
          { name: 'Sarah Chen', skill: 'React · TypeScript', score: 97, color: 'bg-primary-500' },
          { name: 'Marcus Kim', skill: 'Node.js · AWS', score: 94, color: 'bg-purple-500' },
          { name: 'Aria Patel', skill: 'React · GraphQL', score: 91, color: 'bg-indigo-500' },
        ].map((expert, i) => (
          <div key={i} className="mb-2 flex items-center gap-3 rounded-xl border border-slate-100 p-3">
            <div className={`h-8 w-8 rounded-full ${expert.color} flex items-center justify-center text-white text-xs font-bold`}>
              {expert.name[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">{expert.name}</p>
              <p className="text-xs text-slate-400 truncate">{expert.skill}</p>
            </div>
            <span className="text-xs font-bold text-orange-500 bg-orange-50 rounded-full px-2 py-0.5">
              ⚡ {expert.score}%
            </span>
          </div>
        ))}
      </div>
    ),
  },
  {
    badge: 'Zero Risk',
    badgeBg: 'bg-green-50 text-green-700 border-green-200',
    icon: Shield,
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    headline: ['Pay only for work', "you're delighted with."],
    body: 'Funds are held in secure escrow until each milestone is approved. Built-in contracts define scope, timeline, and deliverables — legally enforceable in 40+ countries. Dispute resolution is handled by our team.',
    proof: '72-hour dispute resolution guarantee.',
    cta: { label: 'See How Payments Work', href: '/how-it-works' },
    imageRight: true,
    visual: (
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-lg">
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-800">Milestone Progress</span>
          <span className="text-xs text-green-600 font-medium">3 of 4 complete</span>
        </div>
        {[
          { label: 'Requirements & Design', status: 'PAID', amount: '$1,200' },
          { label: 'Frontend Build', status: 'PAID', amount: '$2,400' },
          { label: 'Backend Integration', status: 'IN_PROGRESS', amount: '$1,800' },
          { label: 'Testing & Launch', status: 'PENDING', amount: '$600' },
        ].map((m, i) => (
          <div key={i} className="mb-2 flex items-center gap-3">
            <div className={`h-5 w-5 rounded-full flex items-center justify-center flex-shrink-0 ${
              m.status === 'PAID' ? 'bg-green-100' :
              m.status === 'IN_PROGRESS' ? 'bg-blue-100' : 'bg-slate-100'
            }`}>
              <div className={`h-2 w-2 rounded-full ${
                m.status === 'PAID' ? 'bg-green-500' :
                m.status === 'IN_PROGRESS' ? 'bg-blue-500' : 'bg-slate-300'
              }`} />
            </div>
            <span className="flex-1 text-xs text-slate-600 truncate">{m.label}</span>
            <span className={`text-xs font-semibold ${m.status === 'PAID' ? 'text-green-600' : 'text-slate-400'}`}>
              {m.amount}
            </span>
          </div>
        ))}
        <div className="mt-3 rounded-xl bg-green-50 px-3 py-2 text-xs text-green-700 font-medium text-center">
          ✓ $0 lost to disputes in 2024
        </div>
      </div>
    ),
  },
  {
    badge: 'Full Visibility',
    badgeBg: 'bg-blue-50 text-blue-700 border-blue-200',
    icon: LayoutDashboard,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    headline: ['Always know exactly', 'where your project stands.'],
    body: 'Track milestones, message your expert, review deliverables, and release payments — all from one clean dashboard. No email threads. No status update meetings. Just results.',
    proof: 'Teams save 5.2 hours/week on project management.',
    cta: { label: 'Explore the Dashboard', href: '/auth/register' },
    imageRight: false,
    visual: (
      <div className="rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden">
        <div className="flex h-8 items-center gap-1.5 border-b border-slate-100 px-3">
          <div className="h-2.5 w-2.5 rounded-full bg-red-400" />
          <div className="h-2.5 w-2.5 rounded-full bg-amber-400" />
          <div className="h-2.5 w-2.5 rounded-full bg-green-400" />
          <div className="ml-2 h-3.5 flex-1 rounded-full bg-slate-100" />
        </div>
        <div className="grid grid-cols-3 gap-2 p-4">
          {[
            { label: 'Earnings', value: '$24,800', delta: '+12%', color: 'text-green-600' },
            { label: 'Projects', value: '3 Active', delta: '', color: 'text-blue-600' },
            { label: 'Rating', value: '4.9★', delta: '', color: 'text-amber-500' },
          ].map(stat => (
            <div key={stat.label} className="rounded-xl border border-slate-100 p-2.5">
              <p className="mb-1 text-[10px] uppercase tracking-wide text-slate-400">{stat.label}</p>
              <p className="text-sm font-bold text-slate-800">{stat.value}</p>
              {stat.delta && <p className={`text-[10px] font-medium ${stat.color}`}>{stat.delta}</p>}
            </div>
          ))}
        </div>
        <div className="px-4 pb-4">
          <div className="flex h-16 items-end gap-1">
            {[40, 55, 45, 70, 60, 80, 75, 90, 85, 95, 88, 100].map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-sm bg-primary-200"
                style={{ height: `${h}%` }}
              />
            ))}
          </div>
        </div>
      </div>
    ),
  },
]

export function FeatureSections() {
  return (
    <section className="section bg-slate-50" aria-labelledby="features-heading">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">
            Why ExpertSpork
          </p>
          <h2
            id="features-heading"
            className="text-4xl font-bold tracking-tight text-slate-900"
          >
            Everything you need.
            <br />Nothing you don&apos;t.
          </h2>
        </div>

        <div className="space-y-24">
          {FEATURES.map((feature, i) => (
            <div
              key={i}
              className={`flex flex-col items-center gap-12 lg:flex-row ${feature.imageRight ? 'lg:flex-row-reverse' : ''}`}
            >
              {/* Content */}
              <div className="flex-1 max-w-xl">
                <span
                  className={`mb-4 inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${feature.badgeBg}`}
                >
                  {feature.badge}
                </span>

                <h3 className="mb-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                  {feature.headline[0]}
                  <br />
                  {feature.headline[1]}
                </h3>

                <p className="mb-6 text-lg leading-relaxed text-slate-500">
                  {feature.body}
                </p>

                <div className="mb-8 inline-flex items-center gap-2 rounded-xl bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary-500" aria-hidden="true" />
                  {feature.proof}
                </div>

                <Button
                  asChild
                  variant="primary"
                  rightIcon={<ArrowRight className="h-4 w-4" />}
                >
                  <Link href={feature.cta.href}>{feature.cta.label}</Link>
                </Button>
              </div>

              {/* Visual */}
              <div className="flex-1 w-full max-w-lg">
                {feature.visual}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
