import type { Metadata } from 'next'
import { TopNav } from '@/components/layout/TopNav'
import { Footer } from '@/components/layout/Footer'
import { HowItWorks } from '@/components/marketing/HowItWorks'
import { FeatureSections } from '@/components/marketing/FeatureSections'
import { CTABanner } from '@/components/marketing/CTABanner'

export const metadata: Metadata = {
  title: 'How It Works — ExpertSpork',
  description: 'Learn how ExpertSpork connects clients with top-tier freelance experts using AI matching, escrow payments, and milestone-based contracts.',
}

export default function HowItWorksPage() {
  return (
    <>
      <TopNav />
      <div className="pt-16">
        <div className="bg-gradient-to-b from-slate-50 to-white py-16">
          <div className="container text-center">
            <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">How It Works</p>
            <h1 className="text-5xl font-black tracking-tight text-slate-900">
              The smarter way to
              <br />hire and get hired.
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-500">
              ExpertSpork combines AI precision with human expertise to make freelancing
              faster, safer, and more rewarding for everyone.
            </p>
          </div>
        </div>
        <HowItWorks />
        <FeatureSections />
        <CTABanner />
        <Footer />
      </div>
    </>
  )
}
