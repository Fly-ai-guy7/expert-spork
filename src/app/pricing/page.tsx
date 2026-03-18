import type { Metadata } from 'next'
import { TopNav } from '@/components/layout/TopNav'
import { Footer } from '@/components/layout/Footer'
import { PricingTeaser } from '@/components/marketing/PricingTeaser'
import { CTABanner } from '@/components/marketing/CTABanner'
import { FAQSection } from '@/components/marketing/FAQSection'

export const metadata: Metadata = {
  title: 'Pricing — ExpertSpork',
  description: 'Transparent, honest pricing. Free to post, 8% fee. Pro plan at $49/month with 5% fee and priority matching.',
}

export default function PricingPage() {
  return (
    <>
      <TopNav />
      <div className="pt-16">
        <div className="bg-gradient-to-b from-slate-50 to-white py-16">
          <div className="container text-center">
            <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-600">Pricing</p>
            <h1 className="text-5xl font-black tracking-tight text-slate-900">
              Honest pricing.
              <br />
              No surprises.
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-lg text-slate-500">
              Free to post a project. Pay a platform fee only when you hire.
              Upgrade to Pro and save on every transaction.
            </p>
          </div>
        </div>
        <PricingTeaser />
        <FAQSection />
        <CTABanner />
        <Footer />
      </div>
    </>
  )
}
