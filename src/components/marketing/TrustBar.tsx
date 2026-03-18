import React from 'react'

const BRANDS = [
  'Stripe', 'Notion', 'Linear', 'Figma', 'Vercel', 'Loom', 'Intercom', 'Webflow',
]

export function TrustBar() {
  return (
    <section
      className="border-y border-slate-100 bg-white py-10"
      aria-label="Trusted by leading companies"
    >
      <div className="container">
        <p className="mb-8 text-center text-xs font-semibold uppercase tracking-widest text-slate-400">
          Trusted by teams at
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-10 gap-y-6">
          {BRANDS.map(brand => (
            <div
              key={brand}
              className="text-lg font-bold text-slate-300 transition-colors duration-200 hover:text-slate-500"
              aria-label={brand}
            >
              {brand}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
