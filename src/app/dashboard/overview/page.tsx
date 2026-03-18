import React from 'react'
import { DollarSign, FolderOpen, Star, Eye } from 'lucide-react'
import { StatsCard } from '@/components/dashboard/StatsCard'

// In production: fetch from API
const MOCK_STATS = [
  {
    label: 'Total Earnings',
    value: '$24,800',
    delta: 12.4,
    icon: <DollarSign className="h-5 w-5 text-green-600" />,
    iconBg: 'bg-green-100',
  },
  {
    label: 'Active Projects',
    value: '3',
    delta: 0,
    icon: <FolderOpen className="h-5 w-5 text-primary-600" />,
    iconBg: 'bg-primary-100',
  },
  {
    label: 'Avg Rating',
    value: '4.9 ★',
    delta: 2.1,
    icon: <Star className="h-5 w-5 text-amber-500" />,
    iconBg: 'bg-amber-100',
  },
  {
    label: 'Profile Views',
    value: '1,240',
    delta: 8.7,
    icon: <Eye className="h-5 w-5 text-purple-600" />,
    iconBg: 'bg-purple-100',
  },
]

const MOCK_PROJECTS = [
  { id: '1', title: 'Brand Redesign — SaaS Dashboard', client: 'Marcus T.', milestone: '2 of 4', progress: 50, status: 'In Progress', due: 'Jun 12' },
  { id: '2', title: 'E-commerce Frontend Build',       client: 'Priya S.',  milestone: '1 of 3', progress: 33, status: 'Under Review', due: 'Jun 18' },
  { id: '3', title: 'Mobile App MVP — React Native',   client: 'James R.',  milestone: '3 of 5', progress: 60, status: 'In Progress', due: 'Jul 2' },
]

const MOCK_MILESTONES = [
  { title: 'Wireframes Delivery',    amount: '$1,200', due: 'Jun 10', status: 'SUBMITTED',   project: 'Brand Redesign' },
  { title: 'Frontend Components',    amount: '$2,400', due: 'Jun 14', status: 'IN_PROGRESS', project: 'E-commerce Frontend' },
  { title: 'API Integration',        amount: '$1,800', due: 'Jun 20', status: 'PENDING',     project: 'Mobile App MVP' },
]

const statusStyles = {
  'In Progress':   'bg-blue-50 text-blue-700',
  'Under Review':  'bg-amber-50 text-amber-700',
  'Completed':     'bg-green-50 text-green-700',
}

const milestoneStatusColor = {
  SUBMITTED:   'bg-purple-500',
  IN_PROGRESS: 'bg-blue-500',
  PENDING:     'bg-slate-300',
  FUNDED:      'bg-green-400',
  PAID:        'bg-green-600',
}

export default function DashboardOverviewPage() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Good morning, Sarah 👋</h1>
        <p className="text-sm text-slate-500">Here&apos;s what&apos;s happening with your projects today.</p>
      </div>

      {/* Stats row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {MOCK_STATS.map(stat => (
          <StatsCard key={stat.label} {...stat} />
        ))}
      </div>

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Active projects — 3 cols */}
        <section className="lg:col-span-3" aria-labelledby="active-projects-heading">
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <h2 id="active-projects-heading" className="font-semibold text-slate-900">
                Active Projects
              </h2>
              <a href="/dashboard/projects" className="text-xs font-medium text-primary-600 hover:underline">
                View all
              </a>
            </div>
            <div className="divide-y divide-slate-100">
              {MOCK_PROJECTS.map(project => (
                <div key={project.id} className="flex items-center gap-4 px-5 py-4 hover:bg-slate-50 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{project.title}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{project.client} · Milestone {project.milestone}</p>
                    {/* Progress bar */}
                    <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-primary-500 transition-all"
                        style={{ width: `${project.progress}%` }}
                        role="progressbar"
                        aria-valuenow={project.progress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`${project.progress}% complete`}
                      />
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 shrink-0">
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[project.status as keyof typeof statusStyles] ?? 'bg-slate-100 text-slate-600'}`}
                    >
                      {project.status}
                    </span>
                    <span className="text-xs text-slate-400">Due {project.due}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Milestones — 2 cols */}
        <section className="lg:col-span-2" aria-labelledby="milestones-heading">
          <div className="rounded-xl border border-slate-200 bg-white">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
              <h2 id="milestones-heading" className="font-semibold text-slate-900">
                Upcoming Milestones
              </h2>
            </div>
            <div className="p-5">
              <ol className="relative border-l border-slate-200 pl-5 space-y-5">
                {MOCK_MILESTONES.map((m, i) => (
                  <li key={i} className="relative">
                    {/* Timeline dot */}
                    <div
                      className={`absolute -left-[21px] h-3.5 w-3.5 rounded-full border-2 border-white ${milestoneStatusColor[m.status as keyof typeof milestoneStatusColor] ?? 'bg-slate-300'}`}
                      aria-hidden="true"
                    />
                    <p className="text-xs text-slate-400 mb-0.5">{m.due}</p>
                    <p className="text-sm font-medium text-slate-800">{m.title}</p>
                    <p className="text-xs text-slate-500">{m.project}</p>
                    <p className="mt-1 text-sm font-semibold text-primary-600">{m.amount}</p>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
