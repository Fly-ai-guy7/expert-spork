import React from 'react'
import { Star } from 'lucide-react'
import { Avatar } from '@/components/ui/Avatar'

const TESTIMONIALS = [
  {
    body: "We hired a senior React developer for our product launch in 48 hours. The AI match was eerily accurate — Priya was the exact fit we needed. We've re-hired her three times since.",
    author: 'Marcus T.',
    title: 'CTO at Launchpad AI',
    avatar: null,
    badge: 'Hired 7 experts',
    rating: 5,
    type: 'client',
  },
  {
    body: "ExpertSpork is the only platform where I don't feel like a commodity. Clients come pre-qualified, the contracts protect me, and I've 3x'd my income in 14 months.",
    author: 'Sarah Chen',
    title: 'Lead Product Designer',
    avatar: null,
    badge: '$280K earned',
    rating: 5,
    type: 'expert',
  },
  {
    body: "The escrow system gave us the confidence to hire our first freelancer. Milestones kept everything on track. Genuinely the smoothest agency experience we've ever had.",
    author: 'Jess R.',
    title: 'Founder at Marble Studio',
    avatar: null,
    badge: '100% completion rate',
    rating: 5,
    type: 'client',
  },
]

const METRICS = [
  { value: '$48M+',  label: 'Expert Earnings (2024)' },
  { value: '12K+',   label: 'Active Vetted Experts' },
  { value: '98%',    label: 'On-Time Delivery Rate' },
  { value: '4.9★',   label: 'Average Platform Rating' },
]

export function Testimonials() {
  return (
    <section className="section bg-white" aria-labelledby="testimonials-heading">
      <div className="container">
        {/* Header */}
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">
            What Our Community Says
          </p>
          <h2
            id="testimonials-heading"
            className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl"
          >
            They trusted ExpertSpork.
            <br />Now they won&apos;t work any other way.
          </h2>
        </div>

        {/* Testimonial cards */}
        <div className="mb-20 grid gap-6 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <figure
              key={i}
              className="flex flex-col rounded-2xl border border-slate-200 bg-slate-50 p-6 transition-all duration-200 hover:shadow-md"
            >
              {/* Stars */}
              <div className="mb-4 flex gap-0.5" aria-label={`${t.rating} stars`}>
                {[...Array(5)].map((_, j) => (
                  <Star
                    key={j}
                    className={`h-4 w-4 ${j < t.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}`}
                    aria-hidden="true"
                  />
                ))}
              </div>

              {/* Quote */}
              <blockquote className="mb-6 flex-1 text-sm leading-relaxed text-slate-700">
                &ldquo;{t.body}&rdquo;
              </blockquote>

              {/* Author */}
              <figcaption className="flex items-center gap-3">
                <Avatar
                  name={t.author}
                  size="sm"
                />
                <div>
                  <p className="text-sm font-semibold text-slate-900">{t.author}</p>
                  <p className="text-xs text-slate-500">{t.title}</p>
                </div>
                <div className="ml-auto">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-[11px] font-medium ${
                      t.type === 'expert'
                        ? 'bg-green-50 text-green-700'
                        : 'bg-blue-50 text-blue-700'
                    }`}
                  >
                    {t.badge}
                  </span>
                </div>
              </figcaption>
            </figure>
          ))}
        </div>

        {/* Metrics row */}
        <div className="grid grid-cols-2 gap-6 rounded-2xl bg-slate-900 p-8 lg:grid-cols-4">
          {METRICS.map(metric => (
            <div key={metric.label} className="text-center">
              <p className="mb-1 text-3xl font-black text-white sm:text-4xl">{metric.value}</p>
              <p className="text-sm text-slate-400">{metric.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
