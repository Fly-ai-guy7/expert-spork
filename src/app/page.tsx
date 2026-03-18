import type { Metadata } from 'next'
import { TopNav } from '@/components/layout/TopNav'
import { Hero } from '@/components/marketing/Hero'
import { HowItWorks } from '@/components/marketing/HowItWorks'
import { FeaturedExperts } from '@/components/marketing/FeaturedExperts'
import { FeatureSections } from '@/components/marketing/FeatureSections'
import { Testimonials } from '@/components/marketing/Testimonials'
import { PricingTeaser } from '@/components/marketing/PricingTeaser'
import { FAQSection } from '@/components/marketing/FAQSection'
import { CTABanner } from '@/components/marketing/CTABanner'
import { Footer } from '@/components/layout/Footer'
import { TrustBar } from '@/components/marketing/TrustBar'

export const metadata: Metadata = {
  title: 'ExpertSpork — Work with the Best. Get Paid What You\'re Worth.',
}

// JSON-LD Structured Data
const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'ExpertSpork',
  url: 'https://expertspork.com',
  description: 'AI-powered freelancer marketplace connecting world-class talent with ambitious companies.',
  potentialAction: {
    '@type': 'SearchAction',
    target: 'https://expertspork.com/explore?q={search_term_string}',
    'query-input': 'required name=search_term_string',
  },
}

const orgJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'ExpertSpork',
  url: 'https://expertspork.com',
  logo: 'https://expertspork.com/logo.png',
  sameAs: [
    'https://twitter.com/expertspork',
    'https://linkedin.com/company/expertspork',
    'https://github.com/expertspork',
  ],
  contactPoint: {
    '@type': 'ContactPoint',
    contactType: 'customer support',
    email: 'support@expertspork.com',
  },
}

export default function LandingPage() {
  return (
    <>
      {/* Structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(orgJsonLd) }}
      />

      <TopNav />

      <div className="pt-16"> {/* offset for fixed nav */}
        <Hero />
        <TrustBar />
        <HowItWorks />
        <FeaturedExperts />
        <FeatureSections />
        <Testimonials />
        <PricingTeaser />
        <FAQSection />
        <CTABanner />
        <Footer />
      </div>
    </>
  )
}
