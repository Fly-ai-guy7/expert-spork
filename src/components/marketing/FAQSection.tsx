'use client'

import React, { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

const FAQS = [
  {
    q: 'How does ExpertSpork vet its experts?',
    a: 'Every expert goes through a rigorous 3-stage vetting process: skills assessment, portfolio review, and a live video interview with our team. Less than 3% of applicants are accepted. Experts also maintain a minimum 4.7★ rating or their profiles are suspended.',
  },
  {
    q: 'How does escrow payment work?',
    a: "When you approve a contract, you fund the agreed milestone amount into our secure escrow account. The expert begins work. When you approve the deliverable, funds are released instantly to the expert. If there's a dispute, our team mediates within 72 hours.",
  },
  {
    q: "What's the platform fee?",
    a: 'Clients on the free plan pay an 8% fee per transaction. Pro clients pay 5%. Experts pay nothing — we believe talent should keep what they earn.',
  },
  {
    q: 'How quickly can I hire?',
    a: 'Most clients receive AI-matched expert recommendations within 2 hours of posting a project. Our fastest hire was 14 minutes. Average is 6 hours.',
  },
  {
    q: 'Can I hire the same expert again?',
    a: "Absolutely. Repeat hires are one-click from your dashboard. We even auto-fill the project brief and contract from your history. Many clients build long-term relationships with their experts.",
  },
  {
    q: "What if the work isn't what I expected?",
    a: "Milestone-based contracts mean you review work before paying. If quality doesn't meet the agreed scope, you can request revisions or open a dispute. Our team will resolve it fairly within 72 hours.",
  },
  {
    q: 'Do experts work globally?',
    a: 'Yes. Our experts are based in 60+ countries, covering every timezone. All contracts are in USD and legally enforceable internationally.',
  },
  {
    q: 'Is there a minimum project size?',
    a: 'No minimum. We support everything from a 2-hour consultation ($50) to a 12-month product build ($500,000+). Our platform scales to your needs.',
  },
]

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const toggle = (i: number) => setOpenIndex(openIndex === i ? null : i)

  return (
    <section className="section bg-slate-50" aria-labelledby="faq-heading">
      {/* JSON-LD FAQPage schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: FAQS.map(faq => ({
              '@type': 'Question',
              name: faq.q,
              acceptedAnswer: { '@type': 'Answer', text: faq.a },
            })),
          }),
        }}
      />

      <div className="container">
        <div className="mx-auto max-w-3xl">
          {/* Header */}
          <div className="mb-12 text-center">
            <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">
              FAQ
            </p>
            <h2
              id="faq-heading"
              className="text-4xl font-bold tracking-tight text-slate-900"
            >
              Questions? Answered.
            </h2>
          </div>

          {/* Accordion */}
          <dl className="divide-y divide-slate-200 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xs">
            {FAQS.map((faq, i) => (
              <div key={i}>
                <dt>
                  <button
                    type="button"
                    className={cn(
                      'flex w-full items-center justify-between gap-4 px-6 py-5 text-left font-medium text-slate-900 transition-colors duration-200',
                      openIndex === i ? 'text-primary-700' : 'hover:bg-slate-50'
                    )}
                    onClick={() => toggle(i)}
                    aria-expanded={openIndex === i}
                    aria-controls={`faq-answer-${i}`}
                  >
                    <span>{faq.q}</span>
                    <ChevronDown
                      className={cn(
                        'h-5 w-5 shrink-0 text-slate-400 transition-transform duration-300',
                        openIndex === i && 'rotate-180 text-primary-600'
                      )}
                      aria-hidden="true"
                    />
                  </button>
                </dt>
                <dd
                  id={`faq-answer-${i}`}
                  role="region"
                  className={cn(
                    'overflow-hidden transition-all duration-300',
                    openIndex === i ? 'max-h-96' : 'max-h-0'
                  )}
                >
                  <p className="px-6 pb-5 text-sm leading-relaxed text-slate-600">
                    {faq.a}
                  </p>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  )
}
