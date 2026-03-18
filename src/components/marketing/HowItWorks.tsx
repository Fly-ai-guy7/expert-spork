import React from 'react'
import { ClipboardList, Sparkles, Shield } from 'lucide-react'

const STEPS = [
  {
    step: '01',
    icon: ClipboardList,
    iconBg: 'bg-blue-50',
    iconColor: 'text-primary-600',
    title: 'Post Your Project',
    body: 'Describe what you need — or let our AI write the brief. We\'ll surface the right experts within hours, not weeks.',
  },
  {
    step: '02',
    icon: Sparkles,
    iconBg: 'bg-purple-50',
    iconColor: 'text-purple-600',
    title: 'Match with Top Talent',
    body: 'Our AI scores and ranks candidates by fit — not just keywords. Interview, review portfolios, and hire with confidence.',
  },
  {
    step: '03',
    icon: Shield,
    iconBg: 'bg-green-50',
    iconColor: 'text-green-600',
    title: 'Pay with Total Protection',
    body: 'Funds are held in escrow until you approve each milestone. Release payment only when the work is exactly right.',
  },
]

export function HowItWorks() {
  return (
    <section className="section bg-white" aria-labelledby="how-it-works-heading">
      <div className="container">
        {/* Section header */}
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">
            How It Works
          </p>
          <h2
            id="how-it-works-heading"
            className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl"
          >
            From brief to brilliant.
            <br />In three steps.
          </h2>
        </div>

        {/* Steps grid */}
        <div className="relative">
          {/* Connector line (desktop) */}
          <div
            className="absolute top-12 left-0 right-0 hidden h-px bg-gradient-to-r from-transparent via-slate-200 to-transparent lg:block"
            aria-hidden="true"
          />

          <ol className="grid gap-8 lg:grid-cols-3">
            {STEPS.map((step, i) => (
              <li key={step.step} className="relative flex flex-col items-start">
                {/* Step number (mobile connector) */}
                {i < STEPS.length - 1 && (
                  <div
                    className="absolute left-6 top-16 h-full w-px bg-slate-200 lg:hidden"
                    aria-hidden="true"
                  />
                )}

                <div className="mb-6 flex items-start gap-4 lg:flex-col">
                  {/* Icon circle */}
                  <div
                    className={`relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${step.iconBg} shadow-sm`}
                    aria-hidden="true"
                  >
                    <step.icon className={`h-6 w-6 ${step.iconColor}`} />
                    <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-slate-900 text-[10px] font-bold text-white">
                      {i + 1}
                    </span>
                  </div>

                  <div className="lg:mt-4">
                    <h3 className="mb-2 text-xl font-bold text-slate-900">{step.title}</h3>
                    <p className="text-base leading-relaxed text-slate-500">{step.body}</p>
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  )
}
