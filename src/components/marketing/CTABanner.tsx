import React from 'react'
import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'

export function CTABanner() {
  return (
    <section
      className="relative overflow-hidden bg-gradient-to-br from-primary-700 via-primary-800 to-slate-900 py-20"
      aria-labelledby="cta-heading"
    >
      {/* Decorative grid pattern */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(to right, rgba(255,255,255,0.1) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
        }}
        aria-hidden="true"
      />

      {/* Radial glow */}
      <div
        className="absolute inset-x-0 top-0 h-64 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,rgba(99,179,237,0.15),transparent)]"
        aria-hidden="true"
      />

      <div className="container relative text-center">
        <h2
          id="cta-heading"
          className="mb-4 text-4xl font-black tracking-tight text-white sm:text-5xl lg:text-6xl"
        >
          Stop settling for average.
          <br />
          <span className="bg-gradient-to-r from-blue-300 to-indigo-300 bg-clip-text text-transparent">
            Hire exceptional.
          </span>
        </h2>

        <p className="mx-auto mb-10 max-w-2xl text-lg text-blue-200">
          Join 8,000+ companies that have shipped better products, faster — with
          ExpertSpork&apos;s AI-powered talent network.
        </p>

        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button
            asChild
            size="xl"
            className="bg-white text-primary-700 hover:bg-blue-50 hover:text-primary-800 border-transparent shadow-lg"
            rightIcon={<ArrowRight className="h-5 w-5" />}
          >
            <Link href="/explore">Find Your Expert Now</Link>
          </Button>
          <Button asChild size="xl" variant="outline-white">
            <Link href="/how-it-works">See How It Works</Link>
          </Button>
        </div>

        <p className="mt-6 text-sm text-blue-300">
          Free to post · No subscription required · 14-day Pro trial
        </p>
      </div>
    </section>
  )
}
