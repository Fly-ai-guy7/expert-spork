import type { Metadata } from 'next'
import { RegisterForm } from '@/components/auth/RegisterForm'
import { Zap, Shield, Star, Users } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Create Account — ExpertSpork',
  description: 'Join ExpertSpork. Post projects or become a vetted expert. Free to get started.',
  robots: { index: false, follow: false },
}

const SOCIAL_PROOF = [
  { icon: Users,  text: '12,000+ active experts' },
  { icon: Shield, text: 'Escrow payment protection' },
  { icon: Star,   text: '4.9★ average rating' },
]

export default function RegisterPage() {
  return (
    <div className="flex min-h-screen">
      {/* Left brand panel */}
      <div className="relative hidden w-[45%] overflow-hidden bg-gradient-to-br from-primary-800 via-primary-700 to-indigo-800 lg:flex lg:flex-col lg:justify-between lg:p-12">
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.5) 1px, transparent 1px)',
            backgroundSize: '32px 32px',
          }}
          aria-hidden="true"
        />

        {/* Logo */}
        <div className="relative flex items-center gap-2 text-white">
          <Zap className="h-7 w-7 fill-white/90" aria-hidden="true" />
          <span className="text-xl font-bold">ExpertSpork</span>
        </div>

        {/* Quote */}
        <div className="relative">
          <blockquote className="mb-8">
            <p className="text-3xl font-bold leading-tight text-white">
              &ldquo;The best freelancer I&apos;ve ever worked with — and I found them in 6 hours.&rdquo;
            </p>
            <footer className="mt-4 text-blue-200">
              — Alex M., Founder at Launchly
            </footer>
          </blockquote>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { value: '$48M+', label: 'Expert earnings' },
              { value: '12K+',  label: 'Vetted experts' },
              { value: '98%',   label: 'On-time delivery' },
            ].map(stat => (
              <div key={stat.label} className="rounded-xl bg-white/10 p-4 text-center">
                <p className="text-2xl font-black text-white">{stat.value}</p>
                <p className="text-xs text-blue-200">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Social proof avatars */}
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="flex -space-x-2">
              {['S', 'M', 'A', 'J', 'P'].map((letter, i) => (
                <div
                  key={i}
                  className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-primary-700 bg-primary-500 text-xs font-bold text-white"
                  aria-hidden="true"
                >
                  {letter}
                </div>
              ))}
            </div>
            <p className="text-sm text-blue-200">
              Join <strong className="text-white">12,000+ experts</strong> already earning more
            </p>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex flex-1 flex-col items-center justify-center px-4 py-12 sm:px-8 lg:px-12">
        {/* Mobile logo */}
        <div className="mb-8 flex items-center gap-2 lg:hidden">
          <Zap className="h-6 w-6 fill-primary-600 text-primary-600" aria-hidden="true" />
          <span className="text-lg font-bold text-slate-900">ExpertSpork</span>
        </div>

        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Join ExpertSpork.</h1>
            <p className="mt-2 text-slate-500">Create your free account in 60 seconds.</p>
          </div>

          <RegisterForm />

          {/* Social proof mobile */}
          <div className="mt-8 flex flex-wrap justify-center gap-4 lg:hidden">
            {SOCIAL_PROOF.map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-1.5 text-xs text-slate-500">
                <Icon className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
