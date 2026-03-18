import React from 'react'
import Link from 'next/link'
import { Check, Zap } from 'lucide-react'
import { Button } from '@/components/ui/Button'

const FREE_FEATURES = [
  'Unlimited project posts',
  'AI-powered expert matching',
  'Escrow payment protection',
  'Basic dashboard analytics',
  'Email support',
]

const PRO_FEATURES = [
  'Everything in Free',
  'Reduced 5% platform fee',
  'Priority AI matching (< 2hr)',
  'Dedicated account manager',
  'Team member access (up to 5)',
  'Advanced analytics + exports',
  'Private talent pool',
  'Custom contract templates',
]

export function PricingTeaser() {
  return (
    <section className="section bg-white" aria-labelledby="pricing-heading">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">
            Pricing
          </p>
          <h2
            id="pricing-heading"
            className="text-4xl font-bold tracking-tight text-slate-900"
          >
            Transparent pricing.
            <br />No hidden fees. Ever.
          </h2>
        </div>

        <div className="mx-auto grid max-w-4xl gap-6 lg:grid-cols-2">
          {/* Free Plan */}
          <div className="rounded-2xl border border-slate-200 bg-white p-8">
            <div className="mb-6">
              <h3 className="mb-1 text-xl font-bold text-slate-900">Free to Post</h3>
              <div className="flex items-baseline gap-1">
                <span className="text-5xl font-black text-slate-900">$0</span>
                <span className="text-slate-500">/month</span>
              </div>
              <p className="mt-2 text-sm text-slate-500">
                Post unlimited projects. Pay only when you hire.
                <br />
                <strong className="text-slate-700">Platform fee: 8%</strong> per transaction.
              </p>
            </div>

            <ul className="mb-8 space-y-3">
              {FREE_FEATURES.map(feature => (
                <li key={feature} className="flex items-center gap-3 text-sm text-slate-700">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100">
                    <Check className="h-3 w-3 text-slate-600" aria-hidden="true" />
                  </div>
                  {feature}
                </li>
              ))}
            </ul>

            <Button asChild variant="secondary" className="w-full">
              <Link href="/auth/register">Post a Project Free</Link>
            </Button>
          </div>

          {/* Pro Plan */}
          <div className="relative rounded-2xl border-2 border-primary-500 bg-white p-8 shadow-lg">
            {/* Popular badge */}
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-600 px-4 py-1.5 text-xs font-bold text-white shadow-md">
                <Zap className="h-3 w-3 fill-current" aria-hidden="true" />
                Most Popular
              </span>
            </div>

            <div className="mb-6">
              <h3 className="mb-1 text-xl font-bold text-slate-900">ExpertSpork Pro</h3>
              <div className="flex items-baseline gap-1">
                <span className="text-5xl font-black text-slate-900">$49</span>
                <span className="text-slate-500">/month</span>
              </div>
              <p className="mt-1 text-sm text-slate-500">
                Billed annually at{' '}
                <strong className="text-slate-700">$39/month</strong>. Save 20%.
              </p>
              <p className="mt-2 text-sm text-slate-500">
                <strong className="text-primary-700">Platform fee: 5%</strong>
                {' '}— save 37% vs free.
              </p>
            </div>

            <ul className="mb-8 space-y-3">
              {PRO_FEATURES.map((feature, i) => (
                <li key={feature} className="flex items-center gap-3 text-sm text-slate-700">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary-100">
                    <Check className="h-3 w-3 text-primary-600" aria-hidden="true" />
                  </div>
                  <span className={i === 0 ? 'font-medium' : ''}>{feature}</span>
                </li>
              ))}
            </ul>

            <Button asChild className="w-full" size="lg">
              <Link href="/auth/register?plan=pro">Start Pro Free for 14 Days</Link>
            </Button>
            <p className="mt-3 text-center text-xs text-slate-400">
              No credit card required · Cancel anytime
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
